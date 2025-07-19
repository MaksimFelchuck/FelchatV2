from typing import Optional

from app.users.models import User
from app.users.repositories.base import AbstractUserRepository
from app.users.schemas import UserCreate


class UserRepositoryDB(AbstractUserRepository):
    def get_by_id(self, user_id: int) -> User | None:
        # TODO: Реализовать через SQLAlchemy
        pass

    def get_by_username(self, username: str) -> User | None:
        # TODO: Реализовать через SQLAlchemy
        pass

    def create(self, user: UserCreate) -> User:
        # TODO: Реализовать через SQLAlchemy
        pass

    def list_users(self) -> list[User]:
        # TODO: Реализовать через SQLAlchemy
        pass

    def block_user(self, user_id: int) -> None:
        # TODO: Реализовать через SQLAlchemy
        pass
