"""Placeholder ETL orchestration entry point."""

from etl.extract import run_extract
from etl.load import run_load
from etl.transform import run_transform


def run_pipeline() -> list[str]:
    """Return the placeholder ETL execution flow."""
    return [run_extract(), run_transform(), run_load()]


if __name__ == "__main__":
    for step in run_pipeline():
        print(step)
