from typing import Optional

from src.users.repositories.abs.user_repo import AbstractUserRepository
from src.users.models.user import User


class UserRepositoryFake(AbstractUserRepository):
    """Fake user repository implementation for testing."""
    
    def __init__(self):
        """Initialize fake repository with sample data."""
        self.users = [
            User(id=1, username="alice", email="alice@example.com", hashed_password="fake_hash_1"),
            User(id=2, username="bob", email="bob@example.com", hashed_password="fake_hash_2"),
            User(id=3, username="charlie", email="charlie@example.com", hashed_password="fake_hash_3"),
        ]
        self.next_id = 4

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return next((user for user in self.users if user.id == user_id), None)

    async def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return next((user for user in self.users if user.username == username), None)

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return next((user for user in self.users if user.email == email), None)

    async def create_user(self, username: str, email: str, hashed_password: str) -> User:
        """Create a new user."""
        user = User(
            id=self.next_id,
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.users.append(user)
        self.next_id += 1
        return user

    async def get_all_users(self) -> list[User]:
        """Get all users."""
        return self.users.copy()
