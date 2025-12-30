from fastapi import HTTPException
import os
import sys
from typing import Optional
from uuid import UUID, uuid4
from pathlib import Path
from time import sleep

# Ensure project root is in sys.path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# TODO: change UserProfileObj to UserProfile
from api.database import SessionLocal
from api.models.auth import User
from api.schema.internal.users import UserProfileObj
from api.services.auth_service import register_user
from api.services.users_service import get_user_profile, get_all_users
from api.services.conversations_service import create_conversation_service, get_all_conversations_service
from api.services.messages_service import send_message_service
from conftest import random_email

db = SessionLocal()
BOT_ID: UUID = db.query(User.id).filter(User.email.contains("botuser")).scalar()
db.close()
if not BOT_ID:
    raise RuntimeError("No valid bot id found")

def create_users(n: int, prefix: str = "testuser", password: str = "PASSWORD") -> None:
    failedRegisters = 0
    for _ in range(0, n):
        email = random_email(prefix=f"{prefix}_")
        try:
            register_user(email=email, password=password)
        except HTTPException:
            failedRegisters += 1

def create_conversations(n: int = 3, prefix: Optional[str] = "testconversation", user_id: Optional[UUID] = None) -> None:
    users: list[UserProfileObj] = []
    if not user_id:
        users = get_all_users()
    else:
        user_profile = get_user_profile(user_id=user_id)
        users.append(user_profile)
    for user in users:
        for _ in range(0, n):
            create_conversation_service(
                name=f"{prefix}_{uuid4()}",
                conversation_type="private",
                created_by=user["user_id"],
                participant_ids=[BOT_ID]
            )

def create_messages(n: int, user: Optional[UUID] = None) -> None:
    if user:
        conversations: list[UUID] = [x["id"] for x in get_all_conversations_service(user_id=user, limit=0)]
    else:
        conversations: list[UUID] = [x["id"] for x in get_all_conversations_service(user_id=BOT_ID, limit=0)]

    for conversation in conversations:
        for _ in range(0, n):
            send_message_service(
                sender_id=BOT_ID,
                conversation_id=conversation,
                content=f"testmessage_{uuid4()}",
            )

if __name__ == "__main__":
    #create_users(n=100)
    #create_conversations(n=10)
    create_messages(n=10, user="bc623504-e710-4252-b0cc-0533cc84acba")
