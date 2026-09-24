from __future__ import annotations

from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .association import RecipeIngredient
    from .ingredient_category import IngredientCategory


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("ingredient_categories.id"), nullable=False)
    category: Mapped[IngredientCategory] = relationship(back_populates="ingredients")

    recipes: Mapped[list[RecipeIngredient]] = relationship(back_populates="ingredient", cascade="all, delete-orphan")

    def __init__(self, name, id:int | None = None, *, category_id: int):
        self.category_id = category_id
        if id is not None:
            self.id = id
        self.name = name.capitalize()
