from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from extensions import bcrypt, db
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association import friend

if TYPE_CHECKING:
    from .association import UserBadge, friend
    from .comment import Comment
    from .favorite import Favorite
    from .rating import Rating
    from .recipe import Recipe


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String, nullable=False)

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[str] = mapped_column(String, nullable=False, default="user")

    avatar_url: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    xp: Mapped[int | None] = mapped_column(Integer)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="user")

    comments: Mapped[list["Comment"]] = relationship(back_populates="user")

    badges: Mapped[list[UserBadge]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")

    ratings: Mapped[list["Rating"]] = relationship(back_populates="user")

    # who is my friend 
    friends1: Mapped[list[User]] = relationship(secondary="friend",
        primaryjoin=id == friend.c.user_id,
        secondaryjoin=id == friend.c.friend_id,)

    # i am a friend of whom
    friends2: Mapped[list[User]] = relationship(secondary="friend",
        primaryjoin=id == friend.c.friend_id,
        secondaryjoin=id == friend.c.user_id,)

    def __init__(self, *, username: str, email: str, password: str, role: str = "user"):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        if role != "user":
            self.role = role


    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict[str, int | str | None]:
        full_avatar_path = f"/uploads/{self.avatar_url}" if self.avatar_url else None

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "avatar_url": full_avatar_path,
        }

    from sqlalchemy import select

    def get_mutual_friends(self) -> list["User"]:
        # just for me cmt
        # SELECT u1.*
        # FROM users AS u1
        # JOIN friend AS f1 ON u1.id = f1.user_id
        # JOIN friend AS f2 ON f2.user_id = f1.friend_id
        #                  AND f2.friend_id = f1.user_id
        # WHERE u1.id = current_user_id;
        f1 = friend.alias("f1")
        f2 = friend.alias("f2")
        stmt = (
            select(User)
            .join(f1, User.id == f1.c.friend_id)
            .join(
                f2,
                (f2.c.user_id == f1.c.friend_id)
                & (f2.c.friend_id == f1.c.user_id),
            )
            .where(f1.c.user_id == self.id)
        )
        return db.session.scalars(stmt).all()
