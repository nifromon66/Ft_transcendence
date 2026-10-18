from datetime import timedelta

from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models import User
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint("auth_management", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify(
            {
                "success": False,
                "error": "Nom d'utilisateur, email et mot de passe requis.",
            }
        ), 400

    existing_user = db.session.execute(
        select(User).where(or_(User.email == email, User.username == username))
    ).scalar_one_or_none()

    if existing_user:
        if existing_user.email == email:
            return jsonify(
                {"success": False, "error": "Cet email est déjà utilisé."}
            ), 409
        return jsonify({"success": False, "error": "Ce pseudo est déjà pris."}), 409

    try:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=str(new_user.id))

        return jsonify(
            {"success": True, "access_token": access_token, "user": new_user.to_private_dict()}
        ), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erreur serveur."}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify(
            {"success": False, "error": "Email et mot de passe requis."}
        ), 400

    user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if user is None or not user.is_active or not user.check_password(password):
        return jsonify(
            {"success": False, "error": "Email ou mot de passe incorrect."}
        ), 401

    if user.is_2fa_enabled:
        temp_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=5),
            additional_claims={"is_2fa_pending": True},
        )
        return jsonify(
            {
                "success": True,
                "status": "2FA_REQUIRED",
                "temp_token": temp_token,
                "message": "Veuillez vérifier votre application d'authentification.",
            }
        ), 200

    access_token = create_access_token(identity=str(user.id))
    return jsonify(
        {"success": True, "access_token": access_token, "user": user.to_private_dict()}
    ), 200
