import pytest
from typing import Optional
from sqlalchemy.orm.session import Session

from api.database import SessionLocal
from api.models.auth import User
from api.models.conversations import Conversation, Participant
from api.models.messages import Message
from api.services import messages_service as svc
from api.tests.conftest import random_email

def create_user_and_conv(db: Session) -> tuple[User, Conversation]:
    user = User(email=random_email(), password="x")
    db.add(instance=user)
    db.commit()
    db.refresh(instance=user)

    conv = Conversation(name="tconv", conversation_type="group", created_by=user.id)
    db.add(instance=conv)
    db.commit()
    db.refresh(instance=conv)

    participant = Participant(conversation_id=conv.id, user_id=user.id, role="admin")
    db.add(instance=participant)
    db.commit()

    return user, conv

def test_send_message_service_inserts_message() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user, conv = create_user_and_conv(db=db)
        msg = svc.send_message_service(sender_id=user.id, conversation_id=conv.id, content="hello")
        assert msg is not None
        assert msg.content == "hello"
    finally:
        if conv is not None:
            db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None:
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_get_single_message_service_returns_message() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user, conv = create_user_and_conv(db=db)
        msg = svc.send_message_service(sender_id=user.id, conversation_id=conv.id, content="hello")
        fetched = svc.get_single_message_service(message_id=msg.id, user_id=user.id)
        assert fetched.id == msg.id
    finally:
        if conv is not None:
            db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None:
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_edit_message_updates_content() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user, conv = create_user_and_conv(db=db)
        msg = svc.send_message_service(sender_id=user.id, conversation_id=conv.id, content="hello")
        edited = svc.edit_message_service(message_id=msg.id, new_content="edited")
        assert edited.content == "edited"
    finally:
        if conv is not None:
            db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None:
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_get_all_messages_service_returns_messages() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user, conv = create_user_and_conv(db=db)
        msg = svc.send_message_service(sender_id=user.id, conversation_id=conv.id, content="hello")
        all_msgs = svc.get_all_messages_service(conversation_id=conv.id, user_id=user.id)
        assert any(m.id == msg.id for m in all_msgs)
    finally:
        if conv is not None:
            db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None:
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_delete_message_service_removes_message() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user, conv = create_user_and_conv(db=db)
        msg = svc.send_message_service(sender_id=user.id, conversation_id=conv.id, content="hello")
        svc.delete_message_service(message_id=msg.id, user_id=user.id)
        remaining = db.query(Message).filter(Message.id == msg.id).first()
        assert remaining is None
    finally:
        if conv is not None:
            db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None:
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()

@pytest.mark.parametrize(argnames="content", argvalues=["hi", "", "a" * 500])
def test_send_various_message_contents(content: str) -> None:
    db = SessionLocal()
    user: Optional[User] = None
    conv: Optional[Conversation] = None
    try:
        user, conv = create_user_and_conv(db=db)
        msg = svc.send_message_service(sender_id=user.id, conversation_id=conv.id, content=content)
        assert msg.content == content
    finally:
        if conv is not None:
            db.query(Message).filter(Message.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Participant).filter(Participant.conversation_id == conv.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.id == conv.id).delete(synchronize_session=False)
        if user is not None:
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()
