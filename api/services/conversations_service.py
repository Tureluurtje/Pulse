from sqlalchemy import func, and_
from sqlalchemy.orm.session import Session
from ..database import SessionLocal
from ..models.auth import User
from ..models.conversations import Conversation, Participant
from ..models.messages import Message
from uuid import UUID
from fastapi import HTTPException, status
from .participants_service import get_user_role
from ..schema.internal import conversationObject
from typing import Optional, Literal

def get_all_conversations_service(
    user_id: UUID,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
) -> list[conversationObject]:
    """Return a paginated list of conversations the user participates in.

    The function queries conversations joined with participants to filter
    results to those the given ``user_id`` is a member of. Each result is
    converted into a ``conversationObject`` with basic metadata.

    Args:
        user_id: UUID of the requesting user.
        limit: Maximum number of conversations to return.
        offset: Number of conversations to skip for pagination.

    Returns:
        A list of ``conversationObject`` instances describing conversations.
    """
    db = SessionLocal()

    # Join conversations with participants to filter only those the user is in
    query = (
        db.query(
            Conversation.id,
            Conversation.name,
            Conversation.created_at,
            Conversation.created_by,
            func.count(Participant.user_id).label("participant_count"),
        )
        .join(Participant, Participant.conversation_id == Conversation.id)
        .filter(Participant.user_id == user_id)
        .group_by(Conversation.id)
        .order_by(Conversation.created_at.desc())
        .offset(offset)
    )

    # Only apply limit if it's not 0
    if limit and limit > 0:
        query = query.limit(limit)

    conversations = query.all()
    db.close()

    # Transform into desired response format
    return [
        conversationObject(
            id= conversation.id,
            name= conversation.name or "Untitled Conversation",
            created_by= conversation.created_by,
            created_at= conversation.created_at.isoformat(),
            participant_count= conversation.participant_count,
        )
        for conversation in conversations
    ]

def get_single_conversation_service(
    user_id: UUID,
    conversation_id: UUID,
    limit: int = 50,
    offset: int = 0,
) -> list[conversationObject]:
    """Return details for a single conversation if the user is a member.

    The function validates that ``user_id`` is a participant in the
    conversation identified by ``conversation_id`` and returns a single-item
    list containing a ``conversationObject`` with its metadata.

    Args:
        user_id: UUID of the requesting user.
        conversation_id: UUID of the conversation to retrieve.
        limit: Unused here but kept for parity with list endpoints.
        offset: Unused here but kept for parity with list endpoints.

    Returns:
        A one-element list with a ``conversationObject`` describing the
        conversation.

    Raises:
        fastapi.HTTPException: If the conversation does not exist
            (HTTP 404).
    """
    db = SessionLocal()

    # Join conversations with participants to filter only those the user is in
    conversation = (
        db.query(
            Conversation.id,
            Conversation.name,
            Conversation.created_at,
            Conversation.created_by,  # Assuming Conversation has created_by
            func.count(Participant.user_id).label("participant_count"),
        )
        .join(Participant, Participant.conversation_id == Conversation.id)
        .filter(and_(Participant.user_id == user_id, Conversation.id == conversation_id))
        .group_by(Conversation.id)
        .order_by(Conversation.created_at.desc())
        .offset(offset=offset)
        .limit(limit=limit)
        .first()
    )
    db.close()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="conversation not found"
        )

    # Transform into desired response format
    return [
        conversationObject(
            id= conversation.id,
            name= conversation.name or "Untitled Conversation",
            created_by= conversation.created_by,
            created_at= conversation.created_at.isoformat(),
            participant_count= conversation.participant_count,
        )
    ]

