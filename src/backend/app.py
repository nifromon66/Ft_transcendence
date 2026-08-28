import os

from seeds import seed_database
from vault import VaultClient

vault = VaultClient()

database_secrets = vault.get_secret("database")
jwt_secrets = vault.get_secret("jwt")

from extensions import bcrypt, db, jwt
from file_upload_management.routes import upload_bp
from flask import Flask, jsonify, request
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

    if user is None or not user.check_password(data["password"]):
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

    if user is None:
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
