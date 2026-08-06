import os

from .constants import UPLOAD_FOLDER


def save_raw_file(file) -> str:
    """Version 2: Raw save of the file with its original name.
    No validation or name modification.
    """

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(file_path)

    return file.filename
