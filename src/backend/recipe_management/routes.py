from extensions import db
from file_upload_management.services import (
    delete_empty_parent_directory,
    delete_file_physically,
)
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
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
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .validators import (
    RecipeValidationError,
    validate_recipe_payload,
)

recipe_bp = Blueprint("recipes", __name__)


@recipe_bp.route("/categories", methods=["GET"])
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


@recipe_bp.route("/ingredients", methods=["GET"])
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


@recipe_bp.route("/utensils", methods=["GET"])
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


@recipe_bp.route("/tags", methods=["GET"])
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


@recipe_bp.route("/recipes/latest", methods=["GET"])
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
                    "image_url": recipe.image_url,
                }
                for recipe in recipes
            ],
        }
    ), 200


@recipe_bp.route("/recipes/<int:recipe_id>", methods=["GET"])
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
                "image_url": recipe.image_url,
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
                        "image_url": step.image_url,
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


@recipe_bp.route("/recipes/<int:recipe_id>", methods=["PUT"])
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
        step.image_url
        for step_id, step in existing_steps_by_id.items()
        if (step_id not in requested_step_ids and step.image_url)
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


@recipe_bp.route("/recipes", methods=["POST"])
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