def create_conversation_service(
    name: str,
    conversation_type: Literal["private", "group"],
    created_by: UUID,
    participant_ids: list[UUID]
) -> Conversation:
    """Create a new conversation and add initial participants.

    Args:
        name: Display name for the new conversation.
        conversation_type: Application-specific conversation type string.
        created_by: UUID of the user creating the conversation.
        participant_ids: List of UUIDs to add as participants, without the creator's UUID.

    Returns:
        The newly created ``Conversation`` ORM instance, with a
        ``participant_count`` attribute set.
    """
    db = SessionLocal()

    # Validate all participant IDs (including creator) exist to avoid FK errors
    candidate_ids = set(participant_ids)
    candidate_ids.add(created_by)
    existing_ids = {
        row.id for row in db.query(User.id).filter(User.id.in_(candidate_ids)).all()
    }
    missing_ids = candidate_ids.difference(existing_ids)
    if missing_ids:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown user ids: {', '.join(str(x) for x in missing_ids)}",
        )

    new_conversation = Conversation(
        name=name,
        conversation_type=conversation_type,
        created_by=created_by
    )

    db.add(instance=new_conversation)
    db.commit()
    db.refresh(instance=new_conversation)

    if created_by not in participant_ids:
        participant_ids.append(created_by)  # Ensure creator is a participant
    participants: list[Participant] = []
    for participant in participant_ids:
        role = "admin" if participant == created_by else "member"
        participants.append(
            Participant(
                conversation_id=new_conversation.id,
                user_id=participant,
                role=role
            )
        )

    db.add_all(instances=participants)
    db.commit()
    db.refresh(instance=new_conversation)
    db.close()

    new_conversation.participant_count = len(participant_ids)

    return new_conversation

def edit_conversation_service(
    conversation_id: UUID,
    user_id: UUID,
    new_name: str
) -> Conversation:
    """Rename an existing conversation if the user has admin privileges.

    Args:
        conversation_id: UUID of the conversation to edit.
        user_id: UUID of the requesting user.
        new_name: New name to set on the conversation.

    Returns:
        The updated ``Conversation`` ORM instance.

    Raises:
        fastapi.HTTPException: If the user is not a participant
            (HTTP 403), not an admin (HTTP 403), or the conversation does
            not exist (HTTP 404).
    """
    db = SessionLocal()

    user_role = get_user_role(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of this conversation."
        )

    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can edit conversations."
        )

    conversation: Optional[Conversation] = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="conversation not found"
        )

    conversation.name = new_name

    db.commit()
    db.refresh(conversation)

    return conversation

def delete_conversation_service(
    conversation_id: UUID,
    user_id: UUID
) -> None:
    """Delete a conversation and its participants if the user is admin.

    The function validates the user's role, removes participant rows to
    satisfy FK constraints, deletes the conversation instance and commits
    the change.

    Args:
        conversation_id: UUID of the conversation to delete.
        user_id: UUID of the requesting user.

    Raises:
        fastapi.HTTPException: If the user is not a participant
            (HTTP 403) or not an admin (HTTP 403).
    """
    db = SessionLocal()

    user_role = get_user_role(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not part of this conversation."
        )

    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can edit conversations."
        )

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id)
    # fetch the instance, then delete
    # remove participants first to avoid foreign key constraint issues
    db.query(Participant).filter(Participant.conversation_id == conversation_id).delete(synchronize_session=False)
    conv_inst = conversation.first()
    if conv_inst:
        db.delete(instance=conv_inst)
    db.commit()
    return

def get_conversation_by_message(
    message_id: UUID,
    db: Session
) -> UUID:
    """Resolve the conversation UUID for a given message.

    Args:
        message_id: UUID of the message whose conversation is required.
        db: SQLAlchemy session used to query the message.

    Returns:
        The UUID of the conversation the message belongs to.

    Raises:
        fastapi.HTTPException: If the message or its conversation cannot be
            found (HTTP 404).
    """
    conversation_id = db.query(Message.conversation_id).filter(
        Message.id == message_id
    ).scalar()

    if not conversation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with id {message_id} not found or has no associated conversation"
        )

    return conversation_id
