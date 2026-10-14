import os

from authlib.integrations.base_client.errors import MismatchingStateError, OAuthError
from extensions import db, oauth
from flask import Blueprint, jsonify, redirect
from flask_jwt_extended import create_access_token
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

    if not user:
        user = User(
            username=username,
            email=email,
            password=None,
            oauth_provider="42",
            oauth_id=oauth_id,
        )
        db.session.add(user)
        db.session.commit()
    elif not user.oauth_id:
        user.oauth_provider = "42"
        user.oauth_id = oauth_id
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    frontend_url = os.environ.get("VITE_API_URL")
    redirect_target = f"{frontend_url}/oauth-success?token={access_token}"

    return redirect(redirect_target)
