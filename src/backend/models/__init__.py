from extensions import db

from .admin_audit import AdminAudit
from .association import RecipeIngredient, UserBadge, recipe_tag
from .badge import Badge
from .category import Category
from .comment import Comment
from .favorite import Favorite
from .ingredient import Ingredient
from .ingredient_category import IngredientCategory
from .message import Message
from .rating import Rating
from .recipe import Recipe
from .recipe_step import RecipeStep
from .tag import Tag
from .user import User
from .user_avatar_frame import UserAvatarFrame

__all__ = [
    "AdminAudit",
    "Badge",
    "Category",
    "Comment",
    "Favorite",
    "Ingredient",
    "IngredientCategory",
    "Message",
    "Rating",
    "Recipe",
    "RecipeIngredient",
    "RecipeStep",
    "Tag",
    "User",
    "UserAvatarFrame",
    "UserBadge",
    "db",
    "recipe_tag",
]
