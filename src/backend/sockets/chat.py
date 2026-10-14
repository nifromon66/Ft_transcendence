from extensions import db, online_users, socketio
from flask import request
from models import Message, User
from sqlalchemy.exc import SQLAlchemyError


@socketio.on("send_message")
def handle_new_message(data):
    sender_id = next(
        (uid for uid, sid in online_users.items() if sid == request.sid), None
    )

    if not sender_id:
        socketio.emit(
            "message_error",
            {"error": "Non authentifié (ou session expirée)."},
            to=request.sid,
        )
        return

    receiver_id = data.get("receiver_id")
    content = data.get("content")
    file_url = data.get("file_url")
    file_name = data.get("file_name")
    file_type = data.get("file_type")
    file_size = data.get("file_size")

    if not receiver_id:
        socketio.emit("message_error", {"Le destinataire est invalide"}, to=request.sid)
        return

    if not content and not file_url:
        socketio.emit(
            "message_error",
            {"error": "Le message doit contenir du texte ou un fichier pdf."},
            to=request.sid,
        )
        return

    sender = db.session.get(User, sender_id)
    if not sender or not sender.is_active:
        socketio.emit(
            "message_error", {"error": "Votre compte est inactif."}, to=request.sid
        )
        return

    friends_list = sender.get_friends()
    is_friend = any(f.id == receiver_id for f in friends_list)

    if not is_friend:
        socketio.emit(
            "message_error",
            {"error": "Cet utilisateur ne fait plus partie de vos amis."},
            to=request.sid,
        )
        return

    try:
        new_message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            file_url=file_url,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
        )
        db.session.add(new_message)
        db.session.commit()

        message_data = new_message.to_dict()

        socketio.emit("receive_message", message_data, room=f"user_{receiver_id}")
        socketio.emit("receive_message", message_data, to=request.sid)

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {e!s}")
        socketio.emit("message_error", {"error": "Erreur serveur."}, to=request.sid)
