.PHONY: help run-api format

help:
	@echo "Available commands:"
	@echo "  run-api    Start the FastAPI server"
	@echo "  format     Format Python files with ruff"
	@echo "  help       Show this help message"

run-api:
	uv run python run_api.py

format:
	uv run ruff format

# Default target
.DEFAULT_GOAL := help