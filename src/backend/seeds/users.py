import os

from extensions import db
from models import User
from sqlalchemy import select


def seed_users():

    # create a site user for test
    username = os.environ["TEST_USERNAME"]
    email = os.environ["TEST_EMAIL"]
    password = os.environ["TEST_PASSWORD"]

    test = User(username=username, email=email, password=password, role="test")
    if db.session.scalar(select(User).where(User.email == test.email)) is None:
        db.session.add(test)

    db.session.commit()
