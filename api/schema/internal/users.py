from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class Claims(BaseModel):
    sub: str
    exp: int

class UserProfileDetail(BaseModel):
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True
        json_encoders = {UUID: lambda u: str(object=u)}
