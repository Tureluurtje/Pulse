from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class MessagePreview(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    edited_at: Optional[datetime] = None
    created_at: datetime
