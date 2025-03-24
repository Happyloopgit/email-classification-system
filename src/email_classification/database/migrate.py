#!/usr/bin/env python
"""
Run database migrations.

Usage:
    python -m email_classification.database.migrate
"""

import sys
import logging
from email_classification.utils import setup_logging
from email_classification.database.migrations import run_migrations

def main():
    """Run database migrations."""
    # Set up logging
    setup_logging(log_level="INFO")
    logger = logging.getLogger(__name__)
    
    logger.info("Starting database migrations...")
    
    try:
        success = run_migrations()
        
        if success:
            logger.info("Migrations completed successfully.")
            return 0
        else:
            logger.error("Migrations failed.")
            return 1
            
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())