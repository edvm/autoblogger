.PHONY: help format backend frontend all clean install-backend install-frontend install test lint typecheck

# Default target - show help when no target is specified
.DEFAULT_GOAL := help

help:
	@echo "AutoBlogger Makefile"
	@echo "===================="
	@echo ""
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  format         - Format all backend Python files using ruff"
	@echo "  lint           - Run linting on backend code"
	@echo "  typecheck      - Run type checking on backend code"
	@echo "  test           - Run backend tests"
	@echo "  backend        - Start only the backend API server"
	@echo "  frontend       - Start only the frontend development server"
	@echo "  all           - Start both backend and frontend"
	@echo "  install       - Install all dependencies (backend + frontend)"
	@echo "  install-backend - Install backend dependencies"
	@echo "  install-frontend - Install frontend dependencies"
	@echo "  clean         - Clean build artifacts and dependencies"
	@echo ""
	@echo "Requirements:"
	@echo "  - Backend environment file: src/.env (create manually with required API keys)"
	@echo "  - Required API keys: OPENAI_API_KEY, TAVILY_API_KEY, CLERK_SECRET_KEY"
	@echo ""
	@echo "Services:"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - API Docs: http://localhost:8000/docs"

# Format all backend Python files
format:
	@echo "Formatting backend Python files..."
	cd src && uv run ruff format .
	@echo "✓ Backend formatting complete"

# Start only the backend API server
backend:
	@echo "Starting backend API server..."
	@if [ ! -f src/.env ]; then \
		echo "❌ Error: src/.env file not found"; \
		echo "Please copy src/env.example to src/.env and configure your API keys"; \
		exit 1; \
	fi
	cd src && uv run python scripts/run_api.py

# Start only the frontend development server
frontend:
	@echo "Starting frontend development server..."
	@if [ ! -d frontend/node_modules ]; then \
		echo "Installing frontend dependencies..."; \
		cd frontend && npm install; \
	fi
	cd frontend && npm run dev

# Start both backend and frontend
all:
	@echo "Starting AutoBlogger (backend + frontend)..."
	@if [ ! -f src/.env ]; then \
		echo "❌ Error: src/.env file not found"; \
		echo "Please copy src/env.example to src/.env and configure your API keys"; \
		exit 1; \
	fi
	./start.sh

# Install all dependencies
install: install-backend install-frontend
	@echo "✓ All dependencies installed"

# Install backend dependencies
install-backend:
	@echo "Installing backend dependencies..."
	cd src && uv sync
	@echo "✓ Backend dependencies installed"

# Install frontend dependencies  
install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✓ Frontend dependencies installed"

# Clean build artifacts and dependencies
clean:
	@echo "Cleaning build artifacts..."
	rm -rf src/.venv
	rm -rf src/__pycache__
	rm -rf src/**/__pycache__
	rm -rf frontend/node_modules
	rm -rf frontend/.next
	rm -rf src/htmlcov
	rm -rf src/coverage.xml
	rm -rf src/pytest-report.xml
	@echo "✓ Clean complete"

# Run backend tests
test:
	@echo "Running backend tests..."
	cd src && uv run python scripts/run_tests.py
	@echo "✓ Backend tests complete"

# Run linting on backend code
lint:
	@echo "Running backend linting..."
	cd src && uv run ruff check .
	@echo "✓ Backend linting complete"

# Run type checking on backend code
typecheck:
	@echo "Running backend type checking..."
	cd src && uv run mypy .
	@echo "✓ Backend type checking complete"