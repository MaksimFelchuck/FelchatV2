"""Dependency injection container for the application."""

import os

from dependency_injector import containers, providers

from src.chat.repositories.db.chat import ChatRepositoryDB
from src.chat.repositories.inmem.chat import ChatRepositoryInMemory
from src.chat.ws_service import ChatWebSocketService
from src.users.repositories.user_repo_db import UserRepositoryDB
from src.db.session import SessionLocal


class Container(containers.DeclarativeContainer):
    """DI container with configuration and repository providers."""
    
    config = providers.Configuration()
    
    # Database session provider
    db_session = providers.Factory(SessionLocal)
    
    # User repository - always PostgreSQL
    user_repository = providers.Factory(UserRepositoryDB, db_session=db_session)
    
    chat_repository = providers.Selector(
        config.env,
        prod=providers.Singleton(
            ChatRepositoryDB, 
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0")
        ),
        test=providers.Singleton(ChatRepositoryInMemory),
    )
    
    chat_service = providers.Singleton(
        ChatWebSocketService, 
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
