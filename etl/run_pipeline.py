"""Command-line entry point for the NovaEnergy ETL loading pipeline."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

from etl.config import DEFAULT_LOAD_MODE, DEFAULT_SOURCE_DIR, SUPPORTED_LOAD_MODES
from etl.database import DatabaseSettings, create_database_engine
from etl.extract import extract_csv_datasets
from etl.load import run_load
from etl.transform import transform_datasets
from etl.validation import validate_datasets


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the ETL pipeline."""
    parser = argparse.ArgumentParser(description="Load NovaEnergy synthetic CSVs into PostgreSQL.")
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE_DIR),
        help="Path to the folder containing the generated CSV files.",
    )
    parser.add_argument(
        "--mode",
        default=DEFAULT_LOAD_MODE,
        choices=sorted(SUPPORTED_LOAD_MODES),
        help="Load strategy to use for the target tables.",
    )
    return parser.parse_args()


def run_pipeline(source: str | Path = DEFAULT_SOURCE_DIR, mode: str = DEFAULT_LOAD_MODE) -> dict[str, Any]:
    """Run the extract, transform, validate, and load workflow."""
    start_time = time.perf_counter()
    source_path = Path(source).resolve()
    database_settings = DatabaseSettings.from_env()

    print("Starting ETL pipeline.")
    print(f"Source folder: {source_path}")
    print(f"Database target: {database_settings.safe_url()}")
    print(f"Load mode: {mode}")

    extracted_datasets, extracted_counts = extract_csv_datasets(source_path)
    transformed_datasets = transform_datasets(extracted_datasets)
    validation_messages = validate_datasets(transformed_datasets)

    engine = create_database_engine(database_settings)
    load_result = run_load(engine, transformed_datasets, mode=mode)

    runtime_seconds = round(time.perf_counter() - start_time, 2)
    summary = {
        "source_folder": str(source_path),
        "database_target": database_settings.target_label(),
        "database_url_safe": database_settings.safe_url(),
        "mode": mode,
        "files_loaded": load_result["tables_loaded"],
        "row_counts": load_result["row_counts"],
        "extracted_counts": extracted_counts,
        "validation_messages": validation_messages,
        "runtime_seconds": runtime_seconds,
    }

    print("ETL pipeline complete.")
    print("Files loaded:")
    for table_name in summary["files_loaded"]:
        print(f"- {table_name}: {summary['row_counts'][table_name]} rows")
    print("Validation status:")
    for message in validation_messages:
        print(f"- {message}")
    print(f"Total runtime: {runtime_seconds} seconds")

    return summary


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    run_pipeline(source=args.source, mode=args.mode)


if __name__ == "__main__":
    main()
