from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import join_room
from jwt import ExpiredSignatureError, InvalidTokenError

from extensions import online_users, socketio


@socketio.on("connect")
def handle_connect(auth=None):
    token = None
    if auth and "token" in auth:
        token = auth["token"]
    elif request.args.get("token"):
        token = request.args.get("token")

    if not token:
        print("Socket connection refused: No token provided by the client.", flush=True)
        return False

    try:
        decoded = decode_token(token)
        uid = int(decoded["sub"])

        room_name = f"user_{uid}"
        join_room(room_name)

        if uid not in online_users:
            online_users[uid] = set()
        online_users[uid].add(request.sid)
        socketio.emit("user_status_changed", {"user_id": uid, "is_online": True})

        print(
            f"Socket connected: User {uid} joined {room_name}",
            flush=True,
        )
        return True

    except ExpiredSignatureError:
        print(
            "WebSocket connection refused: The token has expired.",
            flush=True,
        )
        return False
    except InvalidTokenError as e:
        print(
            f"WebSocket connection refused: Invalid token ({e}).",
            flush=True,
        )
        return False
    except KeyError:
        print(
            "WebSocket connection refused: The token does not contain a user ID (missing 'sub' key).",
            flush=True,
        )
        return False
    except ValueError:
        print(
            "Websocket connection refused: The user ID is not a valid number.",
            flush=True,
        )
        return False


@socketio.on("disconnect")
def handle_disconnect():
    for user_id, sids in list(online_users.items()):
        if request.sid in sids:
            sids.remove(request.sid)
            if not sids:
                del online_users[user_id]
                socketio.emit(
                    "user_status_changed", {"user_id": user_id, "is_online": False}
                )
            break


@socketio.on("request_initial_status")
def handle_initial_status(user_ids):
    if not user_ids:
        return

    for uid in user_ids:
        try:
            uid_int = int(uid)
            if uid_int in online_users:
                socketio.emit(
                    "user_status_changed",
                    {"user_id": uid_int, "is_online": True},
                    to=request.sid,
                )
            else:
                pass
        except (ValueError, TypeError):
            uid_str = str(uid)
            if uid_str in online_users:
                socketio.emit(
                    "user_status_changed",
                    {"user_id": uid_str, "is_online": True},
                    to=request.sid,
                )
            continue
