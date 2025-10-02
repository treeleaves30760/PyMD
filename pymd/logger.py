"""
Logging configuration for PyMD
Provides structured logging throughout the application
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )

        return super().format(record)


def setup_logger(
    name: str = "pymd",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    colored: bool = True,
) -> logging.Logger:
    """
    Setup and configure a logger for PyMD

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Optional file path for logging to file
        colored: Whether to use colored output for console (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Format
    if colored:
        console_formatter = ColoredFormatter(
            "%(levelname)s | %(name)s | %(message)s", datefmt="%H:%M:%S"
        )
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all debug info

        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger
logger = setup_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with a specific name

    Args:
        name: Logger name (typically module name)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"pymd.{name}")


def set_log_level(level: int):
    """
    Set the global logging level

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


# Convenience functions for common log levels
def enable_debug_logging():
    """Enable debug logging"""
    set_log_level(logging.DEBUG)


def enable_verbose_logging():
    """Enable verbose logging (alias for debug)"""
    enable_debug_logging()


def disable_logging():
    """Disable all logging"""
    set_log_level(logging.CRITICAL + 1)


# Export main functions
__all__ = [
    "setup_logger",
    "get_logger",
    "logger",
    "set_log_level",
    "enable_debug_logging",
    "enable_verbose_logging",
    "disable_logging",
]
