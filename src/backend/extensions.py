import os

from authlib.integrations.flask_client import OAuth
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
oauth = OAuth()
online_users = {}

socketio = SocketIO()


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
