# AutoBlogger API Setup Guide

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```bash
# OpenAI API (required for blog generation)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily Search API (required for research)
TAVILY_API_KEY=your_tavily_api_key_here

# Clerk Authentication (required for user management)
CLERK_SECRET_KEY=your_clerk_secret_key_here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./autoblogger.db
```

## Clerk Setup

1. Go to [clerk.com](https://clerk.com) and create an account
2. Create a new application
3. Get your secret key from the API Keys section
4. Get your publishable key from the API Keys section
5. Add both keys to your `.env` file

## Running the API

```bash
# Install dependencies
uv sync

# Run the API server
uv run python run_api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing with Clerk

### Step 1: Get a JWT Token from Clerk

You'll need to integrate with Clerk's frontend SDK to get a JWT token. For testing purposes, you can:

1. Create a simple HTML page with Clerk's JavaScript SDK
2. Login and extract the JWT token from the session
3. Use that token in your curl requests

### Step 2: Test with curl

Here are example curl commands for testing the API:

## curl Examples

### 1. Health Check (No Auth Required)
```bash
curl -X GET "http://localhost:8000/health" \
  -H "Content-Type: application/json"
```

### 2. Get Current User Info (Auth Required)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Get Credit Balance
```bash
curl -X GET "http://localhost:8000/api/v1/credits/balance" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 4. Purchase Credits (Testing - No Real Payment)
```bash
curl -X POST "http://localhost:8000/api/v1/credits/purchase" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100,
    "payment_reference": "test_purchase_123"
  }'
```

### 5. List Available Apps
```bash
curl -X GET "http://localhost:8000/api/v1/apps/" \
  -H "Content-Type: application/json"
```

### 6. Generate Blog Post
```bash
curl -X POST "http://localhost:8000/api/v1/apps/blogger/generate" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The Future of Artificial Intelligence",
    "search_depth": "advanced",
    "search_topic": "general",
    "time_range": "week",
    "max_results": 8,
    "include_answer": true
  }'
```

### 7. Check Blog Generation Status
```bash
curl -X GET "http://localhost:8000/api/v1/apps/blogger/usage/1" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 8. Get App Usage History
```bash
curl -X GET "http://localhost:8000/api/v1/apps/usage/history" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

## Testing Without Clerk (Development)

For development testing, you can temporarily modify the auth middleware to skip JWT verification. However, this should NEVER be done in production.

## API Features

✅ **User Management**
- Automatic user creation from Clerk JWT
- User profile updates
- Account deactivation

✅ **Credits System**
- Credit balance tracking
- Credit purchase (placeholder for payment integration)
- Transaction history
- Automatic credit consumption

✅ **App System**
- Dynamic app registration
- Background task processing
- Usage tracking and history
- Error handling and status updates

✅ **Blogger App**
- Full integration with existing blogger workflow
- Configurable search parameters
- Asynchronous processing
- Status monitoring