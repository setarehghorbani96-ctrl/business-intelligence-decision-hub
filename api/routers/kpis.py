"""KPI endpoints backed by approved PostgreSQL views."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from api.models.schemas import QueryFilters, ViewResponse
from api.services.kpi_service import KpiService


router = APIRouter(prefix="/kpis", tags=["kpis"])


def get_kpi_service() -> KpiService:
    """Return the shared KPI service."""
    return KpiService()


def get_query_filters(
    year: int | None = Query(default=None, description="Filter by calendar year."),
    month: int | None = Query(
        default=None,
        ge=1,
        le=12,
        description="Filter by calendar month.",
    ),
    region: str | None = Query(default=None, description="Filter by region name."),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of rows to return.",
    ),
) -> QueryFilters:
    """Normalize route query parameters into a shared filter model."""
    return QueryFilters(year=year, month=month, region=region, limit=limit)


@router.get("/executive", response_model=ViewResponse)
def get_executive_kpis(
    filters: QueryFilters = Depends(get_query_filters),
    service: KpiService = Depends(get_kpi_service),
) -> ViewResponse:
    """Return executive KPI rollups."""
    return service.get_kpi_view("executive", filters)


@router.get("/finance", response_model=ViewResponse)
def get_finance_kpis(
    filters: QueryFilters = Depends(get_query_filters),
    service: KpiService = Depends(get_kpi_service),
) -> ViewResponse:
    """Return finance KPI rollups."""
    return service.get_kpi_view("finance", filters)


@router.get("/operations", response_model=ViewResponse)
def get_operations_kpis(
    filters: QueryFilters = Depends(get_query_filters),
    service: KpiService = Depends(get_kpi_service),
) -> ViewResponse:
    """Return operations KPI rollups."""
    return service.get_kpi_view("operations", filters)


@router.get("/assets", response_model=ViewResponse)
def get_asset_kpis(
    filters: QueryFilters = Depends(get_query_filters),
    service: KpiService = Depends(get_kpi_service),
) -> ViewResponse:
    """Return asset KPI rollups."""
    return service.get_kpi_view("assets", filters)


@router.get("/customers", response_model=ViewResponse)
def get_customer_kpis(
    filters: QueryFilters = Depends(get_query_filters),
    service: KpiService = Depends(get_kpi_service),
) -> ViewResponse:
    """Return customer KPI rollups."""
    return service.get_kpi_view("customers", filters)


@router.get("/esg", response_model=ViewResponse)
def get_esg_kpis(
    filters: QueryFilters = Depends(get_query_filters),
    service: KpiService = Depends(get_kpi_service),
) -> ViewResponse:
    """Return ESG KPI rollups."""
    return service.get_kpi_view("esg", filters)
