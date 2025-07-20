import pytest
import asyncio
import os
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from src.main import app
from src.di.container import Container
from src.users.services import UserService
from src.chat.ws_service import ChatWebSocketService


def create_and_login_user(client: TestClient, username: str, email: str, password: str):
    """Helper function to create a user and login via API."""
    # Create user
    user_data = {"username": username, "email": email, "password": password}
    register_response = client.post("/api/v1/users/register", json=user_data)
    assert register_response.status_code == 201

    # Login
    login_data = {"username": username, "password": password}
    login_response = client.post("/api/v1/users/login", json=login_data)
    assert login_response.status_code == 200

    # Return cookies for authenticated requests
    return login_response.cookies


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["ENV"] = "test"
    yield
    # Clean up
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
    if "ENV" in os.environ:
        del os.environ["ENV"]


@pytest.fixture
def container() -> Container:
    """Create a test container with automatic InMem repositories."""
    container = Container()
    # Configure the container for test environment
    container.config.env.override("test")
    return container


@pytest.fixture
def user_service(container: Container) -> UserService:
    """Create UserService with InMem repository."""
    return container.user_service()


@pytest.fixture
def chat_service(container: Container) -> ChatWebSocketService:
    """Create ChatWebSocketService with InMem repository."""
    return container.chat_service()


@pytest.fixture
def client(container: Container) -> TestClient:
    """Create test client with automatic InMem repositories."""
    # Override the global container in main.py
    import src.main

    original_container = src.main.container
    src.main.container = container

    with TestClient(app) as test_client:
        yield test_client

    # Restore original container
    src.main.container = original_container


@pytest.fixture
def sample_users():
    """Sample users for testing."""
    return [
        {
            "id": 1,
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "password123",
        },
        {
            "id": 2,
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "password456",
        },
        {
            "id": 3,
            "username": "testuser3",
            "email": "test3@example.com",
            "password": "password789",
        },
    ]


@pytest.fixture
def setup_users(user_service: UserService, sample_users):
    """Setup test users in the repository."""
    from src.users.schemas import UserCreate

    for user_data in sample_users:
        user_create = UserCreate(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
        )
        user_service.register(user_create)
    return sample_users
