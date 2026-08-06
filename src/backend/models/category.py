from extensions import db
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .recipe import Recipe

class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )


    recipes: Mapped[list["Recipe"]] = relationship(
        back_populates="category"
    )