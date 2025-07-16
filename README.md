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
# From the project root
cd src
uv sync
```

Or with pip:
```bash
cd src
pip install -r requirements.txt
```

2. Create environment file:
```bash
# Create .env file in the src directory (if it doesn't exist)
cd src
touch .env
# Then edit src/.env with your API keys (see Configuration section below)
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
# From the src directory
cd src
python cli.py "Your Topic Here"

# Using uv (recommended)
cd src
uv run python cli.py "Your Topic"
```

#### API Mode
```bash
# From the src directory
cd src
uvicorn api.main:app --reload

# Or using the provided script
cd src
python scripts/run_api.py

# Or from project root using Makefile
make backend

# Or using the quick start script (recommended for development)
./start.sh
```

## Project Structure

```
autoblogger/
├── src/                     # Main source code directory
│   ├── agents/             # Multi-agent system
│   ├── api/                # FastAPI application
│   ├── apps/               # Application modules
│   ├── core/               # Core services
│   ├── tools/              # Utility tools
│   ├── configs/            # Configuration files
│   ├── scripts/            # Utility scripts
│   ├── tests/              # Test suite
│   ├── cli.py              # Command-line interface
│   └── pyproject.toml      # Python dependencies
├── frontend/               # Next.js frontend (separate)
├── docs/                   # Documentation
├── Makefile               # Build automation
├── start.sh               # Quick start script
└── README.md              # This file
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
# From src directory
cd src
uv run pytest tests/

# Run with verbose output
cd src
uv run pytest tests/ -v

# Run specific test modules
cd src
uv run pytest tests/unittests/agents/

# Or use Makefile from project root
make test
```

### Code Quality
```bash
# From src directory
cd src
uv run ruff check --fix
uv run ruff format .

# Or use Makefile from project root
make lint
make format
```

### Adding Dependencies
```bash
# From src directory
cd src
uv add package-name

# Add development dependency
cd src
uv add --dev package-name
```

### Quick Commands (Makefile)

```bash
# From project root - these commands handle directory changes automatically
make                # Show all available commands (same as 'make help')
make backend        # Start backend API server
make test           # Run all tests
make lint           # Run code linting
make format         # Format code
make clean          # Clean build artifacts
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