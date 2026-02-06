"""
Configuration management for the e-commerce API.
Handles app settings, environment variables, and feature flags.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    username: str = os.getenv("DB_USER", "ecommerce_user")
    password: str = os.getenv("DB_PASSWORD", "default_password")
    database: str = os.getenv("DB_NAME", "ecommerce_db")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))


@dataclass
class JWTConfig:
    """JWT configuration for authentication."""
    secret_key: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    expiration_minutes: int = 60
    refresh_expiration_days: int = 7


@dataclass
class APIConfig:
    """General API configuration."""
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    max_request_size: int = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    enabled: bool = True
    requests_per_minute: int = 100
    burst_size: int = 20


class AppConfig:
    """Main application configuration container."""

    def __init__(self):
        self.database = DatabaseConfig()
        self.jwt = JWTConfig()
        self.api = APIConfig()
        self.rate_limit = RateLimitConfig()

    def get_database_url(self) -> str:
        """Build database connection URL."""
        return (
            f"postgresql://{self.database.username}:"
            f"{self.database.password}@{self.database.host}:"
            f"{self.database.port}/{self.database.database}"
        )


# Global config instance
config = AppConfig()
