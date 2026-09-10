import os
import uuid

import magic
from extensions import db
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Recipe, RecipeStep, User
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join

from .constants import (
    ALLOWED_AVATAR_EXTENSIONS,
    ALLOWED_AVATAR_MIMETYPES,
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_DOCUMENT_MIMETYPES,
    ALLOWED_RECIPE_IMAGE_EXTENSIONS,
    ALLOWED_RECIPE_IMAGE_MIMETYPES,
    MAX_AVATAR_SIZE,
    MAX_DOCUMENT_SIZE,
    MAX_RECIPE_IMAGE_SIZE,
    UPLOAD_FOLDER,
)
from .services import (
    delete_empty_parent_directory,
    delete_file_physically,
    save_raw_file,
)

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


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
            jsonify(
                {
                    "error": (
                        "System error while saving the file: "
                        f"{error!s}"
                    )
                }
            ),
            500,
        )


@upload_bp.route("/recipes/<int:recipe_id>/image", methods=["POST"])
@jwt_required()
def upload_recipe_image(recipe_id: int):
    max_mb = MAX_RECIPE_IMAGE_SIZE // (1024 * 1024)

    if request.content_length and request.content_length > MAX_RECIPE_IMAGE_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    if "file" not in request.files:
        return jsonify(
            {"error": "No file part in the request"}
        ), 400

    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Tu ne peux modifier que tes propres recettes"
                ),
            }
        ), 403

    file = request.files["file"]

    file_data, error_response, error_code = handle_file_upload(
        file,
        subfolder=f"recipes/{recipe.id}/cover",
        allowed_extensions=ALLOWED_RECIPE_IMAGE_EXTENSIONS,
        allowed_mimetypes=ALLOWED_RECIPE_IMAGE_MIMETYPES,
    )

    if error_response is not None:
        return error_response, error_code

    new_filename = file_data["filename"]
    old_filename = recipe.image_url

    try:
        recipe.image_url = new_filename
        db.session.commit()

    except SQLAlchemyError as error:
        db.session.rollback()

        try:
            delete_file_physically(new_filename)
        except OSError as delete_error:
            current_app.logger.error(
                "Impossible de supprimer le nouveau fichier "
                f"après l'échec SQL : {delete_error!s}"
            )

        current_app.logger.error(
            f"Impossible d'enregistrer l'image de la recette : {error!s}"
        )

        return jsonify(
            {
                "success": False,
                "error": "Impossible d'enregistrer l'image de la recette",
            }
        ), 500

    if old_filename:
        try:
            delete_file_physically(old_filename)
        except OSError as error:
            current_app.logger.error(
                "L'ancienne image n'a pas pu être supprimée : "
                f"{error!s}"
            )

    return jsonify(
        {
            **file_data,
            "image_url": new_filename,
        }
    ), 201


@upload_bp.route(
    "/recipes/<int:recipe_id>/steps/<int:step_id>/image",
    methods=["POST"],
)
@jwt_required()
def upload_recipe_step_image(
    recipe_id: int,
    step_id: int,
):
    max_mb = MAX_RECIPE_IMAGE_SIZE // (1024 * 1024)

    if (
        request.content_length
        and request.content_length > MAX_RECIPE_IMAGE_SIZE
    ):
        return jsonify(
            {"error": f"File too large (Max {max_mb}MB)"}
        ), 413

    if "file" not in request.files:
        return jsonify(
            {"error": "No file part in the request"}
        ), 400

    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Tu ne peux modifier que tes propres recettes"
                ),
            }
        ), 403

    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe.id:
        return jsonify(
            {
                "success": False,
                "error": "Étape introuvable pour cette recette",
            }
        ), 404

    file = request.files["file"]

    file_data, error_response, error_code = handle_file_upload(
        file,
        subfolder=(
            f"recipes/{recipe.id}/steps/{step.id}"
        ),
        allowed_extensions=ALLOWED_RECIPE_IMAGE_EXTENSIONS,
        allowed_mimetypes=ALLOWED_RECIPE_IMAGE_MIMETYPES,
    )

    if error_response is not None:
        return error_response, error_code

    new_filename = file_data["filename"]
    old_filename = step.image_url

    try:
        step.image_url = new_filename
        db.session.commit()

    except SQLAlchemyError as error:
        db.session.rollback()

        try:
            delete_file_physically(new_filename)
        except OSError as delete_error:
            current_app.logger.error(
                "Impossible de supprimer la nouvelle image d'étape "
                f"après l'échec SQL : {delete_error!s}"
            )

        current_app.logger.error(
            "Impossible d'enregistrer l'image de l'étape : "
            f"{error!s}"
        )

        return jsonify(
            {
                "success": False,
                "error": "Impossible d'enregistrer l'image de l'étape",
            }
        ), 500

    if old_filename:
        try:
            delete_file_physically(old_filename)
        except OSError as error:
            current_app.logger.error(
                "L'ancienne image de l'étape n'a pas pu être "
                f"supprimée : {error!s}"
            )

    return jsonify(
        {
            **file_data,
            "image_url": new_filename,
        }
    ), 201


