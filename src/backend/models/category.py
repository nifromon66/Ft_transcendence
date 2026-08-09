from extensions import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .recipe import Recipe


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    recipes: Mapped[list[Recipe]] = relationship(back_populates="category")

    def __init__(self, name:str):
        self.name = name
