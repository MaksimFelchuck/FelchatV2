"""In-memory implementation of chat repository."""

from src.chat.repositories.abs.chat import AbstractChatRepository


class ChatRepositoryInMemory(AbstractChatRepository):
    """In-memory implementation of chat repository for testing."""

    def __init__(self):
        """Initialize the in-memory repository."""
        self.messages = {}

    async def save_message(self, from_user: int, to_user: int, message: str) -> None:
        """
        Save a message to in-memory storage.

        Args:
            from_user: ID of the user sending the message
            to_user: ID of the user receiving the message
            message: The message content
        """
        key = tuple(sorted((from_user, to_user)))
        if key not in self.messages:
            self.messages[key] = []
        self.messages[key].append(
            {"from": from_user, "to": to_user, "message": message}
        )

    async def get_history(
        self, user1: int, user2: int, limit: int = 50
    ) -> list[dict[str, str | int | float | bool | None]]:
        """
        Get chat history from in-memory storage.

        Args:
            user1: ID of the first user
            user2: ID of the second user
            limit: Maximum number of messages to return

        Returns:
            List of message objects
        """
        key = tuple(sorted((user1, user2)))
        return self.messages.get(key, [])[-limit:]
