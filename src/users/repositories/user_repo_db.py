"""Database implementation of user repository using SQLAlchemy."""

from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from src.users.repositories.abs.user import AbstractUserRepository
from src.users.models import User, UserBlock
from src.users.schemas import UserCreate

# Настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepositoryDB(AbstractUserRepository):
    """Database implementation of user repository."""
    
    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db_session = db_session

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    def create_user(self, user_data: UserCreate) -> User | None:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object or None if creation failed
        """
        try:
            # Хэшируем пароль
            hashed_password = self._hash_password(user_data.password)
            
            # Создаем пользователя
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=hashed_password
            )
            
            self.db_session.add(db_user)
            self.db_session.commit()
            self.db_session.refresh(db_user)
            
            return db_user
            
        except IntegrityError:
            # Пользователь с таким username или email уже существует
            self.db_session.rollback()
            return None
        except Exception:
            self.db_session.rollback()
            return None

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        return self.db_session.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> User | None:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None if not found
        """
        return self.db_session.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User object or None if not found
        """
        return self.db_session.query(User).filter(User.email == email).first()

    def list_users(self) -> list[User]:
        """
        Get list of all users.
        
        Returns:
            List of user objects
        """
        return self.db_session.query(User).all()

    def block_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Block a user.
        
        Args:
            blocker_id: ID of the user doing the blocking
            blocked_id: ID of the user being blocked
        """
        # Проверяем, что пользователи существуют
        blocker = self.get_user_by_id(blocker_id)
        blocked = self.get_user_by_id(blocked_id)
        
        if not blocker or not blocked or blocker_id == blocked_id:
            return
        
        # Проверяем, что блокировка еще не существует
        existing_block = self.db_session.query(UserBlock).filter(
            UserBlock.blocker_id == blocker_id,
            UserBlock.blocked_id == blocked_id
        ).first()
        
        if existing_block:
            return
        
        try:
            # Создаем блокировку
            user_block = UserBlock(
                blocker_id=blocker_id,
                blocked_id=blocked_id
            )
            
            self.db_session.add(user_block)
            self.db_session.commit()
            
        except IntegrityError:
            self.db_session.rollback()
        except Exception:
            self.db_session.rollback()

    def unblock_user(self, blocker_id: int, blocked_id: int) -> None:
        """
        Unblock a user.
        
        Args:
            blocker_id: ID of the user doing the unblocking
            blocked_id: ID of the user being unblocked
        """
        try:
            # Находим и удаляем блокировку
            user_block = self.db_session.query(UserBlock).filter(
                UserBlock.blocker_id == blocker_id,
                UserBlock.blocked_id == blocked_id
            ).first()
            
            if user_block:
                self.db_session.delete(user_block)
                self.db_session.commit()
                
        except Exception:
            self.db_session.rollback()

    def is_blocked(self, user1_id: int, user2_id: int) -> bool:
        """
        Check if two users are blocked.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            
        Returns:
            True if either user has blocked the other
        """
        # Проверяем блокировку в обе стороны
        block_exists = self.db_session.query(UserBlock).filter(
            ((UserBlock.blocker_id == user1_id) & (UserBlock.blocked_id == user2_id)) |
            ((UserBlock.blocker_id == user2_id) & (UserBlock.blocked_id == user1_id))
        ).first()
        
        return block_exists is not None

    def who_blocked_whom(self, user1_id: int, user2_id: int) -> tuple[int, int] | None:
        """
        Check who blocked whom between two users.
        
        Args:
            user1_id: ID of the first user
            user2_id: ID of the second user
            
        Returns:
            Tuple (blocker_id, blocked_id) if there's a block, None otherwise
        """
        # Check if user1 blocked user2
        block = self.db_session.query(UserBlock).filter(
            (UserBlock.blocker_id == user1_id) & (UserBlock.blocked_id == user2_id)
        ).first()
        if block:
            return (user1_id, user2_id)
        
        # Check if user2 blocked user1
        block = self.db_session.query(UserBlock).filter(
            (UserBlock.blocker_id == user2_id) & (UserBlock.blocked_id == user1_id)
        ).first()
        if block:
            return (user2_id, user1_id)
        
        return None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)
