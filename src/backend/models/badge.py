from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .association import UserBadge


class Badge(db.Model):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )


    users: Mapped[list["UserBadge"]] = relationship(
        back_populates="badge"
    )