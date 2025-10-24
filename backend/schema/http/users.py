from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Claims(BaseModel):
    sub: str
    exp: int

class UserProfileResponse(BaseModel):
    id: UUID = uuid4()
    user_id: UUID = uuid4()
    first_name: Optional[str] = None
    last_name: Optional[str] = None
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
        # TODO: fix "Type of "json_encoders" is partially unknown" type warning
        json_encoders = {UUID: lambda u: str(object=u)} # type: ignore