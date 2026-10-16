import os

from config import UPLOAD_FOLDER
from extensions import db
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User
from models.message import Message
from sqlalchemy.exc import SQLAlchemyError
from utils.file_services import handle_file_upload

from .constants import (
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_DOCUMENT_MIMETYPES,
    MAX_DOCUMENT_SIZE,
)

messages_bp = Blueprint("messages_management", __name__, url_prefix="/messages")


@messages_bp.route("/documents", methods=["POST"])
@jwt_required()
def upload_document():
    """
    Handles the upload of a document (PDF) for a chat message.
    Verifies the file size, extension, and mimetype.
    Returns the uploaded file details.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"error": "Compte inactif ou supprimé"}), 403

    max_mb = MAX_DOCUMENT_SIZE // (1024 * 1024)

    if request.content_length and request.content_length > MAX_DOCUMENT_SIZE:
        return jsonify({"error": f"File too large (Max {max_mb}MB)"}), 413

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


@messages_bp.route("/<int:friend_id>", methods=["GET"])
@jwt_required()
def get_chat_history(friend_id):
    """
    Retrieves the conversation history between the authenticated user and a given friend.
    """
    current_user_id = int(get_jwt_identity())

    if current_user_id == friend_id:
        return jsonify(
            {
                "success": False,
                "error": "Requête invalide. Vous ne pouvez pas discuter avec vous-même.",
            }
        ), 400

    current_user = db.session.get(User, current_user_id)
    if not current_user or not current_user.is_active:
        return jsonify({"success": False, "error": "Utilisateur introuvable."}), 404

    friends_list = current_user.get_friends()
    is_friend = any(f.id == friend_id for f in friends_list)

    if not is_friend:
        return jsonify(
            {
                "success": False,
                "error": "Cet utilisateur ne fait pas partie de vos amis.",
            }
        ), 403

    try:
        messages = Message.get_conversation(current_user_id, friend_id)

        return jsonify(
            {
                "success": True,
                "messages": [msg.to_dict() for msg in messages],
            }
        ), 200

    except SQLAlchemyError:
        return jsonify(
            {
                "success": False,
                "error": "Erreur lors de la récupération de l'historique de la conversation.",
            }
        ), 500


@messages_bp.route("/documents/<path:filename>", methods=["GET"])
def serve_document(filename):
    """
    Serves a specific document file from the uploads directory securely.
    """
    docs_folder = os.path.join(UPLOAD_FOLDER, "documents")
    return send_from_directory(docs_folder, filename)


@messages_bp.route("/<int:message_id>", methods=["DELETE"])
@jwt_required()
def delete_message(message_id):
    current_user_id = int(get_jwt_identity())
    message = db.session.get(Message, message_id)

    if not message:
        return jsonify({"success": False, "error": "Message introuvable."}), 200

    if message.sender_id != current_user_id:
        return jsonify(
            {"success": False, "error": "Non autorisé à supprimer ce message."}
        ), 200

    file_name = message.file_name
    receiver_id = message.receiver_id
    sender_id = message.sender_id

    try:
        db.session.delete(message)
        db.session.commit()

        if file_name:
            file_path = os.path.join(UPLOAD_FOLDER, "documents", file_name)
            if os.path.exists(file_path):
                os.remove(file_path)

        from extensions import socketio

        socketio.emit(
            "message_deleted", {"message_id": message_id}, to=f"user_{receiver_id}"
        )
        socketio.emit(
            "message_deleted", {"message_id": message_id}, to=f"user_{sender_id}"
        )

        return jsonify(
            {"success": True, "message": "Message supprimé avec succès."}
        ), 200

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erreur serveur."}), 200
