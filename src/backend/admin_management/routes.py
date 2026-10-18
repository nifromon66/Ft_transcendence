from auth_management.decorators import can, permission_required
from auth_management.permissions import ROLES
from extensions import db
from flask import Blueprint, g, jsonify, request
from models import Comment, Recipe, User
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .services import (
    anonymize,
    audit,
    cleanup_account,
    disconnect_account,
    is_last_admin,
    lock_administrators,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.errorhandler(SQLAlchemyError)
def database_error(error):
    db.session.rollback()
    from flask import current_app

    current_app.logger.exception("Erreur d'administration")
    return jsonify(
        success=False, error="Impossible d'enregistrer cette opération."
    ), 500


def body(allowed):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data or set(data) - set(allowed):
        return None
    return data


def page_of(statement):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return None
    if page < 1 or not 1 <= per_page <= 100:
        return None
    total = db.session.scalar(select(func.count()).select_from(statement.subquery()))
    items = db.session.scalars(
        statement.offset((page - 1) * per_page).limit(per_page)
    ).all()
    return items, {"page": page, "per_page": per_page, "total": total}


def invalid(message="Données invalides.", status=400):
    return jsonify(success=False, error=message), status


def valid_identity(data, creating=False):
    for field in ("username", "email"):
        if creating or field in data:
            value = data.get(field)
            if (
                not isinstance(value, str)
                or not value.strip()
                or len(value.strip()) > 254
            ):
                return False
            data[field] = value.strip()
    if "email" in data and (
        "@" not in data["email"] or "." not in data["email"].split("@")[-1]
    ):
        return False
    if "role" in data and data["role"] not in ROLES:
        return False
    if creating:
        password = data.get("password")
        if (
            not isinstance(password, str)
            or not password
            or len(password.encode("utf-8")) > 72
        ):
            return False
    return True


def duplicate_identity(data, exclude_id=None):
    conditions = [
        getattr(User, key) == data[key] for key in ("email", "username") if key in data
    ]
    if not conditions:
        return False
    stmt = select(User.id).where(or_(*conditions))
    if exclude_id:
        stmt = stmt.where(User.id != exclude_id)
    return db.session.scalar(stmt.limit(1)) is not None


@admin_bp.get("/users")
@permission_required("users.read")
def list_users():
    stmt = select(User).order_by(User.id)
    query = request.args.get("q", "").strip()
    if query:
        stmt = stmt.where(
            or_(
                User.username.icontains(query, autoescape=True),
                User.email.icontains(query, autoescape=True),
            )
        )
    role = request.args.get("role")
    if role:
        if role not in ROLES:
            return invalid("Rôle invalide.")
        stmt = stmt.where(User.role == role)
    status = request.args.get("status")
    if status:
        if status == "deleted":
            stmt = stmt.where(User.deleted_at.is_not(None))
        elif status in ("active", "suspended"):
            stmt = stmt.where(
                User.deleted_at.is_(None), User.is_active == (status == "active")
            )
        else:
            return invalid("Statut invalide.")
    result = page_of(stmt)
    if result is None:
        return invalid("Pagination invalide.")
    users, pagination = result
    return jsonify(
        success=True,
        users=[user.to_admin_dict() for user in users],
        pagination=pagination,
        roles=ROLES,
    )


@admin_bp.get("/users/<int:user_id>")
@permission_required("users.read")
def get_user(user_id):
    user = db.session.get(User, user_id)
    return (
        jsonify(success=True, user=user.to_admin_dict())
        if user
        else invalid("Compte introuvable.", 404)
    )


@admin_bp.post("/users")
@permission_required("users.create")
def create_user():
    data = body({"username", "email", "password", "role"})
    if data is None or not valid_identity(data, creating=True):
        return invalid(
            "Pseudo, email, rôle et mot de passe non vide (72 octets maximum) valides requis."
        )
    if data.get("role", "user") != "user" and not can("roles.assign"):
        return invalid("Permission insuffisante.", 403)
    if duplicate_identity(data):
        return invalid("Email ou pseudo déjà utilisé.", 409)
    user = User(**data)
    db.session.add(user)
    try:
        db.session.flush()
        audit("users.create", "user", user.id, role=user.role)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return invalid("Email ou pseudo déjà utilisé.", 409)
    return jsonify(success=True, user=user.to_admin_dict()), 201


def locked_target(user_id, permission):
    administrators = lock_administrators()
    # Refresh the actor after waiting for locks: a concurrent request may revoke access.
    db.session.refresh(g.current_user)
    if not can(permission):
        return None, administrators, invalid("Permission insuffisante.", 403)
    user = db.session.scalar(
        select(User)
        .where(User.id == user_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if not user:
        return None, administrators, invalid("Compte introuvable.", 404)
    if user.deleted_at:
        return None, administrators, invalid("Ce compte a été supprimé.", 409)
    return user, administrators, None


@admin_bp.patch("/users/<int:user_id>")
@permission_required("users.update")
def update_user(user_id):
    data = body({"username", "email", "is_active"})
    if (
        data is None
        or not valid_identity(data)
        or ("is_active" in data and type(data["is_active"]) is not bool)
    ):
        return invalid()
    user, administrators, error = locked_target(user_id, "users.update")
    if error:
        return error
    if data.get("is_active") is False and is_last_admin(user, administrators):
        return invalid("Le dernier administrateur actif doit être conservé.", 409)
    if duplicate_identity(data, user.id):
        return invalid("Email ou pseudo déjà utilisé.", 409)
    suspend = data.get("is_active") is False and user.is_active
    before = {key: getattr(user, key) for key in data}
    for key, value in data.items():
        setattr(user, key, value)
    if suspend:
        user.token_version += 1
    audit("users.update", "user", user.id, before=before, after=data)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return invalid("Email ou pseudo déjà utilisé.", 409)
    if suspend:
        disconnect_account(user.id)
    return jsonify(success=True, user=user.to_admin_dict())


@admin_bp.patch("/users/<int:user_id>/role")
@permission_required("roles.assign")
def change_role(user_id):
    data = body({"role"})
    if (
        data is None
        or not isinstance(data.get("role"), str)
        or data["role"] not in ROLES
    ):
        return invalid("Rôle invalide.")
    user, administrators, error = locked_target(user_id, "roles.assign")
    if error:
        return error
    if data["role"] != "admin" and is_last_admin(user, administrators):
        return invalid("Le dernier administrateur actif doit être conservé.", 409)
    before = user.role
    user.role = data["role"]
    audit("roles.assign", "user", user.id, before=before, after=user.role)
    db.session.commit()
    return jsonify(success=True, user=user.to_admin_dict())


@admin_bp.delete("/users/<int:user_id>")
@permission_required("users.delete")
def delete_user(user_id):
    user, administrators, error = locked_target(user_id, "users.delete")
    if error:
        return error
    if is_last_admin(user, administrators):
        return invalid("Le dernier administrateur actif doit être conservé.", 409)
    avatar = anonymize(user)
    audit("users.delete", "user", user.id)
    db.session.commit()
    cleanup_account(user.id, avatar)
    return jsonify(success=True)


@admin_bp.get("/moderation")
@permission_required("content.moderate")
def moderation():
    kind = request.args.get("kind", "recipes")
    if kind not in ("recipes", "comments"):
        return invalid()
    model = Recipe if kind == "recipes" else Comment
    stmt = select(model).order_by(model.id.desc())
    if kind == "comments":
        stmt = stmt.where(Comment.is_removed.is_(False))
    result = page_of(stmt)
    if result is None:
        return invalid("Pagination invalide.")
    rows, pagination = result
    items = [
        {
            "id": row.id,
            "author": row.user.username,
            **(
                {"title": row.title}
                if kind == "recipes"
                else {"content": row.content, "recipe_id": row.recipe_id}
            ),
        }
        for row in rows
    ]
    return jsonify(success=True, items=items, pagination=pagination)


@admin_bp.delete("/comments/<int:comment_id>")
@permission_required("content.moderate")
def remove_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if not comment:
        return invalid("Commentaire introuvable.", 404)
    comment.content = "[Commentaire retiré par la modération]"
    comment.is_removed = True
    audit("comments.remove", "comment", comment.id)
    db.session.commit()
    return jsonify(success=True)
