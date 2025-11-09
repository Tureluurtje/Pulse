from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(__name_pos=UUID(as_uuid=True), __type_pos=ForeignKey(column="users.id", ondelete="CASCADE"), nullable=False, unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(__name_pos=Text)
    last_name: Mapped[Optional[str]] = mapped_column(__name_pos=Text)
    phone: Mapped[Optional[str]] = mapped_column(__name_pos=Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(__name_pos=Text)
    bio: Mapped[Optional[str]] = mapped_column(__name_pos=Text)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(__name_pos=DateTime(timezone=True))
    location: Mapped[Optional[str]] = mapped_column(__name_pos=Text)
    website: Mapped[Optional[str]] = mapped_column(__name_pos=Text)
    created_at: Mapped[datetime] = mapped_column(__name_pos=DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(__name_pos=DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # relationship back to user
    user: Mapped["User"] = relationship(argument="User", back_populates="profile")

if TYPE_CHECKING:
    from .auth import User  # noqa: F401
