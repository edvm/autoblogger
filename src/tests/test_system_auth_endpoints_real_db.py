"""
Integration tests for system authentication endpoints using real database.
"""

import pytest
from fastapi.testclient import TestClient

from api.database import ApiKey, AuthType, SystemUser, User, get_db
from api.main import app
from tests.utils.auth_test_utils import (
    ApiKeyFactory,
    AuthTestData,
    SystemUserFactory,
    UserFactory,
)


@pytest.mark.skip("Need to fix it soon")
class TestSystemUserRegistrationRealDB:
    """Test cases for system user registration endpoint with real database."""

    def test_register_success(self, test_database_engine):
        """Test successful user registration."""
        from sqlalchemy.orm import sessionmaker
        
        # Create a session from the test engine
        TestSession = sessionmaker(bind=test_database_engine)
        test_session = TestSession()
        
        # Override the get_db dependency with our test database session
        def get_db_override():
            try:
                yield test_session
            finally:
                pass  # Don't close here, we'll close it later
        
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            client = TestClient(app)
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
            created_user = test_session.query(SystemUser).filter(
                SystemUser.username == registration_data["username"]
            ).first()
            assert created_user is not None
            assert created_user.email == registration_data["email"]
        finally:
            test_session.close()
            app.dependency_overrides.clear()

    def test_register_duplicate_username(self, test_database_session):
        """Test registration with duplicate username."""
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
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
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
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


@pytest.mark.skip("Need to fix it soon")
class TestSystemUserLoginRealDB:
    """Test cases for system user login endpoint with real database."""

    def test_login_success(self, test_database_session):
        """Test successful user login."""
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            client = TestClient(app)
            
            # Create a real system user
            password = "testpassword123"
            system_user = SystemUserFactory.create_system_user(
                username="testuser",
                email="test@example.com",
                password=password,
                is_active=True
            )
            test_database_session.add(system_user)
            test_database_session.commit()

            login_data = {"username": "testuser", "password": password}
            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 200
            data = response.json()

            # Check user data
            assert "user" in data
            user_data = data["user"]
            assert user_data["username"] == "testuser"
            assert user_data["is_active"] is True

            # Check API key data
            assert "api_key" in data
            api_key_data = data["api_key"]
            assert "full_key" in api_key_data
            assert api_key_data["full_key"].startswith("abk_live_")
            assert api_key_data["is_active"] is True
            
            # Verify API key was created in database
            created_api_key = test_database_session.query(ApiKey).filter(
                ApiKey.system_user_id == system_user.id
            ).first()
            assert created_api_key is not None
            assert created_api_key.is_active is True
        finally:
            app.dependency_overrides.clear()

    def test_login_invalid_username(self, test_database_session):
        """Test login with invalid username."""
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            client = TestClient(app)
            login_data = {"username": "nonexistent", "password": "password123"}

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 401
            data = response.json()
            assert "Invalid credentials" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_login_invalid_password(self, test_database_session):
        """Test login with invalid password."""
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            client = TestClient(app)
            
            # Create a real system user
            system_user = SystemUserFactory.create_system_user(
                username="testuser",
                email="test@example.com",
                password="correctpassword",
                is_active=True
            )
            test_database_session.add(system_user)
            test_database_session.commit()

            login_data = {"username": "testuser", "password": "wrongpassword"}
            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 401
            data = response.json()
            assert "Invalid credentials" in data["detail"]
        finally:
            app.dependency_overrides.clear()

    def test_login_inactive_user(self, test_database_session):
        """Test login with inactive user."""
        # Override the get_db dependency with our test database session
        def get_db_override():
            return test_database_session
        
        app.dependency_overrides[get_db] = get_db_override
        
        try:
            client = TestClient(app)
            
            # Create an inactive system user
            password = "testpassword123"
            system_user = SystemUserFactory.create_system_user(
                username="testuser",
                email="test@example.com",
                password=password,
                is_active=False  # Inactive user
            )
            test_database_session.add(system_user)
            test_database_session.commit()

            login_data = {"username": "testuser", "password": password}
            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 400
            data = response.json()
            assert "User account is inactive" in data["detail"]
        finally:
            app.dependency_overrides.clear()


@pytest.mark.skip("Need to fix it soon")
class TestApiKeyManagementRealDB:
    """Test cases for API key management endpoints with real database."""

    def test_list_api_keys(self, authenticated_api_key_client):
        """Test listing API keys for authenticated user."""
        response = authenticated_api_key_client.get("/api/v1/auth/api-keys")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_api_key(self, test_database_session):
        """Test creating a new API key."""
        # Create a system user and authenticate
        system_user = SystemUserFactory.create_system_user(
            id=1,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )
        test_database_session.add(system_user)
        test_database_session.commit()

        user = UserFactory.create_system_user(
            id=1,
            system_user_id=system_user.id,
            email="test@example.com",
            username="testuser",
        )
        test_database_session.add(user)
        test_database_session.commit()

        # Override dependencies
        def get_current_user_override():
            return user

        def get_db_override():
            return test_database_session

        app.dependency_overrides[get_current_user] = get_current_user_override
        app.dependency_overrides[get_db] = get_db_override

        try:
            from api.auth import get_current_user
            client = TestClient(app)

            api_key_data = {"name": "Test API Key"}
            response = client.post("/api/v1/auth/api-keys", json=api_key_data)

            assert response.status_code == 200
            data = response.json()
            assert "full_key" in data
            assert data["full_key"].startswith("abk_live_")
            assert data["name"] == "Test API Key"
            assert data["is_active"] is True
            
            # Verify API key was created in database
            created_api_key = test_database_session.query(ApiKey).filter(
                ApiKey.system_user_id == system_user.id,
                ApiKey.name == "Test API Key"
            ).first()
            assert created_api_key is not None
        finally:
            app.dependency_overrides.clear()


@pytest.mark.skip("Need to fix it soon")
class TestCurrentUserEndpointsRealDB:
    """Test cases for current user endpoints with real database."""

    def test_get_current_system_user(self, test_database_session):
        """Test getting current system user information."""
        # Create a system user
        system_user = SystemUserFactory.create_system_user(
            id=1,
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )
        test_database_session.add(system_user)
        test_database_session.commit()

        user = UserFactory.create_system_user(
            id=1,
            system_user_id=system_user.id,
            email="test@example.com",
            username="testuser",
        )
        test_database_session.add(user)
        test_database_session.commit()

        # Override dependencies
        def get_current_user_override():
            return user

        def get_db_override():
            return test_database_session

        app.dependency_overrides[get_current_user] = get_current_user_override
        app.dependency_overrides[get_db] = get_db_override

        try:
            from api.auth import get_current_user
            client = TestClient(app)

            response = client.get("/api/v1/auth/me")

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"
            assert data["email"] == "test@example.com"
            assert data["is_active"] is True
        finally:
            app.dependency_overrides.clear()