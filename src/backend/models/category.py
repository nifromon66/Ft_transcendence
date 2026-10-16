from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    recipes: Mapped[list[Recipe]] = relationship(back_populates="category")

    def __init__(self, name: str, id: int | None = None):
        if id is not None:
            self.id = id
        self.name = name.capitalize()


# TODO
# decide a set of categories
class CategoryType(IntEnum):
    ENTREES = 1
    PLATS_PRINCIPAUX = 2
    ACCOMPAGNEMENTS = 3
    SALADES = 4
    SOUPES = 5
    SAUCES = 6
    SANDWICHS = 7
    PIZZAS = 8
    PATES = 9
    PLATS_DE_RIZ = 10
    GRATINS = 11
    TARTES_SALEES = 12
    DESSERTS = 13
    PATISSERIES = 14
    BOISSONS = 15
