from models import Utensil
from extensions import db

UTENSILS = [
    {"name": "Couteau"},
    {"name": "Planche à découper"},
    {"name": "Économe"},
    {"name": "Éplucheur"},
    {"name": "Râpe"},
    {"name": "Fouet"},
    {"name": "Spatule"},
    {"name": "Cuillère en bois"},
    {"name": "Cuillère"},
    {"name": "Louche"},
    {"name": "Pince de cuisine"},
    {"name": "Passoire"},
    {"name": "Tamis"},
    {"name": "Bol"},
    {"name": "Saladier"},
    {"name": "Mortier et pilon"},
    {"name": "Poêle"},
    {"name": "Casserole"},
    {"name": "Marmite"},
    {"name": "Faitout"},
    {"name": "Plat à gratin"},
    {"name": "Moule à gâteau"},
    {"name": "Plaque de cuisson"},
    {"name": "Rouleau à pâtisserie"},
    {"name": "Presse-purée"},
    {"name": "Ouvre-boîte"},
    {"name": "Thermomètre de cuisine"},
]

def seed_utensils():
    for utensil_data in UTENSILS:
        name = utensil_data["name"].capitalize()

        utensil = db.session.scalar(
            db.select(Utensil).where(
                Utensil.name.ilike(name)
            )
        )

        if utensil is None:
            db.session.add(
                Utensil(**utensil_data)
            )

    db.session.commit()