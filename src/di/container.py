"""Dependency injection container for the application."""

import os

from dependency_injector import containers, providers

from src.chat.repositories.db.chat import ChatRepositoryDB
from src.chat.repositories.inmem.chat import ChatRepositoryInMemory
from src.chat.ws_service import ChatWebSocketService
from src.users.repositories.db.user import UserRepositoryDB
from src.users.repositories.inmem.user import UserRepositoryInMemory


class Container(containers.DeclarativeContainer):
    """DI container with configuration and user/chat repository selector."""
    
    config = providers.Configuration()
    user_repository = providers.Selector(
        config.env,
        prod=providers.Singleton(UserRepositoryDB),
        test=providers.Singleton(UserRepositoryInMemory),
    )
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
