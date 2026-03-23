"""Platform-wide configuration. Loaded always by Wheelwright agents."""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "platform")
    pool_size: int = 20
    max_overflow: int = 10


@dataclass
class CacheConfig:
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    ttl_seconds: int = 3600
    max_connections: int = 50


@dataclass
class MessageQueueConfig:
    broker_url: str = os.getenv("MQ_BROKER", "amqp://localhost")
    prefetch_count: int = 10
    retry_limit: int = 3
    dead_letter_exchange: str = "dlx"


@dataclass
class PlatformConfig:
    environment: str = os.getenv("PLATFORM_ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "changeme")
    api_version: str = "v2"
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    mq: MessageQueueConfig = field(default_factory=MessageQueueConfig)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


config = PlatformConfig()
