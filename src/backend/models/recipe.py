from datetime import datetime
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .association import RecipeIngredient, RecipeTag, RecipeUtensil
    from .category import Category
    from .comment import Comment
    from .favorite import Favorite
    from .rating import Rating
    from .user import User


class Recipe(db.Model):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )

    title: Mapped[str] = mapped_column(String, nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    cooking_time: Mapped[int | None] = mapped_column(Integer)

    difficulty: Mapped[str | None] = mapped_column(String)

    instructions: Mapped[str | None] = mapped_column(Text)

    image_url: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="recipes")

    category: Mapped["Category"] = relationship(back_populates="recipes")

    comments: Mapped[list["Comment"]] = relationship(back_populates="recipe")

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe"
    )

    utensils: Mapped[list["RecipeUtensil"]] = relationship(back_populates="recipe")

    tags: Mapped[list["RecipeTag"]] = relationship(back_populates="recipe")

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe")

    ratings: Mapped[list["Rating"]] = relationship(back_populates="recipe")
