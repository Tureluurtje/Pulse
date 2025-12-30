from ..models.users import UserProfile
from ..models.auth import User
from ..database import SessionLocal
from ..schema.internal.users import UserProfileDetail
from ..schema.http.users import UpdateUserProfileRequest

from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from typing import Optional
from uuid import UUID

def get_user_profile(user_id: UUID) -> UserProfileDetail:
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
        profile: Optional[UserProfile] = (
            db.query(UserProfile)
                .options(joinedload(UserProfile.user))
                .filter(UserProfile.user_id == user_id)
                .first()
        )

        if not profile or not profile.user.email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user profile with id {user_id} not found"
            )

        return UserProfileDetail(
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            email=profile.user.email,
            phone=profile.phone,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            date_of_birth=profile.date_of_birth,
            location=profile.location,
            website=profile.website,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    finally:
        db.close()

def ensure_user_profiles() -> None:
    """Create missing UserProfile records for any User without a profile.

    This is a maintenance function to handle users that may have been created
    before profile creation was mandatory, or without a profile for any reason.
    """
    db = SessionLocal()
    try:
        # Find users without profiles
        users_without_profiles = (
            db.query(User)
            .outerjoin(UserProfile, User.id == UserProfile.user_id)
            .filter(UserProfile.id.is_(None))
            .all()
        )

        if not users_without_profiles:
            return

        # Create profiles for these users
        for user in users_without_profiles:
            profile = UserProfile(user_id=user.id)
            db.add(profile)

        db.commit()
    finally:
        db.close()

def get_all_users() -> list[UserProfileDetail]:
    db = SessionLocal()
    user_list: list[UserProfileDetail] = []
    profiles: list[UserProfile] = (
        db.query(UserProfile)
        .options(joinedload(UserProfile.user))
        .all()
    )
    for profile in profiles:
        user_list.append(
            UserProfileDetail(
                id=profile.id,
                user_id=profile.user_id,
                first_name=profile.first_name,
                last_name=profile.last_name,
                email=profile.user.email,
                phone=profile.phone,
                avatar_url=profile.avatar_url,
                bio=profile.bio,
                date_of_birth=profile.date_of_birth,
                location=profile.location,
                website=profile.website,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
        )
    return user_list

def update_user_profile_service(
    user_id: UUID,
    options: UpdateUserProfileRequest
):
    """Update a user's profile data.

    Args:
        user_id: UUID of the user whose profile should be updated.
        options: UpdateUserProfileRequest object containing fields to update.

    Returns:
        The updated UserProfileDetail object.

    Raises:
        fastapi.HTTPException: If no profile exists for `user_id`
            (HTTP 404).
    """
    db = SessionLocal()
    try:
        profile: Optional[UserProfile] = (
            db.query(UserProfile)
                .filter(UserProfile.user_id == user_id)
                .first()
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user profile with id {user_id} not found"
            )

        # Update fields if provided
        for field, value in options.dict(exclude_unset=True).items():
            if value in ("", ''):
                value = None
            setattr(profile, field, value)

        db.commit()
        db.refresh(profile)

        return get_user_profile(user_id=user_id)
    finally:
        db.close()

def delete_user_service(user_id: UUID) -> None:
    """Delete a user and all associated data.

    Args:
        user_id: UUID of the user to delete.

    Raises:
        fastapi.HTTPException: If the user doesn't exist (HTTP 404).
    """
    db = SessionLocal()
    try:
        user: Optional[User] = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user with id {user_id} not found"
            )

        db.delete(user)
        db.commit()
    finally:
        db.close()
