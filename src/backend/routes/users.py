from extensions import db, online_users
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from user_xp_management.leveling import get_xp_progress
from models.association import friend
from models.user import User
from sqlalchemy import and_, or_, select

users_bp = Blueprint("users", __name__)


@users_bp.route("/users/<int:user_id>/profile", methods=["GET"])
@jwt_required()
def get_public_profile(user_id):
    current_user_id = int(get_jwt_identity())
    target_user = db.session.get(User, user_id)

    if not target_user or not target_user.is_active:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 404

    public_data = target_user.to_dict()
    public_data.pop("email", None)
    public_data["xp_progress"] = get_xp_progress(target_user.xp)

    public_data["is_online"] = target_user.id in online_users

    if current_user_id == user_id:
        status = "self"
    else:
        rel_stmt = select(friend).where(
            or_(
                and_(
                    friend.c.user_id == current_user_id, friend.c.friend_id == user_id
                ),
                and_(
                    friend.c.user_id == user_id, friend.c.friend_id == current_user_id
                ),
            )
        )
        relation = db.session.execute(rel_stmt).mappings().first()

        if not relation:
            status = "none"
        elif relation["status"] == "accepted":
            status = "accepted"
        elif relation["status"] == "pending":
            if relation["user_id"] == current_user_id:
                status = "pending_sent"
            else:
                status = "pending_received"

    public_data["friendship_status"] = status

    return jsonify({"success": True, "profile": public_data}), 200
