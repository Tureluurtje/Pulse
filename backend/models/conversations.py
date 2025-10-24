from __future__ import annotations

from typing import List, TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import String, Text, func, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_type: Mapped[str] = mapped_column(__name_pos=String, nullable=False)  # 'private' or 'group'
    name: Mapped[str] = mapped_column(__name_pos=Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(__name_pos=DateTime(timezone=True), default=func.now(), nullable=False)

    # relationships
    messages: Mapped[List["Message"]] = relationship(argument="Message", back_populates="conversation", cascade="all, delete-orphan")
    participants: Mapped[List["Participant"]] = relationship(argument="Participant", back_populates="conversation", cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), __type_pos=ForeignKey(column="conversations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), __type_pos=ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(__name_pos=String, default="member", nullable=False)  # 'member' or 'admin'
    joined_at: Mapped[datetime] = mapped_column(__name_pos=DateTime(timezone=True), default=func.now())

    # relationships
    conversation: Mapped["Conversation"] = relationship(argument="Conversation", back_populates="participants")
    user: Mapped["User"] = relationship(argument="User")

if TYPE_CHECKING:
    from .messages import Message  # noqa: F401
    from .auth import User  # noqa: F401