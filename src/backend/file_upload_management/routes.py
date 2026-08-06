from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .constants import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
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

    file_extension = file.filename.rsplit(".", 1)[1].lower()

    try:
        # Call save_raw_file to save the file and return its name
        saved_filename = save_raw_file(file)

        return jsonify(
            {
                "message": "File uploaded successfully",
                "filename": saved_filename,
                "extension": file_extension,
            }
        ), 201

    except OSError as e:
        return jsonify({"error": f"System error while saving the file: {e!s}"}), 500
