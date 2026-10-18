from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import verify_jwt_in_request

from .permissions import permissions_for


def can(permission):
    user = getattr(g, "current_user", None)
    return bool(user and user.is_active and permission in permissions_for(user.role))


def permission_required(permission):
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            verify_jwt_in_request()
            if not can(permission):
                return jsonify(success=False, error="Permission insuffisante."), 403
            return function(*args, **kwargs)

        return wrapped

    return decorate
