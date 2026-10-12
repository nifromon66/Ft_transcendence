import os

from flask import current_app

from .constants import UPLOAD_FOLDER


def save_raw_file(file, subfolder="") -> str:
    target_dir = os.path.join(UPLOAD_FOLDER, subfolder) if subfolder else UPLOAD_FOLDER
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, file.filename)
    file.save(file_path)

    if subfolder:
        return os.path.join(subfolder, file.filename)

    return file.filename


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

    except OSError as error:
        return (
            None,
            jsonify({"error": (f"System error while saving the file: {error!s}")}),
            500,
        )


def delete_file_physically(filename: str) -> None:
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        current_app.logger.warning(
            f"Le fichier {file_path} n'a pas été trouvé sur le disque."
        )


def delete_empty_parent_directory(filename: str) -> None:
    file_path = os.path.join(UPLOAD_FOLDER, filename)
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
        # Le dossier contient encore un fichier : on le conserve.
        pass
