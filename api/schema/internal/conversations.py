from typing import TypedDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class ConversationPreview(TypedDict):
    id: UUID
    name: str
    last_message_preview: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int
    participant_count: int

class ConversationDetail(TypedDict):
    id: UUID
    name: str
    participant_count: int
    created_by: UUID
    created_at: datetime
