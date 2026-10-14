import os
import uuid

import magic
from flask import current_app, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_raw_file(file, subfolder="") -> str:
    target_dir = os.path.join(UPLOAD_FOLDER, subfolder) if subfolder else UPLOAD_FOLDER
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, file.filename)
    file.save(file_path)

    return file.filename


def handle_file_upload(file, subfolder, allowed_extensions, allowed_mimetypes):
    if not file or file.filename == "":
        return None, jsonify({"error": "No selected file"}), 400

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

    file_header = file.read(2048)
    file.seek(0)

    try:
        file_mimetype = magic.from_buffer(file_header, mime=True)
    except magic.MagicException as error:
        current_app.logger.error(f"Erreur de lecture du type MIME : {error!s}")
        return None, jsonify({"error": "Format de fichier illisible ou corrompu"}), 400

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
    safe_filename = secure_filename(file.filename)
    unique_id = uuid.uuid4().hex
    new_filename = f"{unique_id}_{safe_filename}"
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

    except OSError as error:
        return (
            None,
            jsonify({"error": (f"System error while saving the file: {error!s}")}),
            500,
        )


def delete_file_physically(relative_filepath: str) -> None:
    file_path = os.path.join(UPLOAD_FOLDER, relative_filepath)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as error:
            current_app.logger.error(f"Erreur lors de la suppression : {error!s}")
    else:
        current_app.logger.warning(
            f"Le fichier {file_path} n'a pas été trouvé sur le disque."
        )


def delete_empty_parent_directory(relative_filepath: str) -> None:
    file_path = os.path.join(UPLOAD_FOLDER, relative_filepath)
    parent_directory = os.path.dirname(file_path)

    upload_root = os.path.abspath(UPLOAD_FOLDER)
    parent_directory = os.path.abspath(parent_directory)

    if parent_directory == upload_root:
        return

    if os.path.commonpath([upload_root, parent_directory]) != upload_root:
        return

    try:
        os.rmdir(parent_directory)
    except FileNotFoundError:
        pass
    except OSError:
        pass
