import os
import uuid

import magic
from extensions import db
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from .constants import (
    ALLOWED_AVATAR_EXTENSIONS,
    ALLOWED_AVATAR_MIMETYPES,
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_DOCUMENT_MIMETYPES,
    MAX_AVATAR_SIZE,
    MAX_DOCUMENT_SIZE,
    UPLOAD_FOLDER,
)
from .services import delete_file_physically, save_raw_file

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def handle_file_upload(file, subfolder, allowed_extensions, allowed_mimetypes):
    if not file or file.filename == "":
        return None, jsonify({"error": "No selected file"}), 400

    # Check if the extension of the file is allowed
    if not allowed_file(file.filename, allowed_extensions):
        return (
            None,
            jsonify(
                {
                    "error": "File extension not allowed",
                    "allowed extensions": list(allowed_extensions),
                }
            ),
            400,
        )

    # Check if the MIME type of the file is allowed
    file_header = file.read(2048)
    file.seek(0)
    file_mimetype = magic.from_buffer(file_header, mime=True)

    if file_mimetype not in allowed_mimetypes:
        return (
            None,
            jsonify(
                {
                    "error": "File content not allowed",
                    "allowed mimetypes": list(allowed_mimetypes),
                }
            ),
            400,
        )

    file_extension = file.filename.rsplit(".", 1)[1].lower()

    # Sanitize the filename to prevent path traversal attacks
    safe_filename = secure_filename(file.filename)

    # Generate a unique UUID to prevent file overwriting
    unique_id = uuid.uuid4().hex
    new_filename = f"{unique_id}_{safe_filename}"

    # Override the original filename with the secured and unique one
    file.filename = new_filename

    try:
        saved_filename = save_raw_file(file, subfolder=subfolder)

        return (
            {
                "success": True,
                "message": "File uploaded successfully",
                "filename": saved_filename,
                "extension": file_extension,
                "mime type": file_mimetype,
            },
            None,
            None,
        )

    except OSError as e:
        return jsonify({"error": f"System error while saving the file: {e!s}"}), 500


@upload_bp.route("/upload/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    max_mb = MAX_AVATAR_SIZE // (1024 * 1024)

    # Check if the request size is not too large
    if request.content_length and request.content_length > MAX_AVATAR_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    # Check if the multipart/form-data request contains the 'file' part
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
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))

        if user:
            if user.avatar_url:
                try:
                    delete_file_physically(user.avatar_url)
                except OSError:
                    pass
            user.avatar_url = file_data["filename"]
            current_app.logger.info(f"AVATAR URL: {user.avatar_url}")
            db.session.commit()

        return jsonify(file_data), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {e!s}"}), 500


@upload_bp.route("/upload/document", methods=["POST"])
@jwt_required()
def upload_document():
    max_mb = MAX_DOCUMENT_SIZE // (1024 * 1024)

    # Check if the request size is not too large
    if request.content_length and request.content_length > MAX_DOCUMENT_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    # Check if the multipart/form-data request contains the 'file' part
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    file_data, err_resp, err_code = handle_file_upload(
        file,
        subfolder="documents",
        allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
        allowed_mimetypes=ALLOWED_DOCUMENT_MIMETYPES,
    )

    if err_resp:
        return err_resp, err_code

    return jsonify(file_data), 201


@upload_bp.route("/uploads/<path:filename>", methods=["GET"])
@jwt_required()
def get_secure_file(filename):
    # Check if the requested file actually exists on the disk
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"success": False, "error": "File not found"}), 200

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify({"success": False, "error": "Unreadable file"}), 200

    allowed_mimetypes = ALLOWED_AVATAR_MIMETYPES.union(ALLOWED_DOCUMENT_MIMETYPES)
    if mimetype not in allowed_mimetypes:
        return jsonify({"success": False, "error": "Unauthorized file type"}), 200

    directory = os.path.dirname(file_path)
    base_filename = os.path.basename(file_path)
    return send_from_directory(directory, base_filename, mimetype=mimetype)


@upload_bp.route("/users/avatar", methods=["DELETE"])
@jwt_required()
def delete_avatar():
    try:
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))

        if user is None or not user.avatar_url:
            return jsonify({"success": False, "error": "Aucun avatar à supprimer"}), 200

        try:
            delete_file_physically(user.avatar_url)
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

        user.avatar_url = None
        db.session.commit()

        return jsonify({"success": True, "message": "Avatar supprimé avec succès"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression de l'avatar: {e!s}")
        return jsonify(
            {"success": False, "error": "Erreur interne lors de la suppression"}
        ), 500
