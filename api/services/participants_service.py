from ..models.conversations import Participant
from sqlalchemy import and_
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Optional, Literal
from fastapi import HTTPException, status

from ..schema.internal.participants import ParticipantDetail, ParticipantUser
from ..database import SessionLocal

def get_user_role(
    conversation_id: UUID,
    user_id: UUID,
    db: Session
) -> Optional[Literal["owner", "admin", "member"]]:
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

def get_all_particpants_service(
    user_id: UUID,
    conversation_id: UUID
) -> list[ParticipantDetail]:
    db = SessionLocal()

    in_conversation = check_user_in_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    if not in_conversation:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )

    participants = (
        db.query(Participant)
        .filter(Participant.conversation_id == conversation_id)
        .options(joinedload(Participant.user))
        .all()
    )
    db.close()

    participant_details = []
    for participant in participants:
        participant_details.append(
            ParticipantDetail(
                user=ParticipantUser(
                    id=participant.user.id,
                    email=participant.user.email
                ),
                role=participant.role,
                joined_at=participant.joined_at
            )
        )

    return participant_details

def add_participants_service(
    user_id: UUID,
    conversation_id: UUID,
    new_participant_ids: list[UUID]
) -> list[ParticipantDetail]:
    db = SessionLocal()

    in_conversation = check_user_in_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    if not in_conversation:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized"
        )

    participant_details = []
    existing_participants = []

    for new_participant_id in new_participant_ids:
        existing_participant = db.query(Participant).filter(and_(
            Participant.conversation_id == conversation_id,
            Participant.user_id == new_participant_id
        )).first()

        if existing_participant:
            existing_participants.append(new_participant_id)

    if existing_participants:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User(s) with id {', '.join(str(id) for id in existing_participants)} already participant(s)"
        )

    for new_participant_id in new_participant_ids:
        new_participant = Participant(
            conversation_id=conversation_id,
            user_id=new_participant_id,
            role="member"
        )
        db.add(new_participant)

    db.commit()

    for new_participant_id in new_participant_ids:
        new_participant = db.query(Participant).filter(and_(
            Participant.conversation_id == conversation_id,
            Participant.user_id == new_participant_id
        )).options(joinedload(Participant.user)).first()

        participant_details.append(ParticipantDetail(
            user=ParticipantUser(
                id=new_participant.user.id,
                display_name=new_participant.user.email
            ),
            role=new_participant.role,
            joined_at=new_participant.joined_at
        ))

    db.close()
    return participant_details

def update_user_role_service(
    user_id: UUID,
    conversation_id: UUID,
    target_user_id: UUID,
    new_role: Literal["owner", "admin", "member"]
) -> ParticipantDetail:
    db = SessionLocal()

    in_conversation = check_user_in_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    user_role = get_user_role(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    # Must be in conversation and have appropriate role
    if not in_conversation:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to change participant roles"
        )

    # Owner cannot change their own role
    if user_role == "owner" and target_user_id == user_id:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )

    # Only owner and admin can change roles (with restrictions)
    if user_role not in ("owner", "admin"):
        db.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to change participant roles"
        )

    # Ownership cannot be transferred or assigned
    if new_role == "owner":
        """
        if user_role != "owner":
            db.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only owners can assign ownership"
            )

        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ownership cannot be transferred"
        )
        """
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ownership cannot be assigned or transferred"
        )

    # Admin restrictions: can only change between member and admin
    if user_role == "admin":
        target_participant = db.query(Participant).filter(and_(
            Participant.conversation_id == conversation_id,
            Participant.user_id == target_user_id
        )).first()

        if target_participant and target_participant.role == "owner":
            db.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot change owner's role"
            )

        # Admin can only promote members to admin or demote admins to member
        if not (
            (target_participant and target_participant.role == "member" and new_role == "admin") or
            (target_participant and target_participant.role == "admin" and new_role == "member")
        ):
            db.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admins can only change between member and admin roles"
            )

    participant = db.query(Participant).filter(and_(
        Participant.conversation_id == conversation_id,
        Participant.user_id == target_user_id
    )).options(joinedload(Participant.user)).first()

    if not participant:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    if participant.role == new_role:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Participant already has the specified role"
        )

    participant.role = new_role
    db.commit()

    updated_participant_detail = ParticipantDetail(
        user=ParticipantUser(
            id=participant.user.id,
            display_name=participant.user.email
        ),
        role=participant.role,
        joined_at=participant.joined_at
    )

    db.close()
    return updated_participant_detail

def remove_participant_service(
    user_id: UUID,
    conversation_id: UUID,
    target_user_id: UUID
) -> None:
    db = SessionLocal()

    in_conversation = check_user_in_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    user_role = get_user_role(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db
    )

    # Must be in conversation and have appropriate role
    if not in_conversation or user_role not in ("owner", "admin"):
        db.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to remove participants"
        )

    participant = db.query(Participant).filter(and_(
        Participant.conversation_id == conversation_id,
        Participant.user_id == target_user_id
    )).first()

    if not participant:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    db.delete(participant)
    db.commit()
    db.close()
    return
