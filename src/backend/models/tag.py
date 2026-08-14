<<<<<<< HEAD
from __future__ import annotations

from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association import recipe_tag

if TYPE_CHECKING:
    from .recipe import Recipe


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    recipes: Mapped[list[Recipe]] = relationship(
        secondary=recipe_tag, back_populates="tags"
    )

    def __init__(self, name):
        self.name = name
=======
from __future__ import annotations

from typing import TYPE_CHECKING

from extensions import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association import recipe_tag

if TYPE_CHECKING:
    from .recipe import Recipe


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    recipes: Mapped[list[Recipe]] = relationship(secondary=recipe_tag, back_populates="tags")

    def __init__(self, name):
        self.name = name
>>>>>>> shanwang
