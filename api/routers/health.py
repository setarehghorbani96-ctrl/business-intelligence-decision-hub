"""Health-check endpoints for the API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from api.database import ping_database
from api.models.schemas import DatabaseHealthResponse, HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return the basic service health payload."""
    return HealthResponse(
        status="ok",
        service="Business Intelligence Decision Hub API",
    )


@router.get("/health/database", response_model=DatabaseHealthResponse)
def health_check_database() -> DatabaseHealthResponse:
    """Return database connectivity status."""
    try:
        ping_database()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable.",
        ) from exc

    return DatabaseHealthResponse(status="ok", database="connected")
