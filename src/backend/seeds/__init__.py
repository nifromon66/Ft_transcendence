from .badges import seed_badges
from .categories import seed_categories
from .ingredient_categories import seed_ingredient_categories
from .ingredients import seed_ingredients
from .recipes import seed_recipes
from .tags import seed_tags
from .users import seed_users
from .utensils import seed_utensils


def seed_database():
    seed_badges()
    seed_users()
    seed_categories()
    seed_ingredient_categories()
    seed_ingredients()
    seed_utensils()
    seed_tags()
    seed_recipes()
