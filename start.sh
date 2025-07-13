#!/bin/bash

# AutoBlogger Backend Startup Script
# This script exports environment variables and starts the backend API service

set -e

echo "🚀 Starting AutoBlogger Backend Service..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists in backend directory
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env file not found${NC}"
    echo -e "${YELLOW}Please create backend/.env file with the following variables:${NC}"
    echo "OPENAI_API_KEY=your_openai_key_here"
    echo "TAVILY_API_KEY=your_tavily_key_here"
    echo "CLERK_SECRET_KEY=your_clerk_secret_key_here"
    echo "CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here"
    echo ""
    echo -e "${BLUE}You can copy from backend/env.example and fill in your values${NC}"
    exit 1
fi

# Load backend environment variables
echo -e "${BLUE}📦 Loading backend environment variables...${NC}"
export $(grep -v '^#' backend/.env | xargs)

# Backend environment variables
echo -e "${GREEN}✅ Backend environment variables loaded${NC}"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${BLUE}🔧 Starting backend API server...${NC}"
cd backend
uv run python scripts/run_api.py &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait a moment for backend to start
sleep 3

echo ""
echo -e "${GREEN}🎉 AutoBlogger Backend is now running!${NC}"
echo -e "${BLUE}📍 Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}📍 API Documentation: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the backend service${NC}"

# Wait for background processes
wait