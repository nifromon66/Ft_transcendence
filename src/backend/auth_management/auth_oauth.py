import os
from datetime import timedelta

from authlib.integrations.base_client.errors import MismatchingStateError, OAuthError
from flask import Blueprint, jsonify, make_response, redirect, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    set_refresh_cookies,
)
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError

from extensions import db, oauth
from models import User

auth_oauth_bp = Blueprint("auth_oauth", __name__)


@auth_oauth_bp.route("/auth/login/42", methods=["GET"])
def login_42():
    client = oauth.create_client("42")
    base_url = os.environ.get("VITE_API_URL")
    redirect_uri = base_url + "/api/auth/callback/42"
    response = client.authorize_redirect(redirect_uri)
    return response


@auth_oauth_bp.route("/auth/callback/42", methods=["GET"])
def callback_42():
    try:
        client = oauth.create_client("42")
        token = client.authorize_access_token()
    except MismatchingStateError:
        return jsonify(
            {"error": "Session invalide ou expirée. Veuillez relancer la connexion."}
        ), 400
    except OAuthError:
        return jsonify(
            {"error": "L'authentification auprès de l'intra 42 a échoué."}
        ), 401

    resp = client.get("me", token=token)
    profile = resp.json()
    oauth_id = str(profile.get("id"))
    username = profile.get("login")
    email = profile.get("email")

    if not email:
        return jsonify(
            {"error": "Impossible de récupérer l'email depuis l'intra 42"}
        ), 400

    user = User.query.filter_by(email=email).first()
    frontend_url = os.environ.get("VITE_API_URL")

    if not user:
        pending_token = create_access_token(
            identity="0",
            expires_delta=timedelta(minutes=10),
            additional_claims={
                "is_oauth_pending": True,
                "oauth_id": oauth_id,
                "username": username,
                "email": email,
            },
        )
        return redirect(f"{frontend_url}/oauth-success?pending_token={pending_token}")
    if not user.is_active or user.deleted_at:
        return jsonify(error="Compte désactivé."), 403
    if not user.oauth_id:
        user.oauth_provider = "42"
        user.oauth_id = oauth_id
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    redirect_target = f"{frontend_url}/oauth-success?token={access_token}"

    response = redirect(redirect_target)
    refresh_token = create_refresh_token(identity=str(user.id))
    set_refresh_cookies(response, refresh_token)
    return response


@auth_oauth_bp.route("/auth/oauth/complete", methods=["POST"])
def complete_oauth_registration():
    data = request.get_json() or {}

    if data.get("accept_terms") is not True or data.get("accept_privacy") is not True:
        return jsonify(
            {
                "success": False,
                "error": "Veuillez accepter les CGU et la politique de confidentialité.",
            }
        ), 200

    pending_token = data.get("pending_token", "")
    if not pending_token:
        return jsonify(
            {
                "success": False,
                "error": "Jeton d'inscription manquant.",
            }
        ), 200

    try:
        decoded = decode_token(pending_token)
    except (ExpiredSignatureError, InvalidTokenError):
        return jsonify(
            {
                "success": False,
                "error": "La session d'inscription a expiré. Veuillez vous reconnecter avec 42.",
            }
        ), 200

    if not decoded.get("is_oauth_pending"):
        return jsonify(
            {
                "success": False,
                "error": "Jeton d'inscription invalide.",
            }
        ), 200

    oauth_id = decoded.get("oauth_id")
    username = decoded.get("username")
    email = decoded.get("email")

    if not oauth_id or not username or not email:
        return jsonify(
            {
                "success": False,
                "error": "Données OAuth incomplètes.",
            }
        ), 200

    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                username=username,
                email=email,
                password=None,
                oauth_provider="42",
                oauth_id=str(oauth_id),
            )
            db.session.add(user)
            db.session.commit()
        elif not user.is_active or user.deleted_at:
            return jsonify({"success": False, "error": "Compte désactivé."}), 200

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = make_response(
            jsonify(
                {
                    "success": True,
                    "access_token": access_token,
                }
            ),
            201,
        )
        set_refresh_cookies(response, refresh_token)
        return response
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(
            {"success": False, "error": "Erreur lors de la création du compte."}
        ), 500
