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

    if os.path.commonpath(
        [upload_root, parent_directory]
    ) != upload_root:
        return

    try:
        os.rmdir(parent_directory)
    except FileNotFoundError:
        pass
    except OSError:
        # Le dossier contient encore un fichier : on le conserve.
        pass