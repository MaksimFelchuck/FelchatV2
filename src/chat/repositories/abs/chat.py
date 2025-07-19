"""Abstract base class for chat repositories."""

from abc import ABC, abstractmethod
from typing import Any


class AbstractChatRepository(ABC):
    """Abstract base class for chat message repositories."""
    
    @abstractmethod
    async def save_message(self, from_user: int, to_user: int, message: str) -> None:
        """
        Save a message between two users.
        
        Args:
            from_user: ID of the user sending the message
            to_user: ID of the user receiving the message
            message: The message content
        """
        pass

    @abstractmethod
    async def get_history(self, user1: int, user2: int, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get chat history between two users.
        
        Args:
            user1: ID of the first user
            user2: ID of the second user
            limit: Maximum number of messages to return
            
        Returns:
            List of message objects
        """
        pass 