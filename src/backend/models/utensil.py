from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .association import RecipeUtensil

class Utensil(db.Model):

    __tablename__ = "utensils"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )


    recipes: Mapped[list["RecipeUtensil"]] = relationship(
        back_populates="utensil"
    )