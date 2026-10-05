import pyotp
from extensions import db, limiter
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from models import User

auth_2fa_bp = Blueprint("auth_2fa", __name__)


@auth_2fa_bp.route("/auth/2fa/setup", methods=["POST"])
@jwt_required()
def setup_2fa():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404

    data = request.get_json()
    password = data.get("password")

    if user.oauth_provider:
        return jsonify(
            {"error": "Le 2FA n'est pas disponible pour les comptes OAuth."}
        ), 403

    if not password or not user.check_password(password):
        return jsonify({"error": "Mot de passe incorrect."}), 401

    secret = pyotp.random_base32()

    user.totp_secret = secret
    db.session.commit()

    qr_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name="Transcendence"
    )

    return jsonify(
        {
            "secret": secret,
            "qr_uri": qr_uri,
        }
    ), 200


@auth_2fa_bp.route("/auth/2fa/verify-setup", methods=["POST"])
@jwt_required()
def verify_2fa_setup():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user or not user.totp_secret:
        return jsonify({"error": "Configuration 2FA introuvable."}), 400

    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"error": "Le code à 6 chiffres est requis"}), 400

    totp = pyotp.TOTP(user.totp_secret)

    if totp.verify(code):
        user.is_2fa_enabled = True
        db.session.commit()
        return jsonify(
            {"message": "L'authentification à double facteur est activée avec succès !"}
        ), 200
    else:
        return jsonify({"error": "Code invalide. Veuillez réessayer."}), 401


@auth_2fa_bp.route("/auth/2fa/verify-login", methods=["POST"])
@jwt_required()
@limiter.limit("5 per minute")
def verify_login_2fa():
    claims = get_jwt()
    if not claims.get("is_2fa_pending"):
        return jsonify({"error": "Token invalide pour cette opération."}), 403

    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user or not user.is_2fa_enabled:
        return jsonify({"error": "Requête invalide."}), 400

    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"error": "Le code à 6 chiffres est requis."}), 400

    totp = pyotp.TOTP(user.totp_secret)

    if totp.verify(code):
        final_token = create_access_token(identity=str(user.id))

        return jsonify(
            {
                "success": True,
                "access_token": final_token,
                "user": user.to_dict(),
            }
        ), 200
    else:
        return jsonify({"error": "Code 2FA invalide."}), 401


@auth_2fa_bp.route("/auth/2fa/disable", methods=["POST"])
@jwt_required()
def disable_2fa():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "Utilisateur introuvable."}), 404

    if user.oauth_provider:
        return jsonify({"error": "Action non autorisée pour les comptes OAuth."}), 403

    data = request.get_json()
    password = data.get("password")
    code = data.get("code")

    if not password or not user.check_password(password):
        return jsonify({"error": "Mot de passe incorrect."}), 401

    if not code:
        return jsonify({"error": "Le code d'authentification est requis."}), 400

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code):
        return jsonify({"error": "Le code 2FA est invalide ou a expiré."}), 401

    user.is_2fa_enabled = False
    user.totp_secret = None
    db.session.commit()

    return jsonify(
        {"message": "L'authentification à double facteur a été désactivée."}
    ), 200
