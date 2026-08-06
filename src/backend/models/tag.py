from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .association import RecipeTag

class Tag(db.Model):

    __tablename__ = "tags"


    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )


    recipes: Mapped[list["RecipeTag"]] = relationship(
        back_populates="tag"
    )