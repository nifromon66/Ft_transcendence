from extensions import db, online_users
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from user_xp_management.leveling import get_xp_progress
from models.association import friend
from models.user import User
from models.user_avatar_frame import UserAvatarFrame
from user_xp_management.rewards import FRAME_LEVELS, get_active_frame, get_level_rewards
from sqlalchemy.exc import SQLAlchemyError
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
    public_data["level_rewards"] = get_level_rewards(target_user)

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


@users_bp.route("/users/me/avatar-frame", methods=["PUT"])
@jwt_required()
def update_avatar_frame():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "frame" not in data:
        return jsonify({"success": False, "error": "Le cercle est requis."}), 400
    frame = data["frame"]
    if frame is not None and (not isinstance(frame, str) or frame not in FRAME_LEVELS):
        return jsonify({"success": False, "error": "Cercle invalide."}), 400

    try:
        # Serialize preference changes with other changes to this user's XP.
        user = db.session.scalar(select(User).where(User.id == int(get_jwt_identity())).with_for_update())
        if user is None or not user.is_active:
            return jsonify({"success": False, "error": "Utilisateur introuvable"}), 404
        if frame is not None and get_xp_progress(user.xp)["level"] < FRAME_LEVELS[frame]:
            return jsonify({"success": False, "error": "Le niveau requis n’est pas atteint."}), 403
        if user.avatar_frame_preference is None:
            user.avatar_frame_preference = UserAvatarFrame(frame=frame)
        else:
            user.avatar_frame_preference.frame = frame
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Impossible d’enregistrer le cercle."}), 500

    return jsonify({
        "success": True,
        "avatar_frame": get_active_frame(user),
        "level_rewards": get_level_rewards(user),
        "xp_progress": get_xp_progress(user.xp),
    }), 200
