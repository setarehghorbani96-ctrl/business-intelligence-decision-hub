"""Configuration for reproducible NovaEnergy synthetic data generation."""

from __future__ import annotations

from pathlib import Path

RANDOM_SEED = 42
START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

NUMBER_OF_CUSTOMERS = 750
NUMBER_OF_ASSETS = 250
NUMBER_OF_SERVICE_REQUESTS = 10_000
NUMBER_OF_MAINTENANCE_EVENTS = 3_000
NUMBER_OF_FEEDBACK_RECORDS = 5_000
NUMBER_OF_ESG_RECORDS = 5_000

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "data" / "sample"

REGIONS = [
    {
        "region_id": 1,
        "region_name": "North-West",
        "country": "Italy",
        "area_manager": "Giulia Rinaldi",
        "region_profile": (
            "High-revenue industrial territory with older assets, heavier service "
            "pressure, and elevated ESG exposure."
        ),
        "customer_weight": 0.28,
        "asset_weight": 0.27,
        "service_weight": 0.31,
        "revenue_multiplier": 1.20,
        "growth_bias": 0.012,
        "asset_age_mean": 11,
        "asset_age_std": 3.2,
        "maintenance_cost_multiplier": 1.25,
        "downtime_multiplier": 1.28,
        "resolution_multiplier": 1.08,
        "energy_multiplier": 1.22,
        "renewable_base": 24.0,
        "status_risk": 0.10,
    },
    {
        "region_id": 2,
        "region_name": "North-East",
        "country": "Italy",
        "area_manager": "Marco Bellini",
        "region_profile": (
            "Operationally stable region with better asset condition, stronger SLA "
            "discipline, and steady commercial performance."
        ),
        "customer_weight": 0.22,
        "asset_weight": 0.19,
        "service_weight": 0.19,
        "revenue_multiplier": 1.02,
        "growth_bias": 0.008,
        "asset_age_mean": 6,
        "asset_age_std": 2.4,
        "maintenance_cost_multiplier": 0.90,
        "downtime_multiplier": 0.82,
        "resolution_multiplier": 0.94,
        "energy_multiplier": 0.90,
        "renewable_base": 33.0,
        "status_risk": 0.04,
    },
    {
        "region_id": 3,
        "region_name": "Central",
        "country": "Italy",
        "area_manager": "Elena Conti",
        "region_profile": (
            "Balanced portfolio with a growing customer base, medium-high revenue, "
            "and moderate operational backlog."
        ),
        "customer_weight": 0.21,
        "asset_weight": 0.22,
        "service_weight": 0.21,
        "revenue_multiplier": 1.08,
        "growth_bias": 0.015,
        "asset_age_mean": 8,
        "asset_age_std": 2.8,
        "maintenance_cost_multiplier": 1.02,
        "downtime_multiplier": 1.00,
        "resolution_multiplier": 1.00,
        "energy_multiplier": 1.00,
        "renewable_base": 28.0,
        "status_risk": 0.06,
    },
    {
        "region_id": 4,
        "region_name": "South",
        "country": "Italy",
        "area_manager": "Antonio Greco",
        "region_profile": (
            "Lower-revenue region with leaner costs, mixed service reliability, and "
            "room for customer experience improvement."
        ),
        "customer_weight": 0.18,
        "asset_weight": 0.18,
        "service_weight": 0.16,
        "revenue_multiplier": 0.88,
        "growth_bias": 0.010,
        "asset_age_mean": 7,
        "asset_age_std": 2.7,
        "maintenance_cost_multiplier": 0.92,
        "downtime_multiplier": 1.05,
        "resolution_multiplier": 1.05,
        "energy_multiplier": 0.95,
        "renewable_base": 27.0,
        "status_risk": 0.07,
    },
    {
        "region_id": 5,
        "region_name": "Islands",
        "country": "Italy",
        "area_manager": "Sofia Manca",
        "region_profile": (
            "Smaller market with higher logistics complexity, longer resolution times, "
            "and higher service delivery cost."
        ),
        "customer_weight": 0.11,
        "asset_weight": 0.14,
        "service_weight": 0.13,
        "revenue_multiplier": 0.76,
        "growth_bias": 0.009,
        "asset_age_mean": 9,
        "asset_age_std": 3.0,
        "maintenance_cost_multiplier": 1.12,
        "downtime_multiplier": 1.18,
        "resolution_multiplier": 1.22,
        "energy_multiplier": 1.07,
        "renewable_base": 25.0,
        "status_risk": 0.09,
    },
]

DEPARTMENTS = [
    {"department_id": 1, "department_name": "Executive", "department_type": "Leadership"},
    {"department_id": 2, "department_name": "Finance", "department_type": "Corporate"},
    {"department_id": 3, "department_name": "Sales", "department_type": "Commercial"},
    {"department_id": 4, "department_name": "Operations", "department_type": "Operational"},
    {"department_id": 5, "department_name": "Assets", "department_type": "Operational"},
    {"department_id": 6, "department_name": "ESG", "department_type": "Sustainability"},
    {
        "department_id": 7,
        "department_name": "Customer Service",
        "department_type": "Support",
    },
    {
        "department_id": 8,
        "department_name": "Digital Transformation",
        "department_type": "Strategic Enablement",
    },
]

CUSTOMER_SEGMENTS = ["Industrial", "Commercial", "Public Sector", "Residential"]
CUSTOMER_STATUSES = ["Active", "Lost", "Suspended"]
CONTRACT_TYPES = [
    "Managed Services",
    "Performance Contract",
    "Preventive Care",
    "On-Demand Support",
]

ASSET_TYPES = [
    "Energy Unit",
    "HVAC System",
    "Smart Meter",
    "Charging Station",
    "Industrial Equipment",
]
CRITICALITY_LEVELS = ["Low", "Medium", "High", "Critical"]
ASSET_STATUSES = ["Active", "Maintenance", "Retired"]

REQUEST_PRIORITIES = ["Low", "Medium", "High", "Critical"]
REQUEST_STATUSES = ["Open", "In Progress", "Resolved", "Cancelled"]
MAINTENANCE_TYPES = ["Preventive", "Corrective", "Inspection", "Upgrade"]

KPI_TARGET_UNITS = {
    "Revenue": "EUR",
    "Operating Margin": "Percent",
    "SLA Compliance": "Percent",
    "Asset Availability": "Percent",
    "Customer Satisfaction": "Score",
    "CO2 Emissions": "kg",
    "Energy Consumption": "kWh",
}

