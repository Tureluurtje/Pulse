from ..models.users import UserProfile
from ..models.auth import User
from ..database import SessionLocal
from ..schema.internal.user_service import UserProfileObj

from fastapi import HTTPException, status
from typing import Optional
from uuid import UUID

def get_user_profile(user_id: UUID) -> UserProfileObj:
    """Retrieve a user's profile data.

    Args:
        user_id: UUID of the user whose profile should be returned.

    Returns:
        A mapping matching ``UserProfileObj`` containing profile fields.

    Raises:
        fastapi.HTTPException: If no profile exists for ``user_id``
            (HTTP 404).
    """
    db = SessionLocal()
    try:
        profile: Optional[UserProfile] = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        email: Optional[str] = db.query(User.email).filter(User.id == user_id).scalar()
        if not profile or not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user profile with id {user_id} not found"
            )
        # TODO: use UserProfile class instead of UserProfileObj class for return type without triggering type errors
        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": email,
            "phone": profile.phone,
            "avatar_url": profile.avatar_url,
            "bio": profile.bio,
            "date_of_birth": profile.date_of_birth,
            "location": profile.location,
            "website": profile.website,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
    finally:
        db.close()
