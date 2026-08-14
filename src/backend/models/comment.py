<<<<<<< HEAD
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="comments")

    recipe: Mapped[Recipe] = relationship(back_populates="comments")

    parent: Mapped[Comment | None] = relationship(
        remote_side=[id], back_populates="replies"
    )

    replies: Mapped[list[Comment]] = relationship(back_populates="parent")

    def __init__(
        self,
        *,
        user_id: int | None = None,
        user: User | None = None,
        recipe_id: int | None = None,
        recipe: Recipe | None = None,
        content: str,
        parent_id: int | None = None,
        parent: Comment | None = None,
    ):
        if user_id is not None:
            self.user_id = user_id
        elif user is not None:
            self.user = user
        else:
            raise ValueError("Init Comment: Db value must be provided")

        if recipe_id is not None:
            self.recipe_id = recipe_id
        elif recipe is not None:
            self.recipe = recipe
        else:
            raise ValueError("Init Comment: Db value must be provided")

        self.content = content
        if parent_id is not None:
            self.parent_id = parent_id
        elif parent is not None:
            self.parent = parent

        self.created_at = datetime.now(timezone.utc)
=======
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="comments")

    recipe: Mapped[Recipe] = relationship(back_populates="comments")

    parent: Mapped[Comment | None] = relationship(
        remote_side=[id], back_populates="replies"
    )

    replies: Mapped[list[Comment]] = relationship(back_populates="parent")

    def __init__(self, *, user_id: int | None = None, user: User | None = None,
                 recipe_id: int | None = None, recipe: Recipe | None = None,
                 content: str,
                 parent_id: int | None = None, parent: Comment | None = None):
        if user_id is not None:
            self.user_id = user_id
        elif user is not None:
            self.user = user
        else:
            raise ValueError("Init Comment: Db value must be provided")

        if recipe_id is not None:
            self.recipe_id = recipe_id
        elif recipe is not None:
            self.recipe = recipe
        else:
            raise ValueError("Init Comment: Db value must be provided")
    
        self.content = content
        if parent_id is not None:
            self.parent_id = parent_id
        elif parent is not None:
            self.parent = parent

        self.created_at = datetime.now(timezone.utc)
>>>>>>> shanwang
