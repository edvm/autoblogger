#!/bin/bash

# AutoBlogger Startup Script
# This script exports environment variables and starts both backend and frontend

set -e

echo "🚀 Starting AutoBlogger..."

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

# Frontend environment variables
echo -e "${BLUE}📦 Setting frontend environment variables...${NC}"
export NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="${CLERK_PUBLISHABLE_KEY}"
export CLERK_SECRET_KEY="${CLERK_SECRET_KEY}"
export NEXT_PUBLIC_API_BASE_URL="http://dev.orb.local:8000"
echo -e "${GREEN}✅ Frontend environment variables set${NC}"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${BLUE}🔧 Starting backend API server...${NC}"
cd backend
uv run python run_api.py &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait a moment for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}🎨 Starting frontend development server...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}🎉 AutoBlogger is now running!${NC}"
echo -e "${BLUE}📍 Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}📍 Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}📍 API Documentation: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for background processes
wait