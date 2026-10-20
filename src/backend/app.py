import eventlet

eventlet.monkey_patch()

import os

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from admin_management.routes import admin_bp
from auth_management.auth_2fa import auth_2fa_bp
from auth_management.auth_oauth import auth_oauth_bp
from auth_management.routes import auth_bp
from extensions import bcrypt, db, init_oauth, jwt, limiter, socketio
from friends_management.routes import friends_bp
from gamification_management.routes import gamification_bp
from ingredient_management.routes import ingredient_bp
from messages_management.routes import messages_bp
from recipes_management.routes import recipes_bp
from seeds import seed_database
from users_management.routes import users_bp
from vault import VaultClient

vault = VaultClient()

database_secrets = vault.get_secret("database")
jwt_secrets = vault.get_secret("jwt")


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
    ), 200


CORS(
    app,
    resources={
        r"/admin/.*": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        },
        r"/uploads/.*": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/upload/avatar": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
        },
        r"/messages/documents": {
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
        r"/auth/oauth/complete": {
            "origins": [frontend_url],
            "methods": ["POST", "OPTIONS"],
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
            "methods": ["GET", "PUT", "DELETE", "OPTIONS"],
        },
        r"/users/me/avatar-frame": {
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
        r"/friends/request/received": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/friends/request/sent": {
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
        r"/recipe/\d+": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/recipes.*": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        },
        r"/ingredients.*": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        },
        r"/ingredient-categories.*": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/messages/\d+": {
            "origins": [frontend_url],
            "methods": ["GET", "OPTIONS"],
        },
        r"/gamification/.*": {
            "origins": [frontend_url],
            "methods": ["GET", "POST", "OPTIONS"],
        },
    },
    supports_credentials=True,
    allow_headers=["Authorization", "Content-Type"],
)

app.json.ensure_ascii = False
app.config["SQLALCHEMY_DATABASE_URI"] = database_secrets["url"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = jwt_secrets["secret_key"]

app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(jwt_secrets.get("expiration", 3600))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 2592000
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False


jwt.init_app(app)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"success": False, "error": "Session expiree"}), 200


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"success": False, "error": "Token invalide"}), 200


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"success": False, "error": "Authentification requise"}), 200


db.init_app(app)
bcrypt.init_app(app)
socketio.init_app(app, cors_allowed_origins=[frontend_url])
init_oauth(app)


# Crée les tables si elles n'existent pas encore
with app.app_context():
    db.create_all()
    seed_database()


app.register_blueprint(admin_bp)
app.register_blueprint(gamification_bp)
app.register_blueprint(ingredient_bp)
app.register_blueprint(friends_bp)
app.register_blueprint(recipes_bp)
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
