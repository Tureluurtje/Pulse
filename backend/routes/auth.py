from fastapi import APIRouter, HTTPException, status
from schema.auth import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, RefreshRequest, RefreshResponse
from services.auth_service import authenticate_user, register_user, refresh_token
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login")
async def login(data: LoginRequest):
    tokens = authenticate_user(data.email, data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return LoginResponse(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"]
    )

@router.post("/register")
async def register(data: RegisterRequest):
    tokens = register_user(data.email, data.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    return RegisterResponse(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"]
    )

@router.post("/refresh")
async def refresh(data: RefreshRequest):
    tokens = refresh_token(data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    return RefreshResponse(
        refresh_token=tokens["refresh_token"],
        access_token=tokens["access_token"]
    )
