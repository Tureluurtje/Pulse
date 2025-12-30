from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..internal.messages import MessagePreview

class GetMessagesRequest(BaseModel):
    limit: Optional[int] = 50
    offset: Optional[int] = 0
    before: Optional[datetime] = None

class GetMessagesResponse(BaseModel):
    items: list[MessagePreview]
    next_cursor: Optional[int] = None

class SendMessageRequest(BaseModel):
    content: str

class EditMessageRequest(BaseModel):
    content: str
