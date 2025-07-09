"""Logging configuration for linear_v2 MCP server."""

from logging.config import dictConfig


def setup_logging(level: str = "INFO"):
    """Configure logging."""
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "default": {"class": "logging.StreamHandler", "formatter": "default"}
            },
            "root": {"level": level, "handlers": ["default"]},
        }
    )
