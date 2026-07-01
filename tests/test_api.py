"""Smoke tests for the API placeholder."""

from api.main import health_check


def test_health_check_response() -> None:
    assert health_check() == {
        "status": "ok",
        "service": "Business Intelligence Decision Hub API",
    }
