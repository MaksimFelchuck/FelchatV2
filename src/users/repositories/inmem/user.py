"""In-memory implementation of user repository for testing."""

from src.users.models import User, UserBlock
from src.users.repositories.abs.user import AbstractUserRepository
from src.users.schemas import UserCreate


class UserRepositoryInMemory(AbstractUserRepository):
    """In-memory implementation of user repository for testing."""
    
    def __init__(self):
        """Initialize the in-memory repository."""
        self.users = {}
        self.blocks = {}
        self._next_id = 1

    def create_user(self, user_data: UserCreate) -> User | None:
        """
        Create a new user in memory.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object or None if creation failed
        """
        # Check for existing username or email
        for user in self.users.values():
            if user.username == user_data.username or user.email == user_data.email:
                return None
        
        # For testing, we'll use the password as the hash
        # In production, this should be properly hashed
        user = User(
            id=self._next_id,
            username=user_data.username,
            email=user_data.email,
            password_hash=user_data.password  # Store password as hash for testing
        )
        self.users[user.id] = user
        self._next_id += 1
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID from memory.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        """
        Get user by username from memory.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email from memory.
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def list_users(self) -> list[User]:
        """
        Get list of all users from memory.
        
        Returns:
            List of user objects
        """
        return list(self.users.values())

    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Block a user in memory.
        
        Args:
            blocker_id: ID of the user doing the blocking
            blocked_id: ID of the user being blocked
        """
        block_key = (blocker_id, blocked_id)
        if block_key not in self.blocks:
            block = UserBlock(
                id=len(self.blocks) + 1,
                blocker_id=blocker_id,
                blocked_id=blocked_id
            )
            self.blocks[block_key] = block

    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Unblock a user in memory.
        
        Args:
            blocker_id: ID of the user doing the unblocking
            blocked_id: ID of the user being unblocked
        """
        block_key = (blocker_id, blocked_id)
        if block_key in self.blocks:
            del self.blocks[block_key]

    def is_blocked(self, user1_id: int, user2_id: int) -> bool:
        """
        Check if two users are blocked in memory.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            
        Returns:
            True if either user has blocked the other
        """
        return (
            (user1_id, user2_id) in self.blocks or 
            (user2_id, user1_id) in self.blocks
        )

    def who_blocked_whom(self, user1_id: int, user2_id: int) -> tuple[int, int] | None:
        """
        Check who blocked whom between two users.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            
        Returns:
            Tuple (blocker_id, blocked_id) if there's a block, None otherwise
        """
        if (user1_id, user2_id) in self.blocks:
            return (user1_id, user2_id)
        elif (user2_id, user1_id) in self.blocks:
            return (user2_id, user1_id)
        return None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash (simple comparison for testing).
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches
        """
        # For testing purposes, we'll do a simple comparison
        # In production, this should use proper password hashing
        return plain_password == hashed_password
