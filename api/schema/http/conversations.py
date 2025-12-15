from pydantic import BaseModel
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime

class GetConversationsRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class GetConversationsResponse(BaseModel):
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime
    participant_count: int

class CreateConversationRequest(BaseModel):
    name: str
    conversation_type: Literal['private', 'group']
    participant_ids: List[UUID]

class CreateConversationResponse(BaseModel):
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime
    participant_count: int

class EditConversationRequest(BaseModel):
    conversation_id: UUID
    new_name: str

class EditConversationResponse(BaseModel):
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime
    participant_count: int

class DeleteConversationRequest(BaseModel):
    conversation_id: UUID
