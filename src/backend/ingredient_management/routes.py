from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import Ingredient, IngredientCategory, RecipeIngredient
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .analysis import check_ingredient_analysis

ingredient_bp = Blueprint("ingredients", __name__)


@ingredient_bp.route("/ingredient-categories", methods=["GET"])
def get_ingredient_categories():
    categories = db.session.scalars(
        select(IngredientCategory).order_by(IngredientCategory.name)
    ).all()
    return jsonify(
        {
            "success": True,
            "ingredient_categories": [
                {"id": category.id, "name": category.name} for category in categories
            ],
        }
    ), 200


@ingredient_bp.route("/ingredients", methods=["GET"])
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
                    "category_id": ingredient.category_id,
                }
                for ingredient in ingredients
            ],
        }
    ), 200


@ingredient_bp.route("/ingredients", methods=["POST"])
@jwt_required()
def create_ingredient():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Données invalides"}), 200
    name = data.get("name")
    category_id = data.get("category_id")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
        return jsonify(
            {
                "success": False,
                "error": "Le nom doit contenir entre 1 et 100 caractères",
            }
        ), 200
    if not isinstance(category_id, int) or isinstance(category_id, bool):
        return jsonify({"success": False, "error": "Catégorie invalide"}), 200
    category = db.session.get(IngredientCategory, category_id)
    if category is None:
        return jsonify({"success": False, "error": "Catégorie introuvable"}), 200
    name = name.strip().capitalize()
    existing = db.session.scalar(
        select(Ingredient).where(func.lower(Ingredient.name) == name.lower())
    )
    if existing is not None:
        return jsonify(
            {
                "success": False,
                "error": f"Cet ingrédient existe déjà dans la catégorie « {existing.category.name} »",
            }
        ), 200
    analysis_error = check_ingredient_analysis(name, category.name)
    if analysis_error is not None:
        return analysis_error
    ingredient = Ingredient(name=name, category_id=category_id)
    try:
        db.session.add(ingredient)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Cet ingrédient existe déjà"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Impossible de créer l'ingrédient"}
        ), 200
    return jsonify(
        {
            "success": True,
            "ingredient": {
                "id": ingredient.id,
                "name": ingredient.name,
                "category_id": ingredient.category_id,
            },
        }
    ), 201


@ingredient_bp.route("/ingredients/<int:ingredient_id>", methods=["PUT"])
@jwt_required()
def update_ingredient(ingredient_id: int):
    ingredient = db.session.get(Ingredient, ingredient_id)
    if ingredient is None:
        return jsonify({"success": False, "error": "Ingrédient introuvable"}), 200

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Données invalides"}), 200
    name = data.get("name")
    category_id = data.get("category_id")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
        return jsonify(
            {
                "success": False,
                "error": "Le nom doit contenir entre 1 et 100 caractères",
            }
        ), 200
    if not isinstance(category_id, int) or isinstance(category_id, bool):
        return jsonify({"success": False, "error": "Catégorie invalide"}), 200
    if db.session.get(IngredientCategory, category_id) is None:
        return jsonify({"success": False, "error": "Catégorie introuvable"}), 200

    name = name.strip().capitalize()
    existing = db.session.scalar(
        select(Ingredient).where(
            func.lower(Ingredient.name) == name.lower(),
            Ingredient.id != ingredient_id,
        )
    )
    if existing is not None:
        return jsonify({"success": False, "error": "Cet ingrédient existe déjà"}), 200

    try:
        ingredient.name = name
        ingredient.category_id = category_id
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Cet ingrédient existe déjà"}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Impossible de modifier l'ingrédient"}
        ), 200

    return jsonify(
        {
            "success": True,
            "ingredient": {
                "id": ingredient.id,
                "name": ingredient.name,
                "category_id": ingredient.category_id,
            },
        }
    ), 200


@ingredient_bp.route("/ingredients/<int:ingredient_id>", methods=["DELETE"])
@jwt_required()
def delete_ingredient(ingredient_id: int):
    ingredient = db.session.get(Ingredient, ingredient_id)
    if ingredient is None:
        return jsonify({"success": False, "error": "Ingrédient introuvable"}), 200

    used = db.session.scalar(
        select(RecipeIngredient.ingredient_id)
        .where(RecipeIngredient.ingredient_id == ingredient_id)
        .limit(1)
    )
    if used is not None:
        return jsonify(
            {"success": False, "error": "Cet ingrédient est utilisé dans une recette"}
        ), 200

    try:
        db.session.delete(ingredient)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Cet ingrédient est utilisé dans une recette"}
        ), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Impossible de supprimer l'ingrédient"}
        ), 200

    return jsonify({"success": True}), 200
