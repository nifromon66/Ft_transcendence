from datetime import datetime
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .badge import Badge
    from .ingredient import Ingredient
    from .recipe import Recipe
    from .tag import Tag
    from .user import User
    from .utensil import Utensil


class UserBadge(db.Model):
    __tablename__ = "users_badges"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"), primary_key=True)

    date_get: Mapped[datetime | None] = mapped_column(
        DateTime,
    )

    user: Mapped["User"] = relationship(back_populates="badges")

    badge: Mapped["Badge"] = relationship(back_populates="users")


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id"), primary_key=True
    )

    quantity: Mapped[str | None] = mapped_column(String)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")

    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")


class RecipeUtensil(db.Model):
    __tablename__ = "recipe_utensils"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)

    utensil_id: Mapped[int] = mapped_column(ForeignKey("utensils.id"), primary_key=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="utensils")

    utensil: Mapped["Utensil"] = relationship(back_populates="recipes")


class RecipeTag(db.Model):
    __tablename__ = "recipe_tags"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)

    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="tags")

    tag: Mapped["Tag"] = relationship(back_populates="recipes")
