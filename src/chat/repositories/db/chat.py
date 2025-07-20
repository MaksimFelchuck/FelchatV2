"""Database implementation of chat repository using Redis."""

import json
import logging
from datetime import datetime

import redis.asyncio as redis
from redis.asyncio import Redis

from src.chat.repositories.abs.chat import AbstractChatRepository

logger = logging.getLogger(__name__)


class ChatRepositoryDB(AbstractChatRepository):
    """Redis-based implementation of chat repository."""

    def __init__(self, redis_url: str):
        """
        Initialize the repository with Redis connection.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: Redis | None = None

    def _get_redis(self) -> Redis:
        """Get or create Redis connection."""
        if self.redis is None:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
        return self.redis

    async def save_message(self, from_user: int, to_user: int, message: str) -> None:
        """
        Save a message to Redis.

        Args:
            from_user: ID of the user sending the message
            to_user: ID of the user receiving the message
            message: The message content
        """
        try:
            redis_client = self._get_redis()
            key = f"chat:{min(from_user, to_user)}:{max(from_user, to_user)}"
            message_data = {
                "from": from_user,
                "to": to_user,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }
            await redis_client.rpush(key, json.dumps(message_data))  # type: ignore
            logger.debug(f"Message saved from user {from_user} to user {to_user}")
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            raise

    async def get_history(
        self, user1: int, user2: int, limit: int = 50
    ) -> list[dict[str, str | int | float | bool | None]]:
        """
        Get chat history from Redis.

        Args:
            user1: ID of the first user
            user2: ID of the second user
            limit: Maximum number of messages to return

        Returns:
            List of message objects with timestamp, from, to, and message fields
        """
        try:
            redis_client = self._get_redis()
            key = f"chat:{min(user1, user2)}:{max(user1, user2)}"
            messages = await redis_client.lrange(key, -limit, -1)  # type: ignore
            parsed_messages = []
            for message in messages:
                try:
                    parsed_message = json.loads(message)
                    parsed_messages.append(parsed_message)
                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Failed to parse message: {message}, error: {str(e)}"
                    )
                    continue
            return parsed_messages
        except Exception as e:
            logger.error(f"Failed to get chat history: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the Redis connection."""
        try:
            if self.redis:
                await self.redis.aclose()
                self.redis = None
                logger.debug("Redis connection closed")
        except Exception as e:
            logger.error(f"Failed to close Redis connection: {str(e)}")
            raise
