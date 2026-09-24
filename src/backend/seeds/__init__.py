from .badges import seed_badges
from .users import seed_users
from .categories import seed_categories
from .ingredients import seed_ingredients
from .ingredient_categories import seed_ingredient_categories
from .utensils import seed_utensils
from .tags import seed_tags
from .recipes import seed_recipes


def seed_database():
    seed_badges()
    seed_users()
    seed_categories()
    seed_ingredient_categories()
    seed_ingredients()
    seed_utensils()
    seed_tags()
    seed_recipes()