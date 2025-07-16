"""
Simple test to verify database configuration works correctly.
"""

import pytest
from fastapi.testclient import TestClient

from api.database import get_db, SystemUser
from api.main import app
from tests.utils.auth_test_utils import SystemUserFactory


def test_database_setup_verification(test_database_session):
    """Test that database setup works correctly."""
    # Create a system user directly in the test database
    user = SystemUserFactory.create_system_user(
        username="testuser",
        email="test@example.com",
        password="testpassword123"
    )
    test_database_session.add(user)
    test_database_session.commit()
    
    # Verify the user was created
    created_user = test_database_session.query(SystemUser).filter(
        SystemUser.username == "testuser"
    ).first()
    
    assert created_user is not None
    assert created_user.email == "test@example.com"


def test_simple_endpoint_with_real_db(test_database_session):
    """Test a simple endpoint with real database override."""
    
    def get_db_override():
        yield test_database_session
    
    app.dependency_overrides[get_db] = get_db_override
    
    try:
        client = TestClient(app)
        
        # Test a simple endpoint that doesn't require database tables
        response = client.get("/health")
        assert response.status_code == 200
        
    finally:
        app.dependency_overrides.clear()