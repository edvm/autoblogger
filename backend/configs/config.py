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
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM Model Configuration
# We can use a faster model for summary and a powerful one for generation
FAST_LLM_MODEL = "gpt-4.1-nano-2025-04-14"
LARGE_LLM_MODEL = (
    "gpt-4.1-nano-2025-04-14"  # should be powerful enough for editor/writing tasks
)

# Clerk configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

# --- Validate that keys are set ---
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file.")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env file.")
