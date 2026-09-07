import os
import uuid

from file_upload_management.routes import delete_file_physically, upload_bp
from seeds import seed_database
from sqlalchemy.exc import SQLAlchemyError
from vault import VaultClient

vault = VaultClient()

database_secrets = vault.get_secret("database")
jwt_secrets = vault.get_secret("jwt")

from dotenv import dotenv_values
from extensions import bcrypt, db, jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
)
from memo_gamification import gamification_api
from models import User
from sqlalchemy import select

app = Flask(__name__)

env_frontend = dotenv_values(".env.frontend")
frontend_url = env_frontend.get("VITE_API_URL", "https://localhost:8443")

CORS(
    app,
    resources={
        r"/uploads/*": {"origins": [frontend_url], "methods": ["GET", "OPTIONS"]},
        r"/upload": {"origins": [frontend_url], "methods": ["POST", "OPTIONS"]},
        r"/users/avatar": {"origins": [frontend_url], "methods": ["DELETE", "OPTIONS"]},
        r"/login": {"origins": [frontend_url], "methods": ["POST", "OPTIONS"]},
        r"/me": {"origins": [frontend_url], "methods": ["GET", "OPTIONS"]},
        r"/users*": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"success": False, "error": "utilisateur introuvable"}), 200

    data = request.get_json()
    if "username" in data:
        user.username = data["username"]

    db.session.commit()
    return jsonify({"success": True, **user.to_dict()}), 200


# D - Delete : supprimer un utilisateur
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"success": False, "error": "utilisateur introuvable"}), 200

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


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"success": False, "error": "email et password requis"}), 200

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "email et password requis"}), 200

    user = db.session.execute(
        select(User).where(User.email == data["email"])
    ).scalar_one_or_none()

    if user is None or not user.is_active or not user.check_password(data["password"]):
        return jsonify(
            {"success": False, "error": "email ou mot de passe incorrect"}
        ), 200

    access_token = create_access_token(identity=str(user.id))
    return jsonify(
        {"success": True, "access_token": access_token, "user": user.to_dict()}
    ), 200


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None or not user.is_active:
        return jsonify({"success": False, "error": "utilisateur introuvable"}), 200

    return jsonify({"success": True, **user.to_dict()}), 200


# Crée les tables si elles n'existent pas encore
with app.app_context():
    db.create_all()
    seed_database()


app.register_blueprint(upload_bp)
app.register_blueprint(gamification_api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
