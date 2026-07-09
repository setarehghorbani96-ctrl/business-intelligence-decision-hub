"""Reusable Plotly chart helpers for the executive dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
from pandas.api.types import is_datetime64_any_dtype


DEFAULT_CHART_HEIGHT = 390
DEFAULT_BAR_HEIGHT = 360
DEFAULT_TREND_HEIGHT = 470
PERIOD_TICK_ANGLE = -40
LEGEND_FONT_SIZE = 12
CHART_FONT_COLOR = "#0F172A"
AXIS_FONT_COLOR = "#334155"
GRID_COLOR = "rgba(15, 23, 42, 0.08)"
REGION_COLOR_MAP = {
    "North-West": "#155EEF",
    "North-East": "#12B76A",
    "Central": "#F79009",
    "South": "#D92D20",
    "Islands": "#7A5AF8",
}


def _valid_chart_frame(dataframe: pd.DataFrame, required_columns: set[str]) -> bool:
    """Check whether a dataframe has the columns needed for charting."""
    return not dataframe.empty and required_columns.issubset(dataframe.columns)


def _tick_values_for_dates(dataframe: pd.DataFrame, x: str) -> list[pd.Timestamp] | None:
    """Return a readable subset of monthly ticks for dense trend charts."""
    if x not in dataframe.columns or not is_datetime64_any_dtype(dataframe[x]):
        return None

    unique_dates = pd.Series(dataframe[x]).dropna().drop_duplicates().sort_values().tolist()
    if len(unique_dates) <= 6:
        return unique_dates
    if len(unique_dates) <= 12:
        return unique_dates[::2]
    return unique_dates[::3]


def _legend_layout(style: str) -> dict[str, Any]:
    """Return the legend layout for a chart style."""
    if style == "external_right":
        return {
            "orientation": "v",
            "yanchor": "top",
            "y": 1,
            "xanchor": "left",
            "x": 1.02,
            "title_text": "",
            "font": {"size": LEGEND_FONT_SIZE, "color": CHART_FONT_COLOR},
            "itemsizing": "constant",
            "bgcolor": "rgba(255,255,255,0.92)",
            "bordercolor": "rgba(15, 23, 42, 0.08)",
            "borderwidth": 1,
            "tracegroupgap": 6,
        }
    if style == "hidden":
        return {"title_text": ""}
    return {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "left",
        "x": 0,
        "title_text": "",
        "font": {"size": LEGEND_FONT_SIZE, "color": CHART_FONT_COLOR},
        "bgcolor": "rgba(255,255,255,0.85)",
    }


def _apply_chart_layout(
    figure: Any,
    *,
    title: str,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
    height: int = DEFAULT_CHART_HEIGHT,
    tickangle: int | None = None,
    tickvals: list[pd.Timestamp] | None = None,
    legend_style: str = "top",
    showlegend: bool = True,
) -> Any:
    """Apply a consistent layout across dashboard charts."""
    right_margin = 150 if legend_style == "external_right" and showlegend else 24
    bottom_margin = 78 if tickangle is not None else 30
    figure.update_layout(
        title=dict(text=title, x=0.01, xanchor="left", font=dict(size=17, color=CHART_FONT_COLOR)),
        template="plotly_white",
        height=height,
        margin=dict(l=55, r=right_margin, t=82, b=bottom_margin),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=CHART_FONT_COLOR, size=12),
        legend=_legend_layout(legend_style),
        showlegend=showlegend,
        hovermode="x unified",
    )
    figure.update_xaxes(
        showgrid=False,
        automargin=True,
        tickfont=dict(size=11, color=AXIS_FONT_COLOR),
        title_font=dict(size=12, color=CHART_FONT_COLOR),
        title_standoff=10,
    )
    figure.update_yaxes(
        gridcolor=GRID_COLOR,
        automargin=True,
        tickfont=dict(size=11, color=AXIS_FONT_COLOR),
        title_font=dict(size=12, color=CHART_FONT_COLOR),
        title_standoff=10,
    )
    if xaxis_title is not None:
        figure.update_xaxes(title=xaxis_title)
    if yaxis_title is not None:
        figure.update_yaxes(title=yaxis_title)
    if tickangle is not None:
        figure.update_xaxes(tickangle=tickangle)
    if tickvals is not None:
        figure.update_xaxes(tickmode="array", tickvals=tickvals)
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

    color_map = REGION_COLOR_MAP if color_column == "region_name" else None
    figure = px.line(
        dataframe,
        x=x,
        y=y,
        color=color_column,
        color_discrete_map=color_map,
        markers=True,
    )
    if color_column is None and color is not None:
        figure.update_traces(line=dict(color=color, width=3), marker=dict(size=7))
        showlegend = False
        legend_style = "hidden"
    else:
        figure.update_traces(line=dict(width=3), marker=dict(size=6))
        series_count = dataframe[color_column].nunique(dropna=True) if color_column else 1
        showlegend = series_count > 1
        legend_style = "external_right" if showlegend else "hidden"

    tickvals = _tick_values_for_dates(dataframe, x)
    if is_datetime64_any_dtype(dataframe[x]):
        figure.update_xaxes(tickformat="%b %Y", hoverformat="%b %Y")

    return _apply_chart_layout(
        figure,
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        height=DEFAULT_TREND_HEIGHT,
        tickangle=PERIOD_TICK_ANGLE,
        tickvals=tickvals,
        legend_style=legend_style,
        showlegend=showlegend,
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
        height=DEFAULT_BAR_HEIGHT,
        tickangle=PERIOD_TICK_ANGLE if x == "period_label" else None,
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
        height=DEFAULT_BAR_HEIGHT,
    )
