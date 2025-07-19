"""Logging configuration for the application."""

import logging
import sys
from typing import Optional

from src.config import settings


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Setup and configure logger.
    
    Args:
        name: Logger name
        level: Log level (optional, uses config default if not provided)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(settings.log_format)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


# Create default loggers
app_logger = setup_logger("felchat")
websocket_logger = setup_logger("felchat.websocket")
chat_logger = setup_logger("felchat.chat")
user_logger = setup_logger("felchat.users") 