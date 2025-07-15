#!/usr/bin/env python3
"""
Database initialization script for AutoBlogger.
This script creates all necessary database tables.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.database import create_tables
from configs.logging_config import logger

def main():
    """Initialize the database."""
    try:
        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database tables created successfully!")
        print("✅ Database initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()