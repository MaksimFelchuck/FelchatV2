"""Database implementation of user repository using SQLAlchemy."""

from sqlalchemy.exc import IntegrityError

from src.db.session import SessionLocal
from src.users.models import User, UserBlock
from src.users.repositories.abs.user import AbstractUserRepository
from src.users.schemas import UserCreate


class UserRepositoryDB(AbstractUserRepository):
    """SQLAlchemy-based implementation of user repository."""

    def __init__(self):
        """Initialize the database repository."""
        pass  # Убираем создание постоянной сессии

    def create_user(self, user_data: UserCreate) -> User | None:
        """
        Create a new user in the database.

        Args:
            user_data: User creation data

        Returns:
            Created user object or None if creation failed
        """
        with SessionLocal() as db:
            try:
                user = User(
                    username=user_data.username,
                    email=user_data.email,
                    password_hash=user_data.password,
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                return user
            except IntegrityError:
                db.rollback()
                return None

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID from database.

        Args:
            user_id: User ID

        Returns:
            User object or None if not found
        """
        with SessionLocal() as db:
            return db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> User | None:
        """
        Get user by username from database.

        Args:
            username: Username to search for

        Returns:
            User object or None if not found
        """
        with SessionLocal() as db:
            return db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email from database.

        Args:
            email: Email to search for

        Returns:
            User object or None if not found
        """
        with SessionLocal() as db:
            return db.query(User).filter(User.email == email).first()

    def list_users(self) -> list[User]:
        """
        Get list of all users from database.

        Returns:
            List of user objects
        """
        with SessionLocal() as db:
            return db.query(User).all()

    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Block a user in the database.

        Args:
            blocker_id: ID of the user doing the blocking
            blocked_id: ID of the user being blocked
        """
        with SessionLocal() as db:
            try:
                block = UserBlock(blocker_id=blocker_id, blocked_id=blocked_id)
                db.add(block)
                db.commit()
            except IntegrityError:
                db.rollback()

    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Unblock a user in the database.

        Args:
            blocker_id: ID of the user doing the unblocking
            blocked_id: ID of the user being unblocked
        """
        with SessionLocal() as db:
            # Удаляем блокировку в обе стороны
            db.query(UserBlock).filter(
                (
                    (UserBlock.blocker_id == blocker_id)
                    & (UserBlock.blocked_id == blocked_id)
                )
                | (
                    (UserBlock.blocker_id == blocked_id)
                    & (UserBlock.blocked_id == blocker_id)
                )
            ).delete()
            db.commit()

    def is_blocked(self, user1_id: int, user2_id: int) -> bool:
        """
        Check if two users are blocked in the database.

        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user

        Returns:
            True if either user has blocked the other
        """
        with SessionLocal() as db:
            return (
                db.query(UserBlock)
                .filter(
                    (
                        (UserBlock.blocker_id == user1_id)
                        & (UserBlock.blocked_id == user2_id)
                    )
                    | (
                        (UserBlock.blocker_id == user2_id)
                        & (UserBlock.blocked_id == user1_id)
                    )
                )
                .first()
                is not None
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
        with SessionLocal() as db:
            # Check if user1 blocked user2
            block = (
                db.query(UserBlock)
                .filter(
                    (UserBlock.blocker_id == user1_id)
                    & (UserBlock.blocked_id == user2_id)
                )
                .first()
            )
            if block:
                return (user1_id, user2_id)

            # Check if user2 blocked user1
            block = (
                db.query(UserBlock)
                .filter(
                    (UserBlock.blocker_id == user2_id)
                    & (UserBlock.blocked_id == user1_id)
                )
                .first()
            )
            if block:
                return (user2_id, user1_id)

            return None
