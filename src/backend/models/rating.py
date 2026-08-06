from datetime import datetime
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


class Rating(db.Model):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)

    score: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="ratings")

    recipe: Mapped["Recipe"] = relationship(back_populates="ratings")

    __table_args__ = (UniqueConstraint("user_id", "recipe_id"),)
