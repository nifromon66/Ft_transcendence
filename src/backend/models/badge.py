from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db

if TYPE_CHECKING:
    from .association import UserBadge


class Badge(db.Model):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    logo_filename: Mapped[str | None] = mapped_column(String(255))

    users: Mapped[list[UserBadge]] = relationship(
        back_populates="badge", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        *,
        id: int | None,
        name: str,
        description: str | None = None,
        logo_filename: str | None = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.logo_filename = logo_filename


class BadgeType(IntEnum):
    NEW_BEE = 1
    FIRST_RECIPE = 2
    RECIPE_MASTER = 3
