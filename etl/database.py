"""Database helpers for the NovaEnergy ETL pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL


@dataclass(frozen=True)
class DatabaseSettings:
    """Database connection settings loaded from environment variables."""

    host: str
    port: int
    name: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        """Build settings from the expected environment variables."""
        return cls(
            host=os.getenv("DATABASE_HOST", "localhost"),
            port=int(os.getenv("DATABASE_PORT", "5432")),
            name=os.getenv("DATABASE_NAME", "bi_decision_hub"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres"),
        )

    def as_url(self) -> URL:
        """Return a SQLAlchemy URL for the PostgreSQL connection."""
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )

    def safe_url(self) -> str:
        """Return a sanitized URL suitable for logs."""
        return self.as_url().render_as_string(hide_password=True)

    def target_label(self) -> str:
        """Return a short human-readable connection target."""
        return f"{self.host}:{self.port}/{self.name}"


def create_database_engine(settings: DatabaseSettings | None = None) -> Engine:
    """Create a SQLAlchemy engine for the configured PostgreSQL database."""
    database_settings = settings or DatabaseSettings.from_env()
    return create_engine(database_settings.as_url(), future=True)
