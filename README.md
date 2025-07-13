# AutoBlogger API

🤖 An AI-powered backend service for generating high-quality blog articles using a sophisticated multi-agent workflow system.

## Overview

AutoBlogger is a Python-based API service that combines advanced AI agents with web research capabilities to automatically generate well-researched, professionally written blog posts. The system uses specialized agents for research, writing, and editing to produce comprehensive articles on any topic.

**Primary interfaces:**
- **CLI Tool**: Direct command-line blog generation
- **REST API**: Integration with external applications and services
- **Web Demo** *(optional)*: Simple web interface for testing and demonstrations

### Key Features

- **Multi-Agent AI System**: Specialized agents for research, writing, and editing
- **Web Research Integration**: Real-time web search using Tavily API
- **CLI Interface**: Direct command-line blog generation for automation
- **REST API**: Full-featured API for integration with external systems
- **Credit-Based System**: User management with usage tracking
- **Real-Time Status**: Live progress updates via API endpoints
- **Multiple Output Formats**: Markdown files with detailed JSON logs
- **Extensible Architecture**: Easy to integrate with existing workflows

## Architecture

### Core Backend Service (Python)
- **Framework**: FastAPI with SQLAlchemy for robust API development
- **AI Integration**: OpenAI GPT models with structured response handling
- **Search**: Tavily web search API for real-time research
- **Authentication**: Clerk JWT validation for secure API access
- **Database**: SQLite with user and credit management (easily replaceable)
- **Agent System**: Multi-agent workflow with centralized state management

### Optional Web Interface
- **Framework**: Next.js demo interface (located in `frontend/` directory)
- **Purpose**: Testing and demonstration of API capabilities
- **Note**: All functionality available via CLI and API without web interface

## Quick Start

### Prerequisites
- Python 3.13+
- OpenAI API key
- Tavily API key
- Clerk account (optional, for API authentication)

### 1. Install Python Dependency Manager

```bash
# Install uv (recommended Python package manager):
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Setup Backend

```bash
# Clone the repository
git clone <repository-url>
cd autoblogger

# Install dependencies
cd backend
uv sync

# Create environment file
touch .env
# Edit .env with your API keys:
# OPENAI_API_KEY=sk-...
# TAVILY_API_KEY=tvly-...
# CLERK_SECRET_KEY=sk_test_... (optional)
# CLERK_PUBLISHABLE_KEY=pk_test_... (optional)
```

### 3. Start Using AutoBlogger

#### Option A: CLI Mode (Recommended)
```bash
# Generate a blog post directly
uv run python cli.py "Your blog topic here"

# Articles saved to outputs/ directory
```

#### Option B: API Server
```bash
# Start the API server
./start.sh
# Or manually: uv run python scripts/run_api.py
```

Access the API:
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

#### Option C: Web Demo (Optional)
```bash
# Install Node.js dependencies
cd ../frontend
npm install

# Start development server
npm run dev

# Access at: http://localhost:3000
```

## Usage

### CLI Mode (Primary Interface)
Generate blog posts directly from command line:

```bash
cd backend
uv run python cli.py "Latest developments in AI technology"
```

Generated articles are saved to `backend/outputs/` as:
- `{topic}.md` - The final article
- `{topic}_log.json` - Complete workflow state and logs

### API Integration
Use the REST API to integrate with your applications:

```bash
# Start the API server
./start.sh

# Generate via API
curl -X POST "http://localhost:8000/api/v1/apps/blogger/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Your topic here"}'

# Check status
curl "http://localhost:8000/api/v1/apps/blogger/usage/{usage_id}"
```

### Web Demo (Optional)
For testing and demonstration purposes:
1. Start both backend and frontend
2. Sign up/Login at http://localhost:3000
3. Enter your blog topic and monitor progress
4. View and download completed articles

## Agent Workflow

The system uses a sophisticated multi-agent approach:

### 1. Research Agent
- Conducts comprehensive web research using Tavily API
- Gathers current information and sources
- Populates research brief with findings

### 2. Writing Agent
- Creates initial draft based on research
- Structures content with proper formatting
- Develops comprehensive article outline

### 3. Editor Agent
- Reviews and refines the draft
- Ensures quality, coherence, and readability
- Produces final polished article

All agents operate on a shared `WorkflowState` that tracks progress, logs actions, and maintains content through the pipeline.

## Development

### Backend Development (Primary Focus)

```bash
# Install dependencies
cd backend
uv sync

