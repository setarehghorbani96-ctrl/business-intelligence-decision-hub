"""API router modules."""

from api.routers.health import router as health_router
from api.routers.kpis import get_kpi_service, get_query_filters, router as kpis_router
from api.routers.recommendations import router as recommendations_router

__all__ = [
    "get_kpi_service",
    "get_query_filters",
    "health_router",
    "kpis_router",
    "recommendations_router",
]
