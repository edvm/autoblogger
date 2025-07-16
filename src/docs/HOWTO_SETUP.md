# AutoBlogger Backend Setup Guide

This guide provides comprehensive instructions for setting up and running the AutoBlogger backend with different LLM providers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [LLM Provider Configuration](#llm-provider-configuration)
- [Starting the Backend](#starting-the-backend)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Development Commands](#development-commands)

## Prerequisites

- **Python 3.11+** (recommended 3.13)
- **UV package manager** (recommended) or pip
- **Git** for cloning the repository
- **API Keys** for your chosen services:
  - OpenAI API key (if using OpenAI provider)
  - Google Gemini API key (if using Gemini provider)
  - Tavily API key (required for web search)
  - Clerk authentication keys (for API access)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd autoblogger/backend
```

### 2. Install Dependencies

#### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### Using Pip (Alternative)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Configuration

### 1. Create Environment File

Create a `.env` file in the backend directory:

```bash
cp .env.example .env  # If example exists, or create new file
touch .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your configuration:

```env
# LLM Provider Configuration
LLM_PROVIDER=gemini  # Options: "openai" or "gemini"

# API Keys (only the one for your chosen provider is required)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Required for all configurations
TAVILY_API_KEY=your_tavily_api_key_here
CLERK_SECRET_KEY=your_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
```

## LLM Provider Configuration

The AutoBlogger backend supports two LLM providers: **OpenAI** and **Google Gemini**.

### OpenAI Configuration

1. **Get API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Set Environment Variables**:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```
3. **Models Used**:
   - Fast Model: `gpt-4.1-nano-2025-04-14`
   - Large Model: `gpt-4.1-nano-2025-04-14`

### Gemini Configuration

1. **Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Set Environment Variables**:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your-gemini-api-key-here
   ```
3. **Models Used**:
   - Fast Model: `gemini-2.5-flash`
   - Large Model: `gemini-2.5-flash`

### Additional Required Services

#### Tavily Search API

1. **Get API Key**: Visit [Tavily API](https://tavily.com/)
2. **Set Environment Variable**:
   ```env
   TAVILY_API_KEY=your-tavily-api-key-here
   ```

#### Clerk Authentication

1. **Get Keys**: Visit [Clerk Dashboard](https://clerk.com/)
2. **Set Environment Variables**:
   ```env
   CLERK_SECRET_KEY=sk_your-clerk-secret-key-here
   CLERK_PUBLISHABLE_KEY=pk_your-clerk-publishable-key-here
   ```

## Starting the Backend

### Option 1: API Server (Recommended for Web Interface)

```bash
# Using UV
uv run python run_api.py

# Using Python directly (if dependencies installed)
python run_api.py
```

The API server will start on `http://localhost:8000`

### Option 2: CLI Interface (Direct Blog Generation)

```bash
# Generate a blog post directly
uv run python cli.py "Your blog topic here"

# Example
uv run python cli.py "The Future of Artificial Intelligence in Healthcare"
```

### Option 3: Quick Start Script

If available, use the quick start script:

```bash
./start.sh
```

## Verification

### 1. Test LLM Provider Configuration

```bash
# Test OpenAI configuration
LLM_PROVIDER=openai OPENAI_API_KEY=your-key uv run python -c "
from core.llm_services import create_llm_service
service = create_llm_service()
print(f'✅ {type(service).__name__} configured successfully')
"

# Test Gemini configuration
LLM_PROVIDER=gemini GEMINI_API_KEY=your-key uv run python -c "
from core.llm_services import create_llm_service
service = create_llm_service()
print(f'✅ {type(service).__name__} configured successfully')
"
```

### 2. Test API Server

```bash
# Start the server
uv run python run_api.py

# In another terminal, test the health endpoint
curl http://localhost:8000/health
```

### 3. Test Blog Generation

```bash
# Test CLI blog generation
uv run python cli.py "Quick test topic"
```

Check the `outputs/` directory for generated files.

## Troubleshooting

### Common Issues

#### 1. Missing API Keys

**Error**: `ValueError: OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'.`

**Solution**: Ensure the correct API key is set for your chosen provider:
```bash
# Check current provider
echo $LLM_PROVIDER

# Set the appropriate API key
export OPENAI_API_KEY=your-key  # For OpenAI
export GEMINI_API_KEY=your-key  # For Gemini
```

#### 2. Package Import Errors

**Error**: `ImportError: No module named 'google.genai'`

**Solution**: Install missing dependencies:
```bash
uv sync  # Reinstall all dependencies
# or
pip install google-genai
```

#### 3. Permission Errors

**Error**: File permission issues

**Solution**:
```bash
# Make sure you have write permissions
chmod +w outputs/
mkdir -p outputs/
```

#### 4. Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=8001 uv run python run_api.py
```

### Environment Variable Debugging

```bash
# Check all environment variables
env | grep -E "(LLM_|OPENAI_|GEMINI_|TAVILY_|CLERK_)"

# Test configuration loading
uv run python -c "
from configs.config import LLM_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY
print(f'Provider: {LLM_PROVIDER}')
print(f'OpenAI Key: {OPENAI_API_KEY[:10] if OPENAI_API_KEY else None}...')
print(f'Gemini Key: {GEMINI_API_KEY[:10] if GEMINI_API_KEY else None}...')
"
```

## Development Commands

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking (if mypy configured)
uv run mypy .
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_llm_services.py

# Run with coverage
uv run pytest --cov=.
```

### Development Server

```bash
# Run with auto-reload (if supported)
uv run python run_api.py --reload

# Run with specific log level
LOG_LEVEL=DEBUG uv run python run_api.py
```

## Configuration Files Overview

- **`.env`**: Environment variables (create this)
- **`configs/config.py`**: Main configuration file
- **`pyproject.toml`**: Python project configuration
- **`requirements.txt`**: Python dependencies
- **`uv.lock`**: UV lockfile (auto-generated)

## Output Files

Generated blog posts are saved in:
- **`outputs/`**: Directory for generated blog posts
  - `topic-name.md`: Final blog post in Markdown
  - `topic-name_log.json`: Full execution log with debugging info

## Need Help?

1. Check the logs in the output JSON files for detailed error information
2. Verify all environment variables are correctly set
3. Ensure API keys have sufficient credits/quota
4. Check network connectivity for API calls
5. Review the troubleshooting section above

For additional support, refer to the main project documentation or open an issue in the repository.