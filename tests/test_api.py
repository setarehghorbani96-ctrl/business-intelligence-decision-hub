"""Contract and endpoint tests for the FastAPI KPI layer."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from api.main import app
from api.models.schemas import QueryFilters, ViewResponse
from api.routers.health import health_check
from api.routers.kpis import get_kpi_service
from api.services.kpi_service import KPI_VIEW_MAP
from api.services.query_service import build_select_query


class StubKpiService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, QueryFilters]] = []

    def get_kpi_view(self, name: str, filters: QueryFilters) -> ViewResponse:
        self.calls.append((name, filters))
        return ViewResponse(
            view=KPI_VIEW_MAP[name],
            filters=filters,
            row_count=1,
            data=[
                {
                    "year": 2025,
                    "month": 1,
                    "region_name": filters.region or "North-West",
                    "total_revenue": 1234567.89,
                }
            ],
        )

    def get_recommendations(self, filters: QueryFilters) -> ViewResponse:
        self.calls.append(("recommendations", filters))
        return ViewResponse(
            view="vw_decision_recommendations",
            filters=filters,
            row_count=1,
            data=[
                {
                    "year": 2025,
                    "month": 6,
                    "region_name": filters.region or "Islands",
                    "recommended_action": "Increase dispatch coverage.",
                    "priority_score": 98.5,
                }
            ],
        )


@pytest.fixture
def client() -> Any:
    service = StubKpiService()
    app.dependency_overrides[get_kpi_service] = lambda: service
    try:
        yield TestClient(app), service
    finally:
        app.dependency_overrides.clear()


def test_health_check_function_response() -> None:
    assert health_check().model_dump() == {
        "status": "ok",
        "service": "Business Intelligence Decision Hub API",
    }


def test_health_endpoint_exists(client: Any) -> None:
    api_client, _service = client

    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Business Intelligence Decision Hub API",
    }


def test_database_health_endpoint_returns_503_when_database_fails(
    client: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_client, _service = client

    def raise_connection_error() -> None:
        raise OperationalError("SELECT 1", {}, Exception("database unavailable"))

    monkeypatch.setattr("api.routers.health.ping_database", raise_connection_error)

    response = api_client.get("/health/database")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database connection unavailable."}


def test_approved_view_protection() -> None:
    with pytest.raises(ValueError, match="not approved"):
        build_select_query(
            "vw_not_allowed",
            QueryFilters(limit=100),
        )


def test_executive_endpoint_returns_dashboard_ready_response(client: Any) -> None:
    api_client, service = client

    response = api_client.get("/kpis/executive?year=2025&region=North-West")

    assert response.status_code == 200
    body = response.json()
    assert body["view"] == "vw_executive_kpis"
    assert body["filters"] == {
        "year": 2025,
        "month": None,
        "region": "North-West",
        "limit": 100,
    }
    assert body["row_count"] == 1
    assert isinstance(body["data"], list)
    assert body["data"][0]["region_name"] == "North-West"
    assert service.calls[0][0] == "executive"


def test_limit_defaults_to_100(client: Any) -> None:
    api_client, service = client

    response = api_client.get("/kpis/finance")

    assert response.status_code == 200
    assert service.calls[0][1].limit == 100


def test_invalid_limit_is_rejected(client: Any) -> None:
    api_client, _service = client

    response = api_client.get("/recommendations/actions?limit=1001")

    assert response.status_code == 422
