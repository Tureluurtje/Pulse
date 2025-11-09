from typing import TypedDict
from uuid import UUID

class conversationObject(TypedDict):
    id: UUID
    name: str
    created_by: UUID
    created_at: str
    participant_count: int