from fastapi import WebSocket
from typing import List, Dict, Any
import json

class ConnectionManager:
    def __init__(self):
        # Store active connections: {debate_id: [websockets]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store connection metadata: {websocket: {debate_id, user_id, connected_at}}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, debate_id: int):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        
        if debate_id not in self.active_connections:
            self.active_connections[debate_id] = []
        
        self.active_connections[debate_id].append(websocket)
        self.connection_metadata[websocket] = {
            "debate_id": debate_id,
            "connected_at": str(websocket.scope.get("state", {}).get("time", "unknown"))
        }

    def disconnect(self, websocket: WebSocket, debate_id: int):
        """Remove a WebSocket connection"""
        if debate_id in self.active_connections:
            if websocket in self.active_connections[debate_id]:
                self.active_connections[debate_id].remove(websocket)
            
            # Clean up empty debate rooms
            if not self.active_connections[debate_id]:
                del self.active_connections[debate_id]
        
        # Remove connection metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending personal message: {e}")
            # Remove disconnected websocket
            self.disconnect(websocket, self.connection_metadata.get(websocket, {}).get("debate_id", 0))

    async def broadcast(self, message: Dict[str, Any], debate_id: int, exclude_websocket: WebSocket = None):
        """Broadcast a message to all connections in a debate room"""
        if debate_id not in self.active_connections:
            return
        
        disconnected_websockets = []
        
        for websocket in self.active_connections[debate_id]:
            if websocket == exclude_websocket:
                continue
                
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                disconnected_websockets.append(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected_websockets:
            self.disconnect(websocket, debate_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        for debate_id in list(self.active_connections.keys()):
            await self.broadcast(message, debate_id)

    def get_connection_count(self, debate_id: int) -> int:
        """Get the number of active connections for a debate"""
        return len(self.active_connections.get(debate_id, []))

    def get_total_connections(self) -> int:
        """Get the total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())

    def get_active_debates(self) -> List[int]:
        """Get list of debate IDs with active connections"""
        return list(self.active_connections.keys())

    def get_connection_info(self, websocket: WebSocket) -> Dict[str, Any]:
        """Get metadata for a specific connection"""
        return self.connection_metadata.get(websocket, {})

    async def ping_all(self):
        """Send ping to all connections to check if they're still alive"""
        for debate_id, websockets in self.active_connections.items():
            disconnected_websockets = []
            
            for websocket in websockets:
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    disconnected_websockets.append(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected_websockets:
                self.disconnect(websocket, debate_id)
