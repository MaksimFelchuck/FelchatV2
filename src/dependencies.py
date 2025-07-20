"""FastAPI dependency injection functions."""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.chat.ws_service import ChatWebSocketService
from src.users.services import UserService
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


def get_user_service(container=Depends(get_container)) -> UserService:
    """Get UserService instance from DI container."""
    return container.user_service()


def get_chat_service(container=Depends(get_container)) -> ChatWebSocketService:
    """Get ChatWebSocketService instance from DI container."""
    return container.chat_service()
