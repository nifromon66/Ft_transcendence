from __future__ import annotations

from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe


class RecipeStep(db.Model):
    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )

    step_number: Mapped[int] = mapped_column(Integer, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    image_filename: Mapped[str | None] = mapped_column(String)

    recipe: Mapped[Recipe] = relationship(back_populates="steps")

    def __init__(
        self,
        *,
        recipe_id: int | None = None,
        recipe: Recipe | None = None,
        step_number: int,
        description: str,
        image_filename: str | None = None,
    ):
        if recipe is not None:
            self.recipe = recipe
        elif recipe_id is not None:
            self.recipe_id = recipe_id
        # else:
        #     raise ValueError("Init RecipeStep: recipe or recipe_id must be provided")

        self.step_number = step_number
        self.description = description
        self.image_filename = image_filename

    def to_dict(self):
        full_image_path = (
            f"/api/recipes/{self.recipe_id}/steps/{self.id}/image"
            if self.image_filename
            else None
        )
        return {
            "id": self.id,
            "step_number": self.step_number,
            "description": self.description,
            "image_url": full_image_path,
        }
