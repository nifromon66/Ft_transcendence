from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Category, Recipe, User
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

    instructions = data.get("instructions")
    if instructions is not None:
        if not isinstance(instructions, str):
            return jsonify(
                {"success": False, "error": "Les instructions doivent être du texte"}
            ), 400
        instructions = instructions.strip() or None

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

    recipe = Recipe(
        user=user,
        category=category,
        title=title,
        description=description,
        cooking_time=cooking_time,
        difficulty=difficulty,
        instructions=instructions,
    )

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
