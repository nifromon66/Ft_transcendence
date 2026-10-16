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
    Rating,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    Tag,
    User,
)
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .analysis import check_recipe_analysis
from user_xp_management.experience import (
    RECIPE_CREATED_XP,
    RECIPE_RATED_XP,
    add_xp,
    remove_xp,
)
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
        ), 200

    title = validated["title"]
    category_id = validated["category_id"]
    description = validated["description"]
    cooking_time = validated["cooking_time"]
    difficulty = validated["difficulty"]

    step_descriptions = validated["step_descriptions"]
    ingredient_entries = validated["ingredients"]
    tag_ids = validated["tag_ids"]

    selected_ingredient_ids = {entry["ingredient_id"] for entry in ingredient_entries}
    selected_tag_ids = set(tag_ids)

    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Utilisateur non authentifié"}), 200

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200

    category = db.session.get(Category, category_id)
    if category is None:
        return jsonify({"success": False, "error": "Catégorie introuvable"}), 200

    ingredients = (
        db.session.execute(
            select(Ingredient).where(Ingredient.id.in_(selected_ingredient_ids))
        )
        .scalars()
        .all()
    )

    tags = (
        db.session.execute(select(Tag).where(Tag.id.in_(selected_tag_ids)))
        .scalars()
        .all()
    )

    ingredients_by_id = {ingredient.id: ingredient for ingredient in ingredients}
    tags_by_id = {tag.id: tag for tag in tags}

    missing_ingredient_ids = selected_ingredient_ids - ingredients_by_id.keys()
    if missing_ingredient_ids:
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ingrédients sont introuvables",
            }
        ), 200

    missing_tag_ids = selected_tag_ids - tags_by_id.keys()
    if missing_tag_ids:
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs tags sont introuvables",
            }
        ), 200

    analysis_error = check_recipe_analysis(validated, ingredients_by_id)
    if analysis_error is not None:
        return analysis_error

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

    db.session.add_all(ingredient_associations)

    recipe.tags = [tags_by_id[tag_id] for tag_id in tag_ids]

    try:
        db.session.add(recipe)
        add_xp(user_id, RECIPE_CREATED_XP)
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
        return jsonify({"success": False, "error": f"File too large (Max {max_mb}MB)"}), 200

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 200

    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 200

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 200

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 200

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
        ), 200

    if "file" not in request.files:
        return jsonify(
            {
                "success": False,
                "error": "Aucun fichier dans la requête",
            }
        ), 200

    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 200

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 200

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 200

    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe.id:
        return jsonify(
            {
                "success": False,
                "error": "Étape introuvable pour cette recette",
            }
        ), 200

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
        ), 200

    user_id = get_jwt_identity()

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 200

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": "Tu ne peux modifier que tes propres recettes",
            }
        ), 200

    data = request.get_json(silent=True)

    try:
        validated = validate_recipe_payload(data)
    except RecipeValidationError as error:
        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 200

    title = validated["title"]
    category_id = validated["category_id"]
    description = validated["description"]
    cooking_time = validated["cooking_time"]
    difficulty = validated["difficulty"]

    step_entries = validated["steps"]
    ingredient_entries = validated["ingredients"]
    tag_ids = validated["tag_ids"]

    selected_ingredient_ids = {entry["ingredient_id"] for entry in ingredient_entries}
    selected_tag_ids = set(tag_ids)

    category = db.session.get(Category, category_id)

    if category is None:
        return jsonify(
            {
                "success": False,
                "error": "Catégorie introuvable",
            }
        ), 200

    ingredients = (
        db.session.execute(
            select(Ingredient).where(Ingredient.id.in_(selected_ingredient_ids))
        )
        .scalars()
        .all()
    )

    tags = (
        db.session.execute(select(Tag).where(Tag.id.in_(selected_tag_ids)))
        .scalars()
        .all()
    )

    ingredients_by_id = {ingredient.id: ingredient for ingredient in ingredients}

    tags_by_id = {tag.id: tag for tag in tags}

    if selected_ingredient_ids - ingredients_by_id.keys():
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ingrédients sont introuvables",
            }
        ), 200

    if selected_tag_ids - tags_by_id.keys():
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs tags sont introuvables",
            }
        ), 200

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
        ), 200

    analysis_error = check_recipe_analysis(validated, ingredients_by_id)
    if analysis_error is not None:
        return analysis_error

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

        db.session.add_all(ingredient_associations)

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
        ), 200

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 200

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 200

    if not recipe.image_filename:
        return jsonify(
            {
                "success": False,
                "error": "Cette recette n'a pas d'image",
            }
        ), 200

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
        ), 200

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 200

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": ("Tu ne peux modifier que tes propres recettes"),
            }
        ), 200

    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe.id:
        return jsonify(
            {
                "success": False,
                "error": "Étape introuvable pour cette recette",
            }
        ), 200

    if not step.image_filename:
        return jsonify(
            {
                "success": False,
                "error": "Cette étape n'a pas d'image",
            }
        ), 200

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
        sort_by
        sort_order
    """

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    sort_by = request.args.get("sort_by", "").strip()
    sort_order = request.args.get("sort_order", "").strip()

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

        query = query.where(
            or_(
                Recipe.title.ilike(search_pattern),
                Recipe.description.ilike(search_pattern),

                Recipe.ingredients.any(
                    Ingredient.name.ilike(search_pattern)
                ),

                Recipe.tags.any(
                    Tag.name.ilike(search_pattern)
                ),
            )
        )

    if category:
        query = query.join(Recipe.category).where(Category.name.ilike(category))

    if difficulty:
        query = query.where(Recipe.difficulty.ilike(difficulty))

    if sort_by == "rating":
        column = (
            select(func.avg(Rating.score))
            .where(Rating.recipe_id == Recipe.id)
            .scalar_subquery()
        )
    elif sort_by == "cooking_time":
        column = Recipe.cooking_time
    elif sort_by == "random":
        column = func.random()
    else:
        column = func.coalesce(Recipe.updated_at, Recipe.created_at)

    if sort_order.upper() == "DESC":
        column = column.desc().nulls_last() if sort_by == "rating" else column.desc()
    else:
        column = column.asc().nulls_last() if sort_by == "rating" else column.asc()

    query = query.order_by(column)

    total = db.session.scalar(
        db.select(db.func.count()).select_from(query.order_by(None).subquery())
    )

    offset = (page - 1) * per_page

    query = query.offset(offset).limit(per_page)

    recipes = db.session.scalars(query).unique().all()
    # print("recipes:", [recipe.id for recipe in recipes], flush=True)

    return jsonify(
        {
            "recipes": [recipe.to_dict() for recipe in recipes],
            "page": page,
            "per_page": per_page,
            "count": len(recipes),
            "total": total,
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
                    "rating": (
                        round(
                            sum(rating.score for rating in recipe.ratings)
                            / len(recipe.ratings),
                            1,
                        )
                        if recipe.ratings
                        else None
                    ),
                }
                for recipe in recipes
            ],
        }
    ), 200


@recipes_bp.route("/<int:recipe_id>", methods=["GET"])
@jwt_required(optional=True)
def get_recipe(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 200

    my_rating = None
    identity = get_jwt_identity()

    if identity is not None:
        user_id = int(identity)

        rating = db.session.scalar(
            select(Rating).where(
                Rating.user_id == user_id,
                Rating.recipe_id == recipe_id,
            )
        )

        if rating is not None:
            my_rating = rating.score

    return jsonify(
        {
            "success": True,
            "recipe": {
                "id": recipe.id,
                "my_rating": my_rating,
                "rating": (
                    round(sum(r.score for r in recipe.ratings) / len(recipe.ratings), 1)
                    if recipe.ratings
                    else None
                ),
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
                    "avatar_url": (
                        f"/api/users/avatars/{recipe.user.avatar_filename}"
                        if recipe.user.avatar_filename
                        else None
                    ),
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
                        "category_id": recipe_ingredient.ingredient.category_id,
                        "quantity": recipe_ingredient.quantity,
                    }
                    for recipe_ingredient in recipe.ingredients
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


@recipes_bp.route("/<int:recipe_id>", methods=["DELETE"])
@jwt_required()
def delete_recipe(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 200

    user_id = get_jwt_identity()

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 200

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": "Tu ne peux supprimer que tes propres recettes",
            }
        ), 200

    image_paths = [step.image_filename for step in recipe.steps if step.image_filename]

    if recipe.image_filename:
        image_paths.append(recipe.image_filename)

    try:
        db.session.delete(recipe)
        remove_xp(user_id, RECIPE_CREATED_XP)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "error": "Impossible de supprimer la recette",
            }
        ), 500

    for filename in image_paths:
        try:
            delete_file_physically(filename)
            delete_empty_parent_directory(filename)
        except OSError as error:
            current_app.logger.error(
                f"Impossible de supprimer l'image {filename} : {error!s}"
            )

    return jsonify({"success": True}), 200


@recipes_bp.route("/<int:recipe_id>/ratings", methods=["POST"])
@jwt_required()
def rate_recipe(recipe_id: int):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Utilisateur non authentifié"}), 200

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200

    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return jsonify({"success": False, "error": "Recette introuvable"}), 200
    if recipe.user_id == user_id:
        return jsonify(
            {"success": False, "error": "Tu ne peux pas noter ta propre recette"}
        ), 200

    existing_rating = db.session.scalar(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.recipe_id == recipe_id,
        )
    )

    if existing_rating is not None:
        return jsonify(
            {
                "success": False,
                "error": "Tu as déjà noté cette recette",
            }
        ), 200

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "success": False,
                "error": "Un objet JSON est attendu",
            }
        ), 200

    score = data.get("score")

    if type(score) is not int or not 1 <= score <= 5:
        return jsonify(
            {
                "success": False,
                "error": "La note doit être un entier entre 1 et 5",
            }
        ), 200

    rating = Rating(
        user_id=user_id,
        recipe_id=recipe_id,
        score=score,
    )

    try:
        db.session.add(rating)
        add_xp(user_id, RECIPE_RATED_XP)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        existing_rating = db.session.scalar(
            select(Rating).where(
                Rating.user_id == user_id,
                Rating.recipe_id == recipe_id,
            )
        )

        if existing_rating is not None:
            return jsonify(
                {
                    "success": False,
                    "error": "Tu as déjà noté cette recette",
                }
            ), 200

        return jsonify(
            {
                "success": False,
                "error": "Impossible d’enregistrer la note",
            }
        ), 500
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "error": "Impossible d’enregistrer la note",
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "score": rating.score,
        }
    ), 201


@recipes_bp.route("/<int:recipe_id>/ratings", methods=["DELETE"])
@jwt_required()
def delete_recipe_rating(recipe_id: int):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Utilisateur non authentifié"}), 200

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200

    rating = db.session.scalar(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.recipe_id == recipe_id,
        )
    )

    if rating is None:
        return jsonify(
            {
                "success": False,
                "error": "Tu n’as pas encore noté cette recette",
            }
        ), 200

    try:
        db.session.delete(rating)
        remove_xp(user_id, RECIPE_RATED_XP)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "error": "Impossible de supprimer la note",
            }
        ), 500

    return jsonify({"success": True}), 200


@recipes_bp.route("/<int:recipe_id>/ratings", methods=["PUT"])
@jwt_required()
def update_recipe_rating(recipe_id: int):
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Utilisateur non authentifié"}), 200

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200

    rating = db.session.scalar(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.recipe_id == recipe_id,
        )
    )

    if rating is None:
        return jsonify(
            {
                "success": False,
                "error": "Tu n’as pas encore noté cette recette",
            }
        ), 200

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "success": False,
                "error": "Un objet JSON est attendu",
            }
        ), 200

    score = data.get("score")

    if type(score) is not int or not 1 <= score <= 5:
        return jsonify(
            {
                "success": False,
                "error": "La note doit être un entier entre 1 et 5",
            }
        ), 200

    rating.update_score(score)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "error": "Impossible de modifier la note",
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "score": rating.score,
        }
    ), 200


@recipes_bp.route("/<int:recipe_id>/image", methods=["GET"])
def get_public_recipe_image(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None or not recipe.image_filename:
        return jsonify({"success": False, "error": "Image introuvable"}), 200

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
        ), 200

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify(
            {
                "success": False,
                "error": "Image illisible",
            }
        ), 200

    if mimetype not in ALLOWED_RECIPE_IMAGE_MIMETYPES:
        return jsonify(
            {
                "success": False,
                "error": "Type d'image non autorisé",
            }
        ), 200

    return send_from_directory(
        recipe_upload_folder,
        recipe.image_filename,
        mimetype=mimetype,
    )


@recipes_bp.route("/<int:recipe_id>/steps/<int:step_id>/image", methods=["GET"])
def get_public_recipe_step_image(recipe_id: int, step_id: int):
    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe_id or not step.image_filename:
        return jsonify({"success": False, "error": "Image d'étape introuvable"}), 200

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
        ), 200

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify(
            {
                "success": False,
                "error": "Image illisible",
            }
        ), 200

    if mimetype not in ALLOWED_RECIPE_IMAGE_MIMETYPES:
        return jsonify(
            {
                "success": False,
                "error": "Type d'image non autorisé",
            }
        ), 200

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
