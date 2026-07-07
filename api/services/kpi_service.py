"""Service layer for KPI and recommendation endpoints."""

from __future__ import annotations

from sqlalchemy.engine import Engine

from api.database import get_engine
from api.models.schemas import QueryFilters, ViewResponse
from api.services.query_service import RECOMMENDATION_ORDER_BY, fetch_view_rows


KPI_VIEW_MAP = {
    "executive": "vw_executive_kpis",
    "finance": "vw_finance_performance",
    "operations": "vw_operations_performance",
    "assets": "vw_asset_performance",
    "customers": "vw_customer_performance",
    "esg": "vw_esg_performance",
}

RECOMMENDATIONS_VIEW = "vw_decision_recommendations"


class KpiService:
    """Read-only API service for business KPI views."""

    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or get_engine()

    def get_kpi_view(self, name: str, filters: QueryFilters) -> ViewResponse:
        """Return a formatted response for a named KPI surface."""
        view_name = KPI_VIEW_MAP[name]
        return self._build_response(view_name, filters)

    def get_recommendations(self, filters: QueryFilters) -> ViewResponse:
        """Return prioritized decision recommendations."""
        return self._build_response(
            RECOMMENDATIONS_VIEW,
            filters,
            order_by=RECOMMENDATION_ORDER_BY,
        )

    def _build_response(
        self,
        view_name: str,
        filters: QueryFilters,
        *,
        order_by: str | None = None,
    ) -> ViewResponse:
        rows = fetch_view_rows(self.engine, view_name, filters, order_by=order_by)
        return ViewResponse(
            view=view_name,
            filters=filters,
            row_count=len(rows),
            data=rows,
        )
