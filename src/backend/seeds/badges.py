from extensions import db
from models import Badge
from models.badge import BadgeType

BADGES = [
    {
        "id": BadgeType.NEW_BEE,
        "name": "New Bee",
        "description": "Now you have your account",
    },
    {
        "id": BadgeType.FIRST_RECIPE,
        "name": "First Recipe",
        "description": "Create your first recipe",
    },
    {
        "id": BadgeType.RECIPE_MASTER,
        "name": "Recipe Master",
        "description": "Create 10 recipes",
    },
]


def seed_badges():
    for badge_data in BADGES:
        if db.session.get(Badge, badge_data["id"]) is None:
            db.session.add(Badge(**badge_data))

    db.session.commit()