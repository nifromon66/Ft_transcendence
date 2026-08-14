import os

from .constants import UPLOAD_FOLDER


def save_raw_file(file) -> str:
    """Version 6: Save the file using its current filename attribute.
    The filename is expected to have been secured and made unique (UUID)
    by the route before calling this function.
    """

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(file_path)

    return file.filename
