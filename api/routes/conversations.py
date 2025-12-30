from fastapi import APIRouter, status, Depends, HTTPException
from uuid import UUID
from typing import Optional

from api.models.conversations import Conversation
from api.schema.internal.conversations import ConversationDetail

from ..services.auth_service import get_http_user_id
from ..services.conversations_service import get_all_conversations_service, get_single_conversation_service, create_conversation_service, edit_conversation_service, delete_conversation_service, leave_conversation_service
from ..schema.http.conversations import GetConversationsRequest, GetConversationsResponse, CreateConversationRequest, CreateConversationResponse, EditConversationRequest, DeleteConversationRequest

from ..schema.http.messages import GetMessagesRequest, GetMessagesResponse, SendMessageRequest
from ..services.messages_service import get_all_messages_service, send_message_service
from ..schema.internal.messages import MessagePreview

from ..schema.internal.participants import ParticipantDetail
from ..schema.http.participants import GetParticipantsRequest, GetParticipantsResponse, AddParticipantsRequest, AddParticipantsResponse, PatchParticipantRequest
from ..services.participants_service import get_all_particpants_service, add_participants_service, update_user_role_service, remove_participant_service

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"]
)

@router.get(path="/", response_model=GetConversationsResponse)
def get_conversations(
    data: GetConversationsRequest = Depends(),
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> GetConversationsResponse:
    conversations = get_all_conversations_service(
        user_id=user_id,
        limit=data.limit,
        offset=data.offset,
    )

    if data.offset is None:
        data.offset = 0
    next_cursor: Optional[int] = data.offset + len(conversations) if len(conversations) == data.limit else None

    return GetConversationsResponse(
        items=conversations,
        next_cursor=next_cursor
    )

@router.get(path="/{conversation_id}", response_model=ConversationDetail)
def get_conversation_details(
    conversation_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> ConversationDetail:
    conversation = get_single_conversation_service(
        conversation_id=conversation_id,
        user_id=user_id
    )
    return conversation

@router.post(path="/")
def create_conversation(
    data: CreateConversationRequest,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> CreateConversationResponse:
    new_conversation =  create_conversation_service(
        name=data.name,
        conversation_type=data.conversation_type,
        created_by=user_id,
        participant_ids=data.participant_ids
    )

    return CreateConversationResponse(
        id=new_conversation.id,
        name=new_conversation.name,
        created_by=new_conversation.created_by,
        created_at=new_conversation.created_at,
        participant_count=new_conversation.participant_count
    )

@router.patch(path="/{conversation_id}", response_model=ConversationDetail)
def edit_conversation(
    conversation_id: UUID,
    data: EditConversationRequest,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> Conversation:
    return edit_conversation_service(
        conversation_id=conversation_id,
        user_id=user_id,
        new_name=data.new_name
    )

@router.delete(path="/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    data: DeleteConversationRequest,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> None:
    delete_conversation_service(
        conversation_id=data.conversation_id,
        user_id=user_id
        )
    return

@router.post(path="/{conversation_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> None:
    leave_conversation_service(
        conversation_id=conversation_id,
        user_id=user_id
    )
    return

"""
messages endpoints within conversations router
"""
@router.get("/{conversation_id}/messages", response_model=GetMessagesResponse)
def get_messages(
    conversation_id: UUID,
    data: GetMessagesRequest = Depends(),
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> GetMessagesResponse:
    messages = get_all_messages_service(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=data.limit,
            offset=data.offset,
            before=data.before
        )
    if data.offset is None:
        data.offset = 0
    next_cursor = data.offset + len(messages) if len(messages) == data.limit and len(messages) > 0 else None

    return GetMessagesResponse(
        items=messages,
        next_cursor=next_cursor
    )

@router.post("/{conversation_id}/messages")
def send_message(
    data: SendMessageRequest,
    conversation_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> MessagePreview:
    new_message: MessagePreview = send_message_service(
        sender_id=user_id,
        conversation_id=conversation_id,
        content=data.content
    )
    if not new_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Message not send"
        )

    return MessagePreview(
        id=new_message.id,
        conversation_id=new_message.conversation_id,
        sender_id=new_message.sender_id,
        content=new_message.content,
        created_at=new_message.created_at
    )

"""
participants endpoints within conversations router
"""
@router.get("/{conversation_id}/participants", response_model=GetParticipantsResponse)
def get_participants(
    conversation_id: UUID,
    data: GetParticipantsRequest = Depends(),
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> GetParticipantsResponse:
    # raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="This endpoint is not yet implemented.")
    participants: list[ParticipantDetail] = get_all_particpants_service(
        user_id=user_id,
        conversation_id=conversation_id
    )
    if data.offset is None:
        data.offset = 0
    next_cursor = data.offset + len(participants) if len(participants) == data.limit else None
    return GetParticipantsResponse(
        items=participants,
        next_cursor=next_cursor
    )

@router.get("/{conversation_id}/participants/{target_user_id}", response_model=ParticipantDetail)
def get_single_participant(
    target_user_id: UUID,
    conversation_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> ParticipantDetail:
    participants: list[ParticipantDetail] = get_all_particpants_service(
        user_id=user_id,
        conversation_id=conversation_id
    )
    for participant in participants:
        if participant.user.id == target_user_id:
            return participant
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Participant not found"
    )

@router.post("/{conversation_id}/participants", response_model=AddParticipantsResponse)
def add_participants(
    data: AddParticipantsRequest,
    conversation_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> AddParticipantsResponse:
    participants: list[ParticipantDetail] = add_participants_service(
        user_id=user_id,
        conversation_id=conversation_id,
        new_participant_ids=data.user_ids
    )
    return AddParticipantsResponse(
        participants=participants

    )

@router.patch("/{conversation_id}/participants/{target_user_id}", response_model=ParticipantDetail)
def patch_participants(
    data: PatchParticipantRequest,
    target_user_id: UUID,
    conversation_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> ParticipantDetail:
    updated_participant = update_user_role_service(
        user_id=user_id,
        conversation_id=conversation_id,
        target_user_id=target_user_id,
        new_role=data.role
    )
    return updated_participant

@router.delete("/{conversation_id}/participants/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant(
    target_user_id: UUID,
    conversation_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> None:
    remove_participant_service(
        user_id=user_id,
        conversation_id=conversation_id,
        target_user_id=target_user_id
    )
    return
