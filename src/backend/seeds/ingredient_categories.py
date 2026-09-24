from extensions import db
from models import IngredientCategory


INGREDIENT_GROUPS = {
    "Légumes": "tomate,oignon,ail,carotte,courgette,poivron,aubergine,pomme de terre,champignon,épinards,brocoli,tomates concassées",
    "Fruits": "avocat,citron",
    "Herbes et épices": "persil,basilic,thym,sel,poivre",
    "Viandes": "poulet,boeuf,porc",
    "Poissons": "saumon,thon",
    "Œufs et produits laitiers": "oeuf,lait,beurre,crème fraîche,fromage,mozzarella,parmesan",
    "Céréales et féculents": "farine,riz,pâtes,pain",
    "Épicerie": "sucre,huile d'olive,vinaigre,lait de coco",
    "Autres": "",
}


def category_name_for(name):
    return next((category for category, names in INGREDIENT_GROUPS.items()
                 if name.casefold() in names.split(",")), "Autres")


def seed_ingredient_categories():
    for name in INGREDIENT_GROUPS:
        if db.session.scalar(db.select(IngredientCategory).filter_by(name=name)) is None:
            db.session.add(IngredientCategory(name=name))
    db.session.commit()
