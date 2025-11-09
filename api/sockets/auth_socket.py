from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status

from .connection_manager import ConnectionManager
from ..services.auth_service import get_ws_user_id
from ..services.users_service import get_user_profile

router = APIRouter()
manager = ConnectionManager()

@router.websocket(path="/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    try:
        user_id = await get_ws_user_id(websocket=websocket)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")
        return

    connection_id = await manager.connect(user_id=user_id, websocket=websocket)

    try:
        await manager.broadcast(message=f"{get_user_profile(user_id)["email"]}")
    except WebSocketDisconnect:
        await manager.disconnect(user_id=user_id, connection_id=connection_id)
        await manager.broadcast(message=f"User {user_id} left the chat")
