"""Reusable Plotly chart helpers for the executive dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px


def _valid_chart_frame(dataframe: pd.DataFrame, required_columns: set[str]) -> bool:
    """Check whether a dataframe has the columns needed for charting."""
    return not dataframe.empty and required_columns.issubset(dataframe.columns)


def _apply_chart_layout(
    figure: Any,
    *,
    title: str,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
) -> Any:
    """Apply a consistent layout across dashboard charts."""
    figure.update_layout(
        title=title,
        template="plotly_white",
        height=340,
        margin=dict(l=16, r=16, t=56, b=16),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    if xaxis_title is not None:
        figure.update_xaxes(title=xaxis_title)
    if yaxis_title is not None:
        figure.update_yaxes(title=yaxis_title)
    return figure


def build_line_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    color_column: str | None = None,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
) -> Any | None:
    """Build a line chart from a dataframe."""
    required_columns = {x, y}
    if color_column is not None:
        required_columns.add(color_column)
    if not _valid_chart_frame(dataframe, required_columns):
        return None

    figure = px.line(
        dataframe,
        x=x,
        y=y,
        color=color_column,
        markers=True,
    )
    if color_column is None and color is not None:
        figure.update_traces(line=dict(color=color, width=3), marker=dict(size=8))
    else:
        figure.update_traces(line=dict(width=3), marker=dict(size=7))
    return _apply_chart_layout(
        figure,
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
    )


def build_bar_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    color_column: str | None = None,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
) -> Any | None:
    """Build a vertical bar chart from a dataframe."""
    required_columns = {x, y}
    if color_column is not None:
        required_columns.add(color_column)
    if not _valid_chart_frame(dataframe, required_columns):
        return None

    figure = px.bar(dataframe, x=x, y=y, color=color_column)
    if color_column is None and color is not None:
        figure.update_traces(marker_color=color)
    return _apply_chart_layout(
        figure,
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
    )


def build_horizontal_bar_chart(
    dataframe: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    color_column: str | None = None,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
) -> Any | None:
    """Build a horizontal bar chart from a dataframe."""
    required_columns = {x, y}
    if color_column is not None:
        required_columns.add(color_column)
    if not _valid_chart_frame(dataframe, required_columns):
        return None

    figure = px.bar(dataframe, x=x, y=y, color=color_column, orientation="h")
    if color_column is None and color is not None:
        figure.update_traces(marker_color=color)
    return _apply_chart_layout(
        figure,
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
    )
