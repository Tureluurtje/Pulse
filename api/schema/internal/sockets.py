from uuid import UUID
from fastapi import WebSocket
from typing import TypedDict

class ConnectionEntry(TypedDict):
    connection_id: UUID
    websocket: WebSocket