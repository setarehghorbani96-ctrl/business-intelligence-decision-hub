"""Database loading step for the NovaEnergy ETL pipeline."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import Engine, text

from etl.config import DEFAULT_TO_SQL_CHUNKSIZE, LOAD_ORDER, SEQUENCE_TABLES


def truncate_target_tables(engine: Engine) -> None:
    """Clear target tables before a replace-mode load."""
    truncate_sql = "TRUNCATE TABLE " + ", ".join(LOAD_ORDER) + " RESTART IDENTITY CASCADE;"
    with engine.begin() as connection:
        connection.execute(text(truncate_sql))


def _prepare_for_database(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convert pandas nullable values into DB-friendly Python None values."""
    prepared = dataframe.copy()
    prepared = prepared.astype(object)
    return prepared.where(pd.notna(prepared), None)


def load_datasets_to_database(engine: Engine, datasets: dict[str, pd.DataFrame]) -> dict[str, int]:
    """Append transformed datasets to PostgreSQL in the required dependency order."""
    row_counts: dict[str, int] = {}

    with engine.begin() as connection:
        for table_name in LOAD_ORDER:
            dataframe = _prepare_for_database(datasets[table_name])
            dataframe.to_sql(
                name=table_name,
                con=connection,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=DEFAULT_TO_SQL_CHUNKSIZE,
            )
            row_counts[table_name] = len(dataframe)
            print(f"Loaded {table_name}: {len(dataframe)} rows")

    return row_counts


def reset_postgres_sequences(engine: Engine) -> None:
    """Set SERIAL sequences to the maximum loaded ID after explicit-ID inserts."""
    with engine.begin() as connection:
        for table_name, id_column in SEQUENCE_TABLES.items():
            sequence_sql = text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', '{id_column}'),
                    COALESCE((SELECT MAX({id_column}) FROM {table_name}), 1),
                    COALESCE((SELECT MAX({id_column}) IS NOT NULL FROM {table_name}), false)
                );
                """
            )
            connection.execute(sequence_sql)


def run_load(engine: Engine, datasets: dict[str, pd.DataFrame], mode: str = "replace") -> dict[str, Any]:
    """Load the prepared datasets into PostgreSQL using the requested mode."""
    if mode != "replace":
        raise ValueError(f"Unsupported load mode: {mode}")

    truncate_target_tables(engine)
    row_counts = load_datasets_to_database(engine, datasets)
    reset_postgres_sequences(engine)
    return {
        "mode": mode,
        "row_counts": row_counts,
        "tables_loaded": LOAD_ORDER,
    }
