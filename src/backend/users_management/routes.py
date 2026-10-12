import os
import uuid

import magic
from extensions import db, online_users, socketio
from file_upload_management.constants import UPLOAD_FOLDER
from file_upload_management.services import delete_file_physically, handle_file_upload
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from models import User
from models.association import friend
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError

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
            "user": user.to_dict(),
        }
    ), 200


@users_bp.route("/me/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"error": "Compte inactif ou supprimé"}), 403

    max_mb = MAX_AVATAR_SIZE // (1024 * 1024)

    if request.content_length and request.content_length > MAX_AVATAR_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

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

    try:
        if user.avatar_filename:
            try:
                delete_file_physically(user.avatar_filename)
            except OSError:
                return jsonify(
                    {
                        "success": False,
                        "error": "Erreur lors de la suppression de l'avatar.",
                    }
                ), 500

            user.avatar_filename = None

        user.is_active = False
        user.username = "Utilisateur supprimé"
        user.email = f"deleted_{uuid.uuid4().hex}@anonymized.invalid"
        user.password_hash = "!"

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Votre compte a été supprimé avec succès.",
            }
        ), 200

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "error": "Erreur lors de la suppression du compte.",
            }
        ), 500


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
            "user": user.to_dict(),
        }
    ), 200


@users_bp.route("", methods=["GET"])
@jwt_required()
def get_users():
    users = db.session.execute(select(User)).scalars().all()
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

    public_data = target_user.to_dict()
    public_data.pop("email", None)

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


@users_bp.route("/avatars/<filename>", methods=["GET"])
@jwt_required()
def get_avatar_file(filename):
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"error": "Accès refusé"}), 403

    avatar_folder = os.path.join(UPLOAD_FOLDER, "avatars")
    file_path = os.path.join(avatar_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"success": False, "error": "Fichier introuvable"}), 404

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify({"success": False, "error": "Fichier illisible"}), 422

    if mimetype not in ALLOWED_AVATAR_MIMETYPES:
        return jsonify({"success": False, "error": "Type de fichier non autorisé"}), 415

    return send_from_directory(avatar_folder, filename, mimetype=mimetype)
