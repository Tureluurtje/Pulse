from ..models.messages import Message
from ..database import SessionLocal
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from ..services.participants_service import get_user_role, check_user_in_conversation
from ..schema.internal.messages import MessagePreview
from ..models.messages import Message

def get_all_messages_service(
    conversation_id: UUID,
    user_id: UUID,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    before: Optional[datetime] = None
) -> List[MessagePreview]:
    """Retrieve messages for a conversation with optional pagination and time filter.

    The function verifies the requesting user's membership in the
    conversation, then returns messages ordered by creation time descending.

    Args:
        conversation_id: UUID of the conversation to fetch messages from.
        user_id: UUID of the requesting user (used for authorization).
        limit: Maximum number of messages to return.
        offset: Number of messages to skip for pagination.
        before: Optional datetime to only return messages created before this
            timestamp.

    Returns:
        A list of ``Message`` ORM instances matching the query.

    Raises:
        fastapi.HTTPException: If the requesting user is not a participant
            (HTTP 401).
    """
    db = SessionLocal()

    in_conversation = check_user_in_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    if not in_conversation:
        raise HTTPException(
            status_code=401,
            detail="Not authorized"
        )

    query = db.query(Message).filter(Message.conversation_id == conversation_id)

    if before:
        query = query.filter(Message.created_at < before)

    messages = query.order_by(Message.created_at.desc()).offset(offset=offset).limit(limit=limit).all()
    db.close()
    return [
        MessagePreview(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            content=message.content,
            edited_at=message.edited_at,
            created_at=message.created_at
        ) for message in messages
    ]

def get_single_message_service(
    message_id: UUID,
    user_id: UUID
) -> MessagePreview:
    """Return a single message if the requesting user belongs to its conversation.

    Args:
        message_id: UUID of the message to retrieve.
        user_id: UUID of the requesting user (authorization check).

    Returns:
        The ``Message`` ORM instance.

    Raises:
        fastapi.HTTPException: If the user is not authorized to view the
            message (HTTP 401) or the message cannot be found (HTTP 404).
    """
    db = SessionLocal()

    conversation_id = db.query(Message.conversation_id).filter(
        Message.id == message_id
    ).scalar()

    if not conversation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with id {message_id} not found or has no associated conversation"
        )

    in_conversation = check_user_in_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    if not in_conversation:
        raise HTTPException(
            status_code=401,
            detail="Not authorized"
        )

    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=404,
            detail="message not found"
        )
    db.close()
    return MessagePreview(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        edited_at=message.edited_at,
        created_at=message.created_at
    )

def get_last_message_in_conversation_service(
    conversation_id: UUID
) -> Optional[MessagePreview]:
    """Retrieve the most recent message in a conversation.

    Args:
        conversation_id: UUID of the conversation to query.

    Returns:
        The latest ``Message`` ORM instance, or ``None`` if no messages exist.
    """
    db = SessionLocal()

    message = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .first()
    )

    db.close()
    if not message:
        return None
    return MessagePreview(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        edited_at=message.edited_at,
        created_at=message.created_at
    )

def send_message_service(
    sender_id: UUID,
    conversation_id: UUID,
    content: str
) -> MessagePreview:
    """Persist a new message to the specified conversation.

    Args:
        sender_id: UUID of the user sending the message.
        conversation_id: UUID of the conversation to append the message to.
        content: Message text content.

    Returns:
        The newly created ``Message`` ORM instance.
    """

    db = SessionLocal()

    new_message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content
    )

    db.add(instance=new_message)
    db.commit()
    db.refresh(instance=new_message)
    db.close()

    return MessagePreview(
        id=new_message.id,
        conversation_id=new_message.conversation_id,
        sender_id=new_message.sender_id,
        content=new_message.content,
        edited_at=new_message.edited_at,
        created_at=new_message.created_at
    )

def edit_message_service(
    message_id: UUID,
    new_content: str
) -> MessagePreview:
    """Update the content of an existing message.

    Args:
        message_id: UUID of the message to update.
        new_content: New message content to set.

    Returns:
        The updated ``Message`` ORM instance.

    Raises:
        fastapi.HTTPException: If the message does not exist (HTTP 404).
    """
    db = SessionLocal()

    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="message not found"
        )

    message.content = new_content
    message.edited_at = datetime.utcnow()

    db.commit()
    db.refresh(message)
    db.close()

    return MessagePreview(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        edited_at=message.edited_at,
        created_at=message.created_at
    )

def delete_message_service(
    message_id: UUID,
    user_id: UUID
) -> None:
    """Delete a message if the requesting user has sufficient privileges.

    The function checks the user's role in the conversation that contains the
    message. Only users with an admin role may delete messages.

    Args:
        message_id: UUID of the message to delete.
        user_id: UUID of the requesting user.

    Raises:
        fastapi.HTTPException: If the user is not a participant
            (HTTP 403) or is not an admin (HTTP 403).
    """
    db = SessionLocal()

    conversation_id = db.query(Message.conversation_id).filter(
        Message.id == message_id
    ).scalar()

    if not conversation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with id {message_id} not found or has no associated conversation"
        )

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

    message = db.query(Message).filter(Message.id == message_id).first()

    db.delete(instance=message)
    db.commit()
    db.close()

    return
