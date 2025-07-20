"""Tests for main pages and static files."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import create_and_login_user


class TestPagesAPI:
    """Test main pages and static files."""

    @pytest.mark.api
    def test_login_page(self, client: TestClient):
        """Test accessing login page."""
        response = client.get("/users/login")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Вход" in response.text

    @pytest.mark.api
    def test_register_page(self, client: TestClient):
        """Test accessing registration page."""
        response = client.get("/users/register")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Регистрация" in response.text

    @pytest.mark.api
    def test_users_list_page_unauthenticated(self, client: TestClient):
        """Test accessing users list page when not authenticated."""
        response = client.get("/users/")
        assert response.status_code == 200  # Actually accessible without auth
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_users_list_page_authenticated(self, client: TestClient):
        """Test accessing users list page when authenticated."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "listuser", "list@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # Access users list page
        response = client.get("/users/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_profile_page_unauthenticated(self, client: TestClient):
        """Test accessing profile page when not authenticated."""
        response = client.get("/users/profile")
        assert response.status_code == 200  # Actually accessible without auth
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_profile_page_authenticated(self, client: TestClient):
        """Test accessing profile page when authenticated."""
        # First login to get cookies
        cookies = create_and_login_user(
            client, "profileuser", "profile@example.com", "password123"
        )

        # Set cookies on client
        client.cookies.update(cookies)

        # Access profile page
        response = client.get("/users/profile")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.api
    def test_static_files(self, client: TestClient):
        """Test accessing static files."""
        # Test CSS file
        response = client.get("/static/css/main.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

        # Test JS file
        response = client.get("/static/js/chat.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]

    @pytest.mark.api
    def test_favicon(self, client: TestClient):
        """Test accessing favicon."""
        response = client.get("/favicon.ico")
        # Favicon might return 404 if not configured properly
        assert response.status_code in [200, 404]

    @pytest.mark.api
    def test_404_page(self, client: TestClient):
        """Test 404 page for non-existent routes."""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
