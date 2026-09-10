from extensions import db
from models import Category
from models.category import CategoryType

CATEGORIES = [
    (CategoryType.ENTREES, "Entrées"),
    (CategoryType.PLATS_PRINCIPAUX, "Plats principaux"),
    (CategoryType.ACCOMPAGNEMENTS, "Accompagnements"),
    (CategoryType.SALADES, "Salades"),
    (CategoryType.SOUPES, "Soupes"),
    (CategoryType.SAUCES, "Sauces"),
    (CategoryType.SANDWICHS, "Sandwichs"),
    (CategoryType.PIZZAS, "Pizzas"),
    (CategoryType.PATES, "Pâtes"),
    (CategoryType.PLATS_DE_RIZ, "Plats de riz"),
    (CategoryType.GRATINS, "Gratins"),
    (CategoryType.TARTES_SALEES, "Tartes salées"),
    (CategoryType.DESSERTS, "Desserts"),
    (CategoryType.PATISSERIES, "Pâtisseries"),
    (CategoryType.BOISSONS, "Boissons"),
]


def seed_categories():
    for category_id, name in CATEGORIES:
        category = db.session.get(Category, category_id)
        if category is None:
            db.session.add(
                Category(
                    id=category_id,
                    name=name,
                )
            )

    db.session.commit()
