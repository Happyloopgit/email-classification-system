"""Main entry point for email classification API."""
import os
import logging
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("email_classification")

# Set default values for the API server
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "info"
DEFAULT_RELOAD = False


def main():
    """Run the FastAPI application with uvicorn."""
    # Get configuration from environment variables or use defaults
    host = os.getenv("API_HOST", DEFAULT_HOST)
    port = int(os.getenv("API_PORT", DEFAULT_PORT))
    log_level = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)
    reload = os.getenv("API_RELOAD", str(DEFAULT_RELOAD)).lower() == "true"
    
    logger.info(f"Starting email classification API on {host}:{port}")
    
    # Run the uvicorn server
    uvicorn.run(
        "email_classification.api.app:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )


if __name__ == "__main__":
    main()