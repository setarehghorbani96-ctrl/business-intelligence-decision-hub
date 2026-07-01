"""Generate schema-aligned synthetic CSV data for NovaEnergy Services."""

from __future__ import annotations

from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from . import config

ID_COLUMNS = {
    "dim_date": "date_id",
    "dim_region": "region_id",
    "dim_department": "department_id",
    "dim_customer": "customer_id",
    "dim_asset": "asset_id",
    "fact_finance": "finance_id",
    "fact_service_requests": "request_id",
    "fact_maintenance": "maintenance_id",
    "fact_customer_feedback": "feedback_id",
    "fact_esg": "esg_id",
    "fact_targets": "target_id",
}

EXPECTED_FILES = OrderedDict(
    [
        ("dim_date.csv", "dim_date"),
        ("dim_region.csv", "dim_region"),
        ("dim_department.csv", "dim_department"),
        ("dim_customer.csv", "dim_customer"),
        ("dim_asset.csv", "dim_asset"),
        ("fact_finance.csv", "fact_finance"),
        ("fact_service_requests.csv", "fact_service_requests"),
        ("fact_maintenance.csv", "fact_maintenance"),
        ("fact_customer_feedback.csv", "fact_customer_feedback"),
        ("fact_esg.csv", "fact_esg"),
        ("fact_targets.csv", "fact_targets"),
    ]
)


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a numeric value into an inclusive range."""
    return max(low, min(high, value))


def weighted_choice(rng: np.random.Generator, values: list[Any], weights: list[float]) -> Any:
    """Select one item using normalized weights."""
    probabilities = np.array(weights, dtype=float)
    probabilities = probabilities / probabilities.sum()
    return values[int(rng.choice(len(values), p=probabilities))]


def to_date_id(value: pd.Timestamp) -> int:
    """Convert a timestamp into the schema's YYYYMMDD integer key."""
    return int(value.strftime("%Y%m%d"))


def month_start(value: pd.Timestamp) -> pd.Timestamp:
    """Return the first day of the month for a timestamp."""
    return pd.Timestamp(year=value.year, month=value.month, day=1)


def build_dim_date() -> pd.DataFrame:
    """Create the shared date dimension for the requested daily period."""
    dates = pd.date_range(config.START_DATE, config.END_DATE, freq="D")
    iso_calendar = dates.isocalendar()
    return pd.DataFrame(
        {
            "date_id": dates.strftime("%Y%m%d").astype(int),
            "full_date": dates.strftime("%Y-%m-%d"),
            "year": dates.year,
            "quarter": dates.quarter,
            "month": dates.month,
            "month_name": dates.strftime("%B"),
            "week": iso_calendar.week.astype(int),
            "day": dates.day,
        }
    )


def build_dim_region() -> pd.DataFrame:
    """Create region dimension rows using the documented business profiles."""
    return pd.DataFrame(config.REGIONS)[
        ["region_id", "region_name", "country", "area_manager", "region_profile"]
    ]


def build_dim_department() -> pd.DataFrame:
    """Create department dimension rows aligned to the seed reference data."""
    return pd.DataFrame(config.DEPARTMENTS)[
        ["department_id", "department_name", "department_type"]
    ]


