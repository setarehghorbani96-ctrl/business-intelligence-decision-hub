"""Light transformation step for the NovaEnergy ETL pipeline."""

from __future__ import annotations

import pandas as pd

from etl.config import (
    BOOLEAN_COLUMNS,
    DATE_COLUMNS,
    EXPECTED_COLUMNS,
    INTEGER_COLUMNS,
    NUMERIC_COLUMNS,
    TIMESTAMP_COLUMNS,
)


def _coerce_boolean(value: object) -> object:
    """Convert common boolean-like values into Python booleans."""
    if pd.isna(value):
        return pd.NA
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    truthy_values = {"true", "1", "yes", "y", "t"}
    falsy_values = {"false", "0", "no", "n", "f"}

    if normalized in truthy_values:
        return True
    if normalized in falsy_values:
        return False

    raise ValueError(f"Cannot coerce value {value!r} to boolean.")


def _normalize_missing_strings(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convert empty-string placeholders into nulls."""
    return dataframe.replace(r"^\s*$", pd.NA, regex=True)


def transform_dataset(table_name: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """Apply light schema-aligned type coercion to one dataset."""
    transformed = dataframe.copy()
    transformed = _normalize_missing_strings(transformed)
    transformed.columns = [str(column).strip() for column in transformed.columns]

    expected_columns = EXPECTED_COLUMNS[table_name]
    if list(transformed.columns) != expected_columns:
        raise ValueError(
            f"Column mismatch for {table_name}. "
            f"Expected {expected_columns}, received {list(transformed.columns)}."
        )

    for column_name in DATE_COLUMNS.get(table_name, []):
        transformed[column_name] = pd.to_datetime(
            transformed[column_name],
            errors="coerce",
        ).dt.date

    for column_name in TIMESTAMP_COLUMNS.get(table_name, []):
        transformed[column_name] = pd.to_datetime(
            transformed[column_name],
            errors="coerce",
        )

    for column_name in BOOLEAN_COLUMNS.get(table_name, []):
        transformed[column_name] = transformed[column_name].map(_coerce_boolean).astype("boolean")

    for column_name in NUMERIC_COLUMNS.get(table_name, []):
        transformed[column_name] = pd.to_numeric(transformed[column_name], errors="coerce")

    for column_name in INTEGER_COLUMNS.get(table_name, []):
        transformed[column_name] = pd.to_numeric(transformed[column_name], errors="coerce").astype("Int64")

    return transformed


def transform_datasets(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply light type coercion to all datasets."""
    transformed_datasets: dict[str, pd.DataFrame] = {}
    for table_name, dataframe in datasets.items():
        transformed_datasets[table_name] = transform_dataset(table_name, dataframe)
        print(f"Transformed {table_name}: {len(dataframe)} rows")
    return transformed_datasets


def run_transform(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Return transformed datasets for downstream ETL stages."""
    return transform_datasets(datasets)
