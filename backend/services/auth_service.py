from fastapi import HTTPException, status, Request, WebSocket
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
import jwt
import hashlib
from uuid import UUID
from typing import Optional

from ..database import SessionLocal
from argon2 import PasswordHasher
from ..models.auth import User, Tokens
from ..models.users import UserProfile
from ..schema.http.auth import Claims

from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# Initialize argon2 PasswordHasher instance
_ph = PasswordHasher()

def get_access_token(request: Optional[Request] = None, websocket: Optional[WebSocket] = None) -> Optional[str]:
    """Retrieve a bearer token from an HTTP request or WebSocket.

    The function looks for an Authorization header with a "Bearer <token>"
    value on the provided `request` or `websocket` object. For WebSocket
    connections it also falls back to the "token" query parameter.

    Args:
        request: Optional FastAPI HTTP Request object to inspect for headers.
        websocket: Optional FastAPI WebSocket object to inspect for headers or
            query parameters.

    Returns:
        The extracted token string if present, otherwise ``None``.
    """
    obj = request or websocket

    # Attempt to get token from headers
    auth_header = None
    if obj is not None and hasattr(obj, "headers"):
        auth_header = obj.headers.get("Authorization")

    # For websockets, fallback to ?token= query param
    if not auth_header and obj is not None and hasattr(obj, "query_params"):
        token = obj.query_params.get("token")
        if token:
            return token

    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2 hashed password.

    Args:
        plain_password: The plaintext password provided by the user.
        hashed_password: The stored Argon2 hash to verify against.

    Returns:
        True if the password matches the hash, otherwise False.

    Raises:
        argon2.exceptions.VerifyMismatchError: If the hash does not match the
            supplied password.
        argon2.exceptions.VerificationError: If there is a problem verifying the
            hash (for example a corrupted hash).
    """
    result = _ph.verify(hash=hashed_password, password=plain_password)
    return result

def hash_password(password: str) -> str:
    """Create an Argon2 hash for a plaintext password.

    Args:
        password: The plaintext password to hash.

    Returns:
        The Argon2 hashed password as a string suitable for storage.
    """
    return _ph.hash(password=password)

def hash_token(token: str) -> str:
    """Compute a SHA-256 hex digest for a token string.

    Args:
        token: The raw token string to hash.

    Returns:
        The SHA-256 hex digest of ``token``.
    """
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token(token: str, token_hash: str) -> bool:
    """Verify that a raw token matches a stored SHA-256 token hash.

    Args:
        token: The raw token string to verify.
        token_hash: The stored SHA-256 hex digest to compare against.

    Returns:
        True if the computed digest of ``token`` equals ``token_hash``,
        otherwise False.
    """
    return hashlib.sha256(token.encode()).hexdigest() == token_hash

async def cleanup_tokens() -> None:
    """Remove expired or revoked refresh tokens from persistent storage.

    The function opens a new database session and deletes any ``Tokens``
    records that are either expired (``expires_at`` in the past) or have a
    non-null ``revoked_at`` timestamp. This is intended as a maintenance
    task and does not return a value.
    """
    db = SessionLocal()
    db.query(Tokens).filter(
        (Tokens.expires_at < datetime.now(tz=timezone.utc)) | (Tokens.revoked_at.isnot(other=None))
    ).delete(synchronize_session=False)
    db.commit()

def create_access_token(user_id: UUID) -> str:
    """Create a signed JWT access token for a user identifier.

    The token payload contains a subject (``sub``) equal to the stringified
    ``user_id`` and an expiration time derived from
    ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Args:
        user_id: UUID of the user for whom the token is issued.

    Returns:
        A JWT access token string signed with the application secret.
    """
    expire: datetime = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, str | datetime] = {
        "sub": str(object=user_id),
        "exp": expire
    }

    token: str = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_refresh_token(user_id: UUID, db: Optional[Session] = None) -> str:
    """Generate a refresh JWT, persist a hashed copy, and return the raw token.

    The function issues a refresh token with an expiry based on
    ``REFRESH_TOKEN_EXPIRE_DAYS`` and persists a SHA-256 digest of the token
    to the ``Tokens`` table. If a database session is not supplied the
    function will open and close its own session; otherwise the provided
    session is used and left open.

    Args:
        user_id: UUID of the owning user.
        db: Optional SQLAlchemy session to use for persistence.

    Returns:
        The raw JWT refresh token string.

    Raises:
        sqlalchemy.exc.IntegrityError: If a database constraint is violated
            while creating the token record (propagates after rollback).
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, str] = {"sub": str(user_id), "exp": str(expire)}
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        # remove previous tokens for this user (rotate)
        db.query(Tokens).filter(Tokens.user_id == user_id).delete(synchronize_session=False)

        token_hash = hash_token(token=token)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        token_entry = Tokens(
            user_id=user_id,
            token=token_hash,
            expires_at=expires_at,
            created_at=datetime.now(tz=timezone.utc)
        )
        db.add(instance=token_entry)
        db.commit()
    finally:
        if owns_session:
            db.close()
    return token

def get_user_from_access_token(request: Optional[Request] = None, websocket: Optional[WebSocket] = None) -> UUID:
    """Extract the user UUID from an access token supplied in a request.

    The function attempts to retrieve a bearer token using
    :pyfunc:`get_access_token`, validates it and returns the subject value as
    a UUID string. HTTP exceptions are raised for missing or malformed
    tokens.

    Args:
        request: Optional HTTP Request to extract the token from.
        websocket: Optional WebSocket to extract the token from.

    Returns:
        The user identifier (UUID) present in the validated token payload.

    Raises:
        fastapi.HTTPException: If no token is provided or the token payload
            does not include a user identifier.
    """
    token = get_access_token(request=request, websocket=websocket)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided"
        )

    payload = validate_access_token(token=token)

    user_id = payload.sub
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Malformed token payload: user identifier missing"
        )
    return user_id

