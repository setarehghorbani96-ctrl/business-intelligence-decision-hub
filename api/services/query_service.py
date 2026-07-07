"""Safe SQL query helpers for approved KPI views."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from api.models.schemas import QueryFilters


APPROVED_VIEWS = frozenset(
    {
        "vw_finance_performance",
        "vw_operations_performance",
        "vw_asset_performance",
        "vw_customer_performance",
        "vw_esg_performance",
        "vw_executive_kpis",
        "vw_decision_recommendations",
    }
)

DEFAULT_ORDER_BY = "year DESC, month DESC, region_name ASC"
RECOMMENDATION_ORDER_BY = "priority_score DESC, year DESC, month DESC, region_name ASC"


def validate_view_name(view_name: str) -> None:
    """Allow only known analytical views."""
    if view_name not in APPROVED_VIEWS:
        raise ValueError(f"View '{view_name}' is not approved for API access.")


def build_select_query(
    view_name: str,
    filters: QueryFilters,
    *,
    order_by: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Build a parameterized query for an approved KPI view."""
    validate_view_name(view_name)

    where_clauses: list[str] = []
    params: dict[str, Any] = {"limit": filters.limit}

    if filters.year is not None:
        where_clauses.append("year = :year")
        params["year"] = filters.year

    if filters.month is not None:
        where_clauses.append("month = :month")
        params["month"] = filters.month

    if filters.region is not None:
        where_clauses.append("region_name = :region")
        params["region"] = filters.region

    query = f"SELECT * FROM {view_name}"
    if where_clauses:
        query = f"{query} WHERE {' AND '.join(where_clauses)}"

    query_order = order_by or DEFAULT_ORDER_BY
    query = f"{query} ORDER BY {query_order} LIMIT :limit"
    return query, params


def fetch_view_rows(
    engine: Engine,
    view_name: str,
    filters: QueryFilters,
    *,
    order_by: str | None = None,
) -> list[dict[str, Any]]:
    """Execute a parameterized SELECT against an approved KPI view."""
    query, params = build_select_query(view_name, filters, order_by=order_by)

    with engine.connect() as connection:
        result = connection.execute(text(query), params)
        rows = result.mappings().all()

    return [_serialize_row(dict(row)) for row in rows]


def _serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert SQLAlchemy row values into JSON-safe values."""
    return {key: _serialize_value(value) for key, value in row.items()}


def _serialize_value(value: Any) -> Any:
    """Normalize database values for JSON responses."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
