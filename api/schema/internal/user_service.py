from typing import TypedDict, Optional
from uuid import UUID
from datetime import datetime

class UserProfileObj(TypedDict):
    id: UUID
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    phone: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    date_of_birth: Optional[datetime]
    location: Optional[str]
    website: Optional[str]
    created_at: datetime
    updated_at: datetime
