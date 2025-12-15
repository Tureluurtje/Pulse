from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from uuid import UUID

from api.models.conversations import Conversation
from api.schema.internal.conversations import conversationObject

from ..services.auth_service import get_http_user_id
from ..services.conversations_service import get_all_conversations_service, get_single_conversation_service, create_conversation_service, edit_conversation_service, delete_conversation_service
from ..schema.http.conversations import GetConversationsRequest, GetConversationsResponse, CreateConversationRequest, CreateConversationResponse, EditConversationRequest, EditConversationResponse, DeleteConversationRequest

from ..schema.http.messages import GetMessagesRequest, GetMessagesResponse
from ..services.messages_service import get_all_messages_service, get_single_message_service
from ..models.messages import Message

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"]
)

@router.get(path="/", response_model=List[GetConversationsResponse])
def get_conversations(
    data: GetConversationsRequest = Depends(),
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> List[conversationObject]:
    if data.conversation_id:
        return get_single_conversation_service(
            user_id=user_id,
            conversation_id=data.conversation_id
        )
    return get_all_conversations_service(
        user_id=user_id,
        limit=data.limit,
        offset=data.offset,
    )

@router.post(path="/create")
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

@router.patch(path="/edit", response_model=EditConversationResponse)
def edit_conversation(
    data: EditConversationRequest,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> Conversation:
    return edit_conversation_service(
        conversation_id=data.conversation_id,
        user_id=user_id,
        new_name=data.new_name
    )

@router.delete(path="/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    data: DeleteConversationRequest,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> None:
    delete_conversation_service(
        conversation_id=data.conversation_id,
        user_id=user_id
        )
    return

@router.get("/{conversation_id}/messages", response_model=List[GetMessagesResponse])
def get_messages(
    data: GetMessagesRequest = Depends(),
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> List[Message]:
    if data.message_id:
        return [get_single_message_service(
            message_id=data.message_id,
            user_id=user_id
        )]
    if data.conversation_id:
        return get_all_messages_service(
            conversation_id=data.conversation_id,
            user_id=user_id,
            limit=data.limit,
            offset=data.offset,
            before=data.before
        )
    raise HTTPException(
        status_code=400,
        detail="Must provide conversation_id or message_id")
