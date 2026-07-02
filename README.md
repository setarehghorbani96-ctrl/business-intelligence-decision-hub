# Business Intelligence Decision Hub

Business Intelligence Decision Hub is a professional portfolio project for a role-based business intelligence and decision-support platform built around the fictional company NovaEnergy Services.

The current implementation includes the Docker-ready project foundation, PostgreSQL Schema v1, a reproducible synthetic data generator, ETL Loader v1, and KPI SQL Views v1 for reusable analytical reporting.

## Current Scope

- Dockerized local development workflow
- PostgreSQL service initialization from the `database/` folder
- PostgreSQL Schema v1 for NovaEnergy Services
- Starter seed data for regions and departments
- Synthetic data generator for dimensions, fact tables, and KPI targets
- ETL Loader v1 for CSV validation and PostgreSQL loading
- KPI SQL Views v1 for finance, operations, assets, customers, ESG, executive scorecards, and rule-based recommendations
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

The generator writes schema-aligned CSV files into `data/sample/` for all warehouse dimensions, facts, and KPI target records.

## Load CSV Data Into PostgreSQL

Run the ETL loader from the project root:

```powershell
python -m etl.run_pipeline --source data/sample --mode replace
```

The ETL pipeline checks source files, applies light type coercion, validates key relationships, reloads the target tables in dependency-safe order, and resets PostgreSQL SERIAL sequences after explicit-ID inserts.

## Apply KPI Views

If your PostgreSQL volume is brand new, the SQL files in `database/` may be applied automatically during container initialization. If the database already exists, apply the KPI views manually:

```powershell
docker compose exec postgres psql -U postgres -d bi_decision_hub -f /docker-entrypoint-initdb.d/views.sql
```

You can also run the validation query pack manually:

```powershell
docker compose exec postgres psql -U postgres -d bi_decision_hub -f /docker-entrypoint-initdb.d/validation_queries.sql
```

## Inspect KPI Views

Example commands:

```powershell
docker compose exec postgres psql -U postgres -d bi_decision_hub -c "SELECT * FROM vw_executive_kpis LIMIT 5;"
docker compose exec postgres psql -U postgres -d bi_decision_hub -c "SELECT * FROM vw_decision_recommendations ORDER BY priority_score DESC LIMIT 10;"
```

## Verify The Load

You can verify a loaded fact table with:

```powershell
docker compose exec postgres psql -U postgres -d bi_decision_hub -c "SELECT COUNT(*) FROM fact_service_requests;"
```

## Resetting The Database

If you need a clean reset of the local PostgreSQL volume, use:

```powershell
docker compose down -v
docker compose up --build
```

Then regenerate, reload, and reapply views:

```powershell
python -m data_generation.generate_synthetic_data
python -m etl.run_pipeline --source data/sample --mode replace
docker compose exec postgres psql -U postgres -d bi_decision_hub -f /docker-entrypoint-initdb.d/views.sql
```

## What The KPI Views Support

The SQL view layer is intended to:

- centralize business KPI definitions in PostgreSQL
- keep future dashboard queries simple and consistent
- support API endpoints with reusable analytical surfaces
- give future AI insight workflows a stable semantic layer
- surface executive risk and recommendation signals without hardcoding them in application code

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

- Streamlit dashboard pages and KPI visualizations
- FastAPI business endpoints beyond placeholders
- AI insight generation
- Scenario analysis workflows

## Next Planned Phase

The next recommended step is to expose the KPI views through application-facing APIs and dashboard surfaces, while preserving the SQL layer as the source of truth for metric definitions.
