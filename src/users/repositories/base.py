from abc import ABC, abstractmethod

from app.users.models import User
from app.users.schemas import UserCreate


class AbstractUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    def create(self, user: UserCreate) -> User:
        pass

    @abstractmethod
    def list_users(self) -> list[User]:
        pass

    @abstractmethod
    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        pass

    @abstractmethod
    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        pass

    @abstractmethod
    def is_blocked(self, user1_id: int, user2_id: int) -> bool:
        pass
