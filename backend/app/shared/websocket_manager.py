from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps query_id to a list of active websocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, query_id: str):
        await websocket.accept()
        if query_id not in self.active_connections:
            self.active_connections[query_id] = []
        self.active_connections[query_id].append(websocket)
        logger.info(f"WebSocket connected for query {query_id}. Total: {len(self.active_connections[query_id])}")

    def disconnect(self, websocket: WebSocket, query_id: str):
        if query_id in self.active_connections:
            if websocket in self.active_connections[query_id]:
                self.active_connections[query_id].remove(websocket)
            if not self.active_connections[query_id]:
                del self.active_connections[query_id]
        logger.info(f"WebSocket disconnected for query {query_id}.")

    async def broadcast(self, query_id: str, message: dict):
        if query_id in self.active_connections:
            text_data = json.dumps(message)
            disconnected = []
            for connection in self.active_connections[query_id]:
                try:
                    await connection.send_text(text_data)
                except Exception as e:
                    logger.error(f"Error broadcasting to {query_id}: {e}")
                    disconnected.append(connection)
            
            # Cleanup any dead connections
            for conn in disconnected:
                self.disconnect(conn, query_id)

manager = ConnectionManager()
