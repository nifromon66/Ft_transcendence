from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from extensions import bcrypt, db
from sqlalchemy import JSON, Boolean, DateTime, Integer, String, and_, or_, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association import friend

if TYPE_CHECKING:
    from .association import UserBadge
    from .comment import Comment
    from .favorite import Favorite
    from .message import Message
    from .rating import Rating
    from .recipe import Recipe


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String, nullable=False)

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)

    oauth_provider: Mapped[str | None] = mapped_column(String, nullable=True)

    oauth_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    totp_secret: Mapped[str | None] = mapped_column(String, nullable=True)

    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    recovery_codes: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, default=list
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role: Mapped[str] = mapped_column(String, nullable=False, default="user")

    avatar_url: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    xp: Mapped[int | None] = mapped_column(Integer)

    recipes: Mapped[list[Recipe]] = relationship(back_populates="user")

    comments: Mapped[list[Comment]] = relationship(back_populates="user")

    badges: Mapped[list[UserBadge]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    favorites: Mapped[list[Favorite]] = relationship(back_populates="user")

    ratings: Mapped[list[Rating]] = relationship(back_populates="user")

    sent_messages: Mapped[list[Message]] = relationship(
        foreign_keys="Message.sender_id",
        back_populates="sender",
    )

    received_messages: Mapped[list[Message]] = relationship(
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
    )

    def __init__(
        self,
        *,
        username: str,
        email: str,
        password: str | None = None,
        role: str = "user",
        oauth_provider: str | None = None,
        oauth_id: str | None = None,
    ):
        self.username = username
        self.email = email

        if password:
            self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        else:
            self.password_hash = None

        self.oauth_provider = oauth_provider
        self.oauth_id = oauth_id

        self.totp_secret = None
        self.is_2fa_enabled = False
        self.recovery_codes = []

        if role != "user":
            self.role = role
        self.is_active = True

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict[str, int | str | None]:
        full_avatar_path = f"/uploads/{self.avatar_url}" if self.avatar_url else None

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "avatar_url": full_avatar_path,
            "is_2fa_enabled": self.is_2fa_enabled,
            "oauth_provider": self.oauth_provider,
        }

    def get_friends(self) -> list[User]:
        stmt = (
            select(User)
            .join(
                friend,
                or_(
                    and_(User.id == friend.c.friend_id, friend.c.user_id == self.id),
                    and_(User.id == friend.c.user_id, friend.c.friend_id == self.id),
                ),
            )
            .where(and_(friend.c.status == "accepted", User.is_active == True))
        )
        return db.session.scalars(stmt).all()
