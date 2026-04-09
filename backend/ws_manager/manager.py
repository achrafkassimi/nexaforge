from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        print(f"[WS] Client connected to room: {room}")

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)
        print(f"[WS] Client disconnected from room: {room}")

    async def broadcast(self, room: str, message: dict):
        if room not in self.active_connections:
            return
        dead = []
        for connection in self.active_connections[room]:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.active_connections[room].remove(d)

manager = ConnectionManager()