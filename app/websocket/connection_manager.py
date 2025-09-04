"""
WebSocket connection manager for real-time updates
"""

from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by client_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "subscriptions": set()
        }
        print(f"🔌 Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connection_metadata:
            del self.connection_metadata[client_id]
        print(f"🔌 Client {client_id} disconnected")
    
    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
                self.connection_metadata[client_id]["last_activity"] = datetime.utcnow()
            except Exception as e:
                print(f"❌ Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def send_json_message(self, data: dict, client_id: str):
        """Send a JSON message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(data))
                self.connection_metadata[client_id]["last_activity"] = datetime.utcnow()
            except Exception as e:
                print(f"❌ Error sending JSON message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
                self.connection_metadata[client_id]["last_activity"] = datetime.utcnow()
            except Exception as e:
                print(f"❌ Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_json(self, data: dict):
        """Broadcast a JSON message to all connected clients"""
        await self.broadcast(json.dumps(data))
    
    async def broadcast_to_organization(self, data: dict, organization_id: int):
        """Broadcast a message to all clients in a specific organization"""
        # This would require storing organization_id in connection metadata
        # For now, we'll broadcast to all clients
        await self.broadcast_json(data)
    
    def subscribe_to_document(self, client_id: str, document_id: int):
        """Subscribe a client to updates for a specific document"""
        if client_id in self.connection_metadata:
            self.connection_metadata[client_id]["subscriptions"].add(f"document:{document_id}")
    
    def unsubscribe_from_document(self, client_id: str, document_id: int):
        """Unsubscribe a client from updates for a specific document"""
        if client_id in self.connection_metadata:
            self.connection_metadata[client_id]["subscriptions"].discard(f"document:{document_id}")
    
    async def notify_document_update(self, document_id: int, update_data: dict):
        """Notify all clients subscribed to a document about updates"""
        message = {
            "type": "document_update",
            "document_id": document_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to subscribed clients
        for client_id, metadata in self.connection_metadata.items():
            if f"document:{document_id}" in metadata["subscriptions"]:
                await self.send_json_message(message, client_id)
    
    async def notify_processing_progress(self, job_id: str, progress: float, status: str):
        """Notify clients about processing job progress"""
        message = {
            "type": "processing_progress",
            "job_id": job_id,
            "progress": progress,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_json(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_connection_info(self) -> Dict:
        """Get information about active connections"""
        return {
            "total_connections": len(self.active_connections),
            "connections": [
                {
                    "client_id": client_id,
                    "connected_at": metadata["connected_at"].isoformat(),
                    "last_activity": metadata["last_activity"].isoformat(),
                    "subscriptions": list(metadata["subscriptions"])
                }
                for client_id, metadata in self.connection_metadata.items()
            ]
        }
