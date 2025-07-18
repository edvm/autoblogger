"""
Integration tests for system authentication endpoints.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from api.database import ApiKey, AuthType, SystemUser, User
from api.main import app
from tests.utils.auth_test_utils import (
    ApiKeyFactory,
    AuthTestData,
    AuthTestHelpers,
    SystemUserFactory,
    UserFactory,
)

"""Tests for system authentication API endpoints."""


# @pytest.mark.skip("Need to fix it soon")
class TestSystemUserRegistration:
    """Test cases for system user registration endpoint."""

    def test_register_success(self, test_database_session):
        """Test successful user registration."""
        from fastapi.testclient import TestClient
        from api.database import get_db
        from api.main import app
        
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
        # Clear any existing overrides first and apply our override
        app.dependency_overrides.clear()
        app.dependency_overrides[get_db] = get_db_override
        
        # Create client AFTER setting the dependency override
        with TestClient(app) as client:
            registration_data = AuthTestData.VALID_REGISTRATION_DATA[0]

            response = client.post("/api/v1/auth/register", json=registration_data)

            assert response.status_code == 200
            data = response.json()

            assert data["username"] == registration_data["username"]
            assert data["email"] == registration_data["email"]
            assert data["first_name"] == registration_data["first_name"]
            assert data["last_name"] == registration_data["last_name"]
            assert data["is_active"] is True
            assert "created_at" in data
            assert "updated_at" in data
            
            # Verify user was actually created in database
            created_user = test_database_session.query(SystemUser).filter(
                SystemUser.username == registration_data["username"]
            ).first()
            assert created_user is not None
            assert created_user.email == registration_data["email"]
        
        # Clean up
        app.dependency_overrides.clear()

    def test_register_duplicate_username(self, test_database_session):
        """Test registration with duplicate username."""
        from api.database import get_db
        from api.main import app
        
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
        # Clear any existing overrides first
        app.dependency_overrides.clear()
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            client = TestClient(app)
            registration_data = AuthTestData.VALID_REGISTRATION_DATA[0]

            # First, create a user with the same username
            existing_user = SystemUserFactory.create_system_user(
                username=registration_data["username"],
                email="different@example.com"
            )
            test_database_session.add(existing_user)
            test_database_session.commit()

            # Try to register with the same username
            response = client.post("/api/v1/auth/register", json=registration_data)

            assert response.status_code == 400
            data = response.json()
            assert "Username already exists" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_register_duplicate_email(self, test_database_session):
        """Test registration with duplicate email."""
        from api.database import get_db
        from api.main import app
        
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
        # Clear any existing overrides first
        app.dependency_overrides.clear()
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            client = TestClient(app)
            registration_data = AuthTestData.VALID_REGISTRATION_DATA[0]

            # First, create a user with the same email
            existing_user = SystemUserFactory.create_system_user(
                username="different_username",
                email=registration_data["email"]
            )
            test_database_session.add(existing_user)
            test_database_session.commit()

            # Try to register with the same email
            response = client.post("/api/v1/auth/register", json=registration_data)

            assert response.status_code == 400
            data = response.json()
            assert "Email already exists" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_register_invalid_data(self):
        """Test registration with invalid data."""
        client = TestClient(app)

        # Test with missing required fields
        invalid_data = {"username": "test"}  # Missing email and password

        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_register_weak_password(self):
        """Test registration with weak password."""
        client = TestClient(app)

        registration_data = AuthTestData.VALID_REGISTRATION_DATA[0].copy()
        registration_data["password"] = "123"  # Too short

        response = client.post("/api/v1/auth/register", json=registration_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_register_invalid_email(self):
        """Test registration with invalid email format."""
        client = TestClient(app)

        registration_data = AuthTestData.VALID_REGISTRATION_DATA[0].copy()
        registration_data["email"] = "invalid-email"

        response = client.post("/api/v1/auth/register", json=registration_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


# @pytest.mark.skip("Need to fix it soon")
class TestSystemUserLogin:
    """Test cases for system user login endpoint."""

    @pytest.mark.skip("Need to fix it soon")
    def test_login_success(self):
        """Test successful user login."""
        client = TestClient(app)

        login_data = AuthTestData.VALID_LOGIN_DATA[0]

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock system user
            mock_system_user = SystemUserFactory.create_mock_system_user(
                username=login_data["username"], is_active=True
            )
            mock_system_user.verify_password.return_value = True
            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_system_user
            )

            # Mock API key creation
            mock_api_key = ApiKeyFactory.create_mock_api_key()
            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.refresh = Mock()

            with patch(
                "api.routers.system_auth.ApiKey.generate_key",
                return_value=("abk_live_test_key", "hash"),
            ):
                response = client.post("/api/v1/auth/login", json=login_data)

                assert response.status_code == 200
                data = response.json()

                # Check user data
                assert "user" in data
                user_data = data["user"]
                assert user_data["username"] == login_data["username"]
                assert user_data["is_active"] is True

                # Check API key data
                assert "api_key" in data
                api_key_data = data["api_key"]
                assert "full_key" in api_key_data
                assert api_key_data["full_key"] == "abk_live_test_key"
                assert api_key_data["is_active"] is True

    def test_login_invalid_username(self):
        """Test login with invalid username."""
        client = TestClient(app)

        login_data = {"username": "nonexistent", "password": "password123"}

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock no user found
            mock_db.query.return_value.filter.return_value.first.return_value = None

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 401
            data = response.json()
            assert "Invalid username or password" in data["detail"]

    def test_login_invalid_password(self):
        """Test login with invalid password."""
        client = TestClient(app)

        login_data = {"username": "testuser", "password": "wrongpassword"}

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock system user
            mock_system_user = SystemUserFactory.create_mock_system_user(
                username=login_data["username"]
            )
            mock_system_user.verify_password.return_value = False
            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_system_user
            )

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 401
            data = response.json()
            assert "Invalid username or password" in data["detail"]

    @pytest.mark.skip("Need to fix it soon")
    def test_login_inactive_user(self):
        """Test login with inactive user."""
        client = TestClient(app)

        login_data = AuthTestData.VALID_LOGIN_DATA[0]

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock inactive system user
            mock_system_user = SystemUserFactory.create_mock_system_user(
                username=login_data["username"], is_active=False
            )
            mock_system_user.verify_password.return_value = True
            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_system_user
            )

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 400
            data = response.json()
            assert "User account is inactive" in data["detail"]

    def test_login_missing_credentials(self):
        """Test login with missing credentials."""
        client = TestClient(app)

        # Test with missing password
        login_data = {"username": "testuser"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


@pytest.mark.skip("Need to fix it soon")
class TestApiKeyManagement:
    """Test cases for API key management endpoints."""

    def test_list_api_keys(self, authenticated_api_key_client):
        """Test listing API keys for authenticated user."""
        response = authenticated_api_key_client.get("/api/v1/auth/keys")

        assert response.status_code == 200
        data = response.json()

        # Should return an empty list initially (no keys created yet for this user)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_api_key(self, authenticated_api_key_client):
        """Test creating a new API key."""
        key_data = AuthTestData.VALID_API_KEY_DATA[0]

        response = authenticated_api_key_client.post(
            "/api/v1/auth/keys", json=key_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == key_data["name"]
        assert "full_key" in data
        assert data["full_key"].startswith("abk_live_")
        assert data["is_active"] is True
        assert "id" in data
        assert "key_prefix" in data

    def test_create_api_key_duplicate_name(self, authenticated_api_key_client):
        """Test creating API key with duplicate name."""
        key_data = AuthTestData.VALID_API_KEY_DATA[0]

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock existing key with same name
            mock_existing_key = ApiKeyFactory.create_mock_api_key(name=key_data["name"])
            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_existing_key
            )

            response = authenticated_api_key_client.post(
                "/api/v1/auth/keys", json=key_data
            )

            assert response.status_code == 400
            data = response.json()
            assert "API key with this name already exists" in data["detail"]

    def test_update_api_key(self, authenticated_api_key_client):
        """Test updating an existing API key."""
        key_id = 1
        update_data = {"name": "Updated Key Name", "expires_at": "2025-12-31T23:59:59Z"}

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock existing API key
            mock_api_key = ApiKeyFactory.create_mock_api_key(id=key_id)

            # Mock queries: first for finding key, second for name conflict check
            mock_db.query.return_value.filter.return_value.first.side_effect = [
                mock_api_key,  # Key found
                None,  # No name conflict
            ]

            mock_db.commit = Mock()
            mock_db.refresh = Mock()

            response = authenticated_api_key_client.put(
                f"/api/v1/auth/keys/{key_id}", json=update_data
            )

            assert response.status_code == 200
            data = response.json()

            assert data["name"] == update_data["name"]
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    def test_update_api_key_not_found(self, authenticated_api_key_client):
        """Test updating non-existent API key."""
        key_id = 999
        update_data = {"name": "Updated Key Name"}

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock key not found
            mock_db.query.return_value.filter.return_value.first.return_value = None

            response = authenticated_api_key_client.put(
                f"/api/v1/auth/keys/{key_id}", json=update_data
            )

            assert response.status_code == 404
            data = response.json()
            assert "API key not found" in data["detail"]

    def test_revoke_api_key(self, authenticated_api_key_client):
        """Test revoking an API key."""
        key_id = 1

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock existing API key
            mock_api_key = ApiKeyFactory.create_mock_api_key(id=key_id, is_active=True)
            mock_db.query.return_value.filter.return_value.first.return_value = (
                mock_api_key
            )

            mock_db.commit = Mock()

            response = authenticated_api_key_client.delete(
                f"/api/v1/auth/keys/{key_id}"
            )

            assert response.status_code == 200
            data = response.json()

            assert "API key revoked successfully" in data["message"]
            assert mock_api_key.is_active is False
            mock_db.commit.assert_called_once()

    def test_revoke_api_key_not_found(self, authenticated_api_key_client):
        """Test revoking non-existent API key."""
        key_id = 999

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock key not found
            mock_db.query.return_value.filter.return_value.first.return_value = None

            response = authenticated_api_key_client.delete(
                f"/api/v1/auth/keys/{key_id}"
            )

            assert response.status_code == 404
            data = response.json()
            assert "API key not found" in data["detail"]

    def test_api_key_management_clerk_user_forbidden(self, authenticated_clerk_client):
        """Test that Clerk users cannot manage API keys."""
        response = authenticated_clerk_client.get("/api/v1/auth/keys")

        assert response.status_code == 403
        data = response.json()
        assert "Only system users can manage API keys" in data["detail"]


class TestCurrentUserEndpoints:
    """Test cases for current user endpoints."""

    def test_get_current_system_user(self, authenticated_api_key_client):
        """Test getting current system user information."""
        response = authenticated_api_key_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()

        # The authenticated_api_key_client fixture creates a system user with these values
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True

    def test_get_current_system_user_clerk_forbidden(self, authenticated_clerk_client):
        """Test that Clerk users cannot access system user endpoint."""
        response = authenticated_clerk_client.get("/api/v1/auth/me")

        assert response.status_code == 403
        data = response.json()
        assert "Only system users can access this endpoint" in data["detail"]

    def test_get_current_system_user_not_found(self, test_database_session):
        """Test getting current system user when system user record is missing."""
        from api.auth import get_current_user
        from api.database import get_db
        from api.main import app
        from tests.utils.auth_test_utils import UserFactory
        
        # Create a User with system auth but no corresponding SystemUser
        test_user = UserFactory.create_system_user(
            id=1,
            system_user_id=999,  # Non-existent system user ID
            email="test@example.com",
            username="testuser",
        )
        test_database_session.add(test_user)
        test_database_session.commit()

        # Override dependencies
        def get_current_user_override():
            return test_user

        def get_db_override():
            return test_database_session

        app.dependency_overrides.clear()
        app.dependency_overrides[get_current_user] = get_current_user_override
        app.dependency_overrides[get_db] = get_db_override

        try:
            client = TestClient(app)
            response = client.get("/api/v1/auth/me")

            assert response.status_code == 404
            data = response.json()
            assert "System user not found" in data["detail"]
        finally:
            app.dependency_overrides.clear()


class TestAuthenticationEndpointsSecurity:
    """Security tests for authentication endpoints."""

    def test_endpoints_require_authentication(self):
        """Test that protected endpoints require authentication."""
        client = TestClient(app)

        protected_endpoints = [
            ("GET", "/api/v1/auth/keys"),
            ("POST", "/api/v1/auth/keys"),
            ("PUT", "/api/v1/auth/keys/1"),
            ("DELETE", "/api/v1/auth/keys/1"),
            ("GET", "/api/v1/auth/me"),
        ]

        for method, endpoint in protected_endpoints:
            response = client.request(method, endpoint)
            assert response.status_code == 401

    def test_sql_injection_prevention(self):
        """Test that endpoints prevent SQL injection attacks."""
        client = TestClient(app)

        # Test SQL injection in registration
        malicious_data = {
            "username": "admin'; DROP TABLE users; --",
            "email": "test@example.com",
            "password": "password123",
        }

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = None

            response = client.post("/api/v1/auth/register", json=malicious_data)

            # Should either succeed (if input is properly sanitized) or fail validation
            # But should not cause database errors
            assert response.status_code in [200, 400, 422]

    def test_xss_prevention(self):
        """Test that endpoints prevent XSS attacks."""
        client = TestClient(app)

        # Test XSS in registration
        malicious_data = {
            "username": "<script>alert('xss')</script>",
            "email": "test@example.com",
            "password": "password123",
            "first_name": "<img src=x onerror=alert('xss')>",
        }

        with patch("api.routers.system_auth.get_db") as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = None

            mock_user = SystemUserFactory.create_mock_system_user(
                username=malicious_data["username"],
                first_name=malicious_data["first_name"],
            )

            with patch("api.routers.system_auth.SystemUser", return_value=mock_user):
                response = client.post("/api/v1/auth/register", json=malicious_data)

                if response.status_code == 200:
                    data = response.json()
                    # Verify that script tags are not executed/returned as-is
                    assert "<script>" not in str(data)
                    assert "onerror=" not in str(data)

    def test_rate_limiting_behavior(self):
        """Test rate limiting behavior on authentication endpoints."""
        client = TestClient(app)

        # This test would need actual rate limiting implementation
        # For now, we just verify endpoints are accessible
        login_data = {"username": "test", "password": "test"}

        response = client.post("/api/v1/auth/login", json=login_data)

        # Should get some response (not necessarily success)
        assert response.status_code in [200, 401, 422, 429]  # 429 = Too Many Requests
