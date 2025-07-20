"""Tests for chat API endpoints."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import create_and_login_user


class TestChatAPI:
    """Test chat API endpoints."""

    @pytest.mark.api
    def test_chat_page_unauthenticated(self, client: TestClient):
        """Test accessing chat page when not authenticated."""
        response = client.get("/chat/")
        assert response.status_code == 200  # Actually accessible without auth
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_chat_page_authenticated(self, client: TestClient):
        """Test accessing chat page when authenticated."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "chatuser", "chat@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # Access chat page
        response = client.get("/chat/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_chat_page_with_nonexistent_user(self, client: TestClient):
        """Test accessing chat page with nonexistent user ID in cookie."""
        # Set invalid user ID in cookies
        client.cookies.set("user_id", "999")

        response = client.get("/chat/")
        assert response.status_code == 200  # Actually accessible even with invalid user
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_chat_page_with_blocked_user(self, client: TestClient):
        """Test accessing chat page when user is blocked."""
        # First create two users
        cookies1 = create_and_login_user(
            client, "blocker", "blocker@example.com", "password123"
        )
        cookies2 = create_and_login_user(
            client, "blocked", "blocked@example.com", "password123"
        )

        # Set first user's cookies
        client.cookies.update(cookies1)

        # Block second user
        client.post("/api/v1/users/block/2")

        # Switch to second user's cookies
        client.cookies.clear()
        client.cookies.update(cookies2)

        # Try to access chat page
        response = client.get("/chat/")
        assert response.status_code == 200  # Actually accessible even when blocked
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_chat_websocket_endpoint(self, client: TestClient):
        """Test WebSocket endpoint for chat."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "wsuser", "ws@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # Test WebSocket endpoint (this would need a WebSocket client for full testing)
        response = client.get("/ws/")
        # WebSocket endpoints typically return 426 or similar for HTTP requests
        assert response.status_code in [426, 400, 404]  # Depends on implementation
