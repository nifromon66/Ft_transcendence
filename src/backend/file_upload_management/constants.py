import os

UPLOAD_FOLDER = "uploads"

MAX_UPLOAD_SIZE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

ALLOWED_MIMETYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
