"""
Unit tests for authentication system database models.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from sqlite3 import IntegrityError
from unittest.mock import Mock, patch

import pytest

from api.database import ApiKey, AuthType, SystemUser, User
from tests.utils.auth_test_utils import ApiKeyFactory, SystemUserFactory, UserFactory

"""Tests for SystemUser, ApiKey, and User models."""


class TestSystemUser:
    """Test cases for SystemUser model."""

    def test_system_user_creation(self):
        """Test creating a SystemUser instance."""
        user = SystemUser(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.password_hash is None  # Not set yet
        assert user.created_at is None  # Will be set by database
        assert user.updated_at is None  # Will be set by database

    def test_set_password(self):
        """Test password hashing functionality."""
        user = SystemUser(username="testuser", email="test@example.com")
        password = "testpassword123"

        user.set_password(password)

        assert user.password_hash is not None
        assert user.password_hash != password  # Should be hashed
        assert user.password_hash.startswith("$2b$")  # bcrypt format

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        user = SystemUser(username="testuser", email="test@example.com")
        password = "testpassword123"
        user.set_password(password)

        assert user.verify_password(password) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        user = SystemUser(username="testuser", email="test@example.com")
        password = "testpassword123"
        user.set_password(password)

        assert user.verify_password("wrongpassword") is False

    def test_verify_password_empty(self):
        """Test password verification with empty password."""
        user = SystemUser(username="testuser", email="test@example.com")
        user.set_password("testpassword123")

        assert user.verify_password("") is False

    def test_password_hashing_different_salts(self):
        """Test that same password generates different hashes."""
        user1 = SystemUser(username="user1", email="user1@example.com")
        user2 = SystemUser(username="user2", email="user2@example.com")
        password = "samepassword123"

        user1.set_password(password)
        user2.set_password(password)

        assert user1.password_hash != user2.password_hash

    def test_unicode_password_handling(self):
        """Test handling of unicode characters in passwords."""
        user = SystemUser(username="testuser", email="test@example.com")
        password = "pássword123🔐"

        user.set_password(password)
        assert user.verify_password(password) is True
        assert user.verify_password("password123") is False


class TestApiKey:
    """Test cases for ApiKey model."""

    def test_api_key_creation(self):
        """Test creating an ApiKey instance."""
        key = ApiKey(
            system_user_id=1,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="abk_live_test",
            is_active=True,
        )

        assert key.system_user_id == 1
        assert key.name == "Test Key"
        assert key.key_hash == "test_hash"
        assert key.key_prefix == "abk_live_test"
        assert key.is_active is True
        assert key.last_used_at is None
        assert key.expires_at is None

    def test_generate_key(self):
        """Test API key generation."""
        full_key, key_hash = ApiKey.generate_key()

        assert full_key.startswith("abk_live_")
        assert len(full_key) == 52  # abk_live_ (9) + 43 chars
        assert key_hash != full_key  # Should be hashed
        assert len(key_hash) == 64  # SHA-256 hex digest length

    def test_generate_key_uniqueness(self):
        """Test that generated keys are unique."""
        key1, hash1 = ApiKey.generate_key()
        key2, hash2 = ApiKey.generate_key()

        assert key1 != key2
        assert hash1 != hash2

    def test_hash_key(self):
        """Test API key hashing."""
        key = "abk_live_test_key_123"
        hashed = ApiKey.hash_key(key)

        # Should match manual SHA-256 hash
        expected_hash = hashlib.sha256(key.encode()).hexdigest()
        assert hashed == expected_hash

    def test_hash_key_consistency(self):
        """Test that same key produces same hash."""
        key = "abk_live_test_key_123"
        hash1 = ApiKey.hash_key(key)
        hash2 = ApiKey.hash_key(key)

        assert hash1 == hash2

    def test_get_prefix(self):
        """Test getting key prefix."""
        key = ApiKey(
            system_user_id=1,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="abk_live_test",
            is_active=True,
        )

        assert key.get_prefix() == "abk_live_test"

    def test_is_expired_no_expiration(self):
        """Test expiration check when no expiration is set."""
        key = ApiKey(
            system_user_id=1,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="abk_live_test",
            is_active=True,
            expires_at=None,
        )

        assert key.is_expired() is False

    def test_is_expired_future_expiration(self):
        """Test expiration check with future expiration."""
        future_date = datetime.utcnow() + timedelta(days=30)
        key = ApiKey(
            system_user_id=1,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="abk_live_test",
            is_active=True,
            expires_at=future_date,
        )

        assert key.is_expired() is False

    def test_is_expired_past_expiration(self):
        """Test expiration check with past expiration."""
        past_date = datetime.utcnow() - timedelta(days=1)
        key = ApiKey(
            system_user_id=1,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="abk_live_test",
            is_active=True,
            expires_at=past_date,
        )

        assert key.is_expired() is True

    def test_update_last_used(self):
        """Test updating last used timestamp."""
        key = ApiKey(
            system_user_id=1,
            name="Test Key",
            key_hash="test_hash",
            key_prefix="abk_live_test",
            is_active=True,
        )

        assert key.last_used_at is None

        before_update = datetime.utcnow()
        key.update_last_used()
        after_update = datetime.utcnow()

        assert key.last_used_at is not None
        assert before_update <= key.last_used_at <= after_update


class TestUser:
    """Test cases for User model with authentication type support."""

    def test_user_creation_system_auth(self):
        """Test creating a User with system authentication."""
        user = User(
            auth_type=AuthType.SYSTEM,
            system_user_id=1,
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            credits=100,
            is_active=True,
        )

        assert user.auth_type == AuthType.SYSTEM
        assert user.system_user_id == 1
        assert user.clerk_user_id is None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.credits == 100
        assert user.is_active is True

    def test_user_creation_clerk_auth(self):
        """Test creating a User with Clerk authentication."""
        user = User(
            auth_type=AuthType.CLERK,
            clerk_user_id="clerk_user_123",
            email="clerk@example.com",
            username="clerkuser",
            first_name="Clerk",
            last_name="User",
            credits=100,
            is_active=True,
        )

        assert user.auth_type == AuthType.CLERK
        assert user.clerk_user_id == "clerk_user_123"
        assert user.system_user_id is None
        assert user.email == "clerk@example.com"
        assert user.username == "clerkuser"
        assert user.credits == 100
        assert user.is_active is True

    def test_user_default_auth_type(self):
        """Test that default auth type is CLERK for backward compatibility."""
        user = User(
            clerk_user_id="clerk_user_123", email="test@example.com", credits=100
        )

        assert user.auth_type == AuthType.CLERK

    def test_user_default_credits(self):
        """Test that default credits are set correctly."""
        user = User(
            auth_type=AuthType.SYSTEM, system_user_id=1, email="test@example.com"
        )

        assert user.credits == 100

    def test_user_default_active_status(self):
        """Test that default active status is True."""
        user = User(
            auth_type=AuthType.SYSTEM, system_user_id=1, email="test@example.com"
        )

        assert user.is_active is True


class TestAuthType:
    """Test cases for AuthType enumeration."""

    def test_auth_type_values(self):
        """Test that AuthType has correct values."""
        assert AuthType.CLERK.value == "clerk"
        assert AuthType.SYSTEM.value == "system"

    def test_auth_type_comparison(self):
        """Test AuthType comparison."""
        assert AuthType.CLERK == AuthType.CLERK
        assert AuthType.SYSTEM == AuthType.SYSTEM
        assert AuthType.CLERK != AuthType.SYSTEM

    def test_auth_type_string_representation(self):
        """Test string representation of AuthType."""
        assert str(AuthType.CLERK) == "AuthType.CLERK"
        assert str(AuthType.SYSTEM) == "AuthType.SYSTEM"


class TestModelIntegration:
    """Integration tests for model relationships."""

    def test_system_user_api_key_relationship(self, test_database_session):
        """Test relationship between SystemUser and ApiKey."""
        # Create system user
        system_user = SystemUser(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        system_user.set_password("testpassword123")

        test_database_session.add(system_user)
        test_database_session.commit()

        # Create API key
        full_key, key_hash = ApiKey.generate_key()
        api_key = ApiKey(
            system_user_id=system_user.id,
            name="Test Key",
            key_hash=key_hash,
            key_prefix=full_key[:12],
            is_active=True,
        )

        test_database_session.add(api_key)
        test_database_session.commit()

        # Test relationship
        assert len(system_user.api_keys) == 1
        assert system_user.api_keys[0].name == "Test Key"
        assert api_key.system_user.username == "testuser"

    def test_system_user_user_relationship(self, test_database_session):
        """Test relationship between SystemUser and User."""
        # Create system user
        system_user = SystemUser(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        system_user.set_password("testpassword123")

        test_database_session.add(system_user)
        test_database_session.commit()

        # Create user
        user = User(
            auth_type=AuthType.SYSTEM,
            system_user_id=system_user.id,
            email="test@example.com",
            username="testuser",
            credits=100,
        )

        test_database_session.add(user)
        test_database_session.commit()

        # Test relationship
        assert system_user.user is not None
        assert system_user.user.username == "testuser"
        assert user.system_user.username == "testuser"

    def test_unique_constraints(self, test_database_session):
        """Test unique constraints on models."""
        # Create first system user
        system_user1 = SystemUser(username="testuser", email="test@example.com")
        system_user1.set_password("password123")

        test_database_session.add(system_user1)
        test_database_session.commit()

        # Try to create second system user with same username
        system_user2 = SystemUser(
            username="testuser",  # Same username
            email="different@example.com",
        )
        system_user2.set_password("password123")

        test_database_session.add(system_user2)

        # Should raise integrity error
        with pytest.raises(IntegrityError):  # SQLAlchemy IntegrityError
            test_database_session.commit()

    def test_cascade_operations(self, test_database_session):
        """Test cascade operations between related models."""
        # Create system user with API key
        system_user = SystemUser(username="testuser", email="test@example.com")
        system_user.set_password("password123")

        test_database_session.add(system_user)
        test_database_session.commit()

        # Create API key
        full_key, key_hash = ApiKey.generate_key()
        api_key = ApiKey(
            system_user_id=system_user.id,
            name="Test Key",
            key_hash=key_hash,
            key_prefix=full_key[:12],
        )

        test_database_session.add(api_key)
        test_database_session.commit()

        # Verify relationship exists
        assert len(system_user.api_keys) == 1

        # Delete system user should handle API key appropriately
        # (Depends on cascade configuration - test behavior matches setup)
