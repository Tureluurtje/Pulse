from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from fastapi import HTTPException, status
from starlette.datastructures import Headers
from starlette.requests import Request as StarletteRequest
from starlette.types import Scope
from sqlalchemy.orm.session import Session
import asyncio
from typing import Optional

from backend.services import auth_service as svc
from backend.database import SessionLocal
from backend.models.auth import User, Tokens
from backend.models.users import UserProfile
from backend.tests.conftest import make_profile_obj, random_email

def test_hash_password_and_verify() -> None:
    pw = "secret123"
    h = svc.hash_password(password=pw)
    assert h != pw
    assert svc.verify_password(plain_password=pw, hashed_password=h) is True

def test_create_and_validate_access_token() -> None:
    temp_uuid = uuid4()
    token = svc.create_access_token(user_id=temp_uuid)
    payload = svc.validate_access_token(token=token)
    assert payload is not None
    assert payload.sub == temp_uuid

def test_validate_access_token_invalid() -> None:
    with pytest.raises(expected_exception=HTTPException) as exc_info:
        svc.validate_access_token(token="invalid-token")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Access token is invalid or expired"

def test_hash_and_verify_token_helpers() -> None:
    tok = "my-refresh-token"
    h = svc.hash_token(token=tok)
    assert h != tok
    assert svc.verify_token(token=tok, token_hash=h) is True
    assert svc.verify_token(token=tok + "x", token_hash=h) is False

def test_register_user_returns_tokens_and_cleans_up() -> None:
    db = SessionLocal()
    email = random_email()
    password = "MyS3cret!"
    profile = make_profile_obj(first_name="T", last_name="U")

    try:
        tokens = svc.register_user(email=email, password=password, profile_data=profile)
        assert tokens is not None
        assert "access_token" in tokens and "refresh_token" in tokens
    finally:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.query(Tokens).filter(Tokens.user_id == user.id).delete(synchronize_session=False)
            db.query(UserProfile).filter(UserProfile.user_id == user.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
            db.commit()
        db.close()

def test_authenticate_user_with_stored_user() -> None:
    db = SessionLocal()
    email = random_email()
    password = "AuthPass!"
    try:
        # create user directly
        hashed = svc.hash_password(password=password)
        user = User(email=email, password=hashed)
        db.add(instance=user)
        db.commit()
        db.refresh(instance=user)

        auth = svc.authenticate_user(email=email, password=password)
        assert auth is not None
        assert "access_token" in auth and "refresh_token" in auth
    finally:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.query(Tokens).filter(Tokens.user_id == user.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
            db.commit()
        db.close()

def test_refresh_token_rotates_and_returns_new() -> None:
    db = SessionLocal()
    email = random_email()
    password = "Refresh1!"
    profile = make_profile_obj()
    try:
        tokens = svc.register_user(email=email, password=password, profile_data=profile)
        assert tokens is not None

        refreshed = svc.refresh_token(old_refresh_token=tokens["refresh_token"])
        assert refreshed is not None
        assert "access_token" in refreshed and "refresh_token" in refreshed
    finally:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.query(Tokens).filter(Tokens.user_id == user.id).delete(synchronize_session=False)
            db.query(UserProfile).filter(UserProfile.user_id == user.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
            db.commit()
        db.close()

def test_revoke_refresh_token_marks_revoked() -> None:
    db = SessionLocal()
    email = random_email()
    password = "Revoke1!"
    profile = make_profile_obj()
    try:
        tokens = svc.register_user(email=email, password=password, profile_data=profile)
        assert tokens is not None

        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        svc.revoke_refresh_token(user_id=user.id)

        entries = db.query(Tokens).filter(Tokens.user_id == user.id).all()
        for t in entries:
            assert t.revoked_at is not None
    finally:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.query(Tokens).filter(Tokens.user_id == user.id).delete(synchronize_session=False)
            db.query(UserProfile).filter(UserProfile.user_id == user.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
            db.commit()
        db.close()

def test_get_access_token_and_user_from_access_token() -> None:
    temp_uuid = uuid4()
    tok = svc.create_access_token(user_id=temp_uuid)
    
    # simulate a real FastAPI/Starlette request
    scope: Scope = {
        "type": "http",
        "headers": Headers(headers={"Authorization": f"Bearer {tok}"}).raw,
        "query_string": b"",
    }
    request = StarletteRequest(scope=scope)

    uid = svc.get_user_from_access_token(request=request)
    assert uid == temp_uuid

def test_cleanup_tokens_removes_expired() -> None:
    db: Session = SessionLocal()
    user: Optional[User] = None
    try:
        # create a user
        user = User(email=random_email(), password="x")
        db.add(instance=user)
        db.commit()
        db.refresh(instance=user)  # refresh the instance

        # create token strings
        expired_token_str = svc.hash_token(token="oldtoken")
        valid_token_str = svc.hash_token(token="validtoken")

        # create token objects
        expired = Tokens(
            user_id=user.id,
            token=expired_token_str,
            expires_at=datetime.now(tz=timezone.utc) - timedelta(days=1),
            created_at=datetime.now(tz=timezone.utc) - timedelta(days=2),
        )
        valid = Tokens(
            user_id=user.id,
            token=valid_token_str,
            expires_at=datetime.now(tz=timezone.utc) + timedelta(days=1),
            created_at=datetime.now(tz=timezone.utc),
        )
        db.add_all(instances=[expired, valid])
        db.commit()

        # run async cleanup
        asyncio.run(main=svc.cleanup_tokens())

        # Query only token strings
        remaining_tokens = [
            t[0] for t in db.query(Tokens.token).filter(Tokens.user_id == user.id).all()
        ]

        # expired should be gone, valid should remain
        assert valid_token_str in remaining_tokens
        assert expired_token_str not in remaining_tokens

    finally:
        # cleanup
        if user is not None:
            db.query(Tokens).filter(Tokens.user_id == user.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()
