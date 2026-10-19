import os

import magic
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError

from admin_management.services import (
    anonymize,
    cleanup_account,
    is_last_admin,
    lock_administrators,
)
from config import UPLOAD_FOLDER
from extensions import db, limiter, online_users, socketio
from gamification_management.routes import check_badge_eligibility
from models import Badge, User
from models.association import friend
from models.user_avatar_frame import UserAvatarFrame
from user_xp_management.leveling import get_xp_progress
from user_xp_management.rewards import FRAME_LEVELS, get_active_frame, get_level_rewards
from utils.file_services import delete_file_physically, handle_file_upload

from .constants import (
    ALLOWED_AVATAR_EXTENSIONS,
    ALLOWED_AVATAR_MIMETYPES,
    MAX_AVATAR_SIZE,
)

users_bp = Blueprint("users_management", __name__, url_prefix="/users")


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_my_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or not user.is_active:
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur introuvable.",
            }
        ), 404

    data = request.get_json()
    if not data:
        return jsonify(
            {
                "success": False,
                "error": "Aucune donnée fournie.",
            }
        ), 400

    if not isinstance(data, dict) or set(data) - {"username", "email"}:
        return jsonify(success=False, error="Champs non autorisés."), 400

    new_username = data.get("username", "").strip()
    new_email = data.get("email", "").strip()

    has_changed = False

    if new_email and new_email != user.email:
        existing_email = db.session.execute(
            select(User).where(User.email == new_email)
        ).scalar_one_or_none()

        if existing_email:
            return jsonify(
                {
                    "success": False,
                    "error": "Cet email est déjà utilisé par un autre compte.",
                }
            ), 409

        user.email = new_email
        has_changed = True

    if new_username and new_username != user.username:
        existing_username = db.session.execute(
            select(User).where(User.username == new_username)
        ).scalar_one_or_none()

        if existing_username:
            return jsonify(
                {
                    "success": False,
                    "error": "Ce pseudo est déjà utilisé par un autre compte.",
                }
            ), 409

        user.username = new_username
        has_changed = True

    if has_changed:
        db.session.commit()

        socketio.emit(
            "user_profile_updated", {"user_id": user.id, "new_username": user.username}
        )

    return jsonify(
        {
            "success": True,
            "message": "Profil mis à jour avec succès.",
            "user": user.to_private_dict(),
        }
    ), 200


@users_bp.route("/me/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"success": False, "error": "Compte inactif ou supprimé"}), 200

    max_mb = MAX_AVATAR_SIZE // (1024 * 1024)

    if request.content_length and request.content_length > MAX_AVATAR_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 200

    file = request.files["file"]
    file_data, err_resp, err_code = handle_file_upload(
        file,
        subfolder="avatars",
        allowed_extensions=ALLOWED_AVATAR_EXTENSIONS,
        allowed_mimetypes=ALLOWED_AVATAR_MIMETYPES,
    )

    if err_resp:
        return err_resp, err_code

    try:
        if user.avatar_filename:
            try:
                delete_file_physically(user.avatar_filename)
            except OSError:
                pass
        user.avatar_filename = file_data["filename"]
        current_app.logger.info(f"AVATAR URL: {user.avatar_filename}")
        db.session.commit()

        return jsonify(file_data), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {e!s}"}), 500


@users_bp.route("/me/avatar", methods=["DELETE"])
@jwt_required()
def delete_avatar():
    try:
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))

        if user is None or not user.avatar_filename:
            return jsonify({"success": False, "error": "Aucun avatar à supprimer"}), 200

        try:
            delete_file_physically(user.avatar_filename)
        except OSError as e:
            current_app.logger.error(
                f"Erreur système lors de la suppression du fichier {e!s}"
            )
            return jsonify(
                {
                    "success": False,
                    "error": "Erreur système lors de la suppression du fichier",
                }
            ), 500

        user.avatar_filename = None
        db.session.commit()

        return jsonify({"success": True, "message": "Avatar supprimé avec succès"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression de l'avatar: {e!s}")
        return jsonify(
            {"success": False, "error": "Erreur interne lors de la suppression"}
        ), 500


@users_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_my_account():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None:
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur introuvable.",
            }
        ), 404

    data = request.get_json()
    password = data.get("password", "") if data else ""

    if not password:
        return jsonify(
            {
                "success": False,
                "error": "Le mot de passe est requis.",
            }
        ), 400

    if not user.check_password(password):
        return jsonify(
            {
                "success": False,
                "error": "Mot de passe incorrect.",
            }
        ), 403

    administrators = lock_administrators()
    db.session.refresh(user, with_for_update=True)
    if not user.is_active or user.deleted_at:
        return jsonify(success=False, error="Compte désactivé."), 401
    if is_last_admin(user, administrators):
        return jsonify(
            success=False, error="Le dernier administrateur actif doit être conservé."
        ), 409
    try:
        avatar = anonymize(user)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            success=False, error="Erreur lors de la suppression du compte."
        ), 500
    cleanup_account(user.id, avatar)
    return jsonify(
        success=True, message="Votre compte a été supprimé avec succès."
    ), 200


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur introuvable.",
            }
        ), 404

    return jsonify(
        {
            "success": True,
            "user": user.to_private_dict(),
        }
    ), 200


