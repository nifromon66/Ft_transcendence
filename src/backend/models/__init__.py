from extensions import db

from .user import User
from .badge import Badge
from .recipe import Recipe
from .category import Category
from .ingredient import Ingredient
from .utensil import Utensil
from .tag import Tag
from .comment import Comment
from .favorite import Favorite
from .rating import Rating

from .association import (
    UserBadge,
    RecipeIngredient,
    RecipeUtensil,
    RecipeTag
)