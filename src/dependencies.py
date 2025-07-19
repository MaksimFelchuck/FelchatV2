"""FastAPI dependency injection functions."""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from src.chat.ws_service import ChatWebSocketService
from src.users.services import UserService
from src.users.repositories.user_repo_db import UserRepositoryDB
from src.db.session import SessionLocal


def get_container():
    """Get the global DI container."""
    from src.main import container
    return container


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency with automatic cleanup.
    
    Yields:
        Database session that will be automatically closed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get UserService instance with PostgreSQL database session."""
    repo = UserRepositoryDB(db_session=db)
    return UserService(repo=repo)


def get_chat_service(container=Depends(get_container)) -> ChatWebSocketService:
    """Get ChatWebSocketService instance from DI container."""
    return container.chat_service() 