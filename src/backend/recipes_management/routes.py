import os

import magic
from config import UPLOAD_FOLDER
from extensions import db
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from models import (
    Category,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    Tag,
    User,
    Utensil,
)
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from utils.file_services import (
    delete_empty_parent_directory,
    delete_file_physically,
    handle_file_upload,
)
from werkzeug.security import safe_join

from .constants import (
    ALLOWED_RECIPE_IMAGE_EXTENSIONS,
    ALLOWED_RECIPE_IMAGE_MIMETYPES,
    MAX_RECIPE_IMAGE_SIZE,
)
from .validators import (
    RecipeValidationError,
    validate_recipe_payload,
)

recipes_bp = Blueprint("recipes_management", __name__, url_prefix="/recipes")


@recipes_bp.route("", methods=["POST"])
@jwt_required()
def create_recipe():
    data = request.get_json(silent=True)

    try:
        validated = validate_recipe_payload(data)
    except RecipeValidationError as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 400

    title = validated["title"]
    category_id = validated["category_id"]
    description = validated["description"]
    cooking_time = validated["cooking_time"]
    difficulty = validated["difficulty"]

    step_descriptions = validated["step_descriptions"]
    ingredient_entries = validated["ingredients"]
    utensil_ids = validated["utensil_ids"]
    tag_ids = validated["tag_ids"]

    selected_ingredient_ids = {entry["ingredient_id"] for entry in ingredient_entries}
    selected_utensil_ids = set(utensil_ids)
    selected_tag_ids = set(tag_ids)

    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Utilisateur non authentifié"}), 401

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 404

    category = db.session.get(Category, category_id)
    if category is None:
        return jsonify({"success": False, "error": "Catégorie introuvable"}), 404

    ingredients = (
        db.session.execute(
            select(Ingredient).where(Ingredient.id.in_(selected_ingredient_ids))
        )
        .scalars()
        .all()
    )

    utensils = (
        db.session.execute(select(Utensil).where(Utensil.id.in_(selected_utensil_ids)))
        .scalars()
        .all()
    )

    tags = (
        db.session.execute(select(Tag).where(Tag.id.in_(selected_tag_ids)))
        .scalars()
        .all()
    )

    ingredients_by_id = {ingredient.id: ingredient for ingredient in ingredients}
    utensils_by_id = {utensil.id: utensil for utensil in utensils}
    tags_by_id = {tag.id: tag for tag in tags}

    missing_ingredient_ids = selected_ingredient_ids - ingredients_by_id.keys()
    if missing_ingredient_ids:
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ingrédients sont introuvables",
            }
        ), 404

    missing_utensil_ids = selected_utensil_ids - utensils_by_id.keys()
    if missing_utensil_ids:
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ustensiles sont introuvables",
            }
        ), 404

    missing_tag_ids = selected_tag_ids - tags_by_id.keys()
    if missing_tag_ids:
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs tags sont introuvables",
            }
        ), 404

    recipe_steps = [
        RecipeStep(
            step_number=index,
            description=step_description,
        )
        for index, step_description in enumerate(step_descriptions, start=1)
    ]

    recipe = Recipe(
        user=user,
        category=category,
        title=title,
        description=description,
        cooking_time=cooking_time,
        difficulty=difficulty,
        steps=recipe_steps,
    )

    ingredient_associations = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=ingredients_by_id[entry["ingredient_id"]],
            quantity=entry["quantity"],
        )
        for entry in ingredient_entries
    ]

    recipe.utensils = [utensils_by_id[utensil_id] for utensil_id in utensil_ids]
    recipe.tags = [tags_by_id[tag_id] for tag_id in tag_ids]

    try:
        db.session.add(recipe)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Impossible d'enregistrer la recette"}
        ), 500

    return jsonify(
        {
            "success": True,
            "id": recipe.id,
            "title": recipe.title,
            "steps": [
                {
                    "id": step.id,
                    "step_number": step.step_number,
                }
                for step in recipe.steps
            ],
        }
    ), 201


