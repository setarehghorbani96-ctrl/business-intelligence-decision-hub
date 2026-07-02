# Business Intelligence Decision Hub

Business Intelligence Decision Hub is a professional portfolio project for a role-based business intelligence and decision-support platform built around the fictional company NovaEnergy Services.

The current implementation includes the Docker-ready project foundation, PostgreSQL Schema v1, a reproducible synthetic data generator, and ETL Loader v1 for loading synthetic CSV datasets into PostgreSQL.

## Current Scope

- Dockerized local development workflow
- PostgreSQL service initialization from the `database/` folder
- PostgreSQL Schema v1 for NovaEnergy Services
- Starter seed data for regions and departments
- Synthetic data generator for dimensions, fact tables, and KPI targets
- ETL Loader v1 for CSV validation and PostgreSQL loading
- Sample CSV outputs in `data/sample/`
- FastAPI placeholder service with a health endpoint
- Streamlit placeholder application shell
- Starter folders for AI insights, analytics assets, tests, and documentation

## Setup

In Windows PowerShell:

```powershell
Copy-Item .env.example .env -Force
docker compose down -v
docker compose up --build
```

The example environment file defaults the host-side ETL workflow to `localhost`, while Docker overrides container-side database access to `postgres` for the API and Streamlit services.

## Generate Synthetic Data

From a second PowerShell window at the project root, run:

```powershell
python -m data_generation.generate_synthetic_data
```

The generator writes these schema-aligned CSV files into `data/sample/`:

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

The synthetic data is relationship-driven rather than random. It simulates how older assets increase maintenance and downtime, how downtime affects SLA performance, how SLA performance influences customer satisfaction and churn risk, and how asset age and regional mix affect energy consumption and CO2 emissions.

## Load CSV Data Into PostgreSQL

Run the ETL loader from the project root:

```powershell
python -m etl.run_pipeline --source data/sample --mode replace
```

The ETL pipeline:

- checks that all expected CSV files exist
- reads the CSVs into pandas DataFrames
- applies light type coercion for dates, timestamps, booleans, and numeric fields
- validates primary keys and foreign key relationships before load
- truncates the target tables in replace mode
- loads tables in dependency-safe order
- resets PostgreSQL SERIAL sequences after explicit-ID inserts

## Verify The Load

You can verify a loaded table with:

```powershell
docker compose exec postgres psql -U postgres -d bi_decision_hub -c "SELECT COUNT(*) FROM fact_service_requests;"
```

## Resetting The Database

If you need a clean reset of the local PostgreSQL volume, use:

```powershell
docker compose down -v
docker compose up --build
```

Then regenerate and reload the synthetic data:

```powershell
python -m data_generation.generate_synthetic_data
python -m etl.run_pipeline --source data/sample --mode replace
```

## Service Endpoints

- FastAPI: http://localhost:8000
- FastAPI health check: http://localhost:8000/health
- Streamlit: http://localhost:8501
- PostgreSQL: localhost:5432

## Repository Layout

```text
.
|-- api/
|-- ai_insights/
|-- app/
|-- data/
|-- data_generation/
|-- database/
|-- docs/
|-- etl/
|-- notebooks/
|-- powerbi/
|-- tests/
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- LICENSE
`-- requirements.txt
```

## What Is Not Implemented Yet

- KPI SQL views and dashboard logic
- FastAPI business endpoints beyond placeholders
- AI insight generation
- Scenario analysis workflows

## Next Planned Phase

The next recommended step is to add post-load KPI definitions and analytical views on top of the validated warehouse tables, then expose those metrics to the application layer.
