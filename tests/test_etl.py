"""Unit tests for the NovaEnergy ETL pipeline."""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

import pandas as pd

from etl.config import EXPECTED_FILES, LOAD_ORDER
from etl.database import DatabaseSettings
from etl.validation import validate_datasets, validate_source_files


REQUIRED_TABLE_SEQUENCE = [
    "dim_date",
    "dim_region",
    "dim_department",
    "dim_customer",
    "dim_asset",
    "fact_finance",
    "fact_service_requests",
    "fact_maintenance",
    "fact_customer_feedback",
    "fact_esg",
    "fact_targets",
]


def build_valid_datasets() -> dict[str, pd.DataFrame]:
    return {
        "dim_date": pd.DataFrame(
            [
                {
                    "date_id": 20240101,
                    "full_date": "2024-01-01",
                    "year": 2024,
                    "quarter": 1,
                    "month": 1,
                    "month_name": "January",
                    "week": 1,
                    "day": 1,
                }
            ]
        ),
        "dim_region": pd.DataFrame(
            [
                {
                    "region_id": 1,
                    "region_name": "North-West",
                    "country": "Italy",
                    "area_manager": "Manager",
                    "region_profile": "Profile",
                }
            ]
        ),
        "dim_department": pd.DataFrame(
            [
                {
                    "department_id": 1,
                    "department_name": "Operations",
                    "department_type": "Operational",
                }
            ]
        ),
        "dim_customer": pd.DataFrame(
            [
                {
                    "customer_id": 1,
                    "customer_name": "Customer One",
                    "customer_segment": "Industrial",
                    "region_id": 1,
                    "contract_type": "Managed Services",
                    "start_date": "2024-01-01",
                    "status": "Active",
                    "annual_contract_value": 100000.0,
                }
            ]
        ),
        "dim_asset": pd.DataFrame(
            [
                {
                    "asset_id": 1,
                    "asset_name": "Asset One",
                    "asset_type": "Energy Unit",
                    "region_id": 1,
                    "installation_date": "2020-01-01",
                    "asset_age_years": 4,
                    "criticality_level": "High",
                    "asset_status": "Active",
                }
            ]
        ),
        "fact_finance": pd.DataFrame(
            [
                {
                    "finance_id": 1,
                    "date_id": 20240101,
                    "region_id": 1,
                    "department_id": 1,
                    "revenue": 1000.0,
                    "operating_cost": 600.0,
                    "maintenance_cost": 100.0,
                    "budgeted_cost": 650.0,
                    "profit": 300.0,
                }
            ]
        ),
        "fact_service_requests": pd.DataFrame(
            [
                {
                    "request_id": 1,
                    "created_at": "2024-01-01 08:00:00",
                    "resolved_at": "2024-01-01 12:00:00",
                    "date_id": 20240101,
                    "customer_id": 1,
                    "region_id": 1,
                    "asset_id": 1,
                    "request_type": "Emergency Repair",
                    "priority": "High",
                    "status": "Resolved",
                    "sla_target_hours": 8.0,
                    "actual_resolution_hours": 4.0,
                    "within_sla": True,
                }
            ]
        ),
        "fact_maintenance": pd.DataFrame(
            [
                {
                    "maintenance_id": 1,
                    "date_id": 20240101,
                    "asset_id": 1,
                    "region_id": 1,
                    "maintenance_type": "Preventive",
                    "downtime_hours": 2.0,
                    "maintenance_cost": 250.0,
                    "failure_detected": False,
                    "technician_team": "Team A",
                }
            ]
        ),
        "fact_customer_feedback": pd.DataFrame(
            [
                {
                    "feedback_id": 1,
                    "date_id": 20240101,
                    "customer_id": 1,
                    "region_id": 1,
                    "satisfaction_score": 4.5,
                    "complaint_flag": False,
                    "churn_risk_score": 15.0,
                }
            ]
        ),
        "fact_esg": pd.DataFrame(
            [
                {
                    "esg_id": 1,
                    "date_id": 20240101,
                    "region_id": 1,
                    "asset_id": 1,
                    "energy_consumption_kwh": 100.0,
                    "co2_emissions_kg": 40.0,
                    "water_consumption_m3": 2.0,
                    "waste_kg": 1.0,
                    "renewable_energy_share": 25.0,
                }
            ]
        ),
        "fact_targets": pd.DataFrame(
            [
                {
                    "target_id": 1,
                    "date_id": 20240101,
                    "region_id": 1,
                    "department_id": 1,
                    "kpi_name": "Revenue",
                    "target_value": 1100.0,
                    "target_unit": "EUR",
                    "target_period": "Monthly",
                }
            ]
        ),
    }


class EtlContractTests(unittest.TestCase):
    def test_expected_file_list_matches_contract(self) -> None:
        self.assertEqual(list(EXPECTED_FILES.keys()), REQUIRED_TABLE_SEQUENCE)
        self.assertEqual(
            list(EXPECTED_FILES.values()),
            [
                "dim_date.csv",
                "dim_region.csv",
                "dim_department.csv",
                "dim_customer.csv",
                "dim_asset.csv",
                "fact_finance.csv",
                "fact_service_requests.csv",
                "fact_maintenance.csv",
                "fact_customer_feedback.csv",
                "fact_esg.csv",
                "fact_targets.csv",
            ],
        )

    def test_loading_order_matches_dependency_sequence(self) -> None:
        self.assertEqual(LOAD_ORDER, REQUIRED_TABLE_SEQUENCE)

    def test_validate_source_files_detects_missing_files(self) -> None:
        temp_dir = Path("tests") / "_tmp_missing_files"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            with self.assertRaisesRegex(FileNotFoundError, "Missing required source CSV file"):
                validate_source_files(temp_dir)
        finally:
            shutil.rmtree(temp_dir)

    def test_validate_datasets_detects_invalid_foreign_keys(self) -> None:
        datasets = build_valid_datasets()
        datasets["fact_service_requests"].loc[0, "customer_id"] = 999

        with self.assertRaisesRegex(ValueError, "fact_service_requests.customer_id"):
            validate_datasets(datasets)

    def test_database_safe_url_hides_password(self) -> None:
        settings = DatabaseSettings(
            host="localhost",
            port=5432,
            name="bi_decision_hub",
            user="postgres",
            password="super-secret",
        )

        safe_url = settings.safe_url()

        self.assertNotIn("super-secret", safe_url)
        self.assertIn("***", safe_url)
        self.assertEqual(settings.target_label(), "localhost:5432/bi_decision_hub")


if __name__ == "__main__":
    unittest.main()
