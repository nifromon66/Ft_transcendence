import os

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
_ = CORS(app)
app.json.ensure_ascii = False  # pyright: ignore[reportAttributeAccessIssue]
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict[str, int | str]:
        return {"id": self.id, "username": self.username, "email": self.email}


# R - Read : récupérer tous les utilisateurs
@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    return jsonify([user.to_dict() for user in users])


# C - Create : créer un utilisateur
@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if (
        not data
        or "username" not in data
        or "email" not in data
        or "password" not in data
    ):
        return jsonify({"error": "username, email et password requis"}), 400

    new_user = User(
        username=data["username"], email=data["email"], password=data["password"]
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201


# U - Update : modifier un utilisateur existant
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    user = db.session.get(User, user_id)

    if user is None:
        return jsonify({"error": "utilisateur introuvable"}), 404

    data = request.get_json()
    if "username" in data:
        user.username = data["username"]

    db.session.commit()
    return jsonify(user.to_dict())


# D - Delete : supprimer un utilisateur
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "utilisateur introuvable"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "utilisateur supprimé"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "email et password requis"}), 400

    user = db.session.execute(
        select(User).where(User.email == data["email"])
    ).scalar_one_or_none()

    if user is None or not user.check_password(data["password"]):
        return jsonify({"error": "email ou mot de passe incorrect"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "user": user.to_dict()})


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if user is None:
        return jsonify({"error": "utilisateur introuvable"}), 404

    return jsonify(user.to_dict())


# Crée les tables si elles n'existent pas encore
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
