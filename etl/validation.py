"""Validation helpers for ETL extraction and pre-load checks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from etl.config import EXPECTED_COLUMNS, EXPECTED_FILES, PRIMARY_KEYS


def validate_source_files(source_dir: Path) -> None:
    """Ensure every expected CSV file exists in the source directory."""
    missing_files = [
        filename for filename in EXPECTED_FILES.values() if not (source_dir / filename).exists()
    ]
    if missing_files:
        missing_list = ", ".join(sorted(missing_files))
        raise FileNotFoundError(f"Missing required source CSV file(s): {missing_list}")


def validate_expected_columns(table_name: str, dataframe: pd.DataFrame) -> None:
    """Ensure CSV columns exactly match the schema-aligned expectation."""
    expected_columns = EXPECTED_COLUMNS[table_name]
    actual_columns = list(dataframe.columns)
    if actual_columns != expected_columns:
        raise ValueError(
            f"Column mismatch for {table_name}. "
            f"Expected {expected_columns}, received {actual_columns}."
        )


def _ensure_not_empty(table_name: str, dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise ValueError(f"Dataset {table_name} is empty.")


def _ensure_primary_keys(table_name: str, dataframe: pd.DataFrame) -> None:
    primary_key = PRIMARY_KEYS[table_name]
    if primary_key not in dataframe.columns:
        raise ValueError(f"Primary key column {primary_key} is missing from {table_name}.")
    if dataframe[primary_key].isna().any():
        raise ValueError(f"Primary key column {table_name}.{primary_key} contains null values.")


def _ensure_foreign_key(
    dataframe: pd.DataFrame,
    column_name: str,
    valid_values: set[int],
    label: str,
    nullable: bool = False,
) -> None:
    if column_name not in dataframe.columns:
        raise ValueError(f"Foreign key column {label} is missing.")

    column = dataframe[column_name]
    if not nullable and column.isna().any():
        raise ValueError(f"Foreign key column {label} contains null values.")

    populated_values = set(column.dropna().astype(int))
    invalid_values = sorted(populated_values.difference(valid_values))
    if invalid_values:
        sample = invalid_values[:5]
        raise ValueError(f"Invalid foreign key values in {label}: {sample}")


def validate_datasets(datasets: dict[str, pd.DataFrame]) -> list[str]:
    """Validate emptiness, keys, and foreign key relationships before loading."""
    for table_name, dataframe in datasets.items():
        validate_expected_columns(table_name, dataframe)
        _ensure_not_empty(table_name, dataframe)
        _ensure_primary_keys(table_name, dataframe)

    region_ids = set(datasets["dim_region"]["region_id"].dropna().astype(int))
    department_ids = set(datasets["dim_department"]["department_id"].dropna().astype(int))
    date_ids = set(datasets["dim_date"]["date_id"].dropna().astype(int))
    customer_ids = set(datasets["dim_customer"]["customer_id"].dropna().astype(int))
    asset_ids = set(datasets["dim_asset"]["asset_id"].dropna().astype(int))

    _ensure_foreign_key(datasets["dim_customer"], "region_id", region_ids, "dim_customer.region_id")
    _ensure_foreign_key(datasets["dim_asset"], "region_id", region_ids, "dim_asset.region_id")

    _ensure_foreign_key(datasets["fact_finance"], "date_id", date_ids, "fact_finance.date_id")
    _ensure_foreign_key(datasets["fact_finance"], "region_id", region_ids, "fact_finance.region_id")
    _ensure_foreign_key(
        datasets["fact_finance"],
        "department_id",
        department_ids,
        "fact_finance.department_id",
    )

    _ensure_foreign_key(
        datasets["fact_service_requests"],
        "date_id",
        date_ids,
        "fact_service_requests.date_id",
    )
    _ensure_foreign_key(
        datasets["fact_service_requests"],
        "customer_id",
        customer_ids,
        "fact_service_requests.customer_id",
    )
    _ensure_foreign_key(
        datasets["fact_service_requests"],
        "region_id",
        region_ids,
        "fact_service_requests.region_id",
    )
    _ensure_foreign_key(
        datasets["fact_service_requests"],
        "asset_id",
        asset_ids,
        "fact_service_requests.asset_id",
        nullable=True,
    )

    _ensure_foreign_key(
        datasets["fact_maintenance"],
        "date_id",
        date_ids,
        "fact_maintenance.date_id",
    )
    _ensure_foreign_key(
        datasets["fact_maintenance"],
        "asset_id",
        asset_ids,
        "fact_maintenance.asset_id",
    )
    _ensure_foreign_key(
        datasets["fact_maintenance"],
        "region_id",
        region_ids,
        "fact_maintenance.region_id",
    )

    _ensure_foreign_key(
        datasets["fact_customer_feedback"],
        "date_id",
        date_ids,
        "fact_customer_feedback.date_id",
    )
    _ensure_foreign_key(
        datasets["fact_customer_feedback"],
        "customer_id",
        customer_ids,
        "fact_customer_feedback.customer_id",
    )
    _ensure_foreign_key(
        datasets["fact_customer_feedback"],
        "region_id",
        region_ids,
        "fact_customer_feedback.region_id",
    )

    _ensure_foreign_key(datasets["fact_esg"], "date_id", date_ids, "fact_esg.date_id")
    _ensure_foreign_key(datasets["fact_esg"], "region_id", region_ids, "fact_esg.region_id")
    _ensure_foreign_key(datasets["fact_esg"], "asset_id", asset_ids, "fact_esg.asset_id", nullable=True)

    _ensure_foreign_key(datasets["fact_targets"], "date_id", date_ids, "fact_targets.date_id")
    _ensure_foreign_key(
        datasets["fact_targets"],
        "region_id",
        region_ids,
        "fact_targets.region_id",
        nullable=True,
    )
    _ensure_foreign_key(
        datasets["fact_targets"],
        "department_id",
        department_ids,
        "fact_targets.department_id",
        nullable=True,
    )

    return [
        "Expected CSV files are present.",
        "Datasets are non-empty and primary keys are populated.",
        "Foreign key references are valid before loading.",
    ]
