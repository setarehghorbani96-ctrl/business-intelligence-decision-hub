# Synthetic Data Generator

The `data_generation/` package creates reproducible synthetic CSV datasets for the fictional company NovaEnergy Services. The goal is to populate the warehouse model with realistic business relationships while keeping the project safe, portable, and suitable for a professional portfolio.

## Why Synthetic Data

This project intentionally avoids real company information. Synthetic data makes it possible to demonstrate dimensional modeling, KPI design, ETL planning, and later dashboard storytelling without exposing confidential data or depending on unstable external sources.

## Simulated Business Relationships

The generator is not based on random disconnected values. It models several business relationships that will support later analytics:

- Older assets create more corrective maintenance and higher downtime.
- Higher downtime increases service pressure and lowers SLA compliance.
- Lower SLA compliance reduces customer satisfaction and increases churn risk.
- North-West has higher revenue volume but older assets, more maintenance cost, and more ESG pressure.
- North-East has stronger operations, better asset condition, and better SLA performance.
- Islands has lower volume but longer resolution times and higher service complexity.
- Older assets consume more energy, which increases CO2 emissions.
- Renewable energy share improves gradually from 2024 to 2025.

## Output Files

Running the generator writes CSV files to `data/sample/`:

- `dim_date.csv`
- `dim_region.csv`
- `dim_department.csv`
- `dim_customer.csv`
- `dim_asset.csv`
- `fact_finance.csv`
- `fact_service_requests.csv`
- `fact_maintenance.csv`
- `fact_customer_feedback.csv`
- `fact_esg.csv`
- `fact_targets.csv`

## Usage

From the project root, run:

```bash
python -m data_generation.generate_synthetic_data
```

The command prints:

- the output folder
- every generated file
- row counts
- validation status

## Configuration

Key settings live in [config.py](/C:/Users/Setareh/Documents/business-intelligence-decision-hub/data_generation/config.py):

- `RANDOM_SEED`
- `START_DATE`
- `END_DATE`
- `NUMBER_OF_CUSTOMERS`
- `NUMBER_OF_ASSETS`
- `NUMBER_OF_SERVICE_REQUESTS`
- `NUMBER_OF_MAINTENANCE_EVENTS`
- `NUMBER_OF_FEEDBACK_RECORDS`
- `NUMBER_OF_ESG_RECORDS`

Because a fixed random seed is used, the same command produces the same dataset each time unless the configuration changes.
