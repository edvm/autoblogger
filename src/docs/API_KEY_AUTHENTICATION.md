# API Key Authentication for AutoBlogger

This document explains how to use the new API key authentication system to use AutoBlogger without depending on Clerk.

## Overview

The new authentication system supports two methods:
1. **Clerk Authentication** (existing) - Uses JWT tokens from Clerk
2. **API Key Authentication** (new) - Uses API keys for system users

## Getting Started with API Key Authentication

### 1. Register a System User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_secure_password",
    "first_name": "Your",
    "last_name": "Name"
  }'
```

### 2. Login and Get API Key

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_secure_password"
  }'
```

Response includes your API key:
```json
{
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com",
    "first_name": "Your",
    "last_name": "Name",
    "is_active": true,
    "created_at": "2025-07-15T11:40:25.221Z",
    "updated_at": "2025-07-15T11:40:25.221Z"
  },
  "api_key": {
    "id": 1,
    "name": "Login key - 2025-07-15 11:40",
    "key_prefix": "abk_live_xxx",
    "full_key": "abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "is_active": true,
    "expires_at": "2026-07-15T11:40:25.221Z",
    "created_at": "2025-07-15T11:40:25.221Z"
  }
}
```

**Important**: Save the `full_key` value - it won't be shown again!

### 3. Generate Blog Posts with API Key

```bash
curl -X POST "http://localhost:8000/api/v1/apps/blogger/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "topic": "The Future of AI in Healthcare",
    "search_depth": "advanced",
    "search_topic": "general",
    "time_range": "month",
    "max_results": 10,
    "include_answer": true,
    "include_raw_content": false,
    "include_images": false
  }'
```

Response:
```json
{
  "usage_id": 123,
  "status": "pending"
}
```

### 4. Check Blog Generation Status

```bash
curl -X GET "http://localhost:8000/api/v1/apps/blogger/usage/123" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

When completed:
```json
{
  "usage_id": 123,
  "status": "completed",
  "final_content": "# The Future of AI in Healthcare\n\n...",
  "research_brief": {...},
  "sources": ["https://example.com/article1", ...],
  "error_message": null
}
```

## API Key Management

### List Your API Keys

```bash
curl -X GET "http://localhost:8000/api/v1/auth/keys" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Create a New API Key

```bash
curl -X POST "http://localhost:8000/api/v1/auth/keys" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "name": "Production API Key",
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

### Update an API Key

```bash
curl -X PUT "http://localhost:8000/api/v1/auth/keys/1" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d '{
    "name": "Updated Key Name",
    "expires_at": "2026-12-31T23:59:59Z"
  }'
```

### Revoke an API Key

```bash
curl -X DELETE "http://localhost:8000/api/v1/auth/keys/1" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## User Management

### Get Current User Info

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Check Credit Balance

```bash
curl -X GET "http://localhost:8000/api/v1/credits/balance" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Get Usage History

```bash
curl -X GET "http://localhost:8000/api/v1/apps/usage/history" \
  -H "X-API-Key: abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Environment Configuration

Add these environment variables to your `.env` file:

```bash
# Enable/disable authentication methods
ENABLE_CLERK_AUTH=true        # Keep existing Clerk users working
ENABLE_SYSTEM_AUTH=true       # Enable API key authentication

# System authentication settings
SYSTEM_AUTH_SECRET_KEY=your-secret-key-change-in-production
API_KEY_EXPIRATION_DAYS=365   # Default expiration for new keys
```

## Security Best Practices

1. **Keep API Keys Secret**: Never commit API keys to version control
2. **Use HTTPS**: Always use HTTPS in production
3. **Rotate Keys**: Regularly rotate API keys
4. **Set Expiration**: Set appropriate expiration dates for keys
5. **Monitor Usage**: Check the `last_used_at` field to identify unused keys
6. **Revoke Unused Keys**: Deactivate keys that are no longer needed

## API Key Format

- Format: `abk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- Prefix: `abk_live_` (for live keys)
- Length: 52 characters total
- Storage: Keys are hashed using SHA-256 before storage

## Error Handling

Common error responses:

```json
{
  "detail": "X-API-Key header is required"
}
```

```json
{
  "detail": "Invalid API key"
}
```

```json
{
  "detail": "API key has expired"
}
```

```json
{
  "detail": "User account is inactive"
}
```

## Migration from Clerk

Existing Clerk users can continue using their JWT tokens. The system supports both authentication methods simultaneously. To migrate:

1. Create a system user account
2. Generate API keys for your applications
3. Update your applications to use API keys instead of JWT tokens
4. Optionally disable Clerk authentication by setting `ENABLE_CLERK_AUTH=false`

## Rate Limiting

API keys respect the same rate limiting as Clerk users:
- Standard endpoints: 100 requests per minute
- Expensive endpoints (blog generation): Lower limits apply

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review the test script in `test_auth_system.py`
- Report issues on the project repository