# TODO:
# +xp
# Requirements for obtaining the badges

# routers : maybe later move functions routers in the folder backend/routers

from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Badge, User, UserBadge

gamification_api = Blueprint("gamification_api", __name__)

"""
Award a badge to a user

Returns:
	True  -> user successfully awarded a badge
	False -> user has already have it
"""


def award_badge(
    *,
    user_id: int | None = None,
    user: User | None = None,
    badge_id: int | None = None,
    badge: Badge | None = None,
) -> bool:

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


@gamification_api.route("/getbadge", methods=["POST"])
@jwt_required()
def getbadge():
    user_id = get_jwt_identity()

    data = request.get_json()
    if not data or "badge_id" not in data:
        return jsonify({"error": "badge_id is required"}), 400
    badge_id = data["badge_id"]
    badge = db.session.get(Badge, badge_id)
    if badge is None:
        return jsonify({"error": "Badge not found"}), 404

    eligible = check_badge_eligibility(
        user_id=user_id,
        badge=badge,
    )
    # todo
    if not eligible:
        return jsonify({"error": "User is not eligible for this badge"}), 403

    awarded = award_badge(
        user_id=user_id,
        badge=badge,
    )

    if not awarded:
        return jsonify({"error": "Badge already owned"}), 409

    db.session.commit()

    return jsonify(
        {
            "message": "Badge awarded",
            "badge": {
                "id": badge.id,
                "name": badge.name,
            },
        }
    ), 201


@gamification_api.route("/badges", methods=["GET"])
@jwt_required()
def display_badges():
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

    if user is None:
        user = db.session.get(User, user_id)
        if user is None:
            raise ValueError("check_badge_eligibility: User not found")

    if badge is None:
        badge = db.session.get(Badge, badge_id)
        if badge is None:
            raise ValueError("check_badge_eligibility: Badge not found")

    user_id = user.id
    badge_id = badge.id

    if badge_id == 1:
        return True

    elif badge_id == 2:
        return True

    return False
