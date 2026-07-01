"""Smoke tests for ETL placeholders."""

from etl.run_pipeline import run_pipeline


def test_etl_pipeline_placeholders_exist() -> None:
    assert run_pipeline() == [
        "Extract step placeholder.",
        "Transform step placeholder.",
        "Load step placeholder.",
    ]