# Run tests
uv run pytest tests/

# Code quality checks
uv run ruff check .
uv run ruff format .

# Start API server for development
uv run python scripts/run_api.py

# CLI usage and testing
uv run python cli.py "Your topic"
```

### Optional: Frontend Demo Development

```bash
# Only if working on the demo interface
cd frontend
npm install
npm run dev
npm run lint
```

## API Endpoints

### Authentication
- `POST /api/v1/users/me` - Get/update user information

### Credits
- `GET /api/v1/credits/balance` - Check credit balance
- `GET /api/v1/credits/transactions` - Transaction history
- `POST /api/v1/credits/purchase` - Purchase credits

### Blog Generation
- `GET /api/v1/apps/` - List available apps
- `POST /api/v1/apps/blogger/generate` - Generate blog post
- `GET /api/v1/apps/blogger/usage/{usage_id}` - Check generation status
- `GET /api/v1/apps/usage/history` - Usage history

## Configuration

### Required Environment Variables (backend/.env)
- `OPENAI_API_KEY` - OpenAI API key (required for AI agents)
- `TAVILY_API_KEY` - Tavily search API key (required for research)

### Optional Environment Variables
- `CLERK_SECRET_KEY` - Clerk authentication (for API access control)
- `CLERK_PUBLISHABLE_KEY` - Clerk public key (for API access control)
- `DATABASE_URL` - Database URL (defaults to SQLite: `sqlite:///./autoblogger.db`)

### Web Demo Configuration (if using frontend)
Create `frontend/.env.local`:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk public key
- `CLERK_SECRET_KEY` - Clerk secret key
- `NEXT_PUBLIC_API_BASE_URL` - Backend URL (defaults to http://localhost:8000)

## Project Structure

```
autoblogger/
├── backend/                 # Core Python backend service
│   ├── agents/             # AI agent implementations
│   │   ├── research_agent.py    # Web research agent
│   │   ├── writing_agent.py     # Content writing agent
│   │   └── editor_agent.py      # Content editing agent
│   ├── api/                # FastAPI application
│   │   ├── main.py         # API server setup
│   │   └── routers/        # API route handlers
│   ├── apps/               # Application modules
│   │   └── blogger.py      # Blog generation logic
│   ├── core/               # Core services
│   │   ├── llm_services.py # OpenAI integration
│   │   └── state.py        # Workflow state management
│   ├── tools/              # Utility tools
│   │   └── search.py       # Tavily search integration
│   ├── outputs/            # Generated articles and logs
│   ├── tests/              # Comprehensive test suite
│   ├── cli.py              # CLI interface
│   └── scripts/run_api.py  # API server launcher
├── frontend/               # Optional web demo interface
│   ├── src/app/           # Next.js pages
│   ├── src/components/    # React components
│   └── package.json       # Frontend dependencies
├── start.sh               # Backend startup script
└── README.md              # This file
```

## Database Schema

### Users
- User management with Clerk integration
- Credit balance tracking
- Account status and metadata

### Credit Transactions
- Purchase and usage tracking
- Transaction history
- Balance calculations

### App Usage
- Blog generation history
- Status tracking (pending/in_progress/completed/failed)
- Generated content storage

### Usage Logs
- Detailed execution logs
- Agent-level tracking
- Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow existing code conventions
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- **Backend** (primary): Follow Python PEP 8, use Ruff for formatting
- **Frontend** (demo only): Follow Next.js/React conventions, use ESLint
- **Commit messages**: Use conventional commit format
- **Focus**: Backend API and CLI improvements take priority

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **API Documentation**: http://localhost:8000/docs (when API server is running)
- **Development Guide**: Check the CLAUDE.md file for development instructions
- **Issues**: Create an issue on GitHub for bugs or feature requests
- **CLI Help**: Run `uv run python cli.py --help` for CLI usage

## Roadmap (Backend-Focused)

- [ ] Multiple LLM provider support (Anthropic, Gemini, etc.)
- [ ] Advanced agent configuration and templates
- [ ] Bulk generation capabilities via CLI and API
- [ ] Plugin system for custom agents and tools
- [ ] Enhanced API rate limiting and caching
- [ ] Webhook support for integration workflows
- [ ] Advanced search and research capabilities
