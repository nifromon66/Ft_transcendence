from datetime import datetime, timezone

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association import RecipeIngredient, recipe_tag, recipe_utensil
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

    instructions: Mapped[str | None] = mapped_column(Text)

    image_url: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime)

    updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="recipes")

    category: Mapped[Category] = relationship(back_populates="recipes")

    comments: Mapped[list[Comment]] = relationship(back_populates="recipe")

    ingredients: Mapped[list[RecipeIngredient]] = relationship(
        back_populates="recipe")

    utensils: Mapped[list[Utensil]] = relationship(secondary=recipe_utensil, back_populates="recipes")

    tags: Mapped[list[Tag]] = relationship(secondary=recipe_tag, back_populates="recipes")

    favorites: Mapped[list[Favorite]] = relationship(back_populates="recipe")

    ratings: Mapped[list[Rating]] = relationship(back_populates="recipe")

    def __init__(self, *,
        user_id: int | None = None, user: User | None = None,
        category_id: int | None = None, category: Category | None = None,
        title: str,
        description: str | None = None,
        cooking_time: int | None = None,
        difficulty: str | None = None,
        instructions: str | None = None,
        image_url: str | None = None,):

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
        self.instructions = instructions
        self.image_url = image_url

        self.created_at = datetime.now(timezone.utc)
        self.updated_at = None

    def update(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        cooking_time: int | None = None,
        difficulty: str | None = None,
        instructions: str | None = None,
        image_url: str | None = None,
        category_id: int | None = None,
        category: Category | None = None,
    ) -> None:

        if title is not None:
            self.title = title

        if description is not None:
            self.description = description

        if cooking_time is not None:
            self.cooking_time = cooking_time

        if difficulty is not None:
            self.difficulty = difficulty

        if instructions is not None:
            self.instructions = instructions

        if image_url is not None:
            self.image_url = image_url

        if category is not None:
            self.category = category
        elif category_id is not None:
            self.category_id = category_id

        self.updated_at = datetime.now(timezone.utc)