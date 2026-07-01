# Business Intelligence Decision Hub

Business Intelligence Decision Hub is a professional portfolio project for a role-based business intelligence and decision-support platform built around the fictional company NovaEnergy Services.

The current implementation includes the Docker-ready project foundation, PostgreSQL Schema v1, and a reproducible synthetic data generator that produces analytics-friendly CSV datasets aligned to the warehouse model.

## Current Scope

- Dockerized local development workflow
- PostgreSQL service initialization from the `database/` folder
- PostgreSQL Schema v1 for NovaEnergy Services
- Starter seed data for regions and departments
- Synthetic data generator for dimensions, fact tables, and KPI targets
- Sample CSV outputs in `data/sample/`
- FastAPI placeholder service with a health endpoint
- Streamlit placeholder application shell
- Starter folders for ETL, AI insights, analytics assets, tests, and documentation

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

If you are using PowerShell, you can also run:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Generate Synthetic Data

From the project root, run:

```bash
python -m data_generation.generate_synthetic_data
```

The generator creates schema-aligned CSV files in `data/sample/` for:

- `dim_date`
- `dim_region`
- `dim_department`
- `dim_customer`
- `dim_asset`
- `fact_finance`
- `fact_service_requests`
- `fact_maintenance`
- `fact_customer_feedback`
- `fact_esg`
- `fact_targets`

The synthetic data is intentionally relationship-driven rather than random. It simulates how older assets increase maintenance and downtime, how downtime affects SLA performance, how SLA performance influences customer satisfaction and churn risk, and how asset age and regional mix affect energy consumption and CO2 emissions.

## Service Endpoints

- FastAPI: http://localhost:8000
- FastAPI health check: http://localhost:8000/health
- Streamlit: http://localhost:8501
- PostgreSQL: localhost:5432

## PostgreSQL Schema v1

Schema v1 introduces the first analytics-ready PostgreSQL structure for NovaEnergy Services, including shared dimensions, core fact tables, starter reference seeds, and a stable warehouse contract for future ETL and KPI work.

If you change the schema and need a clean database reset in Windows PowerShell, run:

```powershell
docker compose down -v
docker compose up --build
```

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

- ETL logic
- Dashboard pages and KPI visualizations
- FastAPI business endpoints beyond placeholders
- AI insight generation
- Scenario analysis workflows

## Next Planned Phase

The next recommended step is to build the ETL flow that validates and loads the synthetic CSV datasets into PostgreSQL before adding KPI views and dashboard logic.
