import os

from authlib.integrations.flask_client import OAuth
from flask import request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
oauth = OAuth()
online_users = {}

socketio = SocketIO()


@jwt.token_verification_loader
def verify_not_pending_2fa(jwt_header, jwt_payload):
    if jwt_payload.get("is_2fa_pending"):
        return request.endpoint == "auth_2fa.verify_login_2fa"
    return True


def init_oauth(app):
    oauth.init_app(app)

    oauth.register(
        name="42",
        client_id=os.environ.get("FORTY_TWO_CLIENT_ID"),
        client_secret=os.environ.get("FORTY_TWO_CLIENT_SECRET"),
        access_token_url="https://api.intra.42.fr/oauth/token",
        authorize_url="https://api.intra.42.fr/oauth/authorize",
        api_base_url="https://api.intra.42.fr/v2/",
        client_kwargs={"scope": "public"},
    )


limiter = Limiter(
    get_remote_address,
    storage_uri="memory://",
    default_limits=["2000 per hour", "200 per minute"],
)
