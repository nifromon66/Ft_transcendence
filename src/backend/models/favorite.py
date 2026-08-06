from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db

if TYPE_CHECKING:
    from .user import User
    from .recipe import Recipe


class Favorite(db.Model):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id"),
        primary_key=True
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    user: Mapped["User"] = relationship(
        back_populates="favorites"
    )

    recipe: Mapped["Recipe"] = relationship(
        back_populates="favorites"
    )