import os
import uuid
from datetime import timedelta

from auth_management.auth_2fa import auth_2fa_bp
from file_upload_management.routes import delete_file_physically, upload_bp
from flask_socketio import join_room
from friends_management.routes import friends_bp
from jwt import ExpiredSignatureError, InvalidTokenError
from seeds import seed_database
from sqlalchemy.exc import SQLAlchemyError
from vault import VaultClient
from werkzeug.middleware.proxy_fix import ProxyFix

vault = VaultClient()

database_secrets = vault.get_secret("database")
jwt_secrets = vault.get_secret("jwt")

from auth_management.auth_oauth import auth_oauth_bp
from auth_management.routes import auth_bp
from extensions import bcrypt, db, init_oauth, jwt, limiter, online_users, socketio
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    decode_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
)
from messages_management.routes import messages_bp
from models import User
from models.message import Message
from recipe_management.routes import recipe_bp

# to be re-organized here
from routes import gamification_api, recipes_bp
from routes.users import users_bp
from sqlalchemy import select

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

frontend_url = os.environ.get("VITE_API_URL")

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

limiter.init_app(app)


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(
        {"success": False, "error": "Trop de tentatives. Veuillez réessayer plus tard."}
    ), 429


CORS(
    app,
    resources={
        r"/uploads/.*": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/upload/avatar": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/upload/document": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/auth/login": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/auth/register": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/me": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/users": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "OPTIONS"],
        },
        r"/users/\d+": {
            "origins": [frontend_url],
            "methods": ["PUT", "DELETE", "OPTIONS"],
        },
        r"/users/avatar": {
            "origins": [frontend_url],
            "methods": ["DELETE", "OPTIONS"],
        },
        r"/users/me": {
            "origins": [frontend_url],
            "methods": ["PUT", "OPTIONS"],
        },
        r"/users/me/delete": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/friends": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/friends/search": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/friends/discover": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/friends/requests/received": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/friends/requests/sent": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/friends/\d+": {
            "origins": [frontend_url],
            "methods": ["DELETE", "OPTIONS"],
        },
        r"/friends/request/\d+": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/friends/request/\d+/accept": {
            "origins": [frontend_url],
            "methods": ["PATCH", "OPTIONS"],
        },
        r"/friends/request/\d+/cancel": {
            "origins": [frontend_url],
            "methods": ["DELETE", "OPTIONS"],
        },
        r"/friends/request/\d+/deny": {
            "origins": [frontend_url],
            "methods": ["DELETE", "OPTIONS"],
        },
        r"/badges": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/getbadge": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/recipe/\d+": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/messages/\d+": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
    },
    supports_credentials=True,
    allow_headers=["Authorization", "Content-Type"],
)

app.json.ensure_ascii = False  # pyright: ignore[reportAttributeAccessIssue]
app.config["SQLALCHEMY_DATABASE_URI"] = database_secrets["url"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = jwt_secrets["secret_key"]

jwt.init_app(app)
db.init_app(app)
bcrypt.init_app(app)
socketio.init_app(app, cors_allowed_origins=[frontend_url])
init_oauth(app)


# R - Read : récupérer tous les utilisateurs
@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return jsonify([user.to_dict() for user in users]), 200


# C - Create : créer un utilisateur
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "Aucune donnée fournie"}), 200

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify(
            {"success": False, "error": "username, email et password requis"}
        ), 200

    existing_user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({"success": False, "error": "Cet email est déjà utilisé."}), 200

    new_user = User(
        username=data["username"], email=data["email"], password=data["password"]
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, **new_user.to_dict()}), 201


# U - Update : modifier un utilisateur existant
@app.route("/users/me", methods=["PUT"])
@jwt_required()
def update_my_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if user is None or not user.is_active:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Aucune donnée fournie."}), 400

    new_username = data.get("username", "").strip()
    new_email = data.get("email", "").strip()

    has_changed = False

    if new_email and new_email != user.email:
        existing_email = db.session.execute(
            select(User).where(User.email == new_email)
        ).scalar_one_or_none()

        if existing_email:
            return jsonify(
                {
                    "success": False,
                    "error": "Cet email est déjà utilisé par un autre compte.",
                }
            ), 400

        user.email = new_email
        has_changed = True

    if new_username and new_username != user.username:
        existing_username = db.session.execute(
            select(User).where(User.username == new_username)
        ).scalar_one_or_none()

        if existing_username:
            return jsonify(
                {
                    "success": False,
                    "error": "Ce pseudo est déjà utilisé par un autre compte.",
                }
            ), 400

        user.username = new_username
        has_changed = True

    if has_changed:
        db.session.commit()

        from extensions import socketio

        socketio.emit(
            "user_profile_updated", {"user_id": user.id, "new_username": user.username}
        )

    return jsonify(
        {
            "success": True,
            "message": "Profil mis à jour avec succès.",
            "user": user.to_dict(),
        }
    ), 200


# D - Delete : supprimer un utilisateur
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200

    db.session.delete(user)
    db.session.commit()

    return jsonify({"success": True, "message": "utilisateur supprimé"}), 200


@app.route("/users/me/delete", methods=["POST"])
@jwt_required()
def delete_my_account():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 404

    data = request.get_json()
    password = data.get("password", "") if data else ""

    if not password:
        return jsonify({"success": False, "error": "Le mot de passe est requis."}), 400

    if not user.check_password(password):
        return jsonify({"success": False, "error": "Mot de passe incorrect."}), 400

    try:
        if user.avatar_url:
            try:
                delete_file_physically(user.avatar_url)
            except OSError as e:
                app.logger.error(f"Erreur lors de la suppression de l'avatar: {e!s}")
                return jsonify(
                    {
                        "sucess": False,
                        "error": "Erreur lors de la suppression de l'avatar.",
                    }
                ), 500

            user.avatar_url = None

        user.is_active = False
        user.username = "Utilisateur supprimé"
        user.email = f"deleted_{uuid.uuid4().hex}@anonymized.invalid"
        user.password_hash = "!"

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Votre compte a été supprimé avec succès.",
            }
        ), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Erreur lors de la suppression du compte : {e!s}")
        return jsonify(
            {"success": False, "error": "Erreur lors de la suppression du compte."}
        ), 500


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"success": False, "error": "Utilisateur introuvable"}), 200

    return jsonify({"success": True, **user.to_dict()}), 200


# Crée les tables si elles n'existent pas encore
with app.app_context():
    db.create_all()
    seed_database()


app.register_blueprint(upload_bp)
app.register_blueprint(gamification_api)
app.register_blueprint(recipe_bp)
app.register_blueprint(friends_bp)
app.register_blueprint(recipes_bp)  ##for search func
app.register_blueprint(users_bp)
app.register_blueprint(messages_bp)
app.register_blueprint(auth_oauth_bp)
app.register_blueprint(auth_2fa_bp)
app.register_blueprint(auth_bp)

import sockets.chat
import sockets.connection

_ = (sockets.chat, sockets.connection)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
