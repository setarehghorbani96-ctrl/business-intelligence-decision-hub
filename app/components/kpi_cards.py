"""Reusable KPI card components for the Streamlit executive dashboard."""

from __future__ import annotations

import streamlit as st

from app.utils.formatting import format_metric_value


def render_kpi_card(
    label: str,
    value: float | int | None,
    value_format: str,
    helper_text: str | None = None,
) -> None:
    """Render a single KPI card with defensive formatting."""
    formatted_value = format_metric_value(value, value_format)
    helper_markup = (
        f'<div class="metric-card-helper">{helper_text}</div>' if helper_text else ""
    )
    st.markdown(
        (
            '<div class="metric-card">'
            f'<div class="metric-card-label">{label}</div>'
            f'<div class="metric-card-value">{formatted_value}</div>'
            f"{helper_markup}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_kpi_grid(metrics: list[dict], *, columns: int = 4) -> None:
    """Render KPI cards across a configurable grid."""
    if not metrics:
        st.info("No KPI metrics are available to display.")
        return

    for start_index in range(0, len(metrics), columns):
        row_columns = st.columns(columns)
        row_metrics = metrics[start_index : start_index + columns]
        for column, metric in zip(row_columns, row_metrics, strict=False):
            with column:
                render_kpi_card(
                    metric.get("label", "Metric"),
                    metric.get("value"),
                    metric.get("format", "number"),
                    metric.get("helper_text"),
                )
