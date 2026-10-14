from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .recipe_step import RecipeStep

if TYPE_CHECKING:
    from .association import RecipeIngredient
    from .category import Category
    from .comment import Comment
    from .favorite import Favorite
    from .rating import Rating
    from .tag import Tag
    from .user import User
    from .utensil import Utensil


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

    image_url: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime)

    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    steps: Mapped[list[RecipeStep]] = relationship(back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeStep.step_number")

    user: Mapped[User] = relationship(back_populates="recipes")

    category: Mapped[Category] = relationship(back_populates="recipes")

    comments: Mapped[list["Comment"]] = relationship(back_populates="recipe")

    ingredients: Mapped[list["RecipeIngredient"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")

    utensils: Mapped[list["Utensil"]] = relationship(secondary="recipe_utensil", back_populates="recipes")

    tags: Mapped[list["Tag"]] = relationship(secondary="recipe_tag", back_populates="recipes")

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe")

    ratings: Mapped[list["Rating"]] = relationship(back_populates="recipe")

    def __init__(self, *,
        user_id: int | None = None, user: User | None = None,
        category_id: int | None = None, category: Category | None = None,
        title: str,
        description: str | None = None,
        cooking_time: int | None = None,
        difficulty: str | None = None,
        image_url: str | None = None,
        steps: list["RecipeStep"] | None = None):

        if user is not None:
            self.user = user
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Init Recipe: value must be provided")

        if category is not None:
            self.category = category
        elif category_id is not None:
            self.category_id = category_id
        else:
            raise ValueError("Init Recipe: value must be provided")

        self.title = title
        self.description = description
        self.cooking_time = cooking_time
        self.difficulty = difficulty
        self.image_url = image_url
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = None

        self.steps = steps or []

    def update(
        self,
        *,
        title: str,
        category: Category,
        description: str | None,
        cooking_time: int | None,
        difficulty: str | None,
        steps: list["RecipeStep"],
    ) -> None:
        self.title = title
        self.category = category
        self.description = description
        self.cooking_time = cooking_time
        self.difficulty = difficulty
        self.steps = steps
        self.updated_at = datetime.now(timezone.utc)

# no list ratings, list favorites, list comments in this function
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cooking_time": self.cooking_time,
            "difficulty": self.difficulty,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
            "category": {
                "id": self.category.id,
                "name": self.category.name,
            },
            "author": {
                "id": self.user.id,
                "username": self.user.username,
            },
            "steps": [
                step.to_dict()
                for step in self.steps
            ],
            "ingredients": [
                ingredient.to_dict()
                for ingredient in self.ingredients
            ],
            "utensils": [
                utensil.to_dict()
                for utensil in self.utensils
            ],
            "tags": [
                tag.to_dict()
                for tag in self.tags
            ],
        }