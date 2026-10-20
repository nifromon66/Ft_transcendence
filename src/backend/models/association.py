from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from extensions import db

if TYPE_CHECKING:
    from .badge import Badge
    from .ingredient import Ingredient
    from .recipe import Recipe
    from .user import User


class UserBadge(db.Model):
    __tablename__ = "users_badges"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"), primary_key=True)

    date_get: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="badges")

    badge: Mapped[Badge] = relationship(back_populates="users")

    def __init__(
        self,
        *,
        user_id: int | None = None,
        user: User | None = None,
        badge_id: int | None = None,
        badge: Badge | None = None,
    ):

        if user is not None:
            self.user = user
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Init UserBadge: value must be provided")

        if badge is not None:
            self.badge = badge
        elif badge_id is not None:
            self.badge_id = badge_id
        else:
            raise ValueError("Init UserBadge: value must be provided")

        self.date_get = datetime.now(timezone.utc)


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id"), primary_key=True
    )

    quantity: Mapped[str | None] = mapped_column(String)

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")

    ingredient: Mapped[Ingredient] = relationship(back_populates="recipes")

    def __init__(
        self,
        *,
        recipe: Recipe | None = None,
        recipe_id: int | None = None,
        ingredient: Ingredient | None = None,
        ingredient_id: int | None = None,
        quantity: str | None = None,
    ):
        if recipe is not None:
            self.recipe = recipe
        elif recipe_id is not None:
            self.recipe_id = recipe_id

        if ingredient is not None:
            self.ingredient = ingredient
        elif ingredient_id is not None:
            self.ingredient_id = ingredient_id
        else:
            raise ValueError("Init RecipeIngredient: Db value must be provided")

        self.quantity = quantity

    def to_dict(self) -> dict:
        return {
            "ingredient_id": self.ingredient_id,
            "name": self.ingredient.name,
            "quantity": self.quantity,
        }


friend = Table(
    "friend",
    db.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("friend_id", ForeignKey("users.id"), primary_key=True),
    Column("status", String, default="pending", nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)


recipe_tag = Table(
    "recipe_tag",
    db.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

# note for my self:
# 1-N, no need Table()
# N-N without additional attribute, use Table()
# N-N with additional attribute, use ORM class
