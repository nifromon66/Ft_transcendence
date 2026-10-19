from extensions import db
from models import Badge
from models.badge import BadgeType

BADGES = [
    {
        "id": BadgeType.NEW_BEE,
        "name": "New Bee",
        "description": "Now you have your account",
        "logo_filename": "gift-svgrepo-com.svg",
    },
    {
        "id": BadgeType.FIRST_RECIPE,
        "name": "First Recipe",
        "description": "Create your first recipe",
        "logo_filename": "hamburger-svgrepo-com.svg",
    },
    {
        "id": BadgeType.RECIPE_MASTER,
        "name": "Recipe Master",
        "description": "Create 10 recipes",
        "logo_filename": "the-medal-svgrepo-com.svg",
    },
]


def seed_badges():
    for badge_data in BADGES:
        badge = db.session.get(Badge, badge_data["id"])
        if badge is None:
            db.session.add(Badge(**badge_data))
        else:
            badge.logo_filename = badge_data["logo_filename"]

    db.session.commit()
