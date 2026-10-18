import uuid
from datetime import datetime, timezone

from extensions import db, socketio
from flask import g
from models import User
from models.admin_audit import AdminAudit
from sqlalchemy import select


def audit(action, target_type, target_id, **details):
    db.session.add(
        AdminAudit(
            actor_id=g.current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
    )


def lock_administrators():
    """Serialize changes to the active admin set (PostgreSQL row locks)."""
    return db.session.scalars(
        select(User)
        .where(User.role == "admin", User.is_active.is_(True))
        .order_by(User.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).all()


def is_last_admin(user, administrators):
    return user.role == "admin" and user.is_active and len(administrators) <= 1


def anonymize(user):
    """Database changes only; file and socket cleanup happens after commit."""
    avatar = user.avatar_filename
    user.avatar_filename = None
    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)
    user.username = "Utilisateur supprimé"
    user.email = f"deleted_{uuid.uuid4().hex}@anonymized.invalid"
    user.password_hash = None
    user.oauth_provider = None
    user.oauth_id = None
    user.totp_secret = None
    user.is_2fa_enabled = False
    user.recovery_codes = []
    user.token_version += 1
    return avatar


def disconnect_account(user_id):
    # A user can have several tabs, hence several sockets in this room.
    if socketio.server is None:
        return
    participants = list(
        socketio.server.manager.get_participants("/", f"user_{user_id}")
    )
    for sid, _ in participants:
        socketio.server.disconnect(sid, namespace="/")


def cleanup_account(user_id, avatar=None):
    from flask import current_app
    from utils.file_services import delete_file_physically

    disconnect_account(user_id)
    if avatar:
        try:
            delete_file_physically(avatar)
        except OSError:
            current_app.logger.exception(
                "Impossible de supprimer l'avatar du compte %s", user_id
            )
