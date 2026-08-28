from extensions import db
from models import Ingredient


INGREDIENTS = [
    {"name": "tomate"},
    {"name": "oignon"},
    {"name": "ail"},
    {"name": "carotte"},
    {"name": "courgette"},
    {"name": "poivron"},
    {"name": "aubergine"},
    {"name": "pomme de terre"},
    {"name": "champignon"},
    {"name": "épinards"},
    {"name": "brocoli"},
    {"name": "avocat"},
    {"name": "citron"},
    {"name": "persil"},
    {"name": "basilic"},
    {"name": "thym"},
    {"name": "poulet"},
    {"name": "boeuf"},
    {"name": "porc"},
    {"name": "saumon"},
    {"name": "thon"},
    {"name": "oeuf"},
    {"name": "lait"},
    {"name": "beurre"},
    {"name": "crème fraîche"},
    {"name": "fromage"},
    {"name": "mozzarella"},
    {"name": "parmesan"},
    {"name": "farine"},
    {"name": "sucre"},
    {"name": "sel"},
    {"name": "poivre"},
    {"name": "huile d'olive"},
    {"name": "vinaigre"},
    {"name": "riz"},
    {"name": "pâtes"},
    {"name": "pain"},
    {"name": "tomates concassées"},
    {"name": "lait de coco"},
]


def seed_ingredients():
    for ingredient_data in INGREDIENTS:
        name = ingredient_data["name"].capitalize()

        ingredient = db.session.scalar(
            db.select(Ingredient).where(
                Ingredient.name.ilike(name)
            )
        )

        if ingredient is None:
            db.session.add(
                Ingredient(**ingredient_data)
            )

    db.session.commit()