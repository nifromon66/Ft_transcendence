from extensions import db, online_users, socketio
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User
from models.association import friend
from sqlalchemy import and_, case, delete, insert, or_, select, update

friends_bp = Blueprint("friends", __name__)


@friends_bp.route("/friends/request/<int:target_user_id>", methods=["POST"])
@jwt_required()
def send_friend_request(target_user_id):
    current_user_id = int(get_jwt_identity())

    if current_user_id == target_user_id:
        return jsonify(
            {
                "success": False,
                "error": "Vous ne pouvez-pas vous ajouter vous-même en ami.",
            }
        ), 400

    target_user = db.session.get(User, target_user_id)
    if not target_user or not target_user.is_active:
        return jsonify({"success": False, "error": "Utilisateur introuvable."}), 404

    existing_relation = (
        db.session.execute(
            select(friend).where(
                or_(
                    and_(
                        friend.c.user_id == current_user_id,
                        friend.c.friend_id == target_user_id,
                    ),
                    and_(
                        friend.c.user_id == target_user_id,
                        friend.c.friend_id == current_user_id,
                    ),
                )
            )
        )
        .mappings()
        .first()
    )

    if existing_relation:
        status = existing_relation["status"]

        if status == "accepted":
            return jsonify(
                {
                    "success": False,
                    "error": "Vous êtes déjà amis avec cet utilisateur.",
                }
            ), 400

        elif status == "pending":
            if existing_relation["user_id"] == current_user_id:
                return jsonify(
                    {
                        "success": False,
                        "error": "Vous avez déjà envoyé une demande d'ami à cet utilisateur.",
                    }
                ), 400
            else:
                return jsonify(
                    {
                        "success": False,
                        "error": "Cet utilisateur vous a déjà envoyé une demande d'ami.",
                    }
                ), 400

    stmt = insert(friend).values(user_id=current_user_id, friend_id=target_user_id)
    db.session.execute(stmt)
    db.session.commit()

    socketio.emit(
        "friendship_updated",
        {"user_id": current_user_id, "status": "pending_received"},
        room=f"user_{target_user_id}",
    )

    return jsonify({"success": True, "message": "Demande d'ami envoyée."}), 201


@friends_bp.route("/friends/request/<int:sender_id>/accept", methods=["PATCH"])
@jwt_required()
def accept_friend_request(sender_id):
    current_user_id = int(get_jwt_identity())

    sender = db.session.get(User, sender_id)
    if not sender or not sender.is_active:
        return jsonify(
            {"success": False, "error": "Cet utilisateur n'existe plus."}
        ), 404

    stmt = select(friend).where(
        and_(
            friend.c.user_id == sender_id,
            friend.c.friend_id == current_user_id,
            friend.c.status == "pending",
        )
    )
    request_exists = db.session.execute(stmt).first()

    if not request_exists:
        return jsonify(
            {
                "success": False,
                "error": "Aucune demande d'ami en attente de cet utilisateur n'a été trouvée.",
            }
        ), 404

    update_stmt = (
        update(friend)
        .where(
            and_(friend.c.user_id == sender_id, friend.c.friend_id == current_user_id)
        )
        .values(status="accepted")
    )
    db.session.execute(update_stmt)
    db.session.commit()

    socketio.emit(
        "friendship_updated",
        {"user_id": current_user_id, "status": "accepted"},
        room=f"user_{sender_id}",
    )

    return jsonify({"success": True, "message": "Demande d'ami acceptée !"}), 200


@friends_bp.route("/friends/request/<int:target_user_id>/cancel", methods=["DELETE"])
@jwt_required()
def cancel_friend_request(target_user_id):
    current_user_id = int(get_jwt_identity())

    delete_stmt = delete(friend).where(
        and_(
            friend.c.user_id == current_user_id,
            friend.c.friend_id == target_user_id,
            friend.c.status == "pending",
        )
    )
    result = db.session.execute(delete_stmt)
    db.session.commit()

    if result.rowcount == 0:
        return jsonify(
            {
                "success": False,
                "error": "Aucune demande d'ami envoyée et en attente trouvée pour cet utilisateur.",
            }
        ), 404

    socketio.emit(
        "friendship_updated",
        {"user_id": current_user_id, "status": "none"},
        room=f"user_{target_user_id}",
    )

    return jsonify(
        {
            "success": True,
            "message": "La demande d'ami a été annulée.",
        }
    ), 200


@friends_bp.route("/friends/request/<int:sender_id>/deny", methods=["DELETE"])
@jwt_required()
def deny_friend_request(sender_id):
    current_user_id = int(get_jwt_identity())

    delete_stmt = delete(friend).where(
        and_(
            friend.c.user_id == sender_id,
            friend.c.friend_id == current_user_id,
            friend.c.status == "pending",
        )
    )
    result = db.session.execute(delete_stmt)
    db.session.commit()

    if result.rowcount == 0:
        return jsonify(
            {
                "success": False,
                "error": "Aucune demande d'ami reçue et en attente trouvée de la part de cet utilisateur.",
            }
        ), 404

    socketio.emit(
        "friendship_updated",
        {"user_id": current_user_id, "status": "none"},
        room=f"user_{sender_id}",
    )

    return jsonify(
        {
            "success": True,
            "message": "La demande d'ami a été refusée.",
        }
    ), 200


