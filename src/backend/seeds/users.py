import os

from sqlalchemy import select

from extensions import db
from models import User


def seed_users():
    admin_username = os.environ.get("ADMIN_USERNAME", "").strip()
    admin_email = os.environ.get("ADMIN_EMAIL", "").strip()
    admin_password = os.environ.get("ADMIN_PASSWORD", "")
    admin_config = (admin_username, admin_email, admin_password)
    if any(admin_config) and not all(admin_config):
        raise ValueError(
            "ADMIN_USERNAME, ADMIN_EMAIL et ADMIN_PASSWORD doivent être renseignés ensemble."
        )
    if admin_password and len(admin_password.encode("utf-8")) > 72:
        raise ValueError("ADMIN_PASSWORD dépasse la limite bcrypt de 72 octets UTF-8.")
    if admin_email and admin_email == os.environ["TEST_EMAIL"]:
        raise ValueError("ADMIN_EMAIL doit être différent de TEST_EMAIL.")

    # Keep the test user first: existing recipe seeds refer to user_id=1.
    accounts = [
        (
            os.environ["TEST_USERNAME"],
            os.environ["TEST_EMAIL"],
            os.environ["TEST_PASSWORD"],
            "user",
        )
    ]
    if all(admin_config):
        accounts.append((*admin_config, "admin"))

    for username, email, password, role in accounts:
        if db.session.scalar(select(User.id).where(User.email == email)) is not None:
            continue
        if (
            db.session.scalar(select(User.id).where(User.username == username))
            is not None
        ):
            raise ValueError(
                "Le pseudo d'un compte seedé est déjà utilisé par un autre compte."
            )
        db.session.add(
            User(username=username, email=email, password=password, role=role)
        )
        db.session.flush()

    db.session.commit()
