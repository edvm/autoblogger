# AutoBlogger

🤖 An AI-powered full-stack blog generation platform that creates high-quality articles using a multi-agent workflow system.

## Overview

AutoBlogger combines advanced AI agents with modern web technologies to automatically generate well-researched, professionally written blog posts. The system uses specialized agents for research, writing, and editing to produce comprehensive articles on any topic.

### Key Features

- **Multi-Agent AI System**: Specialized agents for research, writing, and editing
- **Web Research Integration**: Real-time web search using Tavily API
- **Professional Web Interface**: Modern Next.js frontend with authentication
- **Credit-Based System**: User management with credit tracking
- **Real-Time Updates**: Live status updates during blog generation
- **Multiple Output Formats**: Markdown files with detailed logs
- **Dark/Light Mode**: Full theme support
- **Responsive Design**: Works on desktop, tablet, and mobile

## Architecture

### Backend (Python)
- **Framework**: FastAPI with SQLAlchemy
- **AI Integration**: OpenAI GPT models
- **Search**: Tavily web search API
- **Authentication**: Clerk JWT validation
- **Database**: SQLite with user and credit management
- **Agent System**: Multi-agent workflow with state management

### Frontend (Next.js)
- **Framework**: Next.js 15 with App Router
- **Authentication**: Clerk integration
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React with API client
- **Components**: Radix UI primitives with custom styling

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- OpenAI API key
- Tavily API key
- Clerk account (for web interface)

### 1. Environment Setup

Before anything, be sure you have `uv` and `node` + `npm` installed. If not, here's how:
```bash
# Install uv:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install nvm (then node):
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
nvm install --lts
```
Finally, `make install`.

```bash
# Clone the repository
git clone <repository-url>
cd autoblogger-py

# Backend environment
cp backend/env.example backend/.env
# Edit backend/.env with your API keys:
# OPENAI_API_KEY=sk-...
# TAVILY_API_KEY=tvly-...
# CLERK_SECRET_KEY=sk_test_...
# CLERK_PUBLISHABLE_KEY=pk_test_...
```

### 2. Backend Setup

```bash
# Install dependencies
cd backend
uv sync

# Run CLI directly (optional)
uv run python cli.py "Your blog topic here"

# Or start the API server
uv run python run_api.py
```

### 3. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### 4. Quick Start (Both Services)

```bash
# From project root - starts both backend and frontend
./start.sh
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

### CLI Mode
Generate blog posts directly from command line:

```bash
cd backend
uv run python cli.py "Latest developments in AI technology"
```

Generated articles are saved to `backend/outputs/` as:
- `{topic}.md` - The final article
- `{topic}_log.json` - Complete workflow state and logs

### Web Interface
1. Sign up/Login at http://localhost:3000
2. Navigate to Dashboard
3. Enter your blog topic
4. Monitor real-time generation progress
5. View and download completed articles

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

### Backend Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest backend/tests/

# Code quality
uv run ruff check backend/
uv run ruff format backend/

# Start API server
uv run python backend/run_api.py

# CLI usage
uv run python backend/cli.py "Your topic"
```

### Frontend Commands

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Linting
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

### Backend Environment Variables
- `OPENAI_API_KEY` - OpenAI API key (required)
- `TAVILY_API_KEY` - Tavily search API key (required)
- `CLERK_SECRET_KEY` - Clerk authentication (required for API)
- `CLERK_PUBLISHABLE_KEY` - Clerk public key (required for API)
- `DATABASE_URL` - Database URL (optional, defaults to SQLite)

### Frontend Environment Variables
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk public key
- `CLERK_SECRET_KEY` - Clerk secret key
- `NEXT_PUBLIC_API_BASE_URL` - Backend API URL (defaults to http://localhost:8000)

## Project Structure

```
autoblogger-py/
├── backend/                 # Python backend
│   ├── agents/             # AI agent implementations
│   ├── api/                # FastAPI application
│   ├── apps/               # Application modules
│   ├── configs/            # Configuration files
│   ├── core/               # Core services (LLM, state)
│   ├── tools/              # Utility tools (search)
│   ├── outputs/            # Generated articles
│   ├── tests/              # Test suite
│   ├── cli.py              # CLI interface
│   └── run_api.py          # API server
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities and API client
│   ├── package.json       # Frontend dependencies
│   └── next.config.ts     # Next.js configuration
├── start.sh               # Quick start script
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
- Backend: Follow Python PEP 8, use Ruff for formatting
- Frontend: Follow Next.js/React conventions, use ESLint
- Commit messages: Use conventional commit format

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Documentation: Check the CLAUDE.md files in each directory
- Issues: Create an issue on GitHub
- API Documentation: http://localhost:8000/docs when running

## Roadmap

- [ ] Multiple LLM provider support
- [ ] Advanced article templates
- [ ] Bulk generation capabilities
- [ ] Social media integration
- [ ] Advanced analytics dashboard
- [ ] Plugin system for custom agents
