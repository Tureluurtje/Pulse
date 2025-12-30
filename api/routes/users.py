from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID

from ..services.auth_service import get_http_user_id
from ..services.users_service import get_user_profile, update_user_profile_service, delete_user_service
from ..schema.internal.users import UserProfileDetail
from ..schema.http.users import UpdateUserProfileRequest

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get(path="/me")
def get_me(
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> UserProfileDetail:
    user_profile = get_user_profile(user_id=user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return user_profile

@router.get(path="/{target_user_id}")
def get_other(
    target_user_id: UUID,
    # For logging purposes
    user_id: UUID = Depends(dependency=get_http_user_id)
):
    """
    Retrieve another user's information by their user ID.

    Args:
        target_user_id (UUID): The unique identifier of the user whose information is being requested.
        user_id (UUID): The unique identifier of the authenticated user making the request.
                       Automatically injected via dependency injection for logging purposes.

    Returns:
        User information for the target user.

    Raises:
        HTTPException: If the target user is not found or access is denied.
    """
    return get_me(user_id=target_user_id)

@router.post(path="/me")
def update_me(
    data: UpdateUserProfileRequest,
    user_id: UUID = Depends(dependency=get_http_user_id)
):
    new_profile = update_user_profile_service(
        user_id=user_id,
        options=data
    )
    return new_profile

@router.delete(path="/")
def remove_me(
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> None:
    """
    Delete the authenticated user's account and all associated data.

    Args:
        user_id (UUID): The unique identifier of the authenticated user to delete.
                       Automatically injected via dependency injection.

    Returns:
        A dictionary with a success message.

    Raises:
        HTTPException: If the user is not found (HTTP 404).
    """
    delete_user_service(user_id=user_id)
    return