@upload_bp.route(
    "/recipes/<int:recipe_id>/steps/<int:step_id>/image",
    methods=["DELETE"],
)
@jwt_required()
def delete_recipe_step_image(
    recipe_id: int,
    step_id: int,
):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Tu ne peux modifier que tes propres recettes"
                ),
            }
        ), 403

    step = db.session.get(RecipeStep, step_id)

    if step is None or step.recipe_id != recipe.id:
        return jsonify(
            {
                "success": False,
                "error": "Étape introuvable pour cette recette",
            }
        ), 404

    if not step.image_url:
        return jsonify(
            {
                "success": False,
                "error": "Cette étape n'a pas d'image",
            }
        ), 404

    filename = step.image_url

    try:
        step.image_url = None
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()

        current_app.logger.error(
            "Impossible de supprimer l'image de l'étape : "
            f"{error!s}"
        )

        return jsonify(
            {
                "success": False,
                "error": "Impossible de supprimer l'image de l'étape",
            }
        ), 500

    try:
        delete_file_physically(filename)
    except OSError as error:
        current_app.logger.error(
            "L'image a été retirée de l'étape, mais son fichier "
            f"n'a pas pu être supprimé : {error!s}"
        )

    return jsonify(
        {
            "success": True,
            "message": "Image de l'étape supprimée",
        }
    ), 200


@upload_bp.route("/recipes/<int:recipe_id>/image", methods=["DELETE"])
@jwt_required()
def delete_recipe_image(recipe_id: int):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return jsonify(
            {
                "success": False,
                "error": "Recette introuvable",
            }
        ), 404

    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify(
            {
                "success": False,
                "error": "Utilisateur non authentifié",
            }
        ), 401

    if recipe.user_id != user_id:
        return jsonify(
            {
                "success": False,
                "error": (
                    "Tu ne peux modifier que tes propres recettes"
                ),
            }
        ), 403

    if not recipe.image_url:
        return jsonify(
            {
                "success": False,
                "error": "Cette recette n'a pas d'image",
            }
        ), 404

    filename = recipe.image_url

    try:
        recipe.image_url = None
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()

        current_app.logger.error(
            f"Impossible de supprimer l'image de la recette : {error!s}"
        )

        return jsonify(
            {
                "success": False,
                "error": "Impossible de supprimer l'image de la recette",
            }
        ), 500

    try:
        delete_file_physically(filename)
        delete_empty_parent_directory(filename)
    except OSError as error:
        current_app.logger.error(
            "L'image a été retirée de la recette, mais le fichier "
            f"n'a pas pu être supprimé : {error!s}"
        )

    return jsonify(
        {
            "success": True,
            "message": "Image de la recette supprimée",
        }
    ), 200


