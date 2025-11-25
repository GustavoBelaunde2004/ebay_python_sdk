"""Utility functions for eBay SDK."""

import logging
from typing import Any

# Configure logger for SDK
logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for the eBay SDK.

    Args:
        level: Logging level (default: INFO)
    """
    # TODO: Configure logging format and handler
    # TODO: Set up console handler with appropriate format
    # TODO: Set logging level
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def sanitize_credentials(credentials: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize credentials dictionary for logging (remove sensitive data).

    Args:
        credentials: Dictionary potentially containing sensitive data

    Returns:
        Sanitized dictionary with sensitive values masked
    """
    # TODO: Create copy of credentials
    # TODO: Mask sensitive fields (client_secret, access_token, etc.)
    # TODO: Return sanitized dict
    sanitized = credentials.copy()
    for key in ["client_secret", "access_token", "refresh_token"]:
        if key in sanitized:
            sanitized[key] = "***REDACTED***"
    return sanitized


def validate_sandbox_flag(sandbox: bool) -> bool:
    """
    Validate and normalize sandbox flag.

    Args:
        sandbox: Sandbox flag value

    Returns:
        Normalized boolean value
    """
    return bool(sandbox)


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error message with optional context.

    Args:
        error: Exception object
        context: Additional context string

    Returns:
        Formatted error message
    """
    message = str(error)
    if context:
        message = f"{context}: {message}"
    return message

