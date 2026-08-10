from __future__ import annotations

from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .association import RecipeIngredient


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    recipes: Mapped[list[RecipeIngredient]] = relationship(back_populates="ingredient")

    def __init__(self, name):
        self.name = name
