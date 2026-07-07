"""Response and filter schemas for the API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check payload."""

    status: str
    service: str


class DatabaseHealthResponse(BaseModel):
    """Database connectivity payload."""

    status: str
    database: str


class QueryFilters(BaseModel):
    """Supported KPI query filters."""

    year: int | None = None
    month: int | None = Field(default=None, ge=1, le=12)
    region: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)

    def as_dict(self) -> dict[str, Any]:
        """Return model data across supported Pydantic versions."""
        if hasattr(self, "model_dump"):
            return self.model_dump()
        return self.dict()


class ViewResponse(BaseModel):
    """Dashboard-ready response wrapper for KPI views."""

    view: str
    filters: QueryFilters
    row_count: int
    data: list[dict[str, Any]]
