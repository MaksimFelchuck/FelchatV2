"""User service for business logic operations."""

from passlib.hash import bcrypt

from src.users.repositories.abs.user import AbstractUserRepository
from src.users.schemas import UserCreate, UserRead


class UserService:
    """Service for user-related business logic."""
    
    def __init__(self, repo: AbstractUserRepository):
        """
        Initialize the user service.
        
        Args:
            repo: User repository implementation
        """
        self.repo = repo

    def register(self, user_data: UserCreate) -> UserRead | None:
        """
        Register a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user or None if registration failed
        """
        hashed = bcrypt.hash(user_data.password)
        user = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=hashed,
        )
        created = self.repo.create_user(user)
        if created is None:
            return None
        return UserRead.model_validate(created)

    def get_user(self, user_id: int) -> UserRead | None:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        user = self.repo.get_user_by_id(user_id)
        return UserRead.model_validate(user) if user else None

    def list_users(self) -> list[UserRead]:
        """
        Get list of all users.
        
        Returns:
            List of user objects
        """
        return [UserRead.model_validate(u) for u in self.repo.list_users()]

    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Block a user.
        
        Args:
            blocker_id: ID of the user doing the blocking
            blocked_id: ID of the user being blocked
        """
        self.repo.block_user(blocker_id, blocked_id)

    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Unblock a user.
        
        Args:
            blocker_id: ID of the user doing the unblocking
            blocked_id: ID of the user being unblocked
        """
        self.repo.unblock_user(blocker_id, blocked_id)

    def is_blocked(self, user1_id: int, user2_id: int) -> bool:
        """
        Check if two users are blocked.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            
        Returns:
            True if either user has blocked the other
        """
        return self.repo.is_blocked(user1_id, user2_id)

    def login(self, username: str, password: str) -> UserRead | None:
        """
        Authenticate user login.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.repo.get_user_by_username(username)
        if not user:
            return None

        if not bcrypt.verify(password, user.password_hash):
            return None

        return UserRead.model_validate(user)
