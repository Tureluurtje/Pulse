from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(__name_pos=String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(__name_pos=String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(__name_pos=TIMESTAMP(timezone=False), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(__name_pos=TIMESTAMP(timezone=False), default=func.now(), onupdate=func.now(), nullable=False)

    # relationships
    tokens: Mapped[List["Tokens"]] = relationship(argument="Tokens", back_populates="user", cascade="all, delete-orphan")
    profile: Mapped[Optional["UserProfile"]] = relationship(argument="UserProfile", back_populates="user", uselist=False)

class Tokens(Base):
    __tablename__ = "tokens"

    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), __type_pos=ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(__name_pos=String, nullable=False, unique=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(__name_pos=TIMESTAMP(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(__name_pos=TIMESTAMP(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(__name_pos=TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(__name_pos=TIMESTAMP(timezone=True), default=func.now(), nullable=False)

    # relationships
    user: Mapped["User"] = relationship(argument="User", back_populates="tokens")

if TYPE_CHECKING:
    # import for type checking only to avoid circular imports at runtime
    from .users import UserProfile  # noqa: F401
    from .auth import User, Tokens  # noqa: F401