"""
Authentication test utilities for AutoBlogger backend tests.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from unittest.mock import Mock

from api.database import SystemUser, ApiKey, User, AuthType

"""Test utilities for authentication system."""


class SystemUserFactory:
    """Factory for creating test SystemUser objects."""
    
    @staticmethod
    def create_system_user(
        id: int = 1,
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "testpassword123",
        first_name: str = "Test",
        last_name: str = "User",
        is_active: bool = True,
        **kwargs
    ) -> SystemUser:
        """Create a SystemUser for testing."""
        system_user = SystemUser(
            id=id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            **kwargs
        )
        system_user.set_password(password)
        return system_user

    @staticmethod
    def create_mock_system_user(
        id: int = 1,
        username: str = "testuser",
        email: str = "test@example.com",
        password_hash: str = "hashed_password",
        first_name: str = "Test",
        last_name: str = "User",
        is_active: bool = True,
        **kwargs
    ) -> Mock:
        """Create a mock SystemUser for testing."""
        mock_user = Mock(spec=SystemUser)
        mock_user.id = id
        mock_user.username = username
        mock_user.email = email
        mock_user.password_hash = password_hash
        mock_user.first_name = first_name
        mock_user.last_name = last_name
        mock_user.is_active = is_active
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()
        
        # Mock methods
        mock_user.set_password = Mock()
        mock_user.verify_password = Mock(return_value=True)
        
        # Apply any additional kwargs
        for key, value in kwargs.items():
            setattr(mock_user, key, value)
        
        return mock_user


class ApiKeyFactory:
    """Factory for creating test ApiKey objects."""
    
    @staticmethod
    def create_api_key(
        id: int = 1,
        system_user_id: int = 1,
        name: str = "Test API Key",
        key_hash: str = "test_key_hash",
        key_prefix: str = "abk_live_test",
        is_active: bool = True,
        last_used_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        **kwargs
    ) -> ApiKey:
        """Create an ApiKey for testing."""
        return ApiKey(
            id=id,
            system_user_id=system_user_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            is_active=is_active,
            last_used_at=last_used_at,
            expires_at=expires_at,
            **kwargs
        )

    @staticmethod
    def create_mock_api_key(
        id: int = 1,
        system_user_id: int = 1,
        name: str = "Test API Key",
        key_hash: str = "test_key_hash",
        key_prefix: str = "abk_live_test",
        is_active: bool = True,
        last_used_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        **kwargs
    ) -> Mock:
        """Create a mock ApiKey for testing."""
        mock_key = Mock(spec=ApiKey)
        mock_key.id = id
        mock_key.system_user_id = system_user_id
        mock_key.name = name
        mock_key.key_hash = key_hash
        mock_key.key_prefix = key_prefix
        mock_key.is_active = is_active
        mock_key.last_used_at = last_used_at
        mock_key.expires_at = expires_at
        mock_key.created_at = datetime.utcnow()
        mock_key.updated_at = datetime.utcnow()
        
        # Mock methods
        mock_key.is_expired = Mock(return_value=False)
        mock_key.update_last_used = Mock()
        mock_key.get_prefix = Mock(return_value=key_prefix)
        
        # Apply any additional kwargs
        for key, value in kwargs.items():
            setattr(mock_key, key, value)
        
        return mock_key

    @staticmethod
    def generate_test_api_key() -> tuple[str, str]:
        """Generate a test API key and its hash."""
        import hashlib
        import secrets
        
        key = secrets.token_urlsafe(32)
        full_key = f"abk_live_{key}"
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        return full_key, key_hash


class UserFactory:
    """Factory for creating test User objects."""
    
    @staticmethod
    def create_system_user(
        id: int = 1,
        system_user_id: int = 1,
        email: str = "test@example.com",
        username: str = "testuser",
        first_name: str = "Test",
        last_name: str = "User",
        credits: int = 100,
        is_active: bool = True,
        **kwargs
    ) -> User:
        """Create a User with system authentication."""
        return User(
            id=id,
            auth_type=AuthType.SYSTEM,
            system_user_id=system_user_id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            credits=credits,
            is_active=is_active,
            **kwargs
        )

    @staticmethod
    def create_clerk_user(
        id: int = 1,
        clerk_user_id: str = "clerk_user_123",
        email: str = "clerk@example.com",
        username: str = "clerkuser",
        first_name: str = "Clerk",
        last_name: str = "User",
        credits: int = 100,
        is_active: bool = True,
        **kwargs
    ) -> User:
        """Create a User with Clerk authentication."""
        return User(
            id=id,
            auth_type=AuthType.CLERK,
            clerk_user_id=clerk_user_id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            credits=credits,
            is_active=is_active,
            **kwargs
        )

    @staticmethod
    def create_mock_user(
        id: int = 1,
        auth_type: AuthType = AuthType.SYSTEM,
        system_user_id: Optional[int] = 1,
        clerk_user_id: Optional[str] = None,
        email: str = "test@example.com",
        username: str = "testuser",
        first_name: str = "Test",
        last_name: str = "User",
        credits: int = 100,
        is_active: bool = True,
        **kwargs
    ) -> Mock:
        """Create a mock User for testing."""
        mock_user = Mock(spec=User)
        mock_user.id = id
        mock_user.auth_type = auth_type
        mock_user.system_user_id = system_user_id
        mock_user.clerk_user_id = clerk_user_id
        mock_user.email = email
        mock_user.username = username
        mock_user.first_name = first_name
        mock_user.last_name = last_name
        mock_user.credits = credits
        mock_user.is_active = is_active
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()
        
        # Apply any additional kwargs
        for key, value in kwargs.items():
            setattr(mock_user, key, value)
        
        return mock_user


class AuthTestData:
    """Test data for authentication scenarios."""
    
    # Valid registration data
    VALID_REGISTRATION_DATA = [
        {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "SecurePassword123!",
            "first_name": "Test",
            "last_name": "User"
        },
        {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "AnotherSecure456!",
            "first_name": "Another",
            "last_name": "User"
        }
    ]
    
    # Invalid registration data
    INVALID_REGISTRATION_DATA = [
        {
            "username": "",
            "email": "test@example.com",
            "password": "validpass123",
            "error": "Username cannot be empty"
        },
        {
            "username": "test",
            "email": "invalid-email",
            "password": "validpass123",
            "error": "Invalid email format"
        },
        {
            "username": "test",
            "email": "test@example.com",
            "password": "123",
            "error": "Password too short"
        },
        {
            "username": "test",
            "email": "test@example.com",
            "password": "",
            "error": "Password cannot be empty"
        }
    ]
    
    # Valid login data
    VALID_LOGIN_DATA = [
        {"username": "testuser1", "password": "SecurePassword123!"},
        {"username": "testuser2", "password": "AnotherSecure456!"}
    ]
    
    # Invalid login data
    INVALID_LOGIN_DATA = [
        {"username": "nonexistent", "password": "validpass123"},
        {"username": "testuser1", "password": "wrongpassword"},
        {"username": "", "password": "validpass123"},
        {"username": "testuser1", "password": ""}
    ]
    
    # Valid API key data
    VALID_API_KEY_DATA = [
        {"name": "Production Key", "expires_at": None},
        {"name": "Development Key", "expires_at": "2025-12-31T23:59:59Z"},
        {"name": "Test Key", "expires_at": "2024-12-31T23:59:59Z"}
    ]
    
    # Invalid API key data
    INVALID_API_KEY_DATA = [
        {"name": "", "expires_at": None},
        {"name": "a" * 101, "expires_at": None},  # Too long
        {"name": "Valid Name", "expires_at": "invalid-date"}
    ]
    
    # Test API keys
    VALID_API_KEYS = [
        "abk_live_" + "x" * 43,  # Valid format
        "abk_live_" + "y" * 43,  # Another valid format
    ]
    
    # Invalid API keys
    INVALID_API_KEYS = [
        "invalid_format",
        "abk_test_" + "x" * 43,  # Wrong prefix
        "abk_live_short",  # Too short
        "",  # Empty
        "abk_live_" + "x" * 100,  # Too long
    ]


class AuthTestHelpers:
    """Helper functions for authentication tests."""
    
    @staticmethod
    def create_test_database_session():
        """Create a test database session."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from api.database import Base
        
        # Create in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        TestSession = sessionmaker(bind=engine)
        return TestSession()
    
    @staticmethod
    def create_auth_headers(api_key: str) -> Dict[str, str]:
        """Create authentication headers for API requests."""
        return {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def create_bearer_headers(token: str) -> Dict[str, str]:
        """Create Bearer token headers for API requests."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    @staticmethod
    def assert_user_response(response_data: Dict[str, Any], expected_user: Dict[str, Any]):
        """Assert that a user response matches expected data."""
        assert response_data["id"] == expected_user["id"]
        assert response_data["username"] == expected_user["username"]
        assert response_data["email"] == expected_user["email"]
        assert response_data["first_name"] == expected_user["first_name"]
        assert response_data["last_name"] == expected_user["last_name"]
        assert response_data["is_active"] == expected_user["is_active"]
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    @staticmethod
    def assert_api_key_response(response_data: Dict[str, Any], expected_key: Dict[str, Any]):
        """Assert that an API key response matches expected data."""
        assert response_data["id"] == expected_key["id"]
        assert response_data["name"] == expected_key["name"]
        assert response_data["key_prefix"] == expected_key["key_prefix"]
        assert response_data["is_active"] == expected_key["is_active"]
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    @staticmethod
    def create_expired_api_key() -> tuple[str, str]:
        """Create an expired API key for testing."""
        full_key, key_hash = ApiKeyFactory.generate_test_api_key()
        return full_key, key_hash
    
    @staticmethod
    def create_inactive_api_key() -> tuple[str, str]:
        """Create an inactive API key for testing."""
        full_key, key_hash = ApiKeyFactory.generate_test_api_key()
        return full_key, key_hash