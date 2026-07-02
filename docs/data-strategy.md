# Data Strategy

NovaEnergy Services uses synthetic enterprise data to demonstrate dimensional modeling, ETL design, KPI planning, and analytics storytelling without exposing confidential business information.

## Why Synthetic Data Is Used

- The project is a portfolio platform, so reproducibility and safety matter more than access to real operational systems.
- Synthetic data allows the warehouse model to be populated with realistic scale and business behavior.
- The same datasets can be regenerated at any time with a fixed random seed, which keeps testing and demos stable.

## Data Generation Scope

The current synthetic data generator produces CSV outputs in `data/sample/` for:

- shared dimensions: date, region, department, customer, asset
- operational facts: service requests and maintenance events
- financial facts: revenue, operating cost, maintenance cost, profit, budgeted cost
- customer facts: satisfaction, complaints, churn risk
- ESG facts: energy consumption, CO2 emissions, water, waste, renewable share
- management targets: monthly KPI targets by region and department where relevant

The generated period covers daily and monthly analytical activity from January 2024 through December 2025.

## Simulated Business Relationships

The generator is designed to preserve business logic that will matter in later analytics layers:

- Older assets create more maintenance events and more corrective work.
- Corrective maintenance creates more downtime than preventive maintenance.
- Higher downtime increases operational pressure and lowers SLA performance.
- Lower SLA performance reduces customer satisfaction and raises churn risk.
- Industrial customers carry higher contract values.
- Public Sector customers have lower churn sensitivity.
- Residential customers have lower contract value and higher churn sensitivity.
- North-West combines strong revenue with older assets, higher maintenance cost, and higher ESG pressure.
- North-East is more stable, with better asset condition and stronger SLA compliance.
- Islands operates at lower volume but with longer resolution time because of logistics complexity.
- Older assets consume more energy, which increases CO2 emissions.
- Renewable energy share improves gradually from 2024 to 2025.

## ETL Loader v1 Scope

ETL Loader v1 reads the generated CSV files from `data/sample/`, applies light type coercion, validates foreign key relationships before load, truncates the warehouse tables in replace mode, loads the tables in dependency order, and resets PostgreSQL SERIAL sequences after explicit-ID inserts.

The loader currently focuses only on clean ingestion into PostgreSQL. It does not yet create KPI views, semantic models, API business endpoints, or AI-generated insights.

## Data Quality And Validation

Before loading, the ETL workflow validates that:

- every expected CSV file is present
- every dataset is non-empty
- primary key columns are populated
- columns match the expected warehouse schema
- foreign key references are valid before database load
- Python source files compile successfully

This validation happens before any truncate-and-reload step is executed against PostgreSQL.

## Refresh Approach

The working refresh flow is:

```bash
python -m data_generation.generate_synthetic_data
python -m etl.run_pipeline --source data/sample --mode replace
```

Configuration values for synthetic data generation live in `data_generation/config.py`. Database connection settings for ETL are read from environment variables via `python-dotenv`.

## Governance Notes

- No real company or customer data is included.
- The generated datasets are designed for analytics development, ETL validation, demos, and dashboard prototyping.
- The warehouse schema remains the source-of-truth contract for column definitions and allowed value domains.
- Replace mode is intended for local development and portfolio demonstration, not for production-grade incremental loading.
