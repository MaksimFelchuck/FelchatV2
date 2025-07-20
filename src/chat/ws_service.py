"""WebSocket service for managing chat connections and message handling."""

import json
import time

import redis.asyncio as redis
from fastapi import WebSocket

from src.config import settings
from src.logger import chat_logger


class ChatWebSocketService:
    """
    Service for managing WebSocket sessions and private chat logic between users.

    Stores active connections, message history in Redis, and ensures message delivery.
    """

    def __init__(self, redis_url: str = None, user_service=None):
        """
        Initialize the service.

        Args:
            redis_url: Redis connection URL (optional, uses config default)
            user_service: User service for checking blocks
        """
        self.active_connections: dict[int, set[WebSocket]] = {}
        self.redis_url = redis_url or settings.redis_url
        self.redis: redis.Redis | None = None
        self.user_service = user_service
        self._logger = chat_logger

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """
        Connect user to chat (connection registration only).

        Args:
            user_id: ID of the user connecting
            websocket: WebSocket connection object
        """
        self._ensure_user_connections(user_id)
        self.active_connections[user_id].add(websocket)
        await self._initialize_redis()
        self._logger.info(f"User {user_id} connected to chat")

    def _ensure_user_connections(self, user_id: int) -> None:
        """Ensure user has a connections set."""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

    async def _initialize_redis(self) -> None:
        """Initialize Redis connection if not already done."""
        if not self.redis:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            self._logger.info("Redis connection initialized")

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
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
                self._logger.info(f"User {user_id} disconnected from chat")

    def get_online_users(self) -> set[int]:
        """
        Get set of currently online user IDs.

        Returns:
            Set of user IDs who have active WebSocket connections
        """
        return set(self.active_connections.keys())

    async def send_personal_message(
        self, message: str, to_user_id: int, from_user_id: int
    ) -> bool:
        """
        Send personal message between users, save to Redis and broadcast to all
        sessions.

        Args:
            message: Message content
            to_user_id: ID of the recipient
            from_user_id: ID of the sender

        Returns:
            True if message was sent successfully, False otherwise
        """
        if self._is_message_blocked(from_user_id, to_user_id):
            return False

        try:
            await self._save_message_to_redis(message, to_user_id, from_user_id)
            message_data = self._create_message_data(message, from_user_id)
            await self._broadcast_message(message_data, to_user_id, from_user_id)

            self._logger.info(f"Message sent from {from_user_id} to {to_user_id}")
            return True

        except Exception as e:
            self._logger.error(
                f"Error sending message from {from_user_id} to {to_user_id}: {e}"
            )
            return False

    def _is_message_blocked(self, from_user_id: int, to_user_id: int) -> bool:
        """Check if message is blocked due to user blocking."""
        if self.is_blocked(from_user_id, to_user_id):
            self._logger.warning(
                f"Message blocked: {from_user_id} -> {to_user_id} (users are blocked)"
            )
            return True
        return False

    async def _save_message_to_redis(
        self, message: str, to_user_id: int, from_user_id: int
    ) -> None:
        """Save message to Redis for chat history with 30-minute expiration."""
        if not self.redis:
            return

        chat_key = self._get_chat_key(to_user_id, from_user_id)

        # Get username from user service if available
        from_username = None
        if self.user_service:
            try:
                user = self.user_service.get_user(from_user_id)
                if user:
                    from_username = user.username
            except Exception as e:
                self._logger.warning(
                    f"Could not get username for user {from_user_id}: {e}"
                )

        message_data = {
            "from": from_user_id,
            "from_username": from_username,
            "to": to_user_id,
            "message": message,
            "timestamp": int(time.time()),
        }

        # Save message to Redis list
        await self.redis.rpush(chat_key, json.dumps(message_data))

        # Set expiration based on config (default 30 minutes)
        expiration_seconds = settings.message_retention_minutes * 60
        await self.redis.expire(chat_key, expiration_seconds)

    def _get_chat_key(self, user1_id: int, user2_id: int) -> str:
        """Generate consistent Redis key for chat between two users."""
        return f"chat:{min(user1_id, user2_id)}:{max(user1_id, user2_id)}"

    def _create_message_data(self, message: str, from_user_id: int) -> str:
        """Create JSON message data for WebSocket transmission."""
        # Get username from user service if available
        from_username = None
        if self.user_service:
            try:
                user = self.user_service.get_user(from_user_id)
                if user:
                    from_username = user.username
            except Exception as e:
                self._logger.warning(
                    f"Could not get username for user {from_user_id}: {e}"
                )

        return json.dumps(
            {
                "from": from_user_id,
                "from_username": from_username,
                "message": message,
                "timestamp": int(time.time()),
            }
        )

    async def _broadcast_message(
        self, message_data: str, to_user_id: int, from_user_id: int
    ) -> None:
        """Broadcast message to all connected sessions of both users."""
        await self._send_to_user_sessions(message_data, to_user_id, "recipient")
        await self._send_to_user_sessions(message_data, from_user_id, "sender")

    async def _send_to_user_sessions(
        self, message_data: str, user_id: int, user_type: str
    ) -> None:
        """Send message to all sessions of a specific user."""
        if user_id not in self.active_connections:
            return

        broken_connections = set()

        for websocket in self.active_connections[user_id].copy():
            try:
                await websocket.send_text(message_data)
            except Exception as e:
                self._logger.error(f"Error sending to {user_type} {user_id}: {e}")
                broken_connections.add(websocket)

        # Remove broken connections
        for websocket in broken_connections:
            self.active_connections[user_id].discard(websocket)

    def is_blocked(self, user1_id: int, user2_id: int) -> bool:
        """
        Check if two users are blocked.

        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user

        Returns:
            True if either user has blocked the other
        """
        if self.user_service:
            return self.user_service.is_blocked(user1_id, user2_id)
        return False

    async def get_history(
        self, user1_id: int, user2_id: int, limit: int = None
    ) -> list[dict]:
        """
        Get message history between two users from Redis.

        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            limit: Number of recent messages to return (uses config default if None)

        Returns:
            List of message dictionaries
        """
        if not self.redis:
            return []

        limit = limit or settings.chat_history_limit
        chat_key = self._get_chat_key(user1_id, user2_id)

        try:
            # Check if key exists (hasn't expired)
            exists = await self.redis.exists(chat_key)
            if not exists:
                self._logger.info(f"Chat history expired for {user1_id}-{user2_id}")
                return []

            messages = await self.redis.lrange(chat_key, -limit, -1)
            parsed_messages = []

            for message in messages:
                try:
                    parsed_messages.append(json.loads(message))
                except json.JSONDecodeError as e:
                    self._logger.warning(f"Failed to parse message: {e}")
                    continue

                    self._logger.info(
                        f"Retrieved {len(parsed_messages)} messages for {user1_id}-{user2_id}"
                    )
            return parsed_messages

        except Exception as e:
            self._logger.error(
                f"Error getting chat history for {user1_id}-{user2_id}: {e}"
            )
            return []

    async def get_message_count(self, user1_id: int, user2_id: int) -> int:
        """
        Get the number of messages in chat history.

        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user

        Returns:
            Number of messages in chat
        """
        if not self.redis:
            return 0

        chat_key = self._get_chat_key(user1_id, user2_id)

        try:
            return await self.redis.llen(chat_key)
        except Exception as e:
            self._logger.error(
                f"Error getting message count for {user1_id}-{user2_id}: {e}"
            )
            return 0

    async def clear_chat_history(self, user1_id: int, user2_id: int) -> bool:
        """
        Clear chat history between two users.

        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user

        Returns:
            True if cleared successfully, False otherwise
        """
        if not self.redis:
            return False

        chat_key = self._get_chat_key(user1_id, user2_id)

        try:
            await self.redis.delete(chat_key)
            self._logger.info(f"Chat history cleared for {user1_id}-{user2_id}")
            return True
        except Exception as e:
            self._logger.error(
                f"Error clearing chat history for {user1_id}-{user2_id}: {e}"
            )
            return False
