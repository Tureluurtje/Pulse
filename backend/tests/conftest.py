import os
import sys
import uuid
from typing import Any
from sqlalchemy.orm.session import Session

# Ensure project root (one level above `backend/`) is on sys.path so `import backend...` works
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import SessionLocal
from backend.models.users import UserProfile

def make_profile_obj(**kwargs: Any) -> UserProfile:
    # Provide all attributes used by register_user with defaults
    defaults = {
        "first_name": None,
        "last_name": None,
        "phone": None,
        "avatar_url": None,
        "bio": None,
        "date_of_birth": None,
        "location": None,
        "website": None,
    }
    defaults.update(kwargs)
    return UserProfile(**defaults)

def random_email(prefix: str="test") -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"

def get_db() -> Session:
    return SessionLocal()
