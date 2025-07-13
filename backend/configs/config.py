"""
Autoblogger - Generate content on demand using online data in real time.
Copyright (C) 2025  Emiliano Dalla Verde Marcozzi <edvm.inbox@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM Provider Selection
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # Default to OpenAI

# OpenAI Model Configuration
OPENAI_FAST_MODEL = "gpt-4.1-nano-2025-04-14"
OPENAI_LARGE_MODEL = (
    "gpt-4.1-nano-2025-04-14"  # should be powerful enough for editor/writing tasks
)

# Gemini Model Configuration
GEMINI_FAST_MODEL = "gemini-2.5-flash"
GEMINI_LARGE_MODEL = "gemini-2.5-flash"  # Using same model for now

# Dynamic model selection based on provider
FAST_LLM_MODEL = GEMINI_FAST_MODEL if LLM_PROVIDER == "gemini" else OPENAI_FAST_MODEL
LARGE_LLM_MODEL = GEMINI_LARGE_MODEL if LLM_PROVIDER == "gemini" else OPENAI_LARGE_MODEL

# Clerk configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

# Security configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# CORS configuration - secure defaults for production
if ENVIRONMENT == "production":
    ALLOWED_ORIGINS = [
        origin.strip() 
        for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") 
        if origin.strip()
    ]
    if not ALLOWED_ORIGINS:
        raise ValueError("ALLOWED_ORIGINS must be set in production environment")
else:
    # Development defaults
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# --- Validate that keys are set ---
# Note: OPENAI_API_KEY and GEMINI_API_KEY validation is now handled at service level
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env file.")

# Validate LLM provider configuration
if LLM_PROVIDER not in ["openai", "gemini"]:
    raise ValueError(
        f"Invalid LLM_PROVIDER '{LLM_PROVIDER}'. Must be 'openai' or 'gemini'."
    )

# Validate required API key based on provider
if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'.")
elif LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER is 'gemini'.")
