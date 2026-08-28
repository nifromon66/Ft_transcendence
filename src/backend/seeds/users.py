import os

from sqlalchemy import select

from models import User
from extensions import db


def seed_users():

    # create a site user for test
    username = os.environ["TEST_USERNAME"]
    email = os.environ["TEST_EMAIL"]
    password = os.environ["TEST_PASSWORD"]

    test = User(
        username=username,
        email=email,
        password=password,
        role="test")
    if db.session.scalar(select(User).where(User.email == test.email)) is None:
        db.session.add(test)

    # create site anonymus user, used to host content from deleted users.
    username = os.environ["ANON_USERNAME"]
    email = os.environ["ANON_EMAIL"]
    password = os.environ["ANON_PASSWORD"]
	
    anon = User(
        username=username,
        email=email,
        password=password,
        role="anon")
    if db.session.scalar(select(User).where(User.email == anon.email)) is None:
        db.session.add(anon)
    db.session.commit()