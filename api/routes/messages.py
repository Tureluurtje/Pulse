from fastapi import APIRouter, status, Depends
from uuid import UUID

from ..services.auth_service import get_http_user_id
from ..services.messages_service import edit_message_service, delete_message_service
from ..schema.internal.messages import MessagePreview
from ..schema.http.messages import EditMessageRequest

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)

@router.patch("/{message_id}", response_model=MessagePreview)
def edit_message(
    data: EditMessageRequest,
    message_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> MessagePreview:
    return edit_message_service(
        message_id=message_id,
        new_content=data.content
    )

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: UUID,
    user_id: UUID = Depends(dependency=get_http_user_id)
) -> None:
    delete_message_service(message_id=message_id, user_id=user_id)
    return