@recipes_bp.route("/<int:recipe_id>/image", methods=["POST"])
@jwt_required()
def upload_recipe_image(recipe_id: int):
    max_mb = MAX_RECIPE_IMAGE_SIZE // (1024 * 1024)

    if request.content_length and request.content_length > MAX_RECIPE_IMAGE_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 403

    file = request.files["file"]

    file_data, error_response, error_code = handle_file_upload(
        file,
        subfolder=f"recipes/{recipe.id}/cover",
        allowed_extensions=ALLOWED_RECIPE_IMAGE_EXTENSIONS,
        allowed_mimetypes=ALLOWED_RECIPE_IMAGE_MIMETYPES,
    )

    if error_response is not None:
        return error_response, error_code

    new_filename = file_data["filename"]
    old_filename = recipe.image_filename

    try:
        recipe.image_filename = new_filename
        db.session.commit()

    except SQLAlchemyError as error:
        db.session.rollback()

        try:
            delete_file_physically(new_filename)
            delete_empty_parent_directory(new_filename)
        except OSError as delete_error:
            current_app.logger.error(
                "Impossible de supprimer le nouveau fichier "
                f"après l'échec SQL : {delete_error!s}"
            )

        current_app.logger.error(
            f"Impossible d'enregistrer l'image de la recette : {error!s}"
        )

        return jsonify(
            {
                "success": False,
                "error": "Impossible d'enregistrer l'image de la recette",
            }
        ), 500

    if old_filename:
        try:
            delete_file_physically(old_filename)
            delete_empty_parent_directory(old_filename)
        except OSError as error:
            current_app.logger.error(
                f"L'ancienne image n'a pas pu être supprimée : {error!s}"
            )

    return jsonify(
        {
            **file_data,
            "image_url": f"/api/recipes/{recipe.id}/image",
        }
    ), 201


@recipes_bp.route("<int:recipe_id>/steps/<int:step_id>/image", methods=["POST"])
@jwt_required()
def upload_recipe_step_image(
    recipe_id: int,
    step_id: int,
):
    max_mb = MAX_RECIPE_IMAGE_SIZE // (1024 * 1024)

    if request.content_length and request.content_length > MAX_RECIPE_IMAGE_SIZE:
        return jsonify(
            {
                "success": False,
                "error": f"Fichier trop volumineux (Max {max_mb}MB)",
            }
        ), 413

    if "file" not in request.files:
        return jsonify(
            {
                "success": False,
                "error": "Aucun fichier dans la requête",
            }
        ), 400

    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 403

    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe.id:
        return jsonify(
            {
                "success": False,
                "error": "Étape introuvable pour cette recette",
            }
        ), 404

    file = request.files["file"]

    file_data, error_response, error_code = handle_file_upload(
        file,
        subfolder=(f"recipes/{recipe.id}/steps/{step.id}"),
        allowed_extensions=ALLOWED_RECIPE_IMAGE_EXTENSIONS,
        allowed_mimetypes=ALLOWED_RECIPE_IMAGE_MIMETYPES,
    )

    if error_response is not None:
        return error_response, error_code

    new_filename = file_data["filename"]
    old_filename = step.image_filename

    try:
        step.image_filename = new_filename
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        try:
            delete_file_physically(new_filename)
            delete_empty_parent_directory(new_filename)

        except OSError as delete_error:
            current_app.logger.error(
                f"Impossible de supprimer la nouvelle image d'étape : {delete_error!s}"
            )

        return jsonify(
            {
                "success": False,
                "error": "Impossible d'enregistrer l'image de l'étape",
            }
        ), 500

    if old_filename:
        try:
            delete_file_physically(old_filename)
        except OSError as error:
            current_app.logger.error(
                f"L'ancienne image de l'étape n'a pas pu être supprimée : {error!s}"
            )

    return jsonify(
        {
            **file_data,
            "image_url": f"/api/recipes/{recipe.id}/steps/{step.id}/image",
        }
    ), 201


