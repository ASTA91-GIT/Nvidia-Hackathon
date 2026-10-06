import json
import logging
from typing import Dict, List, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.incident_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, incident_id: str = "global"):
        await websocket.accept()
        self.active_connections.append(websocket)
        if incident_id not in self.incident_connections:
            self.incident_connections[incident_id] = []
        self.incident_connections[incident_id].append(websocket)
        logger.info(f"WebSocket client connected to incident channel: {incident_id}")

    def disconnect(self, websocket: WebSocket, incident_id: str = "global"):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if incident_id in self.incident_connections and websocket in self.incident_connections[incident_id]:
            self.incident_connections[incident_id].remove(websocket)
        logger.info(f"WebSocket client disconnected from channel: {incident_id}")

    async def broadcast(self, message: Dict[str, Any], incident_id: str = "global"):
        data_str = json.dumps(message)
        # Broadcast to incident specific and global channels
        targets = set(self.incident_connections.get(incident_id, []) + self.incident_connections.get("global", []))
        for connection in targets:
            try:
                await connection.send_text(data_str)
            except Exception as e:
                logger.warning(f"Error sending to websocket: {e}")

ws_manager = ConnectionManager()
