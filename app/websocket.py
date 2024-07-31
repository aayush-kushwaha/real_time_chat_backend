from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
from .schemas import Message
from bson import ObjectId

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[ObjectId, List[WebSocket]] = {}

    async def connect(self, conversation_id: ObjectId, websocket: WebSocket):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, conversation_id: ObjectId, websocket: WebSocket):
        self.active_connections[conversation_id].remove(websocket)
        if not self.active_connections[conversation_id]:
            del self.active_connections[conversation_id]

    async def broadcast(self, conversation_id: ObjectId, message: Message):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await connection.send_text(message.json())

manager = ConnectionManager()
