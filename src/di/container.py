"""Dependency injection container for the application."""

from dependency_injector import containers, providers

from src.chat.repositories.db.chat import ChatRepositoryDB
from src.chat.repositories.inmem.chat import ChatRepositoryInMemory
from src.chat.ws_service import ChatWebSocketService
from src.config import settings
from src.users.repositories.user_repo_db import UserRepositoryDB
from src.users.repositories.inmem.user import UserRepositoryInMemory
from src.users.services import UserService
from src.db.session import SessionLocal


class Container(containers.DeclarativeContainer):
    """DI container with configuration and repository providers."""

    config = providers.Configuration()

    # Database session provider
    db_session = providers.Factory(SessionLocal)

    # User repository - select based on environment
    user_repository = providers.Selector(
        config.env,
        prod=providers.Factory(UserRepositoryDB, db_session=db_session),
        test=providers.Singleton(UserRepositoryInMemory),
    )

    # User service
    user_service = providers.Factory(UserService, repo=user_repository)

    chat_repository = providers.Selector(
        config.env,
        prod=providers.Singleton(ChatRepositoryDB, redis_url=settings.redis_url),
        test=providers.Singleton(ChatRepositoryInMemory),
    )

    chat_service = providers.Singleton(
        ChatWebSocketService, redis_url=settings.redis_url, user_service=user_service
    )