@recipes_bp.route("/<int:recipe_id>", methods=["PUT"])
@jwt_required()
def update_recipe(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    user_id = get_jwt_identity()

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": "Tu ne peux modifier que tes propres recettes",
            }
        ), 403

    data = request.get_json(silent=True)

    try:
        validated = validate_recipe_payload(data)
    except RecipeValidationError as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 400

    title = validated["title"]
    category_id = validated["category_id"]
    description = validated["description"]
    cooking_time = validated["cooking_time"]
    difficulty = validated["difficulty"]

    step_entries = validated["steps"]
    ingredient_entries = validated["ingredients"]
    utensil_ids = validated["utensil_ids"]
    tag_ids = validated["tag_ids"]

    selected_ingredient_ids = {entry["ingredient_id"] for entry in ingredient_entries}

    selected_utensil_ids = set(utensil_ids)
    selected_tag_ids = set(tag_ids)

    category = db.session.get(Category, category_id)

    if category is None:
        return jsonify(
            {
                "success": False,
                "error": "Catégorie introuvable",
            }
        ), 404

    ingredients = (
        db.session.execute(
            select(Ingredient).where(Ingredient.id.in_(selected_ingredient_ids))
        )
        .scalars()
        .all()
    )

    utensils = (
        db.session.execute(select(Utensil).where(Utensil.id.in_(selected_utensil_ids)))
        .scalars()
        .all()
    )

    tags = (
        db.session.execute(select(Tag).where(Tag.id.in_(selected_tag_ids)))
        .scalars()
        .all()
    )

    ingredients_by_id = {ingredient.id: ingredient for ingredient in ingredients}

    utensils_by_id = {utensil.id: utensil for utensil in utensils}

    tags_by_id = {tag.id: tag for tag in tags}

    if selected_ingredient_ids - ingredients_by_id.keys():
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ingrédients sont introuvables",
            }
        ), 404

    if selected_utensil_ids - utensils_by_id.keys():
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ustensiles sont introuvables",
            }
        ), 404

    if selected_tag_ids - tags_by_id.keys():
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs tags sont introuvables",
            }
        ), 404

    existing_steps_by_id = {step.id: step for step in recipe.steps}

    requested_step_ids = {
        entry["id"] for entry in step_entries if entry["id"] is not None
    }

    missing_step_ids = requested_step_ids - existing_steps_by_id.keys()

    removed_step_images = [
        step.image_filename
        for step_id, step in existing_steps_by_id.items()
        if (step_id not in requested_step_ids and step.image_filename)
    ]

    if missing_step_ids:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Une ou plusieurs étapes sont introuvables pour cette recette"
                ),
            }
        ), 404

    recipe_steps = []

    for step_number, entry in enumerate(step_entries, start=1):
        step_id = entry["id"]

        if step_id is None:
            step = RecipeStep(
                step_number=step_number,
                description=entry["description"],
            )
        else:
            step = existing_steps_by_id[step_id]
            step.step_number = step_number
            step.description = entry["description"]

        recipe_steps.append(step)

    try:
        recipe.update(
            title=title,
            category=category,
            description=description,
            cooking_time=cooking_time,
            difficulty=difficulty,
            steps=recipe_steps,
        )

        recipe.ingredients.clear()
        db.session.flush()

        ingredient_associations = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredients_by_id[entry["ingredient_id"]],
                quantity=entry["quantity"],
            )
            for entry in ingredient_entries
        ]

        recipe.utensils = [utensils_by_id[utensil_id] for utensil_id in utensil_ids]

        recipe.tags = [tags_by_id[tag_id] for tag_id in tag_ids]

        db.session.add(recipe)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        return jsonify(
            {
                "success": False,
                "error": "Impossible de modifier la recette",
            }
        ), 500

    for filename in removed_step_images:
        try:
            delete_file_physically(filename)
            delete_empty_parent_directory(filename)
        except OSError as error:
            current_app.logger.error(
                "L'image d'une étape supprimée n'a pas pu être "
                f"retirée du disque : {error!s}"
            )

    return jsonify(
        {
            "success": True,
            "id": recipe.id,
            "title": recipe.title,
            "steps": [
                {
                    "id": step.id,
                    "step_number": step.step_number,
                }
                for step in recipe.steps
            ],
        }
    ), 200


