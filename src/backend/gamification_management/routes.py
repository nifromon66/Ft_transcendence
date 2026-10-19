from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Badge, Recipe, User, UserBadge
from models.badge import BadgeType

gamification_bp = Blueprint(
    "gamification_management", __name__, url_prefix="/gamification"
)


def award_badge(
    *,
    user_id: int | None = None,
    user: User | None = None,
    badge_id: int | None = None,
    badge: Badge | None = None,
) -> bool:
    """
    Award a badge to a user

    Returns:
            True  -> user successfully awarded a badge
            False -> user has already have it
    """
    if user is None:
        user = db.session.get(User, user_id)
        if user is None:
            raise ValueError("award_badge: User not found")

    if badge is None:
        badge = db.session.get(Badge, badge_id)
        if badge is None:
            raise ValueError("award_badge: Badge not found")

    user_id = user.id
    badge_id = badge.id
    existing = db.session.scalar(
        db.select(UserBadge).where(
            UserBadge.user_id == user_id, UserBadge.badge_id == badge_id
        )
    )

    if existing is not None:
        return False

    user_badge = UserBadge(user_id=user_id, badge_id=badge_id)

    db.session.add(user_badge)

    return True


@gamification_bp.route("/award", methods=["POST"])
@jwt_required()
def getbadge():
    """
    Attempts to award a specific badge to the authenticated user.
    Validates eligibility before awarding.
    """
    user_id = get_jwt_identity()

    data = request.get_json()
    if not data or "badge_id" not in data:
        return jsonify({"success": False, "error": "badge_id is required"}), 200
    badge_id = data["badge_id"]
    badge = db.session.get(Badge, badge_id)
    if badge is None:
        return jsonify({"success": False, "error": "Badge not found"}), 200

    eligible = check_badge_eligibility(
        user_id=user_id,
        badge=badge,
    )
    if not eligible:
        return jsonify(
            {"success": False, "error": "User is not eligible for this badge"}
        ), 403

    awarded = award_badge(
        user_id=user_id,
        badge=badge,
    )

    if not awarded:
        return jsonify({"success": False, "error": "Badge already owned"}), 200

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Badge awarded",
            "badge": {
                "id": badge.id,
                "name": badge.name,
                "logo_filename": badge.logo_filename,
            },
        }
    ), 201


@gamification_bp.route("/badges", methods=["GET"])
@jwt_required()
def display_badges():
    """
    Retrieves all available badges, indicating which ones the authenticated user owns
    and which ones they are eligible for.
    """
    user_id = get_jwt_identity()

    badges = db.session.scalars(db.select(Badge)).all()

    result = []

    for badge in badges:
        existing = db.session.scalar(
            db.select(UserBadge).where(
                UserBadge.user_id == user_id,
                UserBadge.badge_id == badge.id,
            )
        )

        user = db.session.get(User, user_id)

        eligible = check_badge_eligibility(
            user=user,
            badge=badge,
        )

        result.append(
            {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "logo_filename": badge.logo_filename,
                "eligible": eligible,
                "owned": existing is not None,
            }
        )

    return jsonify(result), 200

def check_badge_eligibility(
    *,
    user_id: int | None = None,
    user: User | None = None,
    badge_id: int | None = None,
    badge: Badge | None = None,
) -> bool:
    """
    Checks if a user has met the requirements to earn a specific badge.
    """
    if user is None:
        user = db.session.get(User, user_id)
        if user is None:
            raise ValueError("check_badge_eligibility: User not found")

    if badge is None:
        badge = db.session.get(Badge, badge_id)
        if badge is None:
            raise ValueError("check_badge_eligibility: Badge not found")

    recipe_count = db.session.scalar(
        db.select(db.func.count(Recipe.id)).where(Recipe.user_id == user.id)
    )

    requirements = {
        BadgeType.NEW_BEE: True,
        BadgeType.FIRST_RECIPE: recipe_count >= 1,
        BadgeType.RECIPE_MASTER: recipe_count >= 10,
    }
    return requirements.get(badge.id, False)
