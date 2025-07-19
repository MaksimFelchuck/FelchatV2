"""Application configuration settings."""

import os
from typing import Any


class Settings:
    """Application settings with environment variable support."""
    
    def __init__(self):
        # Database settings
        self.database_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://felchat:felchat@db:5432/felchat")
        
        # Redis settings
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        
        # Environment
        self.env = os.getenv("ENV", "prod")
        
        # WebSocket settings
        self.websocket_ping_interval = int(os.getenv("WEBSOCKET_PING_INTERVAL", "20"))
        self.websocket_ping_timeout = int(os.getenv("WEBSOCKET_PING_TIMEOUT", "20"))
        
        # Chat settings
        self.max_message_length = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))
        self.chat_history_limit = int(os.getenv("CHAT_HISTORY_LIMIT", "50"))
        self.message_retention_minutes = int(os.getenv("MESSAGE_RETENTION_MINUTES", "30"))
        
        # Security settings
        self.session_cookie_name = os.getenv("SESSION_COOKIE_NAME", "user_id")
        self.session_cookie_httponly = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
        self.session_cookie_secure = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
        
        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Server settings
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.reload = os.getenv("RELOAD", "true").lower() == "true"


# Global settings instance
settings = Settings() 