"""Smoke tests for KPI planning placeholders."""

from pathlib import Path

from ai_insights.rules import PLANNED_KPIS


def test_planned_kpis_are_listed() -> None:
    assert "Revenue growth" in PLANNED_KPIS


def test_kpi_dictionary_document_exists() -> None:
    content = Path("docs/kpi-dictionary.md").read_text(encoding="utf-8")
    assert "KPI Dictionary" in content
