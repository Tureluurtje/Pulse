from typing import TypedDict

class conversationObject(TypedDict):
    id: str
    name: str
    created_by: str
    created_at: str
    participant_count: int