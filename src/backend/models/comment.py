from datetime import datetime
from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .recipe import Recipe
    from .user import User


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="comments")

    recipe: Mapped["Recipe"] = relationship(back_populates="comments")

    parent: Mapped["Comment | None"] = relationship(
        remote_side=[id], back_populates="replies"
    )

    replies: Mapped[list["Comment"]] = relationship(back_populates="parent")
