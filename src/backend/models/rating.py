from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


class Rating(db.Model):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)

    score: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="ratings")

    recipe: Mapped[Recipe] = relationship(back_populates="ratings")

    __table_args__ = (UniqueConstraint("user_id", "recipe_id"),
                      CheckConstraint("score >= 1 AND score <= 5"),)

    def __init__(self, *,
        user_id: int | None = None, user: User | None = None,
        recipe_id: int | None = None, recipe: Recipe | None = None,
        score: int,):

        if user is not None:
            self.user = user
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Init Rating: value must be provided")

        if recipe is not None:
           self.recipe = recipe
        elif recipe_id is not None:
            self.recipe_id = recipe_id
        else:
            raise ValueError("Init Rating: value must be provided")

        if not 1 <= score <= 5:
            raise ValueError("Init Rating: score must be between 1 and 5")
        self.score = score

        self.created_at = datetime.now(timezone.utc)


    def update_score(self, score: int) -> None:
        if not 1 <= score <= 5:
            raise ValueError("Rating: score must be between 1 and 5")
        self.score = score
        self.created_at = datetime.now(timezone.utc)