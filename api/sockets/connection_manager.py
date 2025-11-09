from typing import Dict, List, Any
from uuid import UUID, uuid4
from fastapi import WebSocket
import asyncio

from ..schema.internal.sockets import ConnectionEntry

class ConnectionManager:
    """Manages active WebSocket connections and user sessions."""
    def __init__(self) -> None:
        # user_id -> list of { connection_id, websocket }
        self.active_connections: Dict[UUID, List[ConnectionEntry]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, user_id: UUID, websocket: WebSocket) -> UUID:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        connection_id = uuid4()
        async with self.lock:
            self.active_connections.setdefault(user_id, []).append({
                "connection_id": connection_id,
                "websocket": websocket
            })
        return connection_id

    async def disconnect(self, user_id: UUID, connection_id: UUID) -> None:
        """Remove a WebSocket connection when closed."""
        async with self.lock:
            if user_id not in self.active_connections:
                return
            self.active_connections[user_id] = [
                c for c in self.active_connections[user_id]
                if c["connection_id"] != connection_id
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_to_user(self, user_id: UUID, message: dict[str, Any]) -> None:
        """Send a message to all active connections of a user."""
        async with self.lock:
            connections: List[ConnectionEntry] = self.active_connections.get(user_id, [])
        to_remove: list[UUID] = []
        for c in connections:
            ws = c["websocket"]
            try:
                if isinstance(message, str):
                    await ws.send_text(data=message)
                else:
                    await ws.send_json(data=message)
            except Exception:
                # Mark this connection for removal; it may have been closed
                to_remove.append(c["connection_id"])

        if to_remove:
            # Cleanup removed connections
            async with self.lock:
                self.active_connections[user_id] = [
                    c for c in self.active_connections.get(user_id, [])
                    if c["connection_id"] not in to_remove
                ]
                if not self.active_connections.get(user_id):
                    self.active_connections.pop(user_id, None)

    async def broadcast(self, message: object) -> None:
        """Send a message to every connected socket. Accepts str or dict-like objects."""
        # Send and remove any dead connections encountered
        to_remove_pairs: list[tuple[UUID, UUID]] = []
        for user_id, conns in list(self.active_connections.items()):
            for c in list(conns):
                ws = c["websocket"]
                try:
                    if isinstance(message, str):
                        await ws.send_text(data=message)
                    else:
                        await ws.send_json(data=message)
                except Exception:
                    to_remove_pairs.append((user_id, c["connection_id"]))

        if to_remove_pairs:
            async with self.lock:
                for uid, cid in to_remove_pairs:
                    conns = self.active_connections.get(uid, [])
                    self.active_connections[uid] = [
                        c for c in conns if c["connection_id"] != cid
                    ]
                    if not self.active_connections[uid]:
                        self.active_connections.pop(uid, None)

    def get_user_connections(self, user_id: UUID) -> list[UUID]:
        """Return connection IDs for a user."""
        return [c["connection_id"] for c in self.active_connections.get(user_id, [])]