def get_http_user_id(request: Request) -> UUID:
    """Extract the user UUID from an HTTP request's access token.

    This wrapper calls :pyfunc:`get_user_from_access_token` with an HTTP
    Request object.

    Args:
        request: FastAPI Request containing an Authorization header.

    Returns:
        The user UUID extracted from the request's access token.
    """
    return get_user_from_access_token(request=request)

async def get_ws_user_id(websocket: WebSocket) -> UUID:
    """Extract the user UUID from a WebSocket's access token.

    This async wrapper calls :pyfunc:`get_user_from_access_token` with a
    WebSocket object and returns the extracted user identifier.

    Args:
        websocket: FastAPI WebSocket containing Authorization header or
            a "token" query parameter.

    Returns:
        The user UUID extracted from the WebSocket's access token.
    """
    return get_user_from_access_token(websocket=websocket)

def authenticate_user(email: str, password: str) -> dict[str, str]:
    """Authenticate a user and return a new access and refresh token pair.

    The function verifies credentials against the stored user record. On
    success it issues a short-lived access token and a persisted refresh
    token.

    Args:
        email: The user's email address used to locate the account.
        password: The plaintext password to verify.

    Returns:
        A dict with keys ``access_token`` and ``refresh_token`` containing
        newly issued tokens.

    Raises:
        fastapi.HTTPException: If credentials are invalid (HTTP 401).
    """
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(plain_password=password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(user_id=user.id)

    refresh_token = create_refresh_token(user_id=user.id, db=db)

    return {"refresh_token": refresh_token, "access_token": access_token}

def register_user(email: str, password: str, profile_data: Optional[UserProfile] = None) -> dict[str, str]:
    """Create a new user account and associated profile, returning tokens.

    The function creates a user record with an Argon2-hashed password and a
    corresponding profile row populated from ``profile_data`` when provided.
    On successful creation it issues and returns an access and refresh token
    pair.

    Args:
        email: Email address for the new account.
        password: Plaintext password which will be hashed for storage.
        profile_data: Optional ``UserProfile`` data to populate the profile
            record.

    Returns:
        A dict containing ``access_token`` and ``refresh_token`` for the new
        user.

    Raises:
        fastapi.HTTPException: If the email is already registered
            (HTTP 409).
    """
    db = SessionLocal()
    try:
        # Hash the password before storing
        hashed_password = hash_password(password=password)

        # Create a new User instance
        new_user = User(email=email, password=hashed_password)

        # Add and commit to the database
        db.add(instance=new_user)
        db.flush()  # Get the generated user ID

        # Create user profile
        user_profile = UserProfile(
            user_id=new_user.id,
            first_name=profile_data.first_name if profile_data else None,
            last_name=profile_data.last_name if profile_data else None,
            phone=profile_data.phone if profile_data else None,
            avatar_url=profile_data.avatar_url if profile_data else None,
            bio=profile_data.bio if profile_data else None,
            date_of_birth=profile_data.date_of_birth if profile_data else None,
            location=profile_data.location if profile_data else None,
            website=profile_data.website if profile_data else None
        )

        db.add(instance=user_profile)
        db.commit()

        refresh_token = create_refresh_token(user_id=new_user.id, db=db)
        access_token = create_access_token(user_id=new_user.id)

        return {"refresh_token": refresh_token, "access_token": access_token}
    except IntegrityError:
        db.rollback()  # if email is already in use
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    finally:
        db.close()

def validate_access_token(token: str) -> Claims:
    """Decode and validate a JWT access token, returning its claims.

    Args:
        token: The JWT access token string to validate.

    Returns:
        A ``Claims`` object constructed from the token payload.

    Raises:
        fastapi.HTTPException: If the token is invalid or expired
            (HTTP 401).
    """
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return Claims(**payload)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid or expired"
        )

def refresh_token(old_refresh_token: str) -> dict[str, str]:
    """Validate a refresh token, rotate it and issue a new token pair.

    The function verifies the provided refresh token against stored hashed
    tokens, marks the existing token as revoked, and issues a new access and
    refresh token pair (the new refresh token is persisted).

    Args:
        old_refresh_token: The raw refresh token presented by the client.

    Returns:
        A dict with keys ``access_token`` and ``refresh_token`` for the
        newly issued tokens.

    Raises:
        fastapi.HTTPException: If the provided refresh token is invalid,
            revoked, or expired (HTTP 401).
    """
    db = SessionLocal()
    token_hash = hash_token(token=old_refresh_token)

    token_entry = db.query(Tokens).filter(
        Tokens.token == token_hash,
        Tokens.revoked_at.is_(other=None),
        Tokens.expires_at > datetime.now(timezone.utc)
    ).first()

    if not token_entry:
        raise HTTPException(  # invalid, expired, or revoked
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Rotate refresh token: revoke old, create new
    token_entry.revoked_at = datetime.now(timezone.utc)
    db.commit()

    # Issue new tokens
    new_access = create_access_token(user_id=token_entry.user_id)

    # create_refresh_token will revoke previous tokens and persist the new one
    new_refresh = create_refresh_token(user_id=token_entry.user_id, db=db)

    return {"refresh_token": new_refresh, "access_token": new_access}

def revoke_refresh_token(user_id: UUID) -> None:
    """Revoke all stored refresh tokens for a given user by updating revoked_at."""
    db = SessionLocal()
    try:
        db.query(Tokens).filter(Tokens.user_id == user_id, Tokens.revoked_at.is_(other=None)).update(values={Tokens.revoked_at: datetime.now(tz=timezone.utc)}, synchronize_session=False)
        db.commit()
    finally:
        db.close()
