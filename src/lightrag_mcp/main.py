"""
Entry point for LightRAG MCP server.
"""

import logging
import os
import sys

from lightrag_mcp import config
from lightrag_mcp.server import mcp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """Main function for server startup."""
    try:
        # Setting up logging level
        log_level = getattr(logging, "INFO")
        logging.getLogger().setLevel(log_level)

        # Setting environment variables to increase timeouts
        os.environ["STARLETTE_KEEP_ALIVE_TIMEOUT"] = str(config.TIMEOUT)
        os.environ["UVICORN_TIMEOUT_KEEP_ALIVE"] = str(config.TIMEOUT)

        # Starting MCP server
        logger.info("Starting LightRAG MCP server")
        logger.info(f"Timeout set: {config.TIMEOUT} seconds")
        logger.info(
            f"LightRAG API server is expected to be already running and available at: {config.LIGHTRAG_API_BASE_URL}"
        )
        mcp.run(transport="stdio")

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Error starting server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