@recipes_bp.route("/<int:recipe_id>/image", methods=["DELETE"])
@jwt_required()
def delete_recipe_image(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 403

    if not recipe.image_filename:
        return jsonify(
            {
                "success": False,
                "error": "Cette recette n'a pas d'image",
            }
        ), 404

    filename = recipe.image_filename

    try:
        recipe.image_filename = None
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()

        current_app.logger.error(
            f"Impossible de supprimer l'image de la recette : {error!s}"
        )

        return jsonify(
            {
                "success": False,
                "error": "Impossible de supprimer l'image de la recette",
            }
        ), 500

    try:
        delete_file_physically(filename)
        delete_empty_parent_directory(filename)
    except OSError:
        current_app.logger.error(
            "L'image a été retirée de la recette, mais le fichier n'a pas pu être supprimé : {error!s}"
        )

    return jsonify(
        {
            "success": True,
            "message": "Image de la recette supprimée",
        }
    ), 200


@recipes_bp.route("/<int:recipe_id>/steps/<int:step_id>/image", methods=["DELETE"])
@jwt_required()
def delete_recipe_step_image(
    recipe_id: int,
    step_id: int,
):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 403

    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe.id:
        return jsonify(
            {
                "success": False,
                "error": "Étape introuvable pour cette recette",
            }
        ), 404

    if not step.image_filename:
        return jsonify(
            {
                "success": False,
                "error": "Cette étape n'a pas d'image",
            }
        ), 404

    filename = step.image_filename

    try:
        step.image_filename = None
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()

        current_app.logger.error(
            f"Impossible de supprimer l'image de l'étape : {error!s}"
        )

        return jsonify(
            {
                "success": False,
                "error": "Impossible de supprimer l'image de l'étape",
            }
        ), 500

    try:
        delete_file_physically(filename)
        delete_empty_parent_directory(filename)

    except OSError as error:
        current_app.logger.error(
            "L'image a été retirée de l'étape, mais son fichier "
            f"n'a pas pu être supprimé : {error!s}"
        )

    return jsonify(
        {
            "success": True,
            "message": "Image de l'étape supprimée",
        }
    ), 200


@recipes_bp.route("", methods=["GET"])
def get_recipes():
    """
    get list of recipes

    surport:
        GET /recipes
        GET /recipes?search=chicken
        GET /recipes?category=dinner
        GET /recipes?search=chicken&category=dinner

    Query parameters:
        search
        category
        difficulty
        page
        per_page
    """

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    difficulty = request.args.get("difficulty", "").strip()

    try:
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(
            max(request.args.get("per_page", 20, type=int), 1),
            100,
        )
    except (TypeError, ValueError):
        page = 1
        per_page = 20

    query = db.select(Recipe)

    if search:
        search_pattern = f"%{search}%"

        query = (
            query.outerjoin(Recipe.ingredients)
            .outerjoin(Recipe.tags)
            .where(
                or_(
                    Recipe.title.ilike(search_pattern),
                    Recipe.description.ilike(search_pattern),
                    Ingredient.name.ilike(search_pattern),
                    Tag.name.ilike(search_pattern),
                )
            )
            .distinct()
        )

    if category:
        query = query.join(Recipe.category).where(Category.name.ilike(category))

    if difficulty:
        query = query.where(Recipe.difficulty.ilike(difficulty))

    offset = (page - 1) * per_page

    query = query.offset(offset).limit(per_page)

    recipes = db.session.scalars(query).unique().all()
    print("recipes:", [recipe.id for recipe in recipes], flush=True)

    return jsonify(
        {
            "recipes": [recipe.to_dict() for recipe in recipes],
            "page": page,
            "per_page": per_page,
            "count": len(recipes),
        }
    ), 200


@recipes_bp.route("/latest", methods=["GET"])
def get_latest_recipes():
    recipes = (
        db.session.execute(select(Recipe).order_by(Recipe.created_at.desc()).limit(4))
        .scalars()
        .all()
    )

    return jsonify(
        {
            "success": True,
            "recipes": [
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "description": recipe.description,
                    "cooking_time": recipe.cooking_time,
                    "image_url": f"/api/recipes/{recipe.id}/image"
                    if recipe.image_filename
                    else None,
                }
                for recipe in recipes
            ],
        }
    ), 200


