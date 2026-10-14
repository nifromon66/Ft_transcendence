# for search func

from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.category import Category
from models.ingredient import Ingredient
from models.recipe import Recipe
from models.tag import Tag
from sqlalchemy import or_

recipes_bp = Blueprint("recipes_bp", __name__, url_prefix="/recipes")


@recipes_bp.get("")
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

    # if sort_by=="updated_at":
    column=Recipe.updated_at
    if sort_by=="cooking_time":
        column=Recipe.cooking_time

    if sort_order.upper()=="DESC":
        column=column.desc()
    else:
        column=column.asc()

    query = query.order_by(column)

    total = db.session.scalar(
        db.select(db.func.count()).select_from(
            query.order_by(None).subquery()
        )
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