@upload_bp.route("/upload/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"error": "Compte inactif ou supprimé"}), 403

    max_mb = MAX_AVATAR_SIZE // (1024 * 1024)

    # Check if the request size is not too large
    if request.content_length and request.content_length > MAX_AVATAR_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    # Check if the multipart/form-data request contains the 'file' part
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    file_data, err_resp, err_code = handle_file_upload(
        file,
        subfolder="avatars",
        allowed_extensions=ALLOWED_AVATAR_EXTENSIONS,
        allowed_mimetypes=ALLOWED_AVATAR_MIMETYPES,
    )

    if err_resp:
        return err_resp, err_code

    try:
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))

        if user:
            if user.avatar_url:
                try:
                    delete_file_physically(user.avatar_url)
                except OSError:
                    pass
            user.avatar_url = file_data["filename"]
            current_app.logger.info(f"AVATAR URL: {user.avatar_url}")
            db.session.commit()

        return jsonify(file_data), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {e!s}"}), 500


@upload_bp.route("/upload/document", methods=["POST"])
@jwt_required()
def upload_document():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"error": "Compte inactif ou supprimé"}), 403

    max_mb = MAX_DOCUMENT_SIZE // (1024 * 1024)

    # Check if the request size is not too large
    if request.content_length and request.content_length > MAX_DOCUMENT_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

    # Check if the multipart/form-data request contains the 'file' part
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    file_data, err_resp, err_code = handle_file_upload(
        file,
        subfolder="documents",
        allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
        allowed_mimetypes=ALLOWED_DOCUMENT_MIMETYPES,
    )

    if err_resp:
        return err_resp, err_code

    return jsonify(file_data), 201


@upload_bp.route(
    "/uploads/recipes/<path:filename>",
    methods=["GET"],
)
def get_public_recipe_image(filename: str):
    recipe_upload_folder = os.path.join(
        UPLOAD_FOLDER,
        "recipes",
    )

    file_path = safe_join(recipe_upload_folder, filename)

    if file_path is None or not os.path.isfile(file_path):
        return jsonify(
            {
                "success": False,
                "error": "Image introuvable",
            }
        ), 404

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify(
            {
                "success": False,
                "error": "Image illisible",
            }
        ), 404

    if mimetype not in ALLOWED_RECIPE_IMAGE_MIMETYPES:
        return jsonify(
            {
                "success": False,
                "error": "Type d'image non autorisé",
            }
        ), 415

    return send_from_directory(
        recipe_upload_folder,
        filename,
        mimetype=mimetype,
    )


@upload_bp.route("/uploads/<path:filename>", methods=["GET"])
@jwt_required()
def get_secure_file(filename):
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"error": "Accès reßfusé"}), 403

    # Check if the requested file actually exists on the disk
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"success": False, "error": "File not found"}), 200

    try:
        mimetype = magic.from_file(file_path, mime=True)
    except (OSError, magic.MagicException):
        return jsonify({"success": False, "error": "Unreadable file"}), 200

    allowed_mimetypes = ALLOWED_AVATAR_MIMETYPES.union(ALLOWED_DOCUMENT_MIMETYPES)
    if mimetype not in allowed_mimetypes:
        return jsonify({"success": False, "error": "Unauthorized file type"}), 200

    directory = os.path.dirname(file_path)
    base_filename = os.path.basename(file_path)
    return send_from_directory(directory, base_filename, mimetype=mimetype)


@upload_bp.route("/users/avatar", methods=["DELETE"])
@jwt_required()
def delete_avatar():
    try:
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))

        if user is None or not user.avatar_url:
            return jsonify({"success": False, "error": "Aucun avatar à supprimer"}), 200

        try:
            delete_file_physically(user.avatar_url)
        except OSError as e:
            current_app.logger.error(
                f"Erreur système lors de la suppression du fichier {e!s}"
            )
            return jsonify(
                {
                    "success": False,
                    "error": "Erreur système lors de la suppression du fichier",
                }
            ), 500

        user.avatar_url = None
        db.session.commit()

        return jsonify({"success": True, "message": "Avatar supprimé avec succès"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de la suppression de l'avatar: {e!s}")
        return jsonify(
            {"success": False, "error": "Erreur interne lors de la suppression"}
        ), 500
