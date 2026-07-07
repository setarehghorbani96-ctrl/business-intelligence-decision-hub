"""Streamlit Executive Command Center for NovaEnergy Services."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.charts import build_bar_chart, build_horizontal_bar_chart, build_line_chart
from app.components.kpi_cards import render_kpi_grid
from app.components.layout import (
    apply_theme,
    render_empty_state,
    render_highlight_box,
    render_page_header,
    render_section_header,
)
from app.utils.api_client import (
    clear_api_cache,
    get_executive_kpis,
    get_finance_kpis,
    get_operations_kpis,
    get_recommendations,
)


PAGE_TITLE = "Business Intelligence Decision Hub"
PAGE_SUBTITLE = "Executive Command Center - NovaEnergy Services"
YEAR_OPTIONS = ["All", 2024, 2025]
MONTH_OPTIONS = ["All", *range(1, 13)]
REGION_OPTIONS = ["North-West", "North-East", "Central", "South", "Islands"]
DATA_LIMIT = 500
RECOMMENDATION_LIMIT = 10


st.set_page_config(page_title=PAGE_TITLE, layout="wide")
apply_theme()


def dataframe_from_response(response: dict) -> pd.DataFrame:
    """Convert the shared API envelope into a dataframe."""
    return pd.DataFrame(response.get("data", []))


def normalize_filter_value(value: str | int) -> int | None:
    """Convert sidebar selectors into API-friendly filter values."""
    return None if value == "All" else int(value)


def normalize_region_selection(selected_regions: list[str]) -> tuple[list[str], bool]:
    """Return selected regions and whether the UI defaulted back to all."""
    if selected_regions:
        return selected_regions, False
    return REGION_OPTIONS.copy(), True


def scope_label(year: int | None, month: int | None, regions: list[str]) -> str:
    """Build a compact scope label for executive summaries."""
    region_scope = ", ".join(regions) if len(regions) <= 3 else f"{len(regions)} regions selected"
    return " | ".join(
        [
            f"Year: {year if year is not None else 'All'}",
            f"Month: {month if month is not None else 'All'}",
            f"Regions: {region_scope}",
        ]
    )


def region_api_filter(selected_regions: list[str]) -> str | None:
    """Use a direct API filter only for single-region views."""
    if len(selected_regions) == 1:
        return selected_regions[0]
    return None


def filter_regions(dataframe: pd.DataFrame, selected_regions: list[str]) -> pd.DataFrame:
    """Filter dashboard dataframes locally when multiple regions are selected."""
    if dataframe.empty or "region_name" not in dataframe.columns:
        return dataframe
    return dataframe[dataframe["region_name"].isin(selected_regions)].copy()


def to_numeric_series(dataframe: pd.DataFrame, column: str) -> pd.Series:
    """Return a numeric series or an empty series when the column is missing."""
    if column not in dataframe.columns:
        return pd.Series(dtype="float64")
    return pd.to_numeric(dataframe[column], errors="coerce")


def average_metric(dataframe: pd.DataFrame, column: str) -> float | None:
    """Safely compute an average metric."""
    series = to_numeric_series(dataframe, column).dropna()
    if series.empty:
        return None
    return float(series.mean())


def sum_metric(dataframe: pd.DataFrame, column: str) -> float | None:
    """Safely compute an additive metric."""
    series = to_numeric_series(dataframe, column).dropna()
    if series.empty:
        return None
    return float(series.sum())


def calculate_operating_margin(finance_df: pd.DataFrame) -> float | None:
    """Calculate an overall operating margin from revenue and profit totals."""
    if not {"total_revenue", "total_profit"}.issubset(finance_df.columns):
        return None

    revenue = pd.to_numeric(finance_df["total_revenue"], errors="coerce").sum()
    profit = pd.to_numeric(finance_df["total_profit"], errors="coerce").sum()
    if revenue == 0:
        return None
    return float((profit / revenue) * 100)


def calculate_sla_compliance(operations_df: pd.DataFrame) -> float | None:
    """Calculate a weighted SLA compliance rate using resolved requests."""
    required_columns = {"sla_compliance_pct", "resolved_requests"}
    if not required_columns.issubset(operations_df.columns):
        return None

    weighted_df = operations_df.copy()
    weighted_df["sla_compliance_pct"] = pd.to_numeric(
        weighted_df["sla_compliance_pct"],
        errors="coerce",
    )
    weighted_df["resolved_requests"] = pd.to_numeric(
        weighted_df["resolved_requests"],
        errors="coerce",
    ).fillna(0)
    weighted_df = weighted_df.dropna(subset=["sla_compliance_pct"])

    total_resolved = weighted_df["resolved_requests"].sum()
    if total_resolved <= 0:
        return average_metric(operations_df, "sla_compliance_pct")

    weighted_score = (
        weighted_df["sla_compliance_pct"] * weighted_df["resolved_requests"]
    ).sum() / total_resolved
    return float(weighted_score)


def calculate_risk_summary(executive_df: pd.DataFrame) -> float | None:
    """Surface the highest selected regional risk so executives do not miss the worst exposure."""
    series = to_numeric_series(executive_df, "risk_index").dropna()
    if series.empty:
        return None
    return float(series.max())


def prepare_period_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Attach a sortable month label for trend charts."""
    if not {"year", "month"}.issubset(dataframe.columns):
        return pd.DataFrame()

    period_df = dataframe.copy()
    period_df["year"] = pd.to_numeric(period_df["year"], errors="coerce")
    period_df["month"] = pd.to_numeric(period_df["month"], errors="coerce")
    period_df = period_df.dropna(subset=["year", "month"])
    if period_df.empty:
        return pd.DataFrame()

    period_df["period_date"] = pd.to_datetime(
        {
            "year": period_df["year"].astype(int),
            "month": period_df["month"].astype(int),
            "day": 1,
        }
    )
    period_df["period_label"] = period_df["period_date"].dt.strftime("%b %Y")
    return period_df