@users_bp.route("", methods=["GET"])
@jwt_required()
def get_users():
    users = (
        db.session.execute(select(User).where(User.is_active.is_(True))).scalars().all()
    )
    return jsonify(
        {
            "success": True,
            "users": [user.to_dict() for user in users],
        }
    ), 200


@users_bp.route("/<int:user_id>/profile", methods=["GET"])
@jwt_required()
def get_public_profile(user_id):
    current_user_id = int(get_jwt_identity())
    target_user = db.session.get(User, user_id)

    if not target_user or not target_user.is_active:
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur introuvable",
            }
        ), 404

    public_data = target_user.to_public_dict()
    public_data["xp_progress"] = get_xp_progress(target_user.xp)
    public_data["level_rewards"] = get_level_rewards(target_user)
    public_data["is_online"] = target_user.id in online_users
    owned_badges = {user_badge.badge_id for user_badge in target_user.badges}
    public_data["badges"] = [
        {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "logo_filename": badge.logo_filename,
            "eligible": check_badge_eligibility(user=target_user, badge=badge),
            "owned": badge.id in owned_badges,
        }
        for badge in db.session.scalars(select(Badge)).all()
    ]

    if current_user_id == user_id:
        status = "self"
        public_data["is_online"] = True
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


@users_bp.route("/avatars/<filename>", methods=["GET"])
@limiter.exempt
@jwt_required()
def get_avatar_file(filename):
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"success": False, "error": "Accès refusé"}), 200

    avatar_folder = os.path.join(UPLOAD_FOLDER, "avatars")
    file_path = os.path.join(avatar_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"success": False, "error": "Fichier introuvable"}), 200

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify({"success": False, "error": "Fichier illisible"}), 200

    if mimetype not in ALLOWED_AVATAR_MIMETYPES:
        return jsonify({"success": False, "error": "Type de fichier non autorisé"}), 200

    return send_from_directory(avatar_folder, filename, mimetype=mimetype)


@users_bp.route("/me/avatar-frame", methods=["PUT"])
@jwt_required()
def update_avatar_frame():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "frame" not in data:
        return jsonify({"success": False, "error": "Le cercle est requis."}), 200
    frame = data["frame"]
    if frame is not None and (not isinstance(frame, str) or frame not in FRAME_LEVELS):
        return jsonify({"success": False, "error": "Cercle invalide."}), 200

    try:
        # Serialize preference changes with other changes to this user's XP.
        user = db.session.scalar(
            select(User).where(User.id == int(get_jwt_identity())).with_for_update()
        )
        if user is None or not user.is_active:
            return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200
        if (
            frame is not None
            and get_xp_progress(user.xp)["level"] < FRAME_LEVELS[frame]
        ):
            return jsonify(
                {"success": False, "error": "Le niveau requis n’est pas atteint."}
            ), 403
        if user.avatar_frame_preference is None:
            user.avatar_frame_preference = UserAvatarFrame(frame=frame)
        else:
            user.avatar_frame_preference.frame = frame
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Impossible d’enregistrer le cercle."}
        ), 500

    return jsonify(
        {
            "success": True,
            "avatar_frame": get_active_frame(user),
            "level_rewards": get_level_rewards(user),
            "xp_progress": get_xp_progress(user.xp),
        }
    ), 200
