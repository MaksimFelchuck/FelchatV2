"""Abstract base class for user repository implementations."""

from abc import ABC, abstractmethod
from typing import Any

from src.users.schemas import UserCreate


class AbstractUserRepository(ABC):
    """Abstract base class for user repositories."""
    
    @abstractmethod
    def create_user(self, user_data: UserCreate) -> Any | None:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object or None if creation failed
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Any | None:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Any | None:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Any | None:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        pass

    @abstractmethod
    def list_users(self) -> list[Any]:
        """
        Get list of all users.
        
        Returns:
            List of user objects
        """
        pass

    @abstractmethod
    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Block a user.
        
        Args:
            blocker_id: ID of the user doing the blocking
            blocked_id: ID of the user being blocked
        """
        pass

    @abstractmethod
    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Unblock a user.
        
        Args:
            blocker_id: ID of the user doing the unblocking
            blocked_id: ID of the user being unblocked
        """
        pass

    @abstractmethod
    def is_blocked(self, user1_id: int, user2_id: int) -> bool:
        """
        Check if two users are blocked.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            
        Returns:
            True if either user has blocked the other
        """
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches
        """
        pass
