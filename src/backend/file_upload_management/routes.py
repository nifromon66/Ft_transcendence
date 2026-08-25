import os
import uuid

import magic
from extensions import db
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User
from werkzeug.utils import secure_filename

from .constants import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIMETYPES,
    MAX_UPLOAD_SIZE,
    UPLOAD_FOLDER,
)
from .services import save_raw_file

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    # Check if the request size is not too large
    if request.content_length and request.content_length > MAX_UPLOAD_SIZE:
        return jsonify({"error": "File too large (Max 10MB)"}), 413

    # Check if the multipart/form-data request contains the 'file' part
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    # Check if the user submitted an empty form
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Check if the extension of the file is allowed
    if not allowed_file(file.filename):
        return jsonify(
            {
                "error": "File extension not allowed",
                "allowed extensions": list(ALLOWED_EXTENSIONS),
            }
        ), 400

    # Check if the MIME type of the file is allowed
    file_header = file.read(2048)
    file.seek(0)

    file_mimetype = magic.from_buffer(file_header, mime=True)
    if file_mimetype not in ALLOWED_MIMETYPES:
        return jsonify(
            {
                "error": "File content not allowed",
                "allowed mimetypes": list(ALLOWED_MIMETYPES),
            }
        ), 400

    file_extension = file.filename.rsplit(".", 1)[1].lower()

    # Sanitize the filename to prevent path traversal attacks
    safe_filename = secure_filename(file.filename)

    # Generate a unique UUID to prevent file overwriting
    unique_id = uuid.uuid4().hex
    new_filename = f"{unique_id}_{safe_filename}"

    # Override the original filename with the secured and unique one
    file.filename = new_filename

    try:
        saved_filename = save_raw_file(file)

        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))

        if user:
            user.avatar_url = saved_filename
            db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "File uploaded successfully",
                "filename": saved_filename,
                "extension": file_extension,
                "mime type": file_mimetype,
            }
        ), 201

    except OSError as e:
        return jsonify({"error": f"System error while saving the file: {e!s}"}), 500


@upload_bp.route("/uploads/<filename>", methods=["GET"])
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

    if mimetype not in ALLOWED_MIMETYPES:
        return jsonify({"success": False, "error": "Unauthorized file type"}), 200

    return send_from_directory(UPLOAD_FOLDER, filename, mimetype=mimetype)
