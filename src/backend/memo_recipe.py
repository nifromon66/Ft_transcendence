# TODO
# backend funcs to display recipes and relatived routers

from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Recipe

recipes_api = Blueprint("recipes_api", __name__)


@recipes_api.route("/recipe/<int:recipe_id>", methods=["GET"])
def display_recipe(recipe_id: int | None = None):
    if recipe_id is None:
        return jsonify({"error": "missing request id"}), 400

    recipe = db.session.scalar(db.select(Recipe).where(Recipe.id == recipe_id))

    if recipe is None:
        return jsonify({"error": "resource not found"}), 404

    return jsonify(recipe.to_dict()), 200
