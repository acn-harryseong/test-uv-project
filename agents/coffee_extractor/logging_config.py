"""
Logging configuration for Coffee Bean Data Extractor Agent.
"""
import logging
import sys


def configure_logging(level: int = logging.INFO, format_string: str | None = None) -> None:
    """
    Configure logging for the Coffee Extractor Agent.

    This function should be called once at application startup to set up
    logging configuration. It's safe to call multiple times - subsequent
    calls will only update the level if the handler already exists.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        format_string: Custom format string for log messages. If None, uses default format.

    Example:
        >>> from agents.coffee_extractor.logging_config import configure_logging
        >>> import logging
        >>> configure_logging(level=logging.DEBUG)
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Get the root logger for this module
    module_logger = logging.getLogger('agents.coffee_extractor')
    module_logger.setLevel(level)

    # Only add handler if one doesn't exist
    if not module_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        module_logger.addHandler(handler)
    else:
        # Update existing handler level
        for handler in module_logger.handlers:
            handler.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the Coffee Extractor Agent.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from agents.coffee_extractor.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    return logging.getLogger(name)
