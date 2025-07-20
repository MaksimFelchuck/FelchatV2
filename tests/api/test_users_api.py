"""Tests for user API endpoints (JSON responses)."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import create_and_login_user


class TestUsersAPI:
    """Test user API endpoints."""

    @pytest.mark.api
    def test_register_user_success(self, client: TestClient):
        """Test successful user registration via API."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }

        response = client.post("/api/v1/users/register", json=user_data)

        assert response.status_code == 201  # API returns 201 for creation
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data  # Password should not be returned

    @pytest.mark.api
    def test_register_user_duplicate(self, client: TestClient):
        """Test registration with duplicate username via API."""
        user_data = {
            "username": "duplicateuser",
            "email": "duplicate@example.com",
            "password": "password123",
        }

        # First registration
        response1 = client.post("/api/v1/users/register", json=user_data)
        assert response1.status_code == 201

        # Second registration with same username
        response2 = client.post("/api/v1/users/register", json=user_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    @pytest.mark.api
    def test_login_user_success(self, client: TestClient):
        """Test successful user login via API."""
        # First register a user
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123",
        }
        client.post("/api/v1/users/register", json=user_data)

        # Then login
        login_data = {"username": "loginuser", "password": "password123"}
        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "loginuser"
        assert "user_id" in response.cookies

    @pytest.mark.api
    def test_login_user_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials via API."""
        login_data = {"username": "nonexistent", "password": "wrongpassword"}
        response = client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    @pytest.mark.api
    def test_logout_user(self, client: TestClient):
        """Test user logout via API."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "logoutuser", "logout@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # Then logout
        response = client.post("/api/v1/users/logout")
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]

    @pytest.mark.api
    def test_get_user_info_authenticated(self, client: TestClient):
        """Test getting user info when authenticated via API."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "infouser", "info@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # Get user info
        response = client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "infouser"
        assert data["email"] == "info@example.com"

    @pytest.mark.api
    def test_get_user_info_unauthenticated(self, client: TestClient):
        """Test getting user info when not authenticated via API."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.api
    def test_list_users(self, client: TestClient):
        """Test getting list of all users via API."""
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.api
    def test_block_user_success(self, client: TestClient):
        """Test successful user blocking via API."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "blocker", "blocker@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # Block user (assuming user ID 2 exists from setup)
        response = client.post("/api/v1/users/block/2")
        assert response.status_code == 200
        assert "User blocked successfully" in response.json()["message"]

    @pytest.mark.api
    def test_block_user_unauthenticated(self, client: TestClient):
        """Test blocking user when not authenticated via API."""
        response = client.post("/api/v1/users/block/2")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.api
    def test_unblock_user_success(self, client: TestClient):
        """Test successful user unblocking via API."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "unblocker", "unblocker@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # First block user
        client.post("/api/v1/users/block/2")

        # Then unblock (uses DELETE method)
        response = client.delete("/api/v1/users/block/2")
        assert response.status_code == 200
        assert "User unblocked successfully" in response.json()["message"]

    @pytest.mark.api
    def test_unblock_user_unauthenticated(self, client: TestClient):
        """Test unblocking user when not authenticated via API."""
        response = client.delete("/api/v1/users/block/2")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
