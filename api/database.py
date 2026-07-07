"""Shared database configuration helpers for the API layer."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class DatabaseSettings:
    """Environment-backed PostgreSQL settings for the API."""

    host: str = "postgres"
    port: int = 5432
    name: str = "bi_decision_hub"
    user: str = "postgres"
    password: str = "postgres"

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        """Load database settings from environment variables."""
        return cls(
            host=os.getenv("DATABASE_HOST", "postgres"),
            port=int(os.getenv("DATABASE_PORT", "5432")),
            name=os.getenv("DATABASE_NAME", "bi_decision_hub"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres"),
        )

    def url(self) -> str:
        """Build the SQLAlchemy connection URL."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    def safe_url(self) -> str:
        """Return a log-safe connection URL with the password masked."""
        return (
            f"postgresql+psycopg2://{self.user}:***"
            f"@{self.host}:{self.port}/{self.name}"
        )

    def target_label(self) -> str:
        """Return a compact database label for diagnostics."""
        return f"{self.host}:{self.port}/{self.name}"


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Return cached environment-backed database settings."""
    return DatabaseSettings.from_env()


@lru_cache
def get_engine() -> Engine:
    """Create a reusable SQLAlchemy engine."""
    settings = get_database_settings()
    return create_engine(
        settings.url(),
        future=True,
        pool_pre_ping=True,
    )


def get_database_url() -> str:
    """Return the SQLAlchemy connection URL."""
    return get_database_settings().url()


def ping_database(engine: Engine | None = None) -> None:
    """Raise if the database is unavailable."""
    active_engine = engine or get_engine()
    with active_engine.connect() as connection:
        connection.execute(text("SELECT 1"))
