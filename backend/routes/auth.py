from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
import asyncio

from ..schema.http.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, ValidateRequest, ValidateResponse, RefreshRequest, RefreshResponse
from ..services.auth_service import authenticate_user, register_user, validate_access_token, refresh_token, get_http_user_id, revoke_refresh_token, cleanup_tokens

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post(path="/login")
async def login(data: LoginRequest) -> LoginResponse:
    tokens = authenticate_user(email=data.email, password=data.password)
    
    return LoginResponse(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"]
    )

@router.post(path="/register")
async def register(data: RegisterRequest) -> RegisterResponse:
    tokens = register_user(email=data.email, password=data.password)

    return RegisterResponse(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"]
    )

@router.post(path="/validate")
async def validate(data: ValidateRequest) -> ValidateResponse:
    payload = validate_access_token(data.access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid or expired"
        )
        
    return ValidateResponse(
        active=True,
        payload=payload
    )

@router.post(path="/refresh")
async def refresh(data: RefreshRequest) -> RefreshResponse:
    tokens = refresh_token(old_refresh_token=data.refresh_token)
    
    return RefreshResponse(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"]
    )

@router.get(path="/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user_id: UUID = Depends(dependency=get_http_user_id)) -> None:
    # Revoke any active refresh tokens for this user
    revoke_refresh_token(user_id=user_id)
    
    asyncio.create_task(coro=cleanup_tokens())  # Run cleanup before the request
    return None
