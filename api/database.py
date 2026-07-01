"""Shared database configuration helpers for the API layer."""

import os


def get_database_url() -> str:
    """Build the PostgreSQL connection URL from environment variables."""
    host = os.getenv("DATABASE_HOST", "postgres")
    port = os.getenv("DATABASE_PORT", "5432")
    name = os.getenv("DATABASE_NAME", "bi_decision_hub")
    user = os.getenv("DATABASE_USER", "postgres")
    password = os.getenv("DATABASE_PASSWORD", "postgres")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"
