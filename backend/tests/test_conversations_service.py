from sqlalchemy.orm.session import Session
from typing import Optional

from backend.database import SessionLocal
from backend.models.auth import User
from backend.models.conversations import Conversation, Participant
from backend.services import conversations_service as svc
from backend.tests.conftest import random_email

def create_test_user(db: Session, email: Optional[str] = None) -> User:
    u = User(email=email or random_email(), password="x")
    db.add(instance=u)
    db.commit()
    db.refresh(instance=u)
    return u

def test_create_conversation_creates_participants() -> None:
    db = SessionLocal()
    conv: Optional[Conversation] = None
    user1: Optional[User] = None
    user2: Optional[User] = None
    try:
        user1 = create_test_user(db=db)
        user2 = create_test_user(db=db)

        conv = svc.create_conversation_service(
            name="Test Conv",
            conversation_type="group",
            created_by=user1.id,
            participant_ids=[user1.id, user2.id]
        )

        assert conv is not None
        assert conv.participant_count == 2
    finally:
        if conv is not None:
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user1 is not None and user2 is not None:
            db.query(User).filter(User.id.in_(other=[user1.id, user2.id])).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_get_all_conversations_for_user() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    other: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user = create_test_user(db=db)
        other = create_test_user(db=db)
        conv = svc.create_conversation_service(name="c", conversation_type="group", created_by=user.id, participant_ids=[user.id, other.id])

        all_for_user = svc.get_all_conversations_service(user_id=user.id)
        assert any(conv.id == c["id"] for c in all_for_user)
    finally:
        if conv is not None:
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None and other is not None:
            db.query(User).filter(User.id.in_(other=[user.id, other.id])).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_get_single_conversation_service_returns_expected_fields() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    other: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user = create_test_user(db=db)
        other = create_test_user(db=db)
        conv = svc.create_conversation_service(name="single", conversation_type="group", created_by=user.id, participant_ids=[user.id, other.id])

        single = svc.get_single_conversation_service(user_id=user.id, conversation_id=conv.id)
        assert single[0]["id"] == conv.id
        assert "name" in single[0] and "participant_count" in single[0]
    finally:
        if conv is not None:
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None and other is not None:
            db.query(User).filter(User.id.in_(other=[user.id, other.id])).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_edit_conversation_as_admin_updates_name() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    other: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user = create_test_user(db=db)
        other = create_test_user(db=db)
        conv = svc.create_conversation_service(name="old", conversation_type="group", created_by=user.id, participant_ids=[user.id, other.id])

        edited = svc.edit_conversation_service(conversation_id=conv.id, user_id=user.id, new_name="Renamed")
        assert edited.name == "Renamed"
    finally:
        if conv is not None:
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None and other is not None:
            db.query(User).filter(User.id.in_(other=[user.id, other.id])).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_delete_conversation_as_admin_removes_it() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    other: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user = create_test_user(db=db)
        other = create_test_user(db=db)
        conv = svc.create_conversation_service(name="todel", conversation_type="group", created_by=user.id, participant_ids=[user.id, other.id])

        svc.delete_conversation_service(conversation_id=conv.id, user_id=user.id)

        remaining = db.query(Conversation).filter(Conversation.id == conv.id).first()
        assert remaining is None
    finally:
        # cleanup users
        if user is not None and other is not None:
            db.query(Participant).filter(Participant.user_id.in_(other=[user.id, other.id])).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.created_by.in_(other=[user.id, other.id])).delete(synchronize_session=False)
            db.query(User).filter(User.id.in_(other=[user.id, other.id])).delete(synchronize_session=False)
        db.commit()
        db.close()