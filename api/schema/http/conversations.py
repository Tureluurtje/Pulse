from pydantic import BaseModel
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime
from api.schema.internal.conversations import ConversationPreview

class GetConversationsRequest(BaseModel):
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class GetConversationsResponse(BaseModel):
    items: list[ConversationPreview]
    next_cursor: Optional[int] = None

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
    new_name: str

class DeleteConversationRequest(BaseModel):
    conversation_id: UUID
