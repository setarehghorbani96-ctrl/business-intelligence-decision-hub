"""Minimal FastAPI application for the project foundation."""

from fastapi import FastAPI

app = FastAPI(title="Business Intelligence Decision Hub API")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a simple health response for local verification."""
    return {
        "status": "ok",
        "service": "Business Intelligence Decision Hub API",
    }
