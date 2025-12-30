from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class ParticipantUser(BaseModel):
    id: UUID
    email: str
    # avatar_url: Optional[str] = None  # Future enhancement for user avatars

class ParticipantDetail(BaseModel):
    user: ParticipantUser
    role: Optional[Literal["owner", "admin", "member"]] = "member"
    joined_at: datetime
