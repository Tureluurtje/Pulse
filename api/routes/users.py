from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID

from ..services.auth_service import get_http_user_id
from ..services.users_service import get_user_profile
from ..schema.http.users import UserProfileResponse

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get(path="/me")
async def me(user_id: UUID = Depends(dependency=get_http_user_id)) -> UserProfileResponse:
    user_profile = get_user_profile(user_id=user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return UserProfileResponse(**user_profile)