@recipes_bp.route("/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "recipe": {
                "id": recipe.id,
                "title": recipe.title,
                "description": recipe.description,
                "cooking_time": recipe.cooking_time,
                "difficulty": recipe.difficulty,
                "image_url": f"/api/recipes/{recipe.id}/image"
                if recipe.image_filename
                else None,
                "created_at": recipe.created_at.isoformat(),
                "category": {
                    "id": recipe.category.id,
                    "name": recipe.category.name,
                },
                "author": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                },
                "steps": [
                    {
                        "id": step.id,
                        "step_number": step.step_number,
                        "description": step.description,
                        "image_url": f"/api/recipes/{recipe.id}/steps/{step.id}/image"
                        if step.image_filename
                        else None,
                    }
                    for step in recipe.steps
                ],
                "ingredients": [
                    {
                        "id": recipe_ingredient.ingredient.id,
                        "name": recipe_ingredient.ingredient.name,
                        "quantity": recipe_ingredient.quantity,
                    }
                    for recipe_ingredient in recipe.ingredients
                ],
                "utensils": [
                    {
                        "id": utensil.id,
                        "name": utensil.name,
                    }
                    for utensil in recipe.utensils
                ],
                "tags": [
                    {
                        "id": tag.id,
                        "name": tag.name,
                    }
                    for tag in recipe.tags
                ],
            },
        }
    ), 200


@recipes_bp.route("/<int:recipe_id>/image", methods=["GET"])
def get_public_recipe_image(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None or not recipe.image_filename:
        return jsonify({"success": False, "error": "Image introuvable"}), 404

    recipe_upload_folder = os.path.join(
        UPLOAD_FOLDER, "recipes", str(recipe.id), "cover"
    )

    file_path = safe_join(recipe_upload_folder, recipe.image_filename)

    if file_path is None or not os.path.isfile(file_path):
        return jsonify(
            {
                "success": False,
                "error": "Image introuvable",
            }
        ), 404

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify(
            {
                "success": False,
                "error": "Image illisible",
            }
        ), 404

    if mimetype not in ALLOWED_RECIPE_IMAGE_MIMETYPES:
        return jsonify(
            {
                "success": False,
                "error": "Type d'image non autorisé",
            }
        ), 415

    return send_from_directory(
        recipe_upload_folder,
        recipe.image_filename,
        mimetype=mimetype,
    )


@recipes_bp.route("/<int:recipe_id>/steps/<int:step_id>/image", methods=["GET"])
def get_public_recipe_step_image(recipe_id: int, step_id: int):
    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe_id or not step.image_filename:
        return jsonify({"success": False, "error": "Image d'étape introuvable"}), 404

    recipe_upload_folder = os.path.join(
        UPLOAD_FOLDER, "recipes", str(recipe_id), "steps", str(step.id)
    )
    file_path = safe_join(recipe_upload_folder, step.image_filename)

    if file_path is None or not os.path.isfile(file_path):
        return jsonify(
            {
                "success": False,
                "error": "Image introuvable",
            }
        ), 404

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify(
            {
                "success": False,
                "error": "Image illisible",
            }
        ), 404

    if mimetype not in ALLOWED_RECIPE_IMAGE_MIMETYPES:
        return jsonify(
            {
                "success": False,
                "error": "Type d'image non autorisé",
            }
        ), 415

    return send_from_directory(
        recipe_upload_folder,
        step.image_filename,
        mimetype=mimetype,
    )


@recipes_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = (
        db.session.execute(select(Category).order_by(Category.name)).scalars().all()
    )

    return jsonify(
        {
            "success": True,
            "categories": [
                {"id": category.id, "name": category.name} for category in categories
            ],
        }
    ), 200


@recipes_bp.route("/ingredients", methods=["GET"])
def get_ingredients():
    ingredients = (
        db.session.execute(select(Ingredient).order_by(Ingredient.name)).scalars().all()
    )

    return jsonify(
        {
            "success": True,
            "ingredients": [
                {
                    "id": ingredient.id,
                    "name": ingredient.name,
                }
                for ingredient in ingredients
            ],
        }
    ), 200


@recipes_bp.route("/utensils", methods=["GET"])
def get_utensils():
    utensils = (
        db.session.execute(select(Utensil).order_by(Utensil.name)).scalars().all()
    )

    return jsonify(
        {
            "success": True,
            "utensils": [
                {
                    "id": utensil.id,
                    "name": utensil.name,
                }
                for utensil in utensils
            ],
        }
    ), 200


@recipes_bp.route("/tags", methods=["GET"])
def get_tags():
    tags = db.session.execute(select(Tag).order_by(Tag.name)).scalars().all()

    return jsonify(
        {
            "success": True,
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                }
                for tag in tags
            ],
        }
    ), 200
