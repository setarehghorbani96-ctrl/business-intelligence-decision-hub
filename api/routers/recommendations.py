"""Recommendation endpoints backed by decision-support views."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.models.schemas import QueryFilters, ViewResponse
from api.routers.kpis import get_kpi_service, get_query_filters
from api.services.kpi_service import KpiService


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/actions", response_model=ViewResponse)
def get_recommended_actions(
    filters: QueryFilters = Depends(get_query_filters),
    service: KpiService = Depends(get_kpi_service),
) -> ViewResponse:
    """Return prioritized management recommendations."""
    return service.get_recommendations(filters)