def build_revenue_trend(finance_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue totals by month and region."""
    period_df = prepare_period_dataframe(finance_df)
    required_columns = {"total_revenue", "region_name"}
    if period_df.empty or not required_columns.issubset(period_df.columns):
        return pd.DataFrame()

    trend_df = (
        period_df.groupby(["period_date", "period_label", "region_name"], as_index=False)[
            "total_revenue"
        ]
        .sum()
        .sort_values(["period_date", "region_name"])
    )
    return trend_df


def build_margin_trend(finance_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate operating margin by month and region using revenue and profit totals."""
    period_df = prepare_period_dataframe(finance_df)
    required_columns = {"total_revenue", "total_profit", "region_name"}
    if period_df.empty or not required_columns.issubset(period_df.columns):
        return pd.DataFrame()

    trend_df = (
        period_df.groupby(["period_date", "period_label", "region_name"], as_index=False)[
            ["total_revenue", "total_profit"]
        ]
        .sum()
        .sort_values(["period_date", "region_name"])
    )
    trend_df["operating_margin_pct"] = (
        trend_df["total_profit"] / trend_df["total_revenue"].replace({0: pd.NA})
    ) * 100
    return trend_df.dropna(subset=["operating_margin_pct"])


def build_sla_trend(operations_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weighted SLA compliance by month and region."""
    period_df = prepare_period_dataframe(operations_df)
    required_columns = {"sla_compliance_pct", "resolved_requests", "region_name"}
    if period_df.empty or not required_columns.issubset(period_df.columns):
        return pd.DataFrame()

    trend_df = period_df.copy()
    trend_df["sla_compliance_pct"] = pd.to_numeric(
        trend_df["sla_compliance_pct"],
        errors="coerce",
    )
    trend_df["resolved_requests"] = pd.to_numeric(
        trend_df["resolved_requests"],
        errors="coerce",
    ).fillna(0)
    trend_df["weighted_score"] = (
        trend_df["sla_compliance_pct"] * trend_df["resolved_requests"]
    )

    trend_df = (
        trend_df.groupby(["period_date", "period_label", "region_name"], as_index=False)[
            ["weighted_score", "resolved_requests"]
        ]
        .sum()
        .sort_values(["period_date", "region_name"])
    )
    trend_df["sla_compliance_pct"] = trend_df["weighted_score"] / trend_df[
        "resolved_requests"
    ].replace({0: pd.NA})
    return trend_df.dropna(subset=["sla_compliance_pct"])


def build_region_metric(
    dataframe: pd.DataFrame,
    value_column: str,
    *,
    aggregation: str = "mean",
    sort_ascending: bool = False,
) -> pd.DataFrame:
    """Aggregate a KPI by region for comparison charts."""
    if dataframe.empty or "region_name" not in dataframe.columns or value_column not in dataframe.columns:
        return pd.DataFrame()

    region_df = dataframe.copy()
    region_df[value_column] = pd.to_numeric(region_df[value_column], errors="coerce")
    region_df = region_df.dropna(subset=[value_column])
    if region_df.empty:
        return pd.DataFrame()

    grouped_df = (
        region_df.groupby("region_name", as_index=False)[value_column]
        .agg(aggregation)
        .sort_values(value_column, ascending=sort_ascending)
    )
    return grouped_df


def build_region_summary(finance_df: pd.DataFrame, operations_df: pd.DataFrame, executive_df: pd.DataFrame) -> pd.DataFrame:
    """Create a region-level summary for comparison insights and tables."""
    summary_frames: list[pd.DataFrame] = []

    if not finance_df.empty and {"region_name", "total_revenue", "total_profit"}.issubset(finance_df.columns):
        finance_summary = finance_df.groupby("region_name", as_index=False)[
            ["total_revenue", "total_profit"]
        ].sum()
        finance_summary["operating_margin_pct"] = (
            finance_summary["total_profit"]
            / finance_summary["total_revenue"].replace({0: pd.NA})
        ) * 100
        summary_frames.append(finance_summary)

    if not operations_df.empty and {"region_name", "sla_compliance_pct", "resolved_requests"}.issubset(operations_df.columns):
        operations_summary = operations_df.copy()
        operations_summary["sla_compliance_pct"] = pd.to_numeric(
            operations_summary["sla_compliance_pct"],
            errors="coerce",
        )
        operations_summary["resolved_requests"] = pd.to_numeric(
            operations_summary["resolved_requests"],
            errors="coerce",
        ).fillna(0)
        operations_summary["weighted_score"] = (
            operations_summary["sla_compliance_pct"] * operations_summary["resolved_requests"]
        )
        operations_summary = operations_summary.groupby("region_name", as_index=False)[
            ["weighted_score", "resolved_requests"]
        ].sum()
        operations_summary["sla_compliance_pct"] = operations_summary["weighted_score"] / operations_summary[
            "resolved_requests"
        ].replace({0: pd.NA})
        summary_frames.append(operations_summary[["region_name", "sla_compliance_pct"]])

    executive_columns = {
        "region_name",
        "avg_satisfaction_score",
        "total_co2_emissions_kg",
        "risk_index",
        "company_health_score",
        "total_downtime_hours",
    }
    if not executive_df.empty and executive_columns.issubset(executive_df.columns):
        executive_summary = executive_df.groupby("region_name", as_index=False).agg(
            {
                # The executive endpoint already exposes modeled averages, so satisfaction uses a simple mean here.
                "avg_satisfaction_score": "mean",
                "total_co2_emissions_kg": "sum",
                "risk_index": "mean",
                "company_health_score": "mean",
                "total_downtime_hours": "sum",
            }
        )
        summary_frames.append(executive_summary)

    if not summary_frames:
        return pd.DataFrame()

    summary_df = summary_frames[0]
    for frame in summary_frames[1:]:
        summary_df = summary_df.merge(frame, on="region_name", how="outer")
    return summary_df


def build_comparison_insights(region_summary_df: pd.DataFrame) -> list[tuple[str, str]]:
    """Generate simple rule-based comparison insights."""
    if region_summary_df.empty:
        return []

    insights: list[tuple[str, str]] = []

    if {"region_name", "total_revenue", "risk_index"}.issubset(region_summary_df.columns):
        revenue_row = region_summary_df.loc[region_summary_df["total_revenue"].idxmax()]
        risk_row = region_summary_df.loc[region_summary_df["risk_index"].idxmax()]
        insights.append(
            (
                "Revenue And Risk",
                (
                    f"{revenue_row['region_name']} generates the highest revenue in the selected scope, "
                    f"while {risk_row['region_name']} carries the highest average risk index. "
                    "This suggests management should balance growth priorities with targeted resilience actions."
                ),
            )
        )

    if {"region_name", "sla_compliance_pct"}.issubset(region_summary_df.columns):
        sla_row = region_summary_df.loc[region_summary_df["sla_compliance_pct"].idxmin()]
        insights.append(
            (
                "Operational Pressure",
                (
                    f"{sla_row['region_name']} shows the lowest SLA compliance across the selected regions, "
                    "making it the clearest candidate for backlog, dispatch, and service recovery review."
                ),
            )
        )

    if {"region_name", "total_co2_emissions_kg"}.issubset(region_summary_df.columns):
        emissions_row = region_summary_df.loc[region_summary_df["total_co2_emissions_kg"].idxmax()]
        insights.append(
            (
                "ESG Watchpoint",
                (
                    f"{emissions_row['region_name']} contributes the highest CO2 emissions in the current scope, "
                    "so efficiency actions there are likely to create the fastest ESG visibility gains."
                ),
            )
        )

    return insights


def prepare_recommendations(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean and sort recommendations for table display."""
    if dataframe.empty:
        return pd.DataFrame()

    display_df = dataframe.copy()
    if "priority_score" in display_df.columns:
        display_df["priority_score"] = pd.to_numeric(display_df["priority_score"], errors="coerce")
        display_df = display_df.sort_values("priority_score", ascending=False)

    selected_columns = [
        "region_name",
        "recommendation_area",
        "issue_detected",
        "recommended_action",
        "impact_level",
        "urgency_level",
        "priority_score",
    ]
    available_columns = [column for column in selected_columns if column in display_df.columns]
    display_df = display_df[available_columns].head(RECOMMENDATION_LIMIT)
    if "priority_score" in display_df.columns:
        display_df["priority_score"] = display_df["priority_score"].map(
            lambda value: f"{value:,.2f}" if pd.notna(value) else "N/A"
        )
    return display_df.rename(
        columns={
            "region_name": "Region",
            "recommendation_area": "Area",
            "issue_detected": "Issue Detected",
            "recommended_action": "Recommended Action",
            "impact_level": "Impact",
            "urgency_level": "Urgency",
            "priority_score": "Priority Score",
        }
    )


with st.sidebar:
    st.header("Executive Filters")
    selected_year = st.selectbox("Reporting year", YEAR_OPTIONS, index=0)
    selected_month = st.selectbox("Reporting month", MONTH_OPTIONS, index=0)
    selected_regions_input = st.multiselect(
        "Regions to compare",
        REGION_OPTIONS,
        default=REGION_OPTIONS,
        help="Select one or more regions for comparison. Leaving this empty defaults back to all regions.",
    )
    refresh_requested = st.button("Refresh dashboard", use_container_width=True)
    st.caption("Data source: FastAPI KPI endpoints")

if refresh_requested:
    clear_api_cache()
    st.rerun()

year_filter = normalize_filter_value(selected_year)
month_filter = normalize_filter_value(selected_month)
selected_regions, defaulted_to_all = normalize_region_selection(selected_regions_input)
if defaulted_to_all:
    st.sidebar.info("No specific region selected. Showing all regions by default.")

region_filter = region_api_filter(selected_regions)

render_page_header(
    title=PAGE_TITLE,
    subtitle=PAGE_SUBTITLE,
    description=(
        "An enterprise-style executive dashboard for leadership visibility across "
        "financial performance, service delivery, customer sentiment, asset downtime, "
        "ESG impact, and strategic risk."
    ),
)

st.caption(f"Current Scope: {scope_label(year_filter, month_filter, selected_regions)}")

with st.spinner("Loading KPI data from FastAPI..."):
    executive_response = get_executive_kpis(
        year=year_filter,
        month=month_filter,
        region=region_filter,
        limit=DATA_LIMIT,
    )
    finance_response = get_finance_kpis(
        year=year_filter,
        month=month_filter,
        region=region_filter,
        limit=DATA_LIMIT,
    )
    operations_response = get_operations_kpis(
        year=year_filter,
        month=month_filter,
        region=region_filter,
        limit=DATA_LIMIT,
    )
    recommendations_response = get_recommendations(
        year=year_filter,
        month=month_filter,
        region=region_filter,
        limit=DATA_LIMIT,
    )

executive_df = filter_regions(dataframe_from_response(executive_response), selected_regions)
finance_df = filter_regions(dataframe_from_response(finance_response), selected_regions)
operations_df = filter_regions(dataframe_from_response(operations_response), selected_regions)
recommendations_df = filter_regions(dataframe_from_response(recommendations_response), selected_regions)

if executive_df.empty and finance_df.empty and operations_df.empty:
    render_empty_state(
        title="No KPI data available for the selected filters.",
        message=(
            "Please make sure the API is running, data has been loaded, and the selected year, month, "
            "and regions have matching KPI records."
        ),
    )
else:
    region_summary_df = build_region_summary(finance_df, operations_df, executive_df)

    render_section_header(
        "Executive Snapshot",
        "Aggregated KPIs for the selected scope.",
    )
    metric_cards = [
        {
            "label": "Total Revenue",
            "value": sum_metric(finance_df, "total_revenue"),
            "format": "currency",
            "helper_text": "Summed across selected regions and months.",
        },
        {
            "label": "Operating Margin %",
            "value": calculate_operating_margin(finance_df),
            "format": "percentage",
            "helper_text": "Recalculated from total profit and revenue.",
        },
        {
            "label": "SLA Compliance %",
            "value": calculate_sla_compliance(operations_df),
            "format": "percentage",
            "helper_text": "Weighted by resolved request volume.",
        },
        {
            "label": "Customer Satisfaction",
            "value": average_metric(executive_df, "avg_satisfaction_score"),
            "format": "score",
            "helper_text": "Average satisfaction score in scope.",
        },
        {
            "label": "Downtime Hours",
            "value": sum_metric(executive_df, "total_downtime_hours"),
            "format": "hours",
            "helper_text": "Summed across the selected scope.",
        },
        {
            "label": "CO2 Emissions",
            "value": sum_metric(executive_df, "total_co2_emissions_kg"),
            "format": "emissions",
            "helper_text": "Summed ESG emissions in scope.",
        },
        {
            "label": "Company Health Score",
            "value": average_metric(executive_df, "company_health_score"),
            "format": "score",
            "helper_text": "Average modeled health score.",
        },
        {
            "label": "Risk Index",
            "value": calculate_risk_summary(executive_df),
            "format": "score",
            "helper_text": "Highest regional risk in the current comparison set.",
        },
    ]
    render_kpi_grid(metric_cards, columns=4)

    render_section_header(
        "Regional Comparison Insights",
        "Rule-based management observations generated from the current comparison scope.",
    )
    comparison_insights = build_comparison_insights(region_summary_df)
    if comparison_insights:
        insight_columns = st.columns(min(3, len(comparison_insights)))
        for column, insight in zip(insight_columns, comparison_insights, strict=False):
            with column:
                render_highlight_box(insight[0], insight[1])
    else:
        st.info("Comparison insights will appear when enough regional KPI data is available.")

    render_section_header(
        "Trend Comparison",
        "Monthly comparison of selected regions across financial and operational KPIs.",
    )
    trend_col_1, trend_col_2, trend_col_3 = st.columns(3)

    revenue_trend = build_revenue_trend(finance_df)
    margin_trend = build_margin_trend(finance_df)
    sla_trend = build_sla_trend(operations_df)

    with trend_col_1:
        revenue_chart = build_line_chart(
            revenue_trend,
            x="period_label",
            y="total_revenue",
            color_column="region_name",
            title="Revenue Trend by Month and Region",
            xaxis_title="Month",
            yaxis_title="Revenue",
        )
        if revenue_chart is not None:
            st.plotly_chart(revenue_chart, use_container_width=True)
        else:
            st.info("Revenue trend data is not available for the selected scope.")

    with trend_col_2:
        margin_chart = build_line_chart(
            margin_trend,
            x="period_label",
            y="operating_margin_pct",
            color_column="region_name",
            title="Operating Margin Trend by Month and Region",
            xaxis_title="Month",
            yaxis_title="Margin %",
        )
        if margin_chart is not None:
            st.plotly_chart(margin_chart, use_container_width=True)
        else:
            st.info("Operating margin trend data is not available for the selected scope.")

    with trend_col_3:
        sla_chart = build_line_chart(
            sla_trend,
            x="period_label",
            y="sla_compliance_pct",
            color_column="region_name",
            title="SLA Compliance by Month and Region",
            xaxis_title="Month",
            yaxis_title="SLA %",
        )
        if sla_chart is not None:
            st.plotly_chart(sla_chart, use_container_width=True)
        else:
            st.info("SLA trend data is not available for the selected scope.")

    render_section_header(
        "Regional Performance",
        "Comparison of selected regions across financial, operational, customer, and ESG indicators.",
    )
    regional_col_1, regional_col_2, regional_col_3 = st.columns(3)

    risk_by_region = build_region_metric(
        executive_df,
        "risk_index",
        aggregation="mean",
        sort_ascending=False,
    )
    co2_by_region = build_region_metric(
        executive_df,
        "total_co2_emissions_kg",
        aggregation="sum",
        sort_ascending=False,
    )
    satisfaction_by_region = build_region_metric(
        executive_df,
        "avg_satisfaction_score",
        aggregation="mean",
        sort_ascending=True,
    )

    with regional_col_1:
        risk_chart = build_bar_chart(
            risk_by_region,
            x="region_name",
            y="risk_index",
            title="Risk Index by Region",
            color="#D92D20",
            xaxis_title="Region",
            yaxis_title="Average Risk Index",
        )
        if risk_chart is not None:
            st.plotly_chart(risk_chart, use_container_width=True)
        else:
            st.info("Risk comparison data is not available for the selected scope.")

    with regional_col_2:
        co2_chart = build_bar_chart(
            co2_by_region,
            x="region_name",
            y="total_co2_emissions_kg",
            title="CO2 Emissions by Region",
            color="#B54708",
            xaxis_title="Region",
            yaxis_title="CO2 Emissions (kg)",
        )
        if co2_chart is not None:
            st.plotly_chart(co2_chart, use_container_width=True)
        else:
            st.info("CO2 comparison data is not available for the selected scope.")

    with regional_col_3:
        satisfaction_chart = build_horizontal_bar_chart(
            satisfaction_by_region,
            x="avg_satisfaction_score",
            y="region_name",
            title="Customer Satisfaction by Region",
            color="#0F766E",
            xaxis_title="Average Satisfaction Score",
            yaxis_title="Region",
        )
        if satisfaction_chart is not None:
            st.plotly_chart(satisfaction_chart, use_container_width=True)
        else:
            st.info("Customer satisfaction comparison data is not available for the selected scope.")

    render_section_header(
        "Recommendations",
        "Rule-based management actions generated from KPI thresholds.",
    )
    recommendations_table = prepare_recommendations(recommendations_df)
    if recommendations_table.empty:
        st.info("No management recommendations are available for the current selected scope.")
    else:
        st.dataframe(recommendations_table, use_container_width=True, hide_index=True)
