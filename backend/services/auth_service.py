from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import jwt
import hashlib

from database import SessionLocal
from passlib.hash import argon2
from models.auth import User, Tokens

***REMOVED*** = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its Argon2 hash."""
    result = argon2.verify(plain_password, hashed_password)
    return result

def hash_password(password: str) -> str:
    """Hash a password with Argon2."""
    return argon2.hash(password)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token(token: str, token_hash: str) -> bool:
    return hashlib.sha256(token.encode()).hexdigest() == token_hash

def cleanup_tokens() -> None:
    db = SessionLocal()
    db.query(Tokens).filter(
        (Tokens.expires_at < datetime.utcnow()) | (Tokens.revoked_at.isnot(None))
    ).delete(synchronize_session=False)
    db.commit()

def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for the given user ID.
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),  # JWT payloads should use strings for subjects
        "exp": expire
    }

    token: str = jwt.encode(payload, ***REMOVED***, algorithm=ALGORITHM)  # PyJWT >=2 returns str
    return token

def create_refresh_token(user_id: int, db=None) -> str:
    """
    Create a JWT refresh token, optionally persist its hashed form in the DB and
    remove previous refresh tokens for the user. Returns the raw JWT string.
    If `db` is not provided, a new session will be created just for storage.
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire}
    token = jwt.encode(payload, ***REMOVED***, algorithm=ALGORITHM)

    # If caller wants persistence, store the hashed token and cleanup old ones
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        # remove previous tokens for this user (rotate)
        db.query(Tokens).filter(Tokens.user_id == user_id).delete(synchronize_session=False)

        token_hash = hash_token(token)
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        token_entry = Tokens(
            user_id=user_id,
            token=token_hash,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        db.add(token_entry)
        db.commit()
    finally:
        if owns_session:
            db.close()

    return token

def authenticate_user(email: str, password: str) -> dict:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    access_token = create_access_token(user.id)
    # Create and persist refresh token (create_refresh_token will handle cleanup)
    refresh_token = create_refresh_token(user.id, db=db)

    return {"refresh_token": refresh_token, "access_token": access_token}

def register_user(email: str, password: str) -> dict:
    db = SessionLocal()
    try:
        # Hash the password before storing
        hashed_password = hash_password(password)

        # Create a new User instance
        new_user = User(email=email, password=hashed_password)

        # Add and commit to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # optional, updates new_user with generated fields (id, timestamps)

        refresh_token = create_refresh_token(new_user.id, db=db)
        access_token = create_access_token(new_user.id)

        return {"refresh_token": refresh_token, "access_token": access_token}
    except IntegrityError:
        db.rollback()  # if email is already in use
        return None
    finally:
        db.close()

def refresh_token(old_refresh_token: str) -> dict:
    db = SessionLocal()
    token_hash = hash_token(old_refresh_token)

    token_entry = db.query(Tokens).filter(
        Tokens.token == token_hash,
        Tokens.revoked_at.is_(None),
        Tokens.expires_at > datetime.utcnow()
    ).first()

    if not token_entry:
        return None  # invalid, expired, or revoked

    # Rotate refresh token: revoke old, create new
    token_entry.revoked_at = datetime.utcnow()
    db.commit()

    # Issue new tokens
    new_access = create_access_token(token_entry.user_id)
    # create_refresh_token will revoke previous tokens and persist the new one
    new_refresh = create_refresh_token(token_entry.user_id, db=db)

    return {"refresh_token": new_refresh, "access_token": new_access}