@friends_bp.route("/friends/<int:target_user_id>", methods=["DELETE"])
@jwt_required()
def remove_friend(target_user_id):
    current_user_id = int(get_jwt_identity())

    delete_stmt = delete(friend).where(
        and_(
            or_(
                and_(
                    friend.c.user_id == current_user_id,
                    friend.c.friend_id == target_user_id,
                ),
                and_(
                    friend.c.user_id == target_user_id,
                    friend.c.friend_id == current_user_id,
                ),
            ),
            friend.c.status == "accepted",
        )
    )
    result = db.session.execute(delete_stmt)
    db.session.commit()

    if result.rowcount == 0:
        return jsonify(
            {
                "success": False,
                "error": "Cet utilisateur ne fait pas partie de vos amis.",
            }
        ), 404

    socketio.emit(
        "friendship_updated",
        {"user_id": current_user_id, "status": "none"},
        room=f"user_{target_user_id}",
    )

    return jsonify(
        {
            "success": True,
            "message": "L'utilisateur a été retiré de votre liste d'amis.",
        }
    ), 200


@friends_bp.route("/friends", methods=["GET"])
@jwt_required()
def get_friends():
    current_user_id = int(get_jwt_identity())

    current_user = db.session.get(User, current_user_id)
    if not current_user:
        return jsonify({"success": False, "error": "Utilisateur introuvable."}), 404

    friends_list = current_user.get_friends()

    result = []
    for f in friends_list:
        friend_data = f.to_dict()
        friend_data["is_online"] = f.id in online_users
        result.append(friend_data)

    return jsonify({"success": True, "friends": result}), 200


@friends_bp.route("/friends/requests/received", methods=["GET"])
@jwt_required()
def get_received_requests():
    current_user_id = int(get_jwt_identity())

    stmt = (
        select(User)
        .join(friend, User.id == friend.c.user_id)
        .where(
            and_(
                friend.c.friend_id == current_user_id,
                friend.c.status == "pending",
                User.is_active == True,
            )
        )
    )

    received_list = db.session.execute(stmt).scalars().all()

    result = []
    for u in received_list:
        user_data = u.to_dict()

        user_data["is_online"] = u.id in online_users
        result.append(user_data)

    return jsonify({"success": True, "received_requests": result}), 200


@friends_bp.route("/friends/requests/sent", methods=["GET"])
@jwt_required()
def get_sent_requests():
    current_user_id = int(get_jwt_identity())

    stmt = (
        select(User)
        .join(friend, User.id == friend.c.friend_id)
        .where(
            and_(
                friend.c.user_id == current_user_id,
                friend.c.status == "pending",
                User.is_active == True,
            )
        )
    )

    sent_list = db.session.execute(stmt).scalars().all()

    result = []
    for u in sent_list:
        user_data = u.to_dict()

        user_data = u.to_dict()
        user_data["is_online"] = u.id in online_users
        result.append(user_data)

    return jsonify({"success": True, "sent_requests": result}), 200


@friends_bp.route("/friends/discover", methods=["GET"])
@jwt_required()
def discover_users():
    current_user_id = int(get_jwt_identity())

    subquery_friends = select(
        case(
            (friend.c.user_id == current_user_id, friend.c.friend_id),
            else_=friend.c.user_id,
        )
    ).where(
        or_(friend.c.user_id == current_user_id, friend.c.friend_id == current_user_id)
    )

    stmt = (
        select(User)
        .where(
            and_(
                User.id != current_user_id,
                User.is_active == True,
                User.id.not_in(subquery_friends),
            )
        )
        .limit(20)
    )

    users_to_discover = db.session.execute(stmt).scalars().all()

    result = []
    for u in users_to_discover:
        user_data = u.to_dict()
        user_data["is_online"] = u.id in online_users
        result.append(user_data)

    return jsonify({"success": True, "users": result}), 200


@friends_bp.route("/friends/search", methods=["GET"])
@jwt_required()
def search_users():
    current_user_id = int(get_jwt_identity())
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"success": True, "users": []}), 200

    stmt = (
        select(User)
        .where(
            and_(
                User.id != current_user_id,
                User.is_active == True,
                User.username.ilike(f"%{query}%"),
            )
        )
        .limit(20)
    )

    users = db.session.execute(stmt).scalars().all()

    result = []
    for u in users:
        rel_stmt = select(friend).where(
            or_(
                and_(friend.c.user_id == current_user_id, friend.c.friend_id == u.id),
                and_(friend.c.user_id == u.id, friend.c.friend_id == current_user_id),
            )
        )
        relation = db.session.execute(rel_stmt).mappings().first()

        if not relation:
            status = "none"
        elif relation["status"] == "accepted":
            status = "accepted"
        elif relation["status"] == "pending":
            if relation["user_id"] == current_user_id:
                status = "pending_sent"
            else:
                status = "pending_received"

        user_data = u.to_dict()
        user_data["friendship_status"] = status
        user_data["is_online"] = u.id in online_users
        result.append(user_data)

    return jsonify({"success": True, "users": result}), 200
