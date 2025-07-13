# AutoBlogger Backend

An AI-powered blog generation system that creates high-quality articles using web research and multi-agent processing.

## Overview

AutoBlogger is a content generation platform that uses a multi-agent architecture to research topics, write drafts, and edit final articles. It combines web search capabilities with OpenAI's language models to produce well-researched, engaging content.

## Features

- **Multi-Agent Architecture**: Specialized agents for research, writing, and editing
- **Real-time Web Research**: Integration with Tavily search for current information
- **FastAPI REST API**: Modern API for web applications
- **User Authentication**: Clerk integration for secure user management
- **Credit System**: Usage tracking and billing management
- **Multiple Output Formats**: Markdown articles with JSON metadata

## Quick Start

### Prerequisites

- Python 3.13+
- **LLM API Key**: Either OpenAI API key OR Google Gemini API key
- Tavily API key (for web search)

### Installation

1. Install dependencies using uv (recommended):
```bash
uv sync
```

Or with pip:
```bash
pip install -r requirements.txt
```

2. Create environment file:
```bash
# Create .env file in the backend directory
touch .env
```

3. Configure your API keys and LLM provider in `.env`:

**For OpenAI (default):**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
```

**For Google Gemini:**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
```

**Note**: If `LLM_PROVIDER` is not set, the system defaults to OpenAI.

### Usage

#### CLI Mode
```bash
# Direct execution
python cli.py "Your Topic Here"

# Using uv (recommended)
uv run python cli.py "Your Topic"
```

#### API Mode
```bash
# Start the API server
uvicorn api.main:app --reload

# Or using the provided script
python run_api.py
```

## Architecture

### Core Components

- **WorkflowState**: Central state management for the entire generation process
- **AbstractAgent**: Base class for all specialized agents
- **BloggerManagerAgent**: Orchestrates the complete workflow

### Agent Pipeline

1. **ResearchAgent**: Conducts web research using Tavily search
2. **WritingAgent**: Creates draft content based on research findings
3. **EditorAgent**: Refines and finalizes the content

### Services

- **LLM Services**: Configurable LLM providers (OpenAI or Google Gemini)
  - **OpenAIService**: GPT-4 and other OpenAI models
  - **GeminiService**: Google Gemini 2.5 Flash and other Gemini models
- **TavilySearch**: Web search integration for research
- **FastAPI**: REST API for web frontend integration

## API Endpoints

- `POST /apps/blogger/generate` - Generate blog content
- `GET /users/profile` - User profile management
- `GET /credits/balance` - Check credit balance

## Development

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test modules
pytest tests/unittests/agents/
```

### Code Quality
```bash
# Lint and fix issues
ruff check --fix

# Format code
ruff format
```

### Adding Dependencies
```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

## Configuration

Environment variables are loaded from `.env`:

### Required Variables
```env
# LLM Provider Configuration
LLM_PROVIDER=openai  # or 'gemini' (defaults to 'openai')

# API Keys (choose based on LLM_PROVIDER)
OPENAI_API_KEY=your_openai_key      # Required if LLM_PROVIDER=openai
GEMINI_API_KEY=your_gemini_key      # Required if LLM_PROVIDER=gemini

# Search API
TAVILY_API_KEY=your_tavily_key      # Required for web research

# Authentication (optional for API usage)
CLERK_SECRET_KEY=your_clerk_secret

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./autoblogger.db
```

### LLM Provider Details

**OpenAI Models:**
- Fast Model: `gpt-4.1-nano-2025-04-14`
- Large Model: `gpt-4.1-nano-2025-04-14`

**Gemini Models:**
- Fast Model: `gemini-2.5-flash`
- Large Model: `gemini-2.5-flash`

The system automatically selects the appropriate models based on your `LLM_PROVIDER` setting.

## Output

Generated articles are saved to the `outputs/` directory:
- `topic_name.md` - The final article in Markdown format
- `topic_name_log.json` - Generation metadata and logs

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.