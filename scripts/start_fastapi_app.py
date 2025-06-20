#!/usr/bin/env python3
"""Start the FastAPI application
"""

import logging
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            f"fastapi_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    try:
        # Import uvicorn here to avoid circular imports
        import uvicorn

        # Get port from environment or use default
        port = int(os.environ.get("PORT", 8000))

        # Get host from environment or use default
        host = os.environ.get("HOST", "0.0.0.0")

        # Get reload flag from environment or use default
        reload = os.environ.get("RELOAD", "true").lower() == "true"

        # Log startup
        logger.info(f"Starting FastAPI application on {host}:{port}")
        logger.info(f"Reload: {reload}")

        # Start uvicorn server
        uvicorn.run(
            "backend.app.fastapi_app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )

        return 0
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
        return 130
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
