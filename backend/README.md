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
- OpenAI API key
- Tavily API key

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
cp env.example .env
```

3. Configure your API keys in `.env`:
```
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
```

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

- **OpenAIService**: Handles LLM interactions with configurable models
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

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
CLERK_SECRET_KEY=your_clerk_secret
DATABASE_URL=sqlite:///./autoblogger.db
```

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