from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    and_,
    func,
    or_,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db

if TYPE_CHECKING:
    from .user import User


class Message(db.Model):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    file_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    file_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    sender: Mapped[User] = relationship(
        foreign_keys=[sender_id],
        back_populates="sent_messages",
    )

    receiver: Mapped[User] = relationship(
        foreign_keys=[receiver_id],
        back_populates="received_messages",
    )

    def __init__(
        self,
        *,
        sender_id: int | None = None,
        sender: User | None = None,
        receiver_id: int | None = None,
        receiver: User | None = None,
        content: str | None = None,
        file_url: str | None = None,
        file_name: str | None = None,
        file_type: str | None = None,
        file_size: int | None = None,
    ):
        if not content and not file_url:
            raise ValueError("Init message: Message must contain text or a file")

        if sender_id is not None:
            self.sender_id = sender_id
        elif sender is not None:
            self.sender_id = sender.id
        else:
            raise ValueError("Init message: Value must be provided")

        if receiver_id is not None:
            self.receiver_id = receiver_id
        elif receiver is not None:
            self.receiver_id = receiver.id

        self.content = content
        self.file_url = file_url
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def get_conversation(user1_id: int, user2_id: int) -> list[Message]:
        stmt = (
            select(Message)
            .where(
                or_(
                    and_(
                        Message.sender_id == user1_id,
                        Message.receiver_id == user2_id,
                    ),
                    and_(
                        Message.sender_id == user2_id,
                        Message.receiver_id == user1_id,
                    ),
                )
            )
            .order_by(Message.created_at)
        )

        return db.session.scalars(stmt).all()
