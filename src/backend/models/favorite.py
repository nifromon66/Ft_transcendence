<<<<<<< HEAD
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


# this is an association table
class Favorite(db.Model):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="favorites")

    recipe: Mapped[Recipe] = relationship(back_populates="favorites")

    def __init__(
        self,
        *,
        user: User | None = None,
        user_id: int | None = None,
        recipe: Recipe | None = None,
        recipe_id: int | None = None,
    ):
        if user is not None:
            self.user = user
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Init Favorite: value must be provided")

        if recipe is not None:
            self.recipe = recipe
        elif recipe_id is not None:
            self.recipe_id = recipe_id
        else:
            raise ValueError("Init Favorite: value must be provided")

        self.created_at = datetime.now(timezone.utc)
=======
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


# this is an association table
class Favorite(db.Model):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), primary_key=True)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="favorites")

    recipe: Mapped[Recipe] = relationship(back_populates="favorites")

    def __init__(self, *,
                user: User | None = None, user_id: int | None = None,
                recipe: Recipe | None = None, recipe_id: int | None = None):
        if user is not None:
            self.user = user
        elif user_id is not None:
            self.user_id = user_id
        else:
            raise ValueError("Init Favorite: value must be provided")

        if recipe is not None:
            self.recipe = recipe
        elif recipe_id is not None:
            self.recipe_id = recipe_id
        else:
            raise ValueError("Init Favorite: value must be provided")

        self.created_at = datetime.now(timezone.utc)
>>>>>>> shanwang
