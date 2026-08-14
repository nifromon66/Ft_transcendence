from datetime import datetime
from typing import TYPE_CHECKING

from extensions import bcrypt, db
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .association import UserBadge
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

    avatar_url: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    xp: Mapped[int | None] = mapped_column(Integer)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="user")

    comments: Mapped[list["Comment"]] = relationship(back_populates="user")

    badges: Mapped[list["UserBadge"]] = relationship(back_populates="user")

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")

    ratings: Mapped[list["Rating"]] = relationship(back_populates="user")

    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict[str, int | str]:
        return {"id": self.id, "username": self.username, "email": self.email}
