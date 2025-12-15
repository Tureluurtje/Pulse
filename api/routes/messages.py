from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from uuid import UUID

from ..models.messages import Message

from ..services.auth_service import get_http_user_id
from ..services.messages_service import get_all_messages_service, send_message_service, get_single_message_service, edit_message_service, delete_message_service
from ..schema.http.messages import GetMessagesRequest, GetMessagesResponse, SendMessageRequest, SendMessageResponse, EditMessageRequest, EditMessageResponse, DeleteMessageRequest

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

@router.get(path="/", response_model=List[GetMessagesResponse])
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

@router.post(path="/send")
def send_message(data: SendMessageRequest, user_id: UUID = Depends(dependency=get_http_user_id)) -> SendMessageResponse:
    new_message: Message = send_message_service(
        sender_id=user_id,
        conversation_id=data.conversation_id,
        content=data.content
    )
    if not new_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Message not send"
        )

    return SendMessageResponse(
        id=new_message.id,
        conversation_id=new_message.conversation_id,
        sender_id=new_message.sender_id,
        content=new_message.content,
        created_at=new_message.created_at
    )

@router.patch(path="/edit", response_model=EditMessageResponse)
def edit_message(data: EditMessageRequest, user_id: UUID = Depends(dependency=get_http_user_id)) -> Message:
    return edit_message_service(
        message_id=data.message_id,
        new_content=data.new_content
    )

@router.delete(path="/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    data: DeleteMessageRequest,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> None:
    delete_message_service(message_id=data.message_id, user_id=user_id)
    return
