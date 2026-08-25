import os

from flask import current_app

from .constants import UPLOAD_FOLDER


def save_raw_file(file) -> str:
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(file_path)

    return file.filename


def delete_file_physically(filename: str) -> None:
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        current_app.logger.warning(
            f"Le fichier {file_path} n'a pas été trouvé sur le disque."
        )
