"""FastAPI client helpers for the Streamlit dashboard."""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_API_PORT = "8000"
LOCAL_FALLBACK_HOST = "localhost"


def clear_api_cache() -> None:
    """Clear cached API responses."""
    _request_json_cached.clear()


def get_executive_kpis(
    year: int | None = None,
    month: int | None = None,
    region: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Fetch executive KPI data from FastAPI."""
    return _fetch_endpoint(
        "/kpis/executive",
        year=year,
        month=month,
        region=region,
        limit=limit,
    )


def get_finance_kpis(
    year: int | None = None,
    month: int | None = None,
    region: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Fetch finance KPI data from FastAPI."""
    return _fetch_endpoint(
        "/kpis/finance",
        year=year,
        month=month,
        region=region,
        limit=limit,
    )


def get_operations_kpis(
    year: int | None = None,
    month: int | None = None,
    region: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Fetch operations KPI data from FastAPI."""
    return _fetch_endpoint(
        "/kpis/operations",
        year=year,
        month=month,
        region=region,
        limit=limit,
    )


def get_recommendations(
    year: int | None = None,
    month: int | None = None,
    region: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Fetch management recommendations from FastAPI."""
    return _fetch_endpoint(
        "/recommendations/actions",
        year=year,
        month=month,
        region=region,
        limit=limit,
    )


def _fetch_endpoint(endpoint: str, **filters: Any) -> dict[str, Any]:
    """Fetch a KPI endpoint with Docker-aware localhost fallback."""
    params = {key: value for key, value in filters.items() if value is not None}
    params_items = tuple(sorted(params.items()))
    attempted_urls: list[str] = []

    for base_url in _candidate_base_urls():
        attempted_urls.append(base_url)
        try:
            return _request_json_cached(base_url, endpoint, params_items)
        except requests.HTTPError as error:
            status_code = error.response.status_code if error.response is not None else None
            if status_code == 503:
                _show_error_once(
                    "api_database_unavailable",
                    (
                        "The API is running, but the database is not available. "
                        "Please make sure data has been loaded and KPI views have been applied."
                    ),
                )
                return _empty_response(endpoint, params)
            break
        except requests.RequestException:
            continue

    _show_error_once(
        "api_unavailable",
        (
            "API is not available. Please start Docker Compose or confirm FastAPI is reachable "
            f"at one of these URLs: {', '.join(attempted_urls)}."
        ),
    )
    return _empty_response(endpoint, params)


def _candidate_base_urls() -> list[str]:
    """Return the configured API URL and a localhost fallback."""
    api_host = os.getenv("API_HOST", "api").strip() or "api"
    api_port = os.getenv("API_PORT", DEFAULT_API_PORT).strip() or DEFAULT_API_PORT
    configured_url = f"http://{api_host}:{api_port}"
    fallback_url = f"http://{LOCAL_FALLBACK_HOST}:{api_port}"

    base_urls = [configured_url]
    if configured_url != fallback_url:
        base_urls.append(fallback_url)
    return base_urls


@st.cache_data(ttl=300, show_spinner=False)
def _request_json_cached(
    base_url: str,
    endpoint: str,
    params_items: tuple[tuple[str, Any], ...],
) -> dict[str, Any]:
    """Execute a cached HTTP GET request and return JSON payloads."""
    response = requests.get(
        f"{base_url}{endpoint}",
        params=dict(params_items),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _show_error_once(key: str, message: str) -> None:
    """Display a Streamlit error once per session state key."""
    shown_messages = st.session_state.setdefault("_shown_api_messages", set())
    if key in shown_messages:
        return
    st.error(message)
    shown_messages.add(key)


def _empty_response(endpoint: str, filters: dict[str, Any]) -> dict[str, Any]:
    """Return an empty response matching the API envelope shape."""
    return {
        "view": endpoint.strip("/"),
        "filters": filters,
        "row_count": 0,
        "data": [],
    }
