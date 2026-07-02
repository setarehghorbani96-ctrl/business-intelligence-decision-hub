"""CSV extraction step for the NovaEnergy ETL pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from etl.config import EXPECTED_FILES
from etl.validation import validate_source_files


def extract_csv_datasets(source_dir: Path) -> tuple[dict[str, pd.DataFrame], dict[str, int]]:
    """Read the expected CSV files into pandas dataframes."""
    validate_source_files(source_dir)

    datasets: dict[str, pd.DataFrame] = {}
    row_counts: dict[str, int] = {}

    for table_name, filename in EXPECTED_FILES.items():
        dataframe = pd.read_csv(source_dir / filename, keep_default_na=True)
        datasets[table_name] = dataframe
        row_counts[table_name] = len(dataframe)
        print(f"Extracted {table_name} from {filename}: {len(dataframe)} rows")

    return datasets, row_counts


def run_extract(source_dir: Path) -> dict[str, pd.DataFrame]:
    """Return extracted datasets for downstream ETL stages."""
    datasets, _ = extract_csv_datasets(source_dir)
    return datasets
