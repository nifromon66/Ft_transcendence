from extensions import db
from models import Tag


TAGS = [
    {"name": "facile"},
    {"name": "rapide"},
    {"name": "économique"},
    {"name": "familial"},
    {"name": "végétarien"},
    {"name": "végétalien"},
    {"name": "sans gluten"},
    {"name": "sans lactose"},
    {"name": "healthy"},
    {"name": "léger"},
    {"name": "épicé"},
    {"name": "sucré"},
    {"name": "salé"},
    {"name": "crémeux"},
    {"name": "croustillant"},
    {"name": "fait maison"},
    {"name": "saisonnier"},
    {"name": "traditionnel"},
    {"name": "festif"},
    {"name": "enfants"},
]


def seed_tags():
    for tag_data in TAGS:
        tag = db.session.scalar(
            db.select(Tag).where(
                Tag.name.ilike(tag_data["name"])
            )
        )
        if tag is None:
            db.session.add(Tag(**tag_data))

    db.session.commit()