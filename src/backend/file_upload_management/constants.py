import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_AVATAR_SIZE = 10 * 1024 * 1024

ALLOWED_AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

ALLOWED_AVATAR_MIMETYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}

MAX_DOCUMENT_SIZE = 5 * 1024 * 1024

ALLOWED_DOCUMENT_EXTENSIONS = {"pdf"}

ALLOWED_DOCUMENT_MIMETYPES = {"application/pdf"}

MAX_RECIPE_IMAGE_SIZE = 10 * 1024 * 1024

ALLOWED_RECIPE_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}

ALLOWED_RECIPE_IMAGE_MIMETYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
}