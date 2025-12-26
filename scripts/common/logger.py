"""
Logging utilities for cloud engineering scripts.

Provides consistent logging configuration across all scripts.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Log level (DEBUG, INFO, WARNING, ERROR). Defaults to INFO
        log_file: Optional file path to write logs to

    Returns:
        Configured logger instance
    """
    # Get log level from argument or environment
    if level is None:
        import os
        level = os.environ.get('LOG_LEVEL', 'INFO')

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
