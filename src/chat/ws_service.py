"""WebSocket service for managing chat connections and message handling."""

import json
from typing import Optional

import redis.asyncio as redis
from fastapi import WebSocket


class ChatWebSocketService:
    """
    Service for managing WebSocket sessions and private chat logic between users.
    
    Stores active connections, message history in Redis, and ensures message delivery.
    """
    
    def __init__(self, redis_url: str):
        """
        Initialize the service.
        
        Args:
            redis_url: Redis connection URL
        """
        self.active_connections: dict[int, set[WebSocket]] = {}
        self.redis_url = redis_url
        self.redis = None

    async def connect(self, user_id: int, websocket: WebSocket):
        """
        Connect user to chat (WebSocket accept and connection registration).
        
        Args:
            user_id: ID of the user connecting
            websocket: WebSocket connection object
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        # Initialize Redis on first connection
        if not self.redis:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)

    def disconnect(self, user_id: int, websocket: WebSocket):
        """
        Disconnect user from chat (remove WebSocket from active connections).
        
        Args:
            user_id: ID of the user disconnecting
            websocket: WebSocket connection object
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(
        self, message: str, to_user_id: int, from_user_id: int
    ):
        """
        Send personal message between users, save to Redis and broadcast to all 
        sessions.
        
        Args:
            message: Message content
            to_user_id: ID of the recipient
            from_user_id: ID of the sender
        """
        # Save message to Redis (chat history between two users)
        if self.redis:
            await self.redis.rpush(  # type: ignore
                f"chat:{min(to_user_id, from_user_id)}:{max(to_user_id, from_user_id)}",
                json.dumps({
                    "from": from_user_id,
                    "to": to_user_id,
                    "message": message
                })
            )
        # Send to all connected sessions of recipient
        if to_user_id in self.active_connections:
            for ws in self.active_connections[to_user_id]:
                await ws.send_text(
                    json.dumps({"from": from_user_id, "message": message})
                )
        # Send to sender (echo)
        if from_user_id in self.active_connections:
            for ws in self.active_connections[from_user_id]:
                await ws.send_text(
                    json.dumps({"from": from_user_id, "message": message})
                )

    async def get_history(self, user1_id: int, user2_id: int, limit: int = 50) -> list[dict]:
        """
        Get message history between two users from Redis.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            limit: Number of recent messages to return
            
        Returns:
            List of message dictionaries
        """
        if not self.redis:
            return []
        key = f"chat:{min(user1_id, user2_id)}:{max(user1_id, user2_id)}"
        messages = await self.redis.lrange(key, -limit, -1)  # type: ignore
        return [json.loads(m) for m in messages] 