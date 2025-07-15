"""
Unit tests for authentication strategies.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, Request

from api.auth_strategies import (
    AuthStrategy, 
    AuthResult, 
    ClerkAuthStrategy, 
    ApiKeyAuthStrategy, 
    AuthStrategyManager
)
from api.database import AuthType, User, SystemUser, ApiKey
from tests.utils.auth_test_utils import UserFactory, SystemUserFactory, ApiKeyFactory

"""Tests for authentication strategies."""


class TestAuthResult:
    """Test cases for AuthResult class."""

    def test_auth_result_creation(self):
        """Test creating an AuthResult instance."""
        user = UserFactory.create_mock_user()
        result = AuthResult(
            user=user,
            auth_type=AuthType.SYSTEM,
            metadata={"api_key_id": 1}
        )
        
        assert result.user == user
        assert result.auth_type == AuthType.SYSTEM
        assert result.metadata == {"api_key_id": 1}

    def test_auth_result_no_metadata(self):
        """Test creating AuthResult without metadata."""
        user = UserFactory.create_mock_user()
        result = AuthResult(
            user=user,
            auth_type=AuthType.CLERK
        )
        
        assert result.user == user
        assert result.auth_type == AuthType.CLERK
        assert result.metadata == {}


class TestClerkAuthStrategy:
    """Test cases for ClerkAuthStrategy."""

    def test_get_auth_type(self):
        """Test that ClerkAuthStrategy returns correct auth type."""
        strategy = ClerkAuthStrategy()
        assert strategy.get_auth_type() == AuthType.CLERK

    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        """Test successful Clerk authentication."""
        strategy = ClerkAuthStrategy()
        
        # Mock request
        mock_request = Mock(spec=Request)
        mock_db = Mock()
        
        # Mock Clerk client and responses
        mock_request_state = Mock()
        mock_request_state.is_signed_in = True
        mock_request_state.payload = {"sub": "clerk_user_123"}
        
        mock_user_response = Mock()
        mock_user_response.email_addresses = [
            Mock(email_address="test@example.com", id="email_123")
        ]
        mock_user_response.primary_email_address_id = "email_123"
        mock_user_response.first_name = "Test"
        mock_user_response.last_name = "User"
        
        # Mock existing user in database
        mock_db_user = UserFactory.create_mock_user(
            auth_type=AuthType.CLERK,
            clerk_user_id="clerk_user_123"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_db_user
        
        with patch.object(strategy.clerk_client, 'authenticate_request', return_value=mock_request_state):
            with patch.object(strategy.clerk_client.users, 'get', return_value=mock_user_response):
                result = await strategy.authenticate(mock_request, mock_db)
                
                assert isinstance(result, AuthResult)
                assert result.auth_type == AuthType.CLERK
                assert result.user == mock_db_user
                assert result.metadata["clerk_user_id"] == "clerk_user_123"

    @pytest.mark.asyncio
    async def test_authenticate_create_new_user(self):
        """Test Clerk authentication creates new user."""
        strategy = ClerkAuthStrategy()
        
        # Mock request
        mock_request = Mock(spec=Request)
        mock_db = Mock()
        
        # Mock Clerk client and responses
        mock_request_state = Mock()
        mock_request_state.is_signed_in = True
        mock_request_state.payload = {"sub": "clerk_user_123"}
        
        mock_user_response = Mock()
        mock_user_response.email_addresses = [
            Mock(email_address="test@example.com", id="email_123")
        ]
        mock_user_response.primary_email_address_id = "email_123"
        mock_user_response.first_name = "Test"
        mock_user_response.last_name = "User"
        
        # Mock no existing user in database
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock new user creation
        mock_new_user = UserFactory.create_mock_user()
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch.object(strategy.clerk_client, 'authenticate_request', return_value=mock_request_state):
            with patch.object(strategy.clerk_client.users, 'get', return_value=mock_user_response):
                with patch('api.auth_strategies.User', return_value=mock_new_user):
                    result = await strategy.authenticate(mock_request, mock_db)
                    
                    assert isinstance(result, AuthResult)
                    assert result.auth_type == AuthType.CLERK
                    assert result.user == mock_new_user
                    assert mock_db.add.called
                    assert mock_db.commit.called
                    assert mock_db.refresh.called

    @pytest.mark.asyncio
    async def test_authenticate_not_signed_in(self):
        """Test Clerk authentication when user is not signed in."""
        strategy = ClerkAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_db = Mock()
        
        mock_request_state = Mock()
        mock_request_state.is_signed_in = False
        
        with patch.object(strategy.clerk_client, 'authenticate_request', return_value=mock_request_state):
            with pytest.raises(HTTPException) as exc_info:
                await strategy.authenticate(mock_request, mock_db)
            
            assert exc_info.value.status_code == 401
            assert "not signed in" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_no_payload(self):
        """Test Clerk authentication when payload is missing."""
        strategy = ClerkAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_db = Mock()
        
        mock_request_state = Mock()
        mock_request_state.is_signed_in = True
        mock_request_state.payload = None
        
        with patch.object(strategy.clerk_client, 'authenticate_request', return_value=mock_request_state):
            with pytest.raises(HTTPException) as exc_info:
                await strategy.authenticate(mock_request, mock_db)
            
            assert exc_info.value.status_code == 401
            assert "Payload is not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self):
        """Test Clerk authentication with inactive user."""
        strategy = ClerkAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_db = Mock()
        
        mock_request_state = Mock()
        mock_request_state.is_signed_in = True
        mock_request_state.payload = {"sub": "clerk_user_123"}
        
        mock_user_response = Mock()
        mock_user_response.email_addresses = [
            Mock(email_address="test@example.com", id="email_123")
        ]
        mock_user_response.primary_email_address_id = "email_123"
        mock_user_response.first_name = "Test"
        mock_user_response.last_name = "User"
        
        # Mock inactive user in database
        mock_db_user = UserFactory.create_mock_user(
            auth_type=AuthType.CLERK,
            clerk_user_id="clerk_user_123",
            is_active=False
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_db_user
        
        with patch.object(strategy.clerk_client, 'authenticate_request', return_value=mock_request_state):
            with patch.object(strategy.clerk_client.users, 'get', return_value=mock_user_response):
                with pytest.raises(HTTPException) as exc_info:
                    await strategy.authenticate(mock_request, mock_db)
                
                assert exc_info.value.status_code == 400
                assert "Inactive user" in str(exc_info.value.detail)


class TestApiKeyAuthStrategy:
    """Test cases for ApiKeyAuthStrategy."""

    def test_get_auth_type(self):
        """Test that ApiKeyAuthStrategy returns correct auth type."""
        strategy = ApiKeyAuthStrategy()
        assert strategy.get_auth_type() == AuthType.SYSTEM

    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        """Test successful API key authentication."""
        strategy = ApiKeyAuthStrategy()
        
        # Mock request with API key
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "abk_live_valid_key_123"}
        mock_db = Mock()
        
        # Mock API key lookup
        mock_api_key = ApiKeyFactory.create_mock_api_key(
            is_active=True,
            expires_at=None
        )
        mock_api_key.is_expired.return_value = False
        
        # Mock system user
        mock_system_user = SystemUserFactory.create_mock_system_user(
            is_active=True
        )
        mock_api_key.system_user = mock_system_user
        
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_api_key,  # First call for API key lookup
            UserFactory.create_mock_user(auth_type=AuthType.SYSTEM)  # Second call for User lookup
        ]
        
        result = await strategy.authenticate(mock_request, mock_db)
        
        assert isinstance(result, AuthResult)
        assert result.auth_type == AuthType.SYSTEM
        assert result.metadata["api_key_id"] == mock_api_key.id
        assert result.metadata["system_user_id"] == mock_system_user.id

    @pytest.mark.asyncio
    async def test_authenticate_no_api_key_header(self):
        """Test authentication when X-API-Key header is missing."""
        strategy = ApiKeyAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await strategy.authenticate(mock_request, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "X-API-Key header is required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_invalid_key_format(self):
        """Test authentication with invalid API key format."""
        strategy = ApiKeyAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "invalid_key_format"}
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await strategy.authenticate(mock_request, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Invalid API key format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_key_not_found(self):
        """Test authentication with non-existent API key."""
        strategy = ApiKeyAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "abk_live_nonexistent_key"}
        mock_db = Mock()
        
        # Mock API key not found
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await strategy.authenticate(mock_request, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_expired_key(self):
        """Test authentication with expired API key."""
        strategy = ApiKeyAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "abk_live_expired_key"}
        mock_db = Mock()
        
        # Mock expired API key
        mock_api_key = ApiKeyFactory.create_mock_api_key(
            is_active=True,
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        mock_api_key.is_expired.return_value = True
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            await strategy.authenticate(mock_request, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "API key has expired" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_inactive_system_user(self):
        """Test authentication with inactive system user."""
        strategy = ApiKeyAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "abk_live_valid_key"}
        mock_db = Mock()
        
        # Mock API key with inactive system user
        mock_api_key = ApiKeyFactory.create_mock_api_key(is_active=True)
        mock_api_key.is_expired.return_value = False
        
        mock_system_user = SystemUserFactory.create_mock_system_user(is_active=False)
        mock_api_key.system_user = mock_system_user
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            await strategy.authenticate(mock_request, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "User account is inactive" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_creates_new_user(self):
        """Test authentication creates new User record if not exists."""
        strategy = ApiKeyAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "abk_live_valid_key"}
        mock_db = Mock()
        
        # Mock API key
        mock_api_key = ApiKeyFactory.create_mock_api_key(is_active=True)
        mock_api_key.is_expired.return_value = False
        
        # Mock system user
        mock_system_user = SystemUserFactory.create_mock_system_user(is_active=True)
        mock_api_key.system_user = mock_system_user
        
        # Mock User not found, then return new user
        mock_new_user = UserFactory.create_mock_user(auth_type=AuthType.SYSTEM)
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_api_key,  # API key found
            None,  # User not found
        ]
        
        # Mock User creation
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('api.auth_strategies.User', return_value=mock_new_user):
            result = await strategy.authenticate(mock_request, mock_db)
            
            assert isinstance(result, AuthResult)
            assert result.auth_type == AuthType.SYSTEM
            assert result.user == mock_new_user
            assert mock_db.add.called
            assert mock_db.commit.called
            assert mock_db.refresh.called

    @pytest.mark.asyncio
    async def test_authenticate_updates_last_used(self):
        """Test authentication updates API key last used timestamp."""
        strategy = ApiKeyAuthStrategy()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "abk_live_valid_key"}
        mock_db = Mock()
        
        # Mock API key
        mock_api_key = ApiKeyFactory.create_mock_api_key(is_active=True)
        mock_api_key.is_expired.return_value = False
        
        # Mock system user
        mock_system_user = SystemUserFactory.create_mock_system_user(is_active=True)
        mock_api_key.system_user = mock_system_user
        
        # Mock existing user
        mock_user = UserFactory.create_mock_user(auth_type=AuthType.SYSTEM)
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_api_key,  # API key found
            mock_user,  # User found
        ]
        
        await strategy.authenticate(mock_request, mock_db)
        
        # Verify last used timestamp was updated
        mock_api_key.update_last_used.assert_called_once()
        mock_db.commit.assert_called()


class TestAuthStrategyManager:
    """Test cases for AuthStrategyManager."""

    def test_initialization(self):
        """Test AuthStrategyManager initialization."""
        manager = AuthStrategyManager()
        
        assert AuthType.CLERK in manager.strategies
        assert AuthType.SYSTEM in manager.strategies
        assert isinstance(manager.strategies[AuthType.CLERK], ClerkAuthStrategy)
        assert isinstance(manager.strategies[AuthType.SYSTEM], ApiKeyAuthStrategy)

    def test_get_strategy(self):
        """Test getting specific strategy."""
        manager = AuthStrategyManager()
        
        clerk_strategy = manager.get_strategy(AuthType.CLERK)
        system_strategy = manager.get_strategy(AuthType.SYSTEM)
        
        assert isinstance(clerk_strategy, ClerkAuthStrategy)
        assert isinstance(system_strategy, ApiKeyAuthStrategy)

    def test_get_strategy_invalid_type(self):
        """Test getting strategy with invalid type."""
        manager = AuthStrategyManager()
        
        invalid_strategy = manager.get_strategy("invalid")
        assert invalid_strategy is None

    @pytest.mark.asyncio
    async def test_authenticate_api_key_first(self):
        """Test authentication tries API key first when X-API-Key header is present."""
        manager = AuthStrategyManager()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-API-Key": "abk_live_test_key"}
        mock_db = Mock()
        
        # Mock API key strategy
        mock_result = AuthResult(
            user=UserFactory.create_mock_user(),
            auth_type=AuthType.SYSTEM,
            metadata={"api_key_id": 1}
        )
        
        with patch.object(manager.strategies[AuthType.SYSTEM], 'authenticate', return_value=mock_result):
            result = await manager.authenticate(mock_request, mock_db)
            
            assert result == mock_result
            assert result.auth_type == AuthType.SYSTEM

    @pytest.mark.asyncio
    async def test_authenticate_clerk_fallback(self):
        """Test authentication falls back to Clerk when Authorization header is present."""
        manager = AuthStrategyManager()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {"Authorization": "Bearer jwt_token"}
        mock_request.headers.get = Mock(side_effect=lambda key: {
            "X-API-Key": None,
            "Authorization": "Bearer jwt_token"
        }.get(key))
        
        mock_db = Mock()
        
        # Mock Clerk strategy
        mock_result = AuthResult(
            user=UserFactory.create_mock_user(),
            auth_type=AuthType.CLERK,
            metadata={"clerk_user_id": "clerk_123"}
        )
        
        with patch.object(manager.strategies[AuthType.CLERK], 'authenticate', return_value=mock_result):
            result = await manager.authenticate(mock_request, mock_db)
            
            assert result == mock_result
            assert result.auth_type == AuthType.CLERK

    @pytest.mark.asyncio
    async def test_authenticate_no_method(self):
        """Test authentication when no auth method is provided."""
        manager = AuthStrategyManager()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.headers.get = Mock(return_value=None)
        mock_db = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await manager.authenticate(mock_request, mock_db)
        
        assert exc_info.value.status_code == 401
        assert "No authentication method provided" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_both_headers_prefers_api_key(self):
        """Test authentication prefers API key when both headers are present."""
        manager = AuthStrategyManager()
        
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            "X-API-Key": "abk_live_test_key",
            "Authorization": "Bearer jwt_token"
        }
        mock_request.headers.get = Mock(side_effect=lambda key: {
            "X-API-Key": "abk_live_test_key",
            "Authorization": "Bearer jwt_token"
        }.get(key))
        
        mock_db = Mock()
        
        # Mock API key strategy
        mock_result = AuthResult(
            user=UserFactory.create_mock_user(),
            auth_type=AuthType.SYSTEM,
            metadata={"api_key_id": 1}
        )
        
        with patch.object(manager.strategies[AuthType.SYSTEM], 'authenticate', return_value=mock_result) as mock_system:
            with patch.object(manager.strategies[AuthType.CLERK], 'authenticate') as mock_clerk:
                result = await manager.authenticate(mock_request, mock_db)
                
                assert result == mock_result
                assert result.auth_type == AuthType.SYSTEM
                mock_system.assert_called_once()
                mock_clerk.assert_not_called()  # Should not be called