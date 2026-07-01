# Business Intelligence Decision Hub

Business Intelligence Decision Hub is a professional portfolio project for a role-based business intelligence and decision-support platform built around the fictional company NovaEnergy Services.

This repository now includes PostgreSQL Schema v1 in addition to the Docker-ready project foundation. The current implementation provides a dimensional database design, starter regional and departmental reference data, a placeholder FastAPI backend, a placeholder Streamlit frontend, shared environment configuration, and project documentation for the next phases.

## Current Scope

- Dockerized local development workflow
- PostgreSQL service initialization from the `database/` folder
- PostgreSQL Schema v1 for NovaEnergy Services
- Starter seed data for regions and departments
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

## Service Endpoints

- FastAPI: http://localhost:8000
- FastAPI health check: http://localhost:8000/health
- Streamlit: http://localhost:8501
- PostgreSQL: localhost:5432

## PostgreSQL Schema v1

Schema v1 introduces the first analytics-ready PostgreSQL structure for NovaEnergy Services, including shared dimensions, core fact tables, starter reference seeds, and placeholder semantic-layer view definitions for future KPI work.

If you change the schema and need a clean database reset in Windows PowerShell, run:

```powershell
docker compose down -v
docker compose up --build
```

## Troubleshooting

If containers or volumes get into a bad state, recreate the stack:

```bash
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

- Synthetic company data generation
- ETL logic
- Dashboard pages and metrics
- AI insight generation
- Scenario analysis workflows

## Next Planned Phase

The next recommended step is to populate the dimensions and fact tables with representative company data and then define KPI logic on top of the validated schema.
