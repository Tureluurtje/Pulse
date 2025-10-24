from ..models.conversations import Participant
from sqlalchemy import and_
from sqlalchemy.orm.session import Session
from uuid import UUID
from typing import Optional

def get_user_role(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> Optional[str]:
    """Return the role of a user within a conversation, if any.

    Args:
        conversation_id: UUID of the conversation to query.
        user_id: UUID of the user whose role is requested.
        db: Active SQLAlchemy session to use for the query.

    Returns:
        The participant role as a string (for example "admin" or "member"),
        or ``None`` if the user is not a participant.
    """
    participant: Participant = db.query(Participant).filter(and_(
        Participant.conversation_id == conversation_id,
        Participant.user_id == user_id)
    ).first()

    if participant:
        return str(object=participant.role)
    return None

def check_user_in_conversation(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> bool:
    """Check whether a user is a participant in a conversation.

    Args:
        conversation_id: UUID of the conversation to check.
        user_id: UUID of the user to verify membership for.
        db: Active SQLAlchemy session to use for the query.

    Returns:
        True if the user is a participant, otherwise False.
    """
    participant: Participant = db.query(Participant).filter(and_(
            Participant.conversation_id == conversation_id,
            Participant.user_id == user_id
        )
    ).first()
    
    if participant:
        return True
    return False