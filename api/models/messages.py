from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), __type_pos=ForeignKey(column="conversations.id", ondelete="CASCADE"), nullable=False)
    sender_id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), __type_pos=ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(__name_pos=Text, nullable=False)
    edited_at: Mapped[datetime | None] = mapped_column(__name_pos=DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(__name_pos=DateTime(timezone=True), default=func.now(), nullable=False)

    # relationships
    conversation: Mapped["Conversation"] = relationship(argument="Conversation", back_populates="messages")
    sender: Mapped["User"] = relationship(argument="User")

if TYPE_CHECKING:
    from .conversations import Conversation  # noqa: F401
    from .auth import User  # noqa: F401
