from extensions import db
from file_upload_management.services import (
    delete_file_physically,
)
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User
from models.message import Message
from sqlalchemy.exc import SQLAlchemyError

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/messages/<int:friend_id>", methods=["GET"])
@jwt_required()
def get_chat_history(friend_id):
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


@messages_bp.route("/messages/<int:message_id>", methods=["DELETE"])
@jwt_required()
def delete_message(message_id):
    current_user_id = int(get_jwt_identity())
    message = db.session.get(Message, message_id)

    if not message:
        return jsonify({"success": False, "error": "Message introuvable."}), 404

    if message.sender_id != current_user_id:
        return jsonify(
            {
                "success": False,
                "error": "Vous ne pouvez supprimer que vos propres messages.",
            }
        ), 403

    file_url = message.file_url

    try:
        db.session.delete(message)
        db.session.commit()

        if file_url:
            filename = file_url.replace("/uploads/", "", 1).lstrip("/")
            delete_file_physically(filename)

        return jsonify(
            {"success": True, "message": "Message supprimé avec succès."}
        ), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Erreur serveur lors de la suppression."}
        ), 500
