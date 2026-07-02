"""Shared configuration for the CSV-to-PostgreSQL ETL pipeline."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "data" / "sample"
DEFAULT_LOAD_MODE = "replace"
SUPPORTED_LOAD_MODES = {"replace"}
DEFAULT_TO_SQL_CHUNKSIZE = 1_000

EXPECTED_FILES = OrderedDict(
    [
        ("dim_date", "dim_date.csv"),
        ("dim_region", "dim_region.csv"),
        ("dim_department", "dim_department.csv"),
        ("dim_customer", "dim_customer.csv"),
        ("dim_asset", "dim_asset.csv"),
        ("fact_finance", "fact_finance.csv"),
        ("fact_service_requests", "fact_service_requests.csv"),
        ("fact_maintenance", "fact_maintenance.csv"),
        ("fact_customer_feedback", "fact_customer_feedback.csv"),
        ("fact_esg", "fact_esg.csv"),
        ("fact_targets", "fact_targets.csv"),
    ]
)

LOAD_ORDER = list(EXPECTED_FILES.keys())

PRIMARY_KEYS = {
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

EXPECTED_COLUMNS = {
    "dim_date": [
        "date_id",
        "full_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "week",
        "day",
    ],
    "dim_region": [
        "region_id",
        "region_name",
        "country",
        "area_manager",
        "region_profile",
    ],
    "dim_department": [
        "department_id",
        "department_name",
        "department_type",
    ],
    "dim_customer": [
        "customer_id",
        "customer_name",
        "customer_segment",
        "region_id",
        "contract_type",
        "start_date",
        "status",
        "annual_contract_value",
    ],
    "dim_asset": [
        "asset_id",
        "asset_name",
        "asset_type",
        "region_id",
        "installation_date",
        "asset_age_years",
        "criticality_level",
        "asset_status",
    ],
    "fact_finance": [
        "finance_id",
        "date_id",
        "region_id",
        "department_id",
        "revenue",
        "operating_cost",
        "maintenance_cost",
        "budgeted_cost",
        "profit",
    ],
    "fact_service_requests": [
        "request_id",
        "created_at",
        "resolved_at",
        "date_id",
        "customer_id",
        "region_id",
        "asset_id",
        "request_type",
        "priority",
        "status",
        "sla_target_hours",
        "actual_resolution_hours",
        "within_sla",
    ],
    "fact_maintenance": [
        "maintenance_id",
        "date_id",
        "asset_id",
        "region_id",
        "maintenance_type",
        "downtime_hours",
        "maintenance_cost",
        "failure_detected",
        "technician_team",
    ],
    "fact_customer_feedback": [
        "feedback_id",
        "date_id",
        "customer_id",
        "region_id",
        "satisfaction_score",
        "complaint_flag",
        "churn_risk_score",
    ],
    "fact_esg": [
        "esg_id",
        "date_id",
        "region_id",
        "asset_id",
        "energy_consumption_kwh",
        "co2_emissions_kg",
        "water_consumption_m3",
        "waste_kg",
        "renewable_energy_share",
    ],
    "fact_targets": [
        "target_id",
        "date_id",
        "region_id",
        "department_id",
        "kpi_name",
        "target_value",
        "target_unit",
        "target_period",
    ],
}

DATE_COLUMNS = {
    "dim_date": ["full_date"],
    "dim_customer": ["start_date"],
    "dim_asset": ["installation_date"],
}

TIMESTAMP_COLUMNS = {
    "fact_service_requests": ["created_at", "resolved_at"],
}

BOOLEAN_COLUMNS = {
    "fact_service_requests": ["within_sla"],
    "fact_maintenance": ["failure_detected"],
    "fact_customer_feedback": ["complaint_flag"],
}

INTEGER_COLUMNS = {
    "dim_date": ["date_id", "year", "quarter", "month", "week", "day"],
    "dim_region": ["region_id"],
    "dim_department": ["department_id"],
    "dim_customer": ["customer_id", "region_id"],
    "dim_asset": ["asset_id", "region_id", "asset_age_years"],
    "fact_finance": ["finance_id", "date_id", "region_id", "department_id"],
    "fact_service_requests": ["request_id", "date_id", "customer_id", "region_id", "asset_id"],
    "fact_maintenance": ["maintenance_id", "date_id", "asset_id", "region_id"],
    "fact_customer_feedback": ["feedback_id", "date_id", "customer_id", "region_id"],
    "fact_esg": ["esg_id", "date_id", "region_id", "asset_id"],
    "fact_targets": ["target_id", "date_id", "region_id", "department_id"],
}

NUMERIC_COLUMNS = {
    "dim_customer": ["annual_contract_value"],
    "fact_finance": ["revenue", "operating_cost", "maintenance_cost", "budgeted_cost", "profit"],
    "fact_service_requests": ["sla_target_hours", "actual_resolution_hours"],
    "fact_maintenance": ["downtime_hours", "maintenance_cost"],
    "fact_customer_feedback": ["satisfaction_score", "churn_risk_score"],
    "fact_esg": [
        "energy_consumption_kwh",
        "co2_emissions_kg",
        "water_consumption_m3",
        "waste_kg",
        "renewable_energy_share",
    ],
    "fact_targets": ["target_value"],
}

SEQUENCE_TABLES = {
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
