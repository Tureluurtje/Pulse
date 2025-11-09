from typing import Optional

from api.database import SessionLocal
from api.models.auth import User
from api.models.users import UserProfile
from api.models.conversations import Conversation, Participant
from api.services import users_service as users_svc
from api.services import participants_service as parts_svc
from api.tests.conftest import random_email

def test_user_profile_and_participant_role() -> None:
    db = SessionLocal()
    user: Optional[User] = None
    try:
        # create user and profile
        user = User(email=random_email(), password="x")
        db.add(instance=user)
        db.commit()
        db.refresh(instance=user)

        profile = UserProfile(user_id=user.id, first_name="A")
        db.add(instance=profile)
        db.commit()

        res = users_svc.get_user_profile(user_id=user.id)
        assert res is not None
        assert res["user_id"] == user.id

        # conversation and participant
        conv = Conversation(name="c", conversation_type="group", created_by=user.id)
        db.add(instance=conv)
        db.commit()
        db.refresh(instance=conv)

        part = Participant(conversation_id=conv.id, user_id=user.id, role="admin")
        db.add(instance=part)
        db.commit()

        role = parts_svc.get_user_role(conversation_id=conv.id, user_id=user.id, db=db)
        assert role is not None
        # participants_service returns the role string
        assert role == "admin"

    finally:
        if user is not None:
            db.query(Participant).filter(Participant.user_id == user.id).delete(synchronize_session=False)
            db.query(Conversation).filter(Conversation.created_by == user.id).delete(synchronize_session=False)
            db.query(UserProfile).filter(UserProfile.user_id == user.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        db.commit()
        db.close()
