from fastapi import HTTPException
import os
import sys
from typing import Optional
from uuid import UUID, uuid4

# Ensure project root (C:\dev\Pulse) is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# TODO: change UserProfileObj to UserProfile
from backend.database import SessionLocal
from backend.models.auth import User
from backend.schema.internal.user_service import UserProfileObj
from backend.services.auth_service import register_user
from backend.services.users_service import get_user_profile, get_all_users
from backend.services.conversations_service import create_conversation_service, get_all_conversations_service
from backend.services.messages_service import send_message_service
from backend.tests.conftest import random_email

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
                created_by=user["id"],
                participant_ids=[BOT_ID, user["user_id"]]
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
    create_users(n=100)
    create_conversations()
    create_messages(n=3)