"""One optional avatar frame preference per user."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db

if TYPE_CHECKING:
    from .user import User


class UserAvatarFrame(db.Model):
    __tablename__ = "user_avatar_frames"
    __table_args__ = (CheckConstraint("frame IN ('bronze', 'silver', 'gold')"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    frame: Mapped[str | None] = mapped_column(String(10), nullable=True)
    user: Mapped[User] = relationship(back_populates="avatar_frame_preference")
