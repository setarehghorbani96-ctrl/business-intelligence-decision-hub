# Business Intelligence Decision Hub

Business Intelligence Decision Hub is a professional portfolio project for a role-based business intelligence and decision-support platform built around the fictional company NovaEnergy Services.

The current implementation includes the Docker-ready project foundation, PostgreSQL Schema v1, a reproducible synthetic data generator, ETL Loader v1, KPI SQL Views v1, FastAPI KPI Endpoints v1, and Streamlit Executive Dashboard v1 for executive-level KPI visibility.

## Current Scope

- Dockerized local development workflow
- PostgreSQL service initialization from the `database/` folder
- PostgreSQL Schema v1 for NovaEnergy Services
- Starter seed data for regions and departments
- Synthetic data generator for dimensions, fact tables, and KPI targets
- ETL Loader v1 for CSV validation and PostgreSQL loading
- KPI SQL Views v1 for finance, operations, assets, customers, ESG, executive scorecards, and rule-based recommendations
- FastAPI KPI endpoints for health, KPI views, and decision recommendations
- Streamlit Executive Command Center connected to FastAPI
- Sample CSV outputs in `data/sample/`
- Starter folders for AI insights, analytics assets, tests, and documentation

## Setup

In Windows PowerShell:

```powershell
Copy-Item .env.example .env -Force
docker compose down -v
docker compose up --build
```

The example environment file defaults the host-side ETL workflow to `localhost`, while Docker overrides container-side database access to `postgres` for the API and `api:8000` for the Streamlit dashboard.

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

## API Endpoints

The backend exposes KPI views directly through FastAPI so the dashboard can consume a stable, governed API contract instead of querying PostgreSQL directly.

Example test URLs:

- http://localhost:8000/health
- http://localhost:8000/health/database
- http://localhost:8000/kpis/executive?limit=5
- http://localhost:8000/kpis/finance?year=2025&limit=5
- http://localhost:8000/recommendations/actions?limit=10

Additional example filters:

- http://localhost:8000/kpis/executive?year=2025&region=North-West
- http://localhost:8000/kpis/operations?year=2025&month=6
- http://localhost:8000/kpis/assets?region=South&limit=25

## Streamlit Executive Dashboard v1

The repository now includes an Executive Command Center built in Streamlit for NovaEnergy Services leadership review. It focuses on the executive layer only and uses FastAPI as the data access boundary.

### What it includes

- Sidebar filters for year, month, and region selection
- KPI cards for revenue, margin, SLA, customer satisfaction, downtime, CO2 emissions, health score, and risk index
- Plotly charts for revenue trend, margin trend, SLA trend, and regional KPI comparisons
- A recommendations panel powered by `GET /recommendations/actions`
- Friendly empty and error states for API, database, and no-data scenarios

### Dashboard Region Comparison

Users can compare one region, several regions, or all regions directly in the executive dashboard. Streamlit consumes the FastAPI KPI endpoints, then filters and aggregates the returned dataframes locally for multi-region comparison. The dashboard does not query PostgreSQL directly.

### Start Docker

```powershell
Copy-Item .env.example .env -Force
docker compose down -v
docker compose up --build
```

### Access The Dashboard

- Streamlit: http://localhost:8501
- API health: http://localhost:8000/health
- API database health: http://localhost:8000/health/database
- Executive KPI endpoint: http://localhost:8000/kpis/executive?limit=5

### Backend API URLs Used By Streamlit

- `GET /kpis/executive`
- `GET /kpis/finance`
- `GET /kpis/operations`
- `GET /recommendations/actions`

The Streamlit app reads `API_HOST` and `API_PORT`. Inside Docker Compose it connects to FastAPI at `http://api:8000`. If you run Streamlit locally outside Docker, it falls back to `http://localhost:8000` when the Docker hostname is not reachable.

### Troubleshooting

- If Streamlit shows `API is not available`, start the stack with `docker compose up --build` and confirm http://localhost:8000/health responds.
- If Streamlit shows a database availability error, reload CSV data with the ETL pipeline and reapply `database/views.sql`.
- If charts are empty, verify data exists with http://localhost:8000/kpis/executive?limit=5 and confirm your selected filters match available rows.
- If Docker was already running before the KPI views changed, reapply the views manually with `docker compose exec postgres psql -U postgres -d bi_decision_hub -f /docker-entrypoint-initdb.d/views.sql`.

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
- keep dashboard and API queries simple and consistent
- support API endpoints with reusable analytical surfaces
- give future AI insight workflows a stable semantic layer
- surface executive risk and recommendation signals without hardcoding them in application code

## Service Endpoints

- FastAPI: http://localhost:8000
- FastAPI health check: http://localhost:8000/health
- FastAPI database health check: http://localhost:8000/health/database
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

- Additional department-specific Streamlit dashboards
- AI insight generation
- Scenario analysis workflows

## Next Planned Phase

The next recommended step is to extend the executive experience into drill-down dashboards for finance, operations, assets, customers, and ESG while keeping FastAPI as the stable contract between business metrics and the UI.
