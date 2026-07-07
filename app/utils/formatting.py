"""Formatting helpers for dashboard values."""

from __future__ import annotations


def format_currency(value: float | int | None) -> str:
    """Format a revenue or cost value."""
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def format_percentage(value: float | int | None) -> str:
    """Format a percentage value with one decimal place."""
    if value is None:
        return "N/A"
    return f"{value:,.1f}%"


def format_score(value: float | int | None) -> str:
    """Format a generic numeric score."""
    if value is None:
        return "N/A"
    return f"{value:,.1f}"


def format_hours(value: float | int | None) -> str:
    """Format downtime hours."""
    if value is None:
        return "N/A"
    return f"{value:,.0f} hrs"


def format_emissions(value: float | int | None) -> str:
    """Format CO2 emissions in kg or tons, depending on scale."""
    if value is None:
        return "N/A"
    if value >= 1000:
        return f"{value / 1000:,.1f} tCO2"
    return f"{value:,.0f} kg CO2"


def format_number(value: float | int | None) -> str:
    """Format a general numeric value."""
    if value is None:
        return "N/A"
    return f"{value:,.0f}"


def format_metric_value(value: float | int | None, value_format: str) -> str:
    """Dispatch dashboard value formatting by metric type."""
    formatters = {
        "currency": format_currency,
        "percentage": format_percentage,
        "score": format_score,
        "hours": format_hours,
        "emissions": format_emissions,
        "number": format_number,
    }
    formatter = formatters.get(value_format, format_number)
    return formatter(value)
