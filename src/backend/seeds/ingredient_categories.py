from extensions import db
from models import IngredientCategory

INGREDIENT_GROUPS = {
    "Légumes": "tomate,oignon,ail,carotte,courgette,poivron,aubergine,pomme de terre,champignon,épinards,brocoli,tomates concassées,échalote,radis,salade,ciboule,olive",
    "Fruits": "avocat,citron,citron vert,pomme",
    "Herbes et épices": "persil,basilic,thym,sel,poivre,coriandre,piment,piment d'espelette,cumin,paprika,sésame",
    "Viandes": "poulet,boeuf,porc,pancetta",
    "Poissons": "saumon,thon,anchois",
    "Œufs et produits laitiers": "oeuf,lait,beurre,crème fraîche,fromage,mozzarella,parmesan,gruyère,cheddar",
    "Céréales et féculents": "farine,riz,pâtes,pain,pâte feuilletée,tortilla",
    "Épicerie": "sucre,huile d'olive,vinaigre,lait de coco,levure chimique,pâte de curry vert,sauce poisson,vin blanc,bouillon de légumes,bouillon de boeuf,chocolat noir,sauce soja,mirin",
    "Autres": "",
}


def category_name_for(name):
    return next(
        (
            category
            for category, names in INGREDIENT_GROUPS.items()
            if name.casefold() in names.split(",")
        ),
        "Autres",
    )


def seed_ingredient_categories():
    for name in INGREDIENT_GROUPS:
        if (
            db.session.scalar(db.select(IngredientCategory).filter_by(name=name))
            is None
        ):
            db.session.add(IngredientCategory(name=name))
    db.session.commit()