def build_dim_customer(
    rng: np.random.Generator,
    region_lookup: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    """Generate customers with region, segment, and contract patterns."""
    region_ids = [region["region_id"] for region in config.REGIONS]
    region_weights = [region["customer_weight"] for region in config.REGIONS]

    segment_weights_by_region = {
        "North-West": [0.34, 0.32, 0.14, 0.20],
        "North-East": [0.28, 0.34, 0.16, 0.22],
        "Central": [0.22, 0.30, 0.22, 0.26],
        "South": [0.18, 0.28, 0.18, 0.36],
        "Islands": [0.20, 0.24, 0.16, 0.40],
    }
    contract_type_by_segment = {
        "Industrial": [0.38, 0.36, 0.16, 0.10],
        "Commercial": [0.28, 0.24, 0.28, 0.20],
        "Public Sector": [0.16, 0.54, 0.18, 0.12],
        "Residential": [0.08, 0.08, 0.30, 0.54],
    }
    name_tokens = {
        "Industrial": ["Forge", "Vector", "Atlas", "Titan", "Helios", "Mercury"],
        "Commercial": ["Vista", "Prime", "Urban", "Harbor", "Orion", "Summit"],
        "Public Sector": ["Civic", "Metro", "Public", "Community", "Regional", "Central"],
        "Residential": ["Home", "Family", "Green", "Bright", "Easy", "Casa"],
    }
    segment_value_ranges = {
        "Industrial": (180_000, 650_000),
        "Commercial": (70_000, 240_000),
        "Public Sector": (120_000, 320_000),
        "Residential": (8_000, 48_000),
    }

    rows = []
    start_floor = pd.Timestamp("2019-01-01")
    start_ceiling = pd.Timestamp(config.END_DATE)
    day_window = (start_ceiling - start_floor).days

    for customer_id in range(1, config.NUMBER_OF_CUSTOMERS + 1):
        region_id = weighted_choice(rng, region_ids, region_weights)
        region_name = region_lookup[region_id]["region_name"]

        segment = weighted_choice(
            rng,
            config.CUSTOMER_SEGMENTS,
            segment_weights_by_region[region_name],
        )
        contract_type = weighted_choice(
            rng,
            config.CONTRACT_TYPES,
            contract_type_by_segment[segment],
        )

        low, high = segment_value_ranges[segment]
        annual_contract_value = float(rng.triangular(low, (low + high) / 2, high))
        annual_contract_value *= 1 + (region_lookup[region_id]["revenue_multiplier"] - 1) * 0.35
        annual_contract_value = round(annual_contract_value, 2)

        active_weight = 0.87 - region_lookup[region_id]["status_risk"]
        if segment == "Public Sector":
            active_weight += 0.05
        if segment == "Residential":
            active_weight -= 0.05
        active_weight = clamp(active_weight, 0.72, 0.93)
        lost_weight = 0.07 + region_lookup[region_id]["status_risk"] * 0.5
        if segment == "Residential":
            lost_weight += 0.04
        if segment == "Public Sector":
            lost_weight -= 0.03
        lost_weight = clamp(lost_weight, 0.03, 0.18)
        suspended_weight = max(0.02, 1 - active_weight - lost_weight)
        status = weighted_choice(
            rng,
            config.CUSTOMER_STATUSES,
            [active_weight, lost_weight, suspended_weight],
        )

        if status == "Lost":
            annual_contract_value *= rng.uniform(0.70, 0.92)
        elif status == "Suspended":
            annual_contract_value *= rng.uniform(0.82, 0.97)
        annual_contract_value = round(annual_contract_value, 2)

        start_date = start_floor + pd.Timedelta(days=int(rng.integers(0, day_window + 1)))
        customer_name = (
            f"{weighted_choice(rng, name_tokens[segment], [1] * len(name_tokens[segment]))} "
            f"{segment.split()[0]} {region_name.replace('-', '')} {customer_id:04d}"
        )

        rows.append(
            {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "customer_segment": segment,
                "region_id": region_id,
                "contract_type": contract_type,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "status": status,
                "annual_contract_value": annual_contract_value,
            }
        )

    return pd.DataFrame(rows)


def build_dim_asset(
    rng: np.random.Generator,
    region_lookup: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    """Generate assets with realistic age and criticality patterns."""
    region_ids = [region["region_id"] for region in config.REGIONS]
    region_weights = [region["asset_weight"] for region in config.REGIONS]

    asset_type_weights_by_region = {
        "North-West": [0.30, 0.15, 0.13, 0.10, 0.32],
        "North-East": [0.18, 0.22, 0.30, 0.18, 0.12],
        "Central": [0.22, 0.22, 0.21, 0.16, 0.19],
        "South": [0.18, 0.26, 0.20, 0.14, 0.22],
        "Islands": [0.24, 0.20, 0.17, 0.12, 0.27],
    }
    criticality_weights = {
        "Energy Unit": [0.05, 0.15, 0.45, 0.35],
        "Industrial Equipment": [0.04, 0.18, 0.42, 0.36],
        "HVAC System": [0.12, 0.44, 0.30, 0.14],
        "Smart Meter": [0.34, 0.42, 0.18, 0.06],
        "Charging Station": [0.18, 0.38, 0.28, 0.16],
    }

    rows = []
    end_date = pd.Timestamp(config.END_DATE)
    max_age_days = int((end_date - pd.Timestamp("2010-01-01")).days)

    for asset_id in range(1, config.NUMBER_OF_ASSETS + 1):
        region_id = weighted_choice(rng, region_ids, region_weights)
        region = region_lookup[region_id]
        region_name = region["region_name"]

        asset_type = weighted_choice(
            rng,
            config.ASSET_TYPES,
            asset_type_weights_by_region[region_name],
        )
        criticality = weighted_choice(
            rng,
            config.CRITICALITY_LEVELS,
            criticality_weights[asset_type],
        )

        raw_age = int(round(rng.normal(region["asset_age_mean"], region["asset_age_std"])))
        asset_age_years = int(clamp(raw_age, 0, 18))
        install_years = max(0, asset_age_years)
        install_anchor = end_date - pd.Timedelta(days=install_years * 365 + int(rng.integers(0, 180)))
        if install_anchor < pd.Timestamp("2010-01-01"):
            install_anchor = pd.Timestamp("2010-01-01") + pd.Timedelta(
                days=int(rng.integers(0, max_age_days + 1))
            )

        maintenance_probability = 0.10 + asset_age_years * 0.015
        retired_probability = 0.01 + max(asset_age_years - 12, 0) * 0.01
        if region_name == "North-East":
            maintenance_probability *= 0.7
        if region_name == "North-West":
            maintenance_probability *= 1.1
            retired_probability *= 1.2

        status_roll = rng.random()
        if status_roll < retired_probability:
            asset_status = "Retired"
        elif status_roll < retired_probability + maintenance_probability:
            asset_status = "Maintenance"
        else:
            asset_status = "Active"

        rows.append(
            {
                "asset_id": asset_id,
                "asset_name": f"{asset_type} {region_name.replace('-', '')}-{asset_id:03d}",
                "asset_type": asset_type,
                "region_id": region_id,
                "installation_date": install_anchor.strftime("%Y-%m-%d"),
                "asset_age_years": asset_age_years,
                "criticality_level": criticality,
                "asset_status": asset_status,
            }
        )

    return pd.DataFrame(rows)


def build_downtime_pressure_map(
    maintenance_df: pd.DataFrame,
    assets_df: pd.DataFrame,
) -> dict[tuple[int, pd.Timestamp], float]:
    """Translate maintenance downtime into monthly service-delivery pressure."""
    pressure_map: dict[tuple[int, pd.Timestamp], float] = {}
    assets_per_region = assets_df.groupby("region_id")["asset_id"].count().to_dict()

    grouped = (
        maintenance_df.assign(
            month=lambda frame: pd.to_datetime(frame["date_id"].astype(str), format="%Y%m%d")
            .dt.to_period("M")
            .dt.to_timestamp()
        )
        .groupby(["region_id", "month"], as_index=False)["downtime_hours"]
        .sum()
    )

    for row in grouped.itertuples(index=False):
        asset_count = assets_per_region.get(row.region_id, 1)
        baseline_hours = asset_count * 24 * row.month.days_in_month
        downtime_ratio = row.downtime_hours / baseline_hours
        pressure_map[(row.region_id, row.month)] = 1 + clamp(downtime_ratio * 12, 0, 0.35)

    return pressure_map


def build_fact_maintenance(
    rng: np.random.Generator,
    assets_df: pd.DataFrame,
    region_lookup: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    """Generate maintenance events influenced by asset age and type."""
    assets = assets_df.copy()
    criticality_factor = assets["criticality_level"].map(
        {"Low": 0.9, "Medium": 1.0, "High": 1.2, "Critical": 1.35}
    )
    assets["selection_weight"] = (
        1
        + assets["asset_age_years"] * 0.10
        + criticality_factor
        + np.where(assets["asset_status"] == "Maintenance", 0.8, 0)
    )

    asset_ids = assets["asset_id"].to_numpy()
    weights = assets["selection_weight"].to_numpy(dtype=float)
    weights = weights / weights.sum()
    asset_map = assets.set_index("asset_id").to_dict(orient="index")

    date_range = pd.date_range(config.START_DATE, config.END_DATE, freq="D")
    team_names = [
        "Alpha Field Team",
        "Bravo Reliability Team",
        "Central Response Team",
        "Delta Upgrade Crew",
        "Island Logistics Team",
    ]

    rows = []
    for maintenance_id in range(1, config.NUMBER_OF_MAINTENANCE_EVENTS + 1):
        asset_id = int(rng.choice(asset_ids, p=weights))
        asset = asset_map[asset_id]
        region_id = int(asset["region_id"])
        region = region_lookup[region_id]
        asset_age = int(asset["asset_age_years"])
        criticality = asset["criticality_level"]

        preventive_weight = max(0.15, 0.40 - asset_age * 0.015)
        corrective_weight = min(0.55, 0.18 + asset_age * 0.02)
        inspection_weight = 0.22
        upgrade_weight = 1 - preventive_weight - corrective_weight - inspection_weight

        if region["region_name"] == "North-East":
            preventive_weight += 0.10
            corrective_weight -= 0.05
        if region["region_name"] == "North-West":
            corrective_weight += 0.06
            preventive_weight -= 0.03

        weights_by_type = np.array(
            [preventive_weight, corrective_weight, inspection_weight, max(0.05, upgrade_weight)],
            dtype=float,
        )
        weights_by_type = weights_by_type / weights_by_type.sum()
        maintenance_type = weighted_choice(
            rng,
            config.MAINTENANCE_TYPES,
            weights_by_type.tolist(),
        )

        failure_detected = maintenance_type == "Corrective" and rng.random() < clamp(
            0.48 + asset_age * 0.02,
            0.48,
            0.88,
        )

        base_downtime = {
            "Preventive": rng.uniform(1.5, 6.0),
            "Corrective": rng.uniform(6.0, 28.0),
            "Inspection": rng.uniform(0.5, 3.0),
            "Upgrade": rng.uniform(4.0, 18.0),
        }[maintenance_type]
        if failure_detected:
            base_downtime *= 1.18
        base_downtime *= region["downtime_multiplier"]
        base_downtime *= {"Low": 0.85, "Medium": 1.0, "High": 1.18, "Critical": 1.28}[criticality]
        downtime_hours = round(base_downtime, 2)

        base_cost = {
            "Preventive": rng.uniform(800, 3_000),
            "Corrective": rng.uniform(2_500, 10_000),
            "Inspection": rng.uniform(300, 1_400),
            "Upgrade": rng.uniform(4_000, 16_000),
        }[maintenance_type]
        base_cost *= 1 + asset_age * 0.04
        if failure_detected:
            base_cost *= 1.10
        base_cost *= region["maintenance_cost_multiplier"]
        base_cost *= {"Low": 0.9, "Medium": 1.0, "High": 1.12, "Critical": 1.22}[criticality]
        maintenance_cost = round(base_cost, 2)

        event_date = pd.Timestamp(rng.choice(date_range.to_numpy()))

        rows.append(
            {
                "maintenance_id": maintenance_id,
                "date_id": to_date_id(event_date),
                "asset_id": asset_id,
                "region_id": region_id,
                "maintenance_type": maintenance_type,
                "downtime_hours": downtime_hours,
                "maintenance_cost": maintenance_cost,
                "failure_detected": failure_detected,
                "technician_team": weighted_choice(rng, team_names, [1] * len(team_names)),
            }
        )

    return pd.DataFrame(rows)


def build_fact_service_requests(
    rng: np.random.Generator,
    customers_df: pd.DataFrame,
    assets_df: pd.DataFrame,
    region_lookup: dict[int, dict[str, Any]],
    downtime_pressure: dict[tuple[int, pd.Timestamp], float],
) -> pd.DataFrame:
    """Generate service requests with SLA performance influenced by asset and region."""
    customer_map = customers_df.set_index("customer_id").to_dict(orient="index")
    asset_map = assets_df.set_index("asset_id").to_dict(orient="index")

    customers_by_region: dict[int, np.ndarray] = {}
    customer_weights_by_region: dict[int, np.ndarray] = {}
    for region_id, group in customers_df.groupby("region_id"):
        weights = (
            1
            + group["annual_contract_value"] / group["annual_contract_value"].median()
            + group["customer_segment"].map(
                {
                    "Industrial": 0.8,
                    "Commercial": 0.45,
                    "Public Sector": 0.25,
                    "Residential": 0.15,
                }
            )
        ).to_numpy(dtype=float)
        customers_by_region[int(region_id)] = group["customer_id"].to_numpy(dtype=int)
        customer_weights_by_region[int(region_id)] = weights / weights.sum()

    assets_by_region: dict[int, np.ndarray] = {}
    asset_weights_by_region: dict[int, np.ndarray] = {}
    for region_id, group in assets_df.groupby("region_id"):
        criticality_factor = group["criticality_level"].map(
            {"Low": 0.8, "Medium": 1.0, "High": 1.3, "Critical": 1.5}
        )
        weights = (
            1
            + group["asset_age_years"] * 0.12
            + criticality_factor
            + np.where(group["asset_status"] == "Maintenance", 0.9, 0)
        ).to_numpy(dtype=float)
        assets_by_region[int(region_id)] = group["asset_id"].to_numpy(dtype=int)
        asset_weights_by_region[int(region_id)] = weights / weights.sum()

    region_ids = [region["region_id"] for region in config.REGIONS]
    region_weights = [region["service_weight"] for region in config.REGIONS]
    date_range = pd.date_range(config.START_DATE, config.END_DATE, freq="D")
    end_of_period = pd.Timestamp(f"{config.END_DATE} 23:59:59")

    request_types = [
        {"name": "Emergency Repair", "asset_related": True, "priority_bias": 1.4},
        {"name": "Preventive Check", "asset_related": True, "priority_bias": 0.8},
        {"name": "Outage Investigation", "asset_related": True, "priority_bias": 1.5},
        {"name": "Installation Support", "asset_related": True, "priority_bias": 1.0},
        {"name": "Performance Review", "asset_related": True, "priority_bias": 0.7},
        {"name": "Billing Inquiry", "asset_related": False, "priority_bias": 0.4},
        {"name": "Contract Update", "asset_related": False, "priority_bias": 0.3},
    ]
    sla_hours_by_priority = {"Low": 72, "Medium": 48, "High": 24, "Critical": 8}

    rows = []
    for request_id in range(1, config.NUMBER_OF_SERVICE_REQUESTS + 1):
        region_id = weighted_choice(rng, region_ids, region_weights)
        region = region_lookup[region_id]
        customer_id = int(
            rng.choice(
                customers_by_region[region_id],
                p=customer_weights_by_region[region_id],
            )
        )
        customer = customer_map[customer_id]

        request_type = request_types[int(rng.integers(0, len(request_types)))]
        created_date = pd.Timestamp(rng.choice(date_range.to_numpy()))
        created_at = created_date + pd.Timedelta(
            hours=int(rng.integers(0, 24)),
            minutes=int(rng.integers(0, 60)),
        )

        asset_id: int | None = None
        asset_age = 0
        criticality = "Medium"
        if request_type["asset_related"] or rng.random() < 0.84:
            asset_id = int(
                rng.choice(
                    assets_by_region[region_id],
                    p=asset_weights_by_region[region_id],
                )
            )
            asset = asset_map[asset_id]
            asset_age = int(asset["asset_age_years"])
            criticality = str(asset["criticality_level"])

        risk_score = 0.10 + request_type["priority_bias"] * 0.10
        risk_score += asset_age * 0.014
        risk_score += {"Low": 0.00, "Medium": 0.03, "High": 0.07, "Critical": 0.12}[criticality]
        if customer["customer_segment"] == "Industrial":
            risk_score += 0.04
        if customer["status"] == "Suspended":
            risk_score += 0.03
        risk_score = clamp(risk_score, 0.12, 0.82)

        priority = weighted_choice(
            rng,
            config.REQUEST_PRIORITIES,
            [
                max(0.10, 0.36 - risk_score * 0.18),
                0.34,
                0.22 + risk_score * 0.08,
                0.08 + risk_score * 0.10,
            ],
        )
        sla_target_hours = round(
            sla_hours_by_priority[priority] * rng.uniform(0.9, 1.1),
            2,
        )

        backlog_factor = {
            "North-West": [0.07, 0.08, 0.78, 0.07],
            "North-East": [0.04, 0.04, 0.88, 0.04],
            "Central": [0.05, 0.06, 0.84, 0.05],
            "South": [0.06, 0.07, 0.79, 0.08],
            "Islands": [0.07, 0.10, 0.73, 0.10],
        }[region["region_name"]]
        status = weighted_choice(rng, config.REQUEST_STATUSES, backlog_factor)

        pressure_key = (region_id, month_start(created_at))
        downtime_factor = downtime_pressure.get(pressure_key, 1.0)
        resolution_multiplier = region["resolution_multiplier"] * downtime_factor
        resolution_multiplier *= 1 + asset_age * 0.008
        resolution_multiplier *= {
            "Low": 0.98,
            "Medium": 1.00,
            "High": 1.05,
            "Critical": 1.12,
        }[criticality]
        resolution_multiplier *= {
            "Low": 1.04,
            "Medium": 1.00,
            "High": 0.97,
            "Critical": 0.94,
        }[priority]

        resolved_at = None
        actual_resolution_hours = None
        within_sla = None

        if status == "Resolved":
            actual_resolution_hours = round(
                max(1.0, sla_target_hours * rng.uniform(0.38, 0.92) * resolution_multiplier),
                2,
            )
            max_hours = max(1.0, (end_of_period - created_at).total_seconds() / 3600)
            actual_resolution_hours = round(min(actual_resolution_hours, max_hours), 2)
            resolved_at = created_at + pd.Timedelta(hours=float(actual_resolution_hours))
            within_sla = bool(actual_resolution_hours <= sla_target_hours)
        elif status == "Cancelled":
            cancel_hours = min(
                max(0.5, float(rng.uniform(1.0, sla_target_hours * 0.4))),
                max(0.5, (end_of_period - created_at).total_seconds() / 3600),
            )
            resolved_at = created_at + pd.Timedelta(hours=cancel_hours)

        rows.append(
            {
                "request_id": request_id,
                "created_at": created_at,
                "resolved_at": resolved_at,
                "date_id": to_date_id(created_at),
                "customer_id": customer_id,
                "region_id": region_id,
                "asset_id": asset_id,
                "request_type": request_type["name"],
                "priority": priority,
                "status": status,
                "sla_target_hours": sla_target_hours,
                "actual_resolution_hours": actual_resolution_hours,
                "within_sla": within_sla,
            }
        )

    return pd.DataFrame(rows)


def build_service_performance_maps(
    service_requests_df: pd.DataFrame,
) -> tuple[dict[tuple[int, pd.Timestamp], float], dict[int, float], pd.Series]:
    """Summarize service performance for downstream customer and target logic."""
    frame = service_requests_df.copy()
    frame["created_at"] = pd.to_datetime(frame["created_at"])
    frame["month"] = frame["created_at"].dt.to_period("M").dt.to_timestamp()

    resolved = frame[frame["status"] == "Resolved"].copy()
    resolved["within_sla_numeric"] = resolved["within_sla"].astype(int)

    monthly_map = {
        (int(row.region_id), row.month): float(row.within_sla_numeric)
        for row in resolved.groupby(["region_id", "month"], as_index=False)["within_sla_numeric"]
        .mean()
        .itertuples(index=False)
    }
    overall_map = {
        int(row.region_id): float(row.within_sla_numeric)
        for row in resolved.groupby("region_id", as_index=False)["within_sla_numeric"]
        .mean()
        .itertuples(index=False)
    }
    request_counts = frame.groupby("customer_id")["request_id"].count()

    return monthly_map, overall_map, request_counts


def build_fact_customer_feedback(
    rng: np.random.Generator,
    customers_df: pd.DataFrame,
    region_lookup: dict[int, dict[str, Any]],
    service_monthly_sla: dict[tuple[int, pd.Timestamp], float],
    service_overall_sla: dict[int, float],
    request_counts: pd.Series,
) -> pd.DataFrame:
    """Generate feedback that reacts to SLA performance and customer mix."""
    customers = customers_df.copy()
    customers["interaction_weight"] = 1 + customers["customer_id"].map(request_counts).fillna(0)
    customer_ids = customers["customer_id"].to_numpy(dtype=int)
    customer_weights = customers["interaction_weight"].to_numpy(dtype=float)
    customer_weights = customer_weights / customer_weights.sum()
    customer_map = customers.set_index("customer_id").to_dict(orient="index")

    date_range = pd.date_range(config.START_DATE, config.END_DATE, freq="D")

    rows = []
    for feedback_id in range(1, config.NUMBER_OF_FEEDBACK_RECORDS + 1):
        customer_id = int(rng.choice(customer_ids, p=customer_weights))
        customer = customer_map[customer_id]
        region_id = int(customer["region_id"])
        feedback_date = pd.Timestamp(rng.choice(date_range.to_numpy()))
        monthly_sla = service_monthly_sla.get(
            (region_id, month_start(feedback_date)),
            service_overall_sla.get(region_id, 0.84),
        )

        base_satisfaction = 2.65 + monthly_sla * 1.45
        base_satisfaction += {
            "Industrial": 0.15,
            "Commercial": 0.05,
            "Public Sector": 0.12,
            "Residential": -0.12,
        }[customer["customer_segment"]]
        base_satisfaction += {
            "North-West": -0.22,
            "North-East": 0.18,
            "Central": 0.04,
            "South": -0.08,
            "Islands": -0.18,
        }[region_lookup[region_id]["region_name"]]
        if customer["status"] == "Lost":
            base_satisfaction -= 0.65
        elif customer["status"] == "Suspended":
            base_satisfaction -= 0.38

        satisfaction_score = round(clamp(rng.normal(base_satisfaction, 0.42), 1.0, 5.0), 2)

        complaint_probability = clamp(0.10 + (3.2 - satisfaction_score) * 0.22, 0.04, 0.78)
        complaint_flag = bool(rng.random() < complaint_probability)

        churn_risk_score = 48 + (3.6 - satisfaction_score) * 14
        churn_risk_score += {
            "Industrial": 2,
            "Commercial": 6,
            "Public Sector": -10,
            "Residential": 12,
        }[customer["customer_segment"]]
        churn_risk_score += (0.85 - monthly_sla) * 45
        if complaint_flag:
            churn_risk_score += 9
        if customer["status"] == "Lost":
            churn_risk_score += 28
        elif customer["status"] == "Suspended":
            churn_risk_score += 14
        churn_risk_score = round(clamp(churn_risk_score + rng.normal(0, 6), 0, 100), 2)

        rows.append(
            {
                "feedback_id": feedback_id,
                "date_id": to_date_id(feedback_date),
                "customer_id": customer_id,
                "region_id": region_id,
                "satisfaction_score": satisfaction_score,
                "complaint_flag": complaint_flag,
                "churn_risk_score": churn_risk_score,
            }
        )

    return pd.DataFrame(rows)


def build_fact_esg(
    rng: np.random.Generator,
    assets_df: pd.DataFrame,
    region_lookup: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    """Generate ESG measurements using asset age and region sustainability profiles."""
    assets = assets_df.copy()
    asset_map = assets.set_index("asset_id").to_dict(orient="index")
    asset_ids = assets["asset_id"].to_numpy(dtype=int)

    criticality_factor = assets["criticality_level"].map(
        {"Low": 0.9, "Medium": 1.0, "High": 1.15, "Critical": 1.3}
    )
    weights = (
        1
        + assets["asset_age_years"] * 0.09
        + criticality_factor
        + np.where(assets["asset_type"].isin(["Energy Unit", "Industrial Equipment"]), 0.8, 0.2)
    ).to_numpy(dtype=float)
    weights = weights / weights.sum()

    date_range = pd.date_range(config.START_DATE, config.END_DATE, freq="D")
    base_consumption = {
        "Energy Unit": 1_200,
        "HVAC System": 620,
        "Smart Meter": 90,
        "Charging Station": 310,
        "Industrial Equipment": 980,
    }

    rows = []
    for esg_id in range(1, config.NUMBER_OF_ESG_RECORDS + 1):
        asset_id = int(rng.choice(asset_ids, p=weights))
        asset = asset_map[asset_id]
        region_id = int(asset["region_id"])
        region = region_lookup[region_id]
        measure_date = pd.Timestamp(rng.choice(date_range.to_numpy()))
        seasonal_factor = 1 + 0.16 * np.cos((measure_date.month - 1) / 12 * 2 * np.pi)
        age_factor = 1 + int(asset["asset_age_years"]) * 0.035
        renewable_share = (
            region["renewable_base"]
            + ((measure_date.year - 2024) * 12 + measure_date.month - 1) * 0.35
            + rng.normal(0, 1.8)
        )
        renewable_share = round(clamp(renewable_share, 12, 65), 2)

        energy_consumption = (
            base_consumption[str(asset["asset_type"])]
            * region["energy_multiplier"]
            * seasonal_factor
            * age_factor
            * rng.uniform(0.82, 1.18)
        )
        energy_consumption = round(max(10.0, energy_consumption), 2)

        emission_factor = clamp(0.44 - renewable_share / 250, 0.18, 0.42)
        co2_emissions = round(energy_consumption * emission_factor, 2)
        water_consumption = round(energy_consumption * rng.uniform(0.0025, 0.0065), 2)
        waste_kg = round(energy_consumption * rng.uniform(0.004, 0.014), 2)

        rows.append(
            {
                "esg_id": esg_id,
                "date_id": to_date_id(measure_date),
                "region_id": region_id,
                "asset_id": asset_id,
                "energy_consumption_kwh": energy_consumption,
                "co2_emissions_kg": co2_emissions,
                "water_consumption_m3": water_consumption,
                "waste_kg": waste_kg,
                "renewable_energy_share": renewable_share,
            }
        )

    return pd.DataFrame(rows)


def build_fact_finance(
    rng: np.random.Generator,
    customers_df: pd.DataFrame,
    maintenance_df: pd.DataFrame,
    region_lookup: dict[int, dict[str, Any]],
    department_lookup: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    """Generate monthly finance performance that ties back to customers and maintenance."""
    monthly_dates = pd.date_range(config.START_DATE, config.END_DATE, freq="MS")
    monthly_customer_value = (
        customers_df.groupby("region_id")["annual_contract_value"].sum().to_dict()
    )

    maintenance_monthly = (
        maintenance_df.assign(
            month=lambda frame: pd.to_datetime(frame["date_id"].astype(str), format="%Y%m%d")
            .dt.to_period("M")
            .dt.to_timestamp()
        )
        .groupby(["region_id", "month"], as_index=False)["maintenance_cost"]
        .sum()
    )
    maintenance_lookup = {
        (int(row.region_id), row.month): float(row.maintenance_cost)
        for row in maintenance_monthly.itertuples(index=False)
    }

    revenue_share = {
        "Executive": 0.04,
        "Finance": 0.05,
        "Sales": 0.26,
        "Operations": 0.22,
        "Assets": 0.16,
        "ESG": 0.06,
        "Customer Service": 0.12,
        "Digital Transformation": 0.09,
    }
    operating_cost_ratio = {
        "Executive": 0.52,
        "Finance": 0.56,
        "Sales": 0.61,
        "Operations": 0.65,
        "Assets": 0.63,
        "ESG": 0.60,
        "Customer Service": 0.62,
        "Digital Transformation": 0.66,
    }
    maintenance_share = {
        "Executive": 0.03,
        "Finance": 0.05,
        "Sales": 0.06,
        "Operations": 0.24,
        "Assets": 0.34,
        "ESG": 0.05,
        "Customer Service": 0.14,
        "Digital Transformation": 0.09,
    }
    seasonal_lift = {
        1: 0.96,
        2: 0.97,
        3: 0.99,
        4: 1.01,
        5: 1.02,
        6: 1.03,
        7: 1.01,
        8: 0.98,
        9: 1.02,
        10: 1.04,
        11: 1.05,
        12: 1.08,
    }

    rows = []
    finance_id = 1
    for date_value in monthly_dates:
        month_index = (date_value.year - 2024) * 12 + (date_value.month - 1)
        growth_factor = 1 + month_index * 0.009

        for region_id, region in region_lookup.items():
            base_region_revenue = (monthly_customer_value.get(region_id, 0) / 12) or 1
            base_region_revenue *= growth_factor
            base_region_revenue *= seasonal_lift[date_value.month]
            base_region_revenue *= region["revenue_multiplier"]
            base_region_revenue *= 1 + region["growth_bias"] * month_index

            region_maintenance = maintenance_lookup.get((region_id, date_value), 0.0)

            for department_id, department in department_lookup.items():
                department_name = department["department_name"]
                revenue = base_region_revenue * revenue_share[department_name] * rng.uniform(0.96, 1.05)
                revenue = round(revenue, 2)

                cost_ratio = operating_cost_ratio[department_name]
                cost_ratio += {
                    "North-West": 0.03,
                    "North-East": -0.02,
                    "Central": 0.00,
                    "South": -0.03,
                    "Islands": 0.02,
                }[region["region_name"]]
                if department_name == "Operations" and region["region_name"] == "Islands":
                    cost_ratio += 0.04
                if department_name == "Assets" and region["region_name"] == "North-East":
                    cost_ratio -= 0.03
                cost_ratio = clamp(cost_ratio, 0.42, 0.76)

                operating_cost = round(revenue * cost_ratio * rng.uniform(0.97, 1.03), 2)
                maintenance_cost = round(
                    region_maintenance * maintenance_share[department_name] * rng.uniform(0.94, 1.06),
                    2,
                )
                budgeted_cost = round(
                    (operating_cost + maintenance_cost * 0.35) * rng.uniform(0.95, 1.05),
                    2,
                )
                profit = round(revenue - operating_cost - maintenance_cost, 2)

                if profit < revenue * 0.06:
                    operating_cost = round(revenue - maintenance_cost - revenue * 0.08, 2)
                    operating_cost = max(0.0, operating_cost)
                    budgeted_cost = round(
                        (operating_cost + maintenance_cost * 0.35) * rng.uniform(0.96, 1.04),
                        2,
                    )
                    profit = round(revenue - operating_cost - maintenance_cost, 2)

                rows.append(
                    {
                        "finance_id": finance_id,
                        "date_id": to_date_id(date_value),
                        "region_id": region_id,
                        "department_id": department_id,
                        "revenue": revenue,
                        "operating_cost": operating_cost,
                        "maintenance_cost": maintenance_cost,
                        "budgeted_cost": budgeted_cost,
                        "profit": profit,
                    }
                )
                finance_id += 1

    return pd.DataFrame(rows)


def build_fact_targets(
    rng: np.random.Generator,
    finance_df: pd.DataFrame,
    service_requests_df: pd.DataFrame,
    maintenance_df: pd.DataFrame,
    feedback_df: pd.DataFrame,
    esg_df: pd.DataFrame,
    assets_df: pd.DataFrame,
) -> pd.DataFrame:
    """Create monthly KPI targets from actual synthetic performance baselines."""
    finance_monthly = finance_df.groupby(["date_id", "region_id", "department_id"], as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
    )
    finance_monthly["operating_margin"] = np.where(
        finance_monthly["revenue"] > 0,
        finance_monthly["profit"] / finance_monthly["revenue"] * 100,
        0,
    )

    service_monthly = (
        service_requests_df[service_requests_df["status"] == "Resolved"]
        .assign(
            month_date_id=lambda frame: pd.to_datetime(frame["date_id"].astype(str), format="%Y%m%d")
            .dt.to_period("M")
            .dt.to_timestamp()
            .dt.strftime("%Y%m%d")
            .astype(int),
            within_sla_numeric=lambda frame: frame["within_sla"].astype(int),
        )
        .groupby(["month_date_id", "region_id"], as_index=False)["within_sla_numeric"]
        .mean()
        .rename(columns={"within_sla_numeric": "sla_compliance"})
    )
    feedback_monthly = (
        feedback_df.assign(
            month_date_id=lambda frame: pd.to_datetime(frame["date_id"].astype(str), format="%Y%m%d")
            .dt.to_period("M")
            .dt.to_timestamp()
            .dt.strftime("%Y%m%d")
            .astype(int)
        )
        .groupby(["month_date_id", "region_id"], as_index=False)["satisfaction_score"]
        .mean()
    )
    esg_monthly = (
        esg_df.assign(
            month_date_id=lambda frame: pd.to_datetime(frame["date_id"].astype(str), format="%Y%m%d")
            .dt.to_period("M")
            .dt.to_timestamp()
            .dt.strftime("%Y%m%d")
            .astype(int)
        )
        .groupby(["month_date_id", "region_id"], as_index=False)
        .agg(
            energy_consumption_kwh=("energy_consumption_kwh", "sum"),
            co2_emissions_kg=("co2_emissions_kg", "sum"),
        )
    )

    maintenance_monthly = (
        maintenance_df.assign(
            month_date_id=lambda frame: pd.to_datetime(frame["date_id"].astype(str), format="%Y%m%d")
            .dt.to_period("M")
            .dt.to_timestamp()
            .dt.strftime("%Y%m%d")
            .astype(int)
        )
        .groupby(["month_date_id", "region_id"], as_index=False)["downtime_hours"]
        .sum()
    )
    assets_per_region = assets_df.groupby("region_id")["asset_id"].count().to_dict()
    maintenance_monthly["asset_availability"] = maintenance_monthly.apply(
        lambda row: clamp(
            100
            - (
                row["downtime_hours"]
                / max(1, assets_per_region.get(int(row["region_id"]), 1) * 24 * 30)
                * 100
            ),
            88.0,
            99.8,
        ),
        axis=1,
    )

    service_lookup = {
        (int(row.month_date_id), int(row.region_id)): float(row.sla_compliance)
        for row in service_monthly.itertuples(index=False)
    }
    feedback_lookup = {
        (int(row.month_date_id), int(row.region_id)): float(row.satisfaction_score)
        for row in feedback_monthly.itertuples(index=False)
    }
    esg_lookup = {
        (int(row.month_date_id), int(row.region_id)): (
            float(row.energy_consumption_kwh),
            float(row.co2_emissions_kg),
        )
        for row in esg_monthly.itertuples(index=False)
    }
    availability_lookup = {
        (int(row.month_date_id), int(row.region_id)): float(row.asset_availability)
        for row in maintenance_monthly.itertuples(index=False)
    }

    rows = []
    target_id = 1

    for row in finance_monthly.itertuples(index=False):
        rows.append(
            {
                "target_id": target_id,
                "date_id": int(row.date_id),
                "region_id": int(row.region_id),
                "department_id": int(row.department_id),
                "kpi_name": "Revenue",
                "target_value": round(float(row.revenue) * rng.uniform(1.03, 1.07), 2),
                "target_unit": config.KPI_TARGET_UNITS["Revenue"],
                "target_period": "Monthly",
            }
        )
        target_id += 1
        rows.append(
            {
                "target_id": target_id,
                "date_id": int(row.date_id),
                "region_id": int(row.region_id),
                "department_id": int(row.department_id),
                "kpi_name": "Operating Margin",
                "target_value": round(clamp(float(row.operating_margin) + rng.uniform(0.4, 2.0), 6, 42), 2),
                "target_unit": config.KPI_TARGET_UNITS["Operating Margin"],
                "target_period": "Monthly",
            }
        )
        target_id += 1

    region_month_pairs = sorted(
        {
            *service_lookup.keys(),
            *feedback_lookup.keys(),
            *esg_lookup.keys(),
            *availability_lookup.keys(),
        }
    )
    for date_id, region_id in region_month_pairs:
        sla_value = service_lookup.get((date_id, region_id), 0.84) * 100
        satisfaction_value = feedback_lookup.get((date_id, region_id), 3.6)
        energy_value, co2_value = esg_lookup.get((date_id, region_id), (0.0, 0.0))
        availability_value = availability_lookup.get((date_id, region_id), 96.0)

        region_level_targets = [
            ("SLA Compliance", round(clamp(sla_value + rng.uniform(1.0, 4.0), 82, 99), 2)),
            (
                "Asset Availability",
                round(clamp(availability_value + rng.uniform(0.2, 1.3), 90, 99.9), 2),
            ),
            (
                "Customer Satisfaction",
                round(clamp(satisfaction_value + rng.uniform(0.05, 0.35), 3.0, 4.95), 2),
            ),
            (
                "CO2 Emissions",
                round(max(0.0, co2_value * rng.uniform(0.93, 0.98)), 2),
            ),
            (
                "Energy Consumption",
                round(max(0.0, energy_value * rng.uniform(0.94, 0.99)), 2),
            ),
        ]
        for kpi_name, target_value in region_level_targets:
            rows.append(
                {
                    "target_id": target_id,
                    "date_id": date_id,
                    "region_id": region_id,
                    "department_id": None,
                    "kpi_name": kpi_name,
                    "target_value": target_value,
                    "target_unit": config.KPI_TARGET_UNITS[kpi_name],
                    "target_period": "Monthly",
                }
            )
            target_id += 1

    return pd.DataFrame(rows)


def validate_generated_data(
    datasets: dict[str, pd.DataFrame],
    output_dir: Path,
) -> list[str]:
    """Validate expected files, keys, foreign keys, and major constraints."""
    issues: list[str] = []

    for filename in EXPECTED_FILES:
        if not (output_dir / filename).exists():
            issues.append(f"Missing expected output file: {filename}")

    for dataset_name, id_column in ID_COLUMNS.items():
        if datasets[dataset_name][id_column].isna().any():
            issues.append(f"Missing values detected in {dataset_name}.{id_column}")
        if datasets[dataset_name][id_column].duplicated().any():
            issues.append(f"Duplicate values detected in {dataset_name}.{id_column}")

    date_ids = set(datasets["dim_date"]["date_id"])
    region_ids = set(datasets["dim_region"]["region_id"])
    department_ids = set(datasets["dim_department"]["department_id"])
    customer_ids = set(datasets["dim_customer"]["customer_id"])
    asset_ids = set(datasets["dim_asset"]["asset_id"])

    def ensure_subset(values: pd.Series, valid_set: set[int], label: str) -> None:
        cleaned = set(values.dropna().astype(int))
        if not cleaned.issubset(valid_set):
            issues.append(f"Foreign key mismatch detected for {label}")

    ensure_subset(datasets["dim_customer"]["region_id"], region_ids, "dim_customer.region_id")
    ensure_subset(datasets["dim_asset"]["region_id"], region_ids, "dim_asset.region_id")
    ensure_subset(datasets["fact_finance"]["date_id"], date_ids, "fact_finance.date_id")
    ensure_subset(datasets["fact_finance"]["region_id"], region_ids, "fact_finance.region_id")
    ensure_subset(
        datasets["fact_finance"]["department_id"],
        department_ids,
        "fact_finance.department_id",
    )
    ensure_subset(
        datasets["fact_service_requests"]["date_id"],
        date_ids,
        "fact_service_requests.date_id",
    )
    ensure_subset(
        datasets["fact_service_requests"]["customer_id"],
        customer_ids,
        "fact_service_requests.customer_id",
    )
    ensure_subset(
        datasets["fact_service_requests"]["region_id"],
        region_ids,
        "fact_service_requests.region_id",
    )
    ensure_subset(
        datasets["fact_service_requests"]["asset_id"],
        asset_ids,
        "fact_service_requests.asset_id",
    )
    ensure_subset(datasets["fact_maintenance"]["date_id"], date_ids, "fact_maintenance.date_id")
    ensure_subset(datasets["fact_maintenance"]["region_id"], region_ids, "fact_maintenance.region_id")
    ensure_subset(datasets["fact_maintenance"]["asset_id"], asset_ids, "fact_maintenance.asset_id")
    ensure_subset(
        datasets["fact_customer_feedback"]["date_id"],
        date_ids,
        "fact_customer_feedback.date_id",
    )
    ensure_subset(
        datasets["fact_customer_feedback"]["customer_id"],
        customer_ids,
        "fact_customer_feedback.customer_id",
    )
    ensure_subset(
        datasets["fact_customer_feedback"]["region_id"],
        region_ids,
        "fact_customer_feedback.region_id",
    )
    ensure_subset(datasets["fact_esg"]["date_id"], date_ids, "fact_esg.date_id")
    ensure_subset(datasets["fact_esg"]["region_id"], region_ids, "fact_esg.region_id")
    ensure_subset(datasets["fact_esg"]["asset_id"], asset_ids, "fact_esg.asset_id")
    ensure_subset(datasets["fact_targets"]["date_id"], date_ids, "fact_targets.date_id")
    ensure_subset(datasets["fact_targets"]["region_id"], region_ids, "fact_targets.region_id")
    ensure_subset(
        datasets["fact_targets"]["department_id"],
        department_ids,
        "fact_targets.department_id",
    )

    customers = datasets["dim_customer"]
    if not customers["customer_segment"].isin(config.CUSTOMER_SEGMENTS).all():
        issues.append("dim_customer contains invalid customer_segment values")
    if not customers["status"].isin(config.CUSTOMER_STATUSES).all():
        issues.append("dim_customer contains invalid status values")
    if (customers["annual_contract_value"] < 0).any():
        issues.append("dim_customer contains negative annual_contract_value values")

    assets = datasets["dim_asset"]
    if not assets["asset_type"].isin(config.ASSET_TYPES).all():
        issues.append("dim_asset contains invalid asset_type values")
    if not assets["criticality_level"].isin(config.CRITICALITY_LEVELS).all():
        issues.append("dim_asset contains invalid criticality_level values")
    if not assets["asset_status"].isin(config.ASSET_STATUSES).all():
        issues.append("dim_asset contains invalid asset_status values")
    if (assets["asset_age_years"] < 0).any():
        issues.append("dim_asset contains negative asset_age_years values")

    finance = datasets["fact_finance"]
    if (
        (finance[["revenue", "operating_cost", "maintenance_cost", "budgeted_cost"]] < 0)
        .any()
        .any()
    ):
        issues.append("fact_finance contains negative financial amounts")
    if not np.isclose(
        finance["profit"],
        finance["revenue"] - finance["operating_cost"] - finance["maintenance_cost"],
        atol=0.01,
    ).all():
        issues.append("fact_finance profit values do not match the schema formula")

    service = datasets["fact_service_requests"].copy()
    service["created_at"] = pd.to_datetime(service["created_at"])
    service["resolved_at"] = pd.to_datetime(service["resolved_at"], errors="coerce")
    if not service["priority"].isin(config.REQUEST_PRIORITIES).all():
        issues.append("fact_service_requests contains invalid priority values")
    if not service["status"].isin(config.REQUEST_STATUSES).all():
        issues.append("fact_service_requests contains invalid status values")
    if (service["sla_target_hours"] < 0).any():
        issues.append("fact_service_requests contains negative sla_target_hours")
    actual_hours = pd.to_numeric(service["actual_resolution_hours"], errors="coerce")
    if (actual_hours.dropna() < 0).any():
        issues.append("fact_service_requests contains negative actual_resolution_hours")
    if not (service["resolved_at"].dropna() >= service.loc[service["resolved_at"].notna(), "created_at"]).all():
        issues.append("fact_service_requests has resolved_at values before created_at")
    null_resolved_invalid = service["resolved_at"].isna() & ~service["status"].isin(["Open", "In Progress"])
    if null_resolved_invalid.any():
        issues.append("fact_service_requests has null resolved_at outside Open or In Progress")
    resolved_rows = service["status"] == "Resolved"
    if actual_hours[resolved_rows].isna().any():
        issues.append("Resolved service requests are missing actual_resolution_hours")
    calculated_sla = actual_hours[resolved_rows] <= service.loc[resolved_rows, "sla_target_hours"]
    if not (
        service.loc[resolved_rows, "within_sla"].astype(bool).reset_index(drop=True)
        == calculated_sla.reset_index(drop=True)
    ).all():
        issues.append("fact_service_requests within_sla flags are inconsistent with resolution hours")

    maintenance = datasets["fact_maintenance"]
    if not maintenance["maintenance_type"].isin(config.MAINTENANCE_TYPES).all():
        issues.append("fact_maintenance contains invalid maintenance_type values")
    if (maintenance[["downtime_hours", "maintenance_cost"]] < 0).any().any():
        issues.append("fact_maintenance contains negative downtime or cost values")

    feedback = datasets["fact_customer_feedback"]
    if not feedback["satisfaction_score"].between(1, 5).all():
        issues.append("fact_customer_feedback satisfaction_score is out of range")
    if not feedback["churn_risk_score"].between(0, 100).all():
        issues.append("fact_customer_feedback churn_risk_score is out of range")

    esg = datasets["fact_esg"]
    if (esg[["energy_consumption_kwh", "co2_emissions_kg", "water_consumption_m3", "waste_kg"]] < 0).any().any():
        issues.append("fact_esg contains negative environmental measures")
    if not esg["renewable_energy_share"].between(0, 100).all():
        issues.append("fact_esg renewable_energy_share is out of range")

    if issues:
        raise ValueError("Validation failed:\n- " + "\n- ".join(issues))

    return [
        "All expected CSV files were created.",
        "Required primary key fields are populated and unique.",
        "Foreign key references are consistent across all tables.",
        "Generated values satisfy key schema constraints and business rules.",
    ]


def write_datasets(datasets: dict[str, pd.DataFrame], output_dir: Path) -> OrderedDict[str, int]:
    """Persist all dataframes to CSV using the required filenames."""
    output_dir.mkdir(parents=True, exist_ok=True)
    row_counts: OrderedDict[str, int] = OrderedDict()

    for filename, dataset_name in EXPECTED_FILES.items():
        dataset = datasets[dataset_name].copy()
        if dataset_name == "fact_service_requests":
            dataset["created_at"] = pd.to_datetime(dataset["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            dataset["resolved_at"] = pd.to_datetime(dataset["resolved_at"], errors="coerce").dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        dataset.to_csv(output_dir / filename, index=False)
        row_counts[filename] = len(dataset)

    return row_counts


def generate_datasets(output_dir: Path | None = None) -> tuple[dict[str, pd.DataFrame], OrderedDict[str, int], list[str]]:
    """Generate the full synthetic dataset collection and validate the outputs."""
    rng = np.random.default_rng(config.RANDOM_SEED)
    output_dir = output_dir or config.OUTPUT_DIR

    dim_date = build_dim_date()
    dim_region = build_dim_region()
    dim_department = build_dim_department()

    region_lookup = {region["region_id"]: region for region in config.REGIONS}
    department_lookup = dim_department.set_index("department_id").to_dict(orient="index")

    dim_customer = build_dim_customer(rng, region_lookup)
    dim_asset = build_dim_asset(rng, region_lookup)
    fact_maintenance = build_fact_maintenance(rng, dim_asset, region_lookup)
    downtime_pressure = build_downtime_pressure_map(fact_maintenance, dim_asset)
    fact_service_requests = build_fact_service_requests(
        rng,
        dim_customer,
        dim_asset,
        region_lookup,
        downtime_pressure,
    )
    service_monthly_sla, service_overall_sla, request_counts = build_service_performance_maps(
        fact_service_requests
    )
    fact_customer_feedback = build_fact_customer_feedback(
        rng,
        dim_customer,
        region_lookup,
        service_monthly_sla,
        service_overall_sla,
        request_counts,
    )
    fact_esg = build_fact_esg(rng, dim_asset, region_lookup)
    fact_finance = build_fact_finance(
        rng,
        dim_customer,
        fact_maintenance,
        region_lookup,
        department_lookup,
    )
    fact_targets = build_fact_targets(
        rng,
        fact_finance,
        fact_service_requests,
        fact_maintenance,
        fact_customer_feedback,
        fact_esg,
        dim_asset,
    )

    datasets = {
        "dim_date": dim_date,
        "dim_region": dim_region,
        "dim_department": dim_department,
        "dim_customer": dim_customer,
        "dim_asset": dim_asset,
        "fact_finance": fact_finance,
        "fact_service_requests": fact_service_requests,
        "fact_maintenance": fact_maintenance,
        "fact_customer_feedback": fact_customer_feedback,
        "fact_esg": fact_esg,
        "fact_targets": fact_targets,
    }

    row_counts = write_datasets(datasets, output_dir)
    validation_messages = validate_generated_data(datasets, output_dir)
    return datasets, row_counts, validation_messages


def main() -> None:
    """CLI entry point for synthetic data generation."""
    _, row_counts, validation_messages = generate_datasets()

    print("Synthetic data generation complete.")
    print(f"Output folder: {config.OUTPUT_DIR}")
    print("Files generated:")
    for filename, row_count in row_counts.items():
        print(f"- {filename}: {row_count} rows")
    print("Validation checks:")
    for message in validation_messages:
        print(f"- {message}")


if __name__ == "__main__":
    main()



