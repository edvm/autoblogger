#!/usr/bin/env python3
"""
Test script to verify the new authentication system works.
"""

import json
import requests
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def test_system_user_registration():
    """Test system user registration."""
    print("🔧 Testing system user registration...")
    
    registration_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json=registration_data)
    
    if response.status_code == 200:
        print("✅ System user registration successful")
        return response.json()
    else:
        print(f"❌ System user registration failed: {response.text}")
        return None

def test_system_user_login():
    """Test system user login."""
    print("🔧 Testing system user login...")
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ System user login successful")
        data = response.json()
        return data.get("api_key", {}).get("full_key")
    else:
        print(f"❌ System user login failed: {response.text}")
        return None

def test_api_key_authentication(api_key: str):
    """Test API key authentication."""
    print("🔧 Testing API key authentication...")
    
    headers = {"X-API-Key": api_key}
    
    response = requests.get(f"{API_BASE_URL}/api/v1/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ API key authentication successful")
        return response.json()
    else:
        print(f"❌ API key authentication failed: {response.text}")
        return None

def test_blog_generation(api_key: str):
    """Test blog generation with API key."""
    print("🔧 Testing blog generation with API key...")
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    blog_data = {
        "topic": "Test Blog Post",
        "search_depth": "basic",
        "max_results": 3
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/apps/blogger/generate", 
                           headers=headers, json=blog_data)
    
    if response.status_code == 200:
        print("✅ Blog generation initiated successfully")
        return response.json()
    else:
        print(f"❌ Blog generation failed: {response.text}")
        return None

def test_api_key_management(api_key: str):
    """Test API key management endpoints."""
    print("🔧 Testing API key management...")
    
    headers = {"X-API-Key": api_key}
    
    # List existing keys
    response = requests.get(f"{API_BASE_URL}/api/v1/auth/keys", headers=headers)
    if response.status_code == 200:
        print("✅ API key listing successful")
        keys = response.json()
        print(f"   Found {len(keys)} existing keys")
    else:
        print(f"❌ API key listing failed: {response.text}")
        return False
    
    # Create a new key
    new_key_data = {
        "name": "Test API Key",
        "expires_at": None
    }
    
    response = requests.post(f"{API_BASE_URL}/api/v1/auth/keys", 
                           headers=headers, json=new_key_data)
    
    if response.status_code == 200:
        print("✅ API key creation successful")
        new_key = response.json()
        return new_key.get("id")
    else:
        print(f"❌ API key creation failed: {response.text}")
        return None

def main():
    """Run all tests."""
    print("🚀 Starting authentication system tests...\n")
    
    # Test registration
    user_data = test_system_user_registration()
    if not user_data:
        return
    
    print()
    
    # Test login
    api_key = test_system_user_login()
    if not api_key:
        return
    
    print(f"   Generated API key: {api_key[:20]}...")
    print()
    
    # Test API key authentication
    user_info = test_api_key_authentication(api_key)
    if not user_info:
        return
    
    print(f"   Authenticated as: {user_info.get('username')} ({user_info.get('email')})")
    print()
    
    # Test API key management
    new_key_id = test_api_key_management(api_key)
    if new_key_id:
        print(f"   Created new API key with ID: {new_key_id}")
    print()
    
    # Test blog generation
    blog_result = test_blog_generation(api_key)
    if blog_result:
        print(f"   Blog generation usage ID: {blog_result.get('usage_id')}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()