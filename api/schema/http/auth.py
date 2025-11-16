from pydantic import BaseModel, EmailStr
from uuid import UUID

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    refresh_token: str
    access_token: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    refresh_token: str
    access_token: str

class Claims(BaseModel):
    sub: UUID
    exp: int

class ValidateResponse(BaseModel):
    active: bool
    payload: Claims

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    refresh_token: str
    access_token: str
