from sqlalchemy.orm import Mapped, mapped_column, relationship
from extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .association import RecipeIngredient

class Ingredient(db.Model):

    __tablename__ = "ingredients"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )


    name: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    recipes: Mapped[list["RecipeIngredient"]] = relationship(
    back_populates="ingredient"
    )