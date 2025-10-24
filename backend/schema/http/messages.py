from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class GetMessagesRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message_id: Optional[UUID] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0
    before: Optional[datetime] = None

class GetMessagesResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime

class SendMessageRequest(BaseModel):
    conversation_id: UUID
    content: str

class SendMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime

class EditMessageRequest(BaseModel):
    message_id: UUID
    new_content: str

class EditMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime

class DeleteMessageRequest(BaseModel):
    message_id: UUID
