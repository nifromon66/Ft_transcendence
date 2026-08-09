
from extensions import db
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association import recipe_utensil
from .recipe import Recipe


class Utensil(db.Model):
    __tablename__ = "utensils"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    recipes: Mapped[list[Recipe]] = relationship(secondary=recipe_utensil, back_populates="tags")

    def __init__(self, name):
            self.name = name
