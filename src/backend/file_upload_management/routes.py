from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .constants import MAX_UPLOAD_SIZE
from .services import save_raw_file

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    """
    Endpoint to upload a file.
    Version 2: Protected by JWT authentication and raw saving.
    """

    # Check if the request size is not too large
    if request.content_length and request.content_length > MAX_UPLOAD_SIZE:
        return jsonify({"error": "File too large (Max 10MB)"}), 413

    # Check if the multipart/form-data request contains the 'file' part
    if "file" not in request.files:
        return ({"error": "No file part in the request"}), 400

    file = request.files["file"]

    # Check if the user submitted an ampty form
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Call save_raw_file to save the file and return its name
        saved_filename = save_raw_file(file)

        return jsonify(
            {"message": "File uploaded successfully", "filename": saved_filename}
        ), 201

    except OSError as e:
        return jsonify({"error": f"System error while saving the file: {e!s}"}), 500
