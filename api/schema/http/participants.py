from pydantic import BaseModel, validator, ValidationError
from typing import Optional, Literal
from uuid import UUID

from ..internal.participants import ParticipantDetail\

class GetParticipantsRequest(BaseModel):
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class GetParticipantsResponse(BaseModel):
    items: list[ParticipantDetail]
    next_cursor: Optional[int] = None

class AddParticipantsRequest(BaseModel):
    user_ids: list[UUID]

class AddParticipantsResponse(BaseModel):
    participants: list[ParticipantDetail]

class PatchParticipantRequest(BaseModel):
    role: Literal["owner", "admin", "member"]
