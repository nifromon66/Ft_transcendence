from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Category, Ingredient, Recipe, RecipeIngredient, RecipeStep, Tag, User, Utensil
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


recipe_bp = Blueprint("recipes", __name__)

ALLOWED_DIFFICULTIES = {"facile", "moyen", "difficile"}


@recipe_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = db.session.execute(
        select(Category).order_by(Category.name)
    ).scalars().all()

    return jsonify(
        {
            "success": True,
            "categories": [
                {"id": category.id, "name": category.name}
                for category in categories
            ],
        }
    ), 200


@recipe_bp.route("/ingredients", methods=["GET"])
def get_ingredients():
    ingredients = db.session.execute(
        select(Ingredient).order_by(Ingredient.name)
    ).scalars().all()

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
    utensils = db.session.execute(
        select(Utensil).order_by(Utensil.name)
    ).scalars().all()

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
    tags = db.session.execute(
        select(Tag).order_by(Tag.name)
    ).scalars().all()

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
    recipes = db.session.execute(
        select(Recipe)
        .order_by(Recipe.created_at.desc())
        .limit(4)
    ).scalars().all()

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


@recipe_bp.route("/recipes", methods=["POST"])
@jwt_required()
def create_recipe():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {"success": False, "error": "Aucune donnée JSON valide fournie"}
        ), 400

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify(
            {"success": False, "error": "Le titre est requis"}
        ), 400

    title = title.strip()
    if len(title) > 150:
        return jsonify(
            {"success": False, "error": "Le titre ne peut pas dépasser 150 caractères"}
        ), 400

    category_id = data.get("category_id")
    if not isinstance(category_id, int) or isinstance(category_id, bool):
        return jsonify(
            {"success": False, "error": "La catégorie est requise"}
        ), 400

    description = data.get("description")
    if description is not None:
        if not isinstance(description, str):
            return jsonify(
                {"success": False, "error": "La description doit être du texte"}
            ), 400
        description = description.strip() or None
        if description is not None and len(description) > 100:
            return jsonify(
                {
                    "success": False,
                    "error": "La description ne peut pas dépasser 100 caractères",
                }
            ), 400

    cooking_time = data.get("cooking_time")
    if cooking_time is not None:
        if (
            not isinstance(cooking_time, int)
            or isinstance(cooking_time, bool)
            or cooking_time < 0
        ):
            return jsonify(
                {
                    "success": False,
                    "error": "Le temps de préparation doit être un entier positif",
                }
            ), 400

    difficulty = data.get("difficulty")
    if difficulty == "":
        difficulty = None
    if difficulty is not None and difficulty not in ALLOWED_DIFFICULTIES:
        return jsonify(
            {"success": False, "error": "La difficulté est invalide"}
        ), 400

    steps_data = data.get("steps")
    if not isinstance(steps_data, list) or not steps_data:
        return jsonify(
            {
                "success": False,
                "error": "La recette doit contenir au moins une étape",
            }
        ), 400

    step_descriptions = []

    for index, step_data in enumerate(steps_data, start=1):
        if not isinstance(step_data, dict):
            return jsonify(
                {
                    "success": False,
                    "error": f"L'étape {index} est invalide",
                }
            ), 400

        step_description = step_data.get("description")

        if not isinstance(step_description, str) or not step_description.strip():
            return jsonify(
                {
                    "success": False,
                    "error": f"La description de l'étape {index} est requise",
                }
            ), 400

        step_descriptions.append(step_description.strip())

    ingredients_data = data.get("ingredients")

    if not isinstance(ingredients_data, list) or not ingredients_data:
        return jsonify(
            {
                "success": False,
                "error": "La recette doit contenir au moins un ingrédient",
            }
        ), 400

    ingredient_entries = []
    selected_ingredient_ids = set()

    for index, ingredient_data in enumerate(ingredients_data, start=1):
        if not isinstance(ingredient_data, dict):
            return jsonify(
                {
                    "success": False,
                    "error": f"L'ingrédient {index} est invalide",
                }
            ), 400

        ingredient_id = ingredient_data.get("ingredient_id")

        if not isinstance(ingredient_id, int) or isinstance(ingredient_id, bool):
            return jsonify(
                {
                    "success": False,
                    "error": f"L'ingrédient {index} est requis",
                }
            ), 400

        if ingredient_id in selected_ingredient_ids:
            return jsonify(
                {
                    "success": False,
                    "error": "Un ingrédient ne peut pas être ajouté deux fois",
                }
            ), 400

        quantity = ingredient_data.get("quantity")

        if quantity is not None:
            if not isinstance(quantity, str):
                return jsonify(
                    {
                        "success": False,
                        "error": f"La quantité de l'ingrédient {index} est invalide",
                    }
                ), 400

            quantity = quantity.strip() or None

        selected_ingredient_ids.add(ingredient_id)
        ingredient_entries.append(
            {
                "ingredient_id": ingredient_id,
                "quantity": quantity,
            }
        )

    utensil_ids = data.get("utensil_ids")

    if not isinstance(utensil_ids, list) or not utensil_ids:
        return jsonify(
            {
                "success": False,
                "error": "La recette doit contenir au moins un ustensile",
            }
        ), 400

    if any(
        not isinstance(utensil_id, int) or isinstance(utensil_id, bool)
        for utensil_id in utensil_ids
    ):
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ustensiles sont invalides",
            }
        ), 400

    selected_utensil_ids = set(utensil_ids)

    if len(selected_utensil_ids) != len(utensil_ids):
        return jsonify(
            {
                "success": False,
                "error": "Un ustensile ne peut pas être ajouté deux fois",
            }
        ), 400

    tag_ids = data.get("tag_ids")

    if not isinstance(tag_ids, list) or not tag_ids:
        return jsonify(
            {
                "success": False,
                "error": "La recette doit contenir au moins un tag",
            }
        ), 400

    if any(
        not isinstance(tag_id, int) or isinstance(tag_id, bool)
        for tag_id in tag_ids
    ):
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs tags sont invalides",
            }
        ), 400

    selected_tag_ids = set(tag_ids)

    if len(selected_tag_ids) != len(tag_ids):
        return jsonify(
            {
                "success": False,
                "error": "Un tag ne peut pas être ajouté deux fois",
            }
        ), 400

    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify(
            {"success": False, "error": "Utilisateur non authentifié"}
        ), 401

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify(
            {"success": False, "error": "Utilisateur introuvable"}
        ), 404

    category = db.session.get(Category, category_id)
    if category is None:
        return jsonify(
            {"success": False, "error": "Catégorie introuvable"}
        ), 404

    ingredients = db.session.execute(
        select(Ingredient).where(
            Ingredient.id.in_(selected_ingredient_ids)
        )
    ).scalars().all()

    utensils = db.session.execute(
        select(Utensil).where(
            Utensil.id.in_(selected_utensil_ids)
        )
    ).scalars().all()

    tags = db.session.execute(
        select(Tag).where(
            Tag.id.in_(selected_tag_ids)
        )
    ).scalars().all()

    ingredients_by_id = {
        ingredient.id: ingredient
        for ingredient in ingredients
    }

    utensils_by_id = {
        utensil.id: utensil
        for utensil in utensils
    }

    tags_by_id = {
        tag.id: tag
        for tag in tags
    }

    missing_ingredient_ids = (
        selected_ingredient_ids - ingredients_by_id.keys()
    )

    if missing_ingredient_ids:
        return jsonify(
            {
                "success": False,
                "error": "Un ou plusieurs ingrédients sont introuvables",
            }
        ), 404

    missing_utensil_ids = (
        selected_utensil_ids - utensils_by_id.keys()
    )

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

    recipe.utensils = [
        utensils_by_id[utensil_id]
        for utensil_id in utensil_ids
    ]

    recipe.tags = [
        tags_by_id[tag_id]
        for tag_id in tag_ids
    ]

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
        }
    ), 201
