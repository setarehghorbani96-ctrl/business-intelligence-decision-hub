# Data Model

Business Intelligence Decision Hub uses a star-schema-inspired PostgreSQL design to support recruiter-friendly analytics storytelling and future dashboard performance. The model keeps business dimensions stable and reusable while allowing fact tables to capture measurable events at clear analytical grain.

## Why This Model

- It separates descriptive business context from measurable activity.
- It supports predictable joins for BI tools, SQL analysis, and semantic-layer views.
- It keeps the initial implementation focused on clean structure before advanced analytics layers are introduced.
- It aligns naturally to KPI development across finance, operations, assets, customers, and ESG.

## Core Relationships

- `dim_date` links to every fact table to standardize time-based reporting.
- `dim_region` links to customers, assets, and all fact domains to support geographic analysis.
- `dim_department` links to finance and targets for accountability and planning use cases.
- `dim_customer` links to service requests and feedback to support service-quality and retention analysis.
- `dim_asset` links to service requests, maintenance, and ESG activity to support operational and sustainability KPIs.

## Dimension Tables

### `dim_date`

Business purpose: provides a reusable calendar dimension for daily, weekly, monthly, quarterly, and yearly analysis.

Current ETL usage: loaded first so every downstream fact table can reference a valid `date_id`.

### `dim_region`

Business purpose: defines NovaEnergy's operating footprint and provides the geographic lens used across the platform.

Current ETL usage: loaded before customers, assets, and facts because it anchors the regional foreign keys used across the model.

### `dim_department`

Business purpose: represents organizational ownership for budget, cost, and target accountability.

Current ETL usage: loaded before finance and target facts so departmental ownership is available during load validation.

### `dim_customer`

Business purpose: stores customer master data, segmentation, contract context, and account status.

Current ETL usage: loaded before service requests and customer feedback because both fact tables depend on valid customer keys.

### `dim_asset`

Business purpose: stores asset inventory and operational classification details across the regional footprint.

Current ETL usage: loaded before service requests, maintenance, and ESG facts because those tables optionally or directly reference `asset_id`.

## Fact Tables

### `fact_finance`

Business purpose: captures financial performance by date, region, and department.

Analytical grain: one finance record per month-region-department combination in the current synthetic dataset.

### `fact_service_requests`

Business purpose: captures customer service activity and operational response performance.

Analytical grain: one service request event per request.

### `fact_maintenance`

Business purpose: records asset maintenance activity and related operational impact.

Analytical grain: one maintenance event per asset/date occurrence.

### `fact_customer_feedback`

Business purpose: captures customer sentiment and retention-risk indicators.

Analytical grain: one feedback event per customer/date occurrence.

### `fact_esg`

Business purpose: records environmental performance measures across regions and assets.

Analytical grain: one ESG measurement record per date, region, and optional asset context.

### `fact_targets`

Business purpose: stores KPI targets for planned-versus-actual comparison.

Analytical grain: one target definition per date, KPI, and optional regional or departmental scope.

## ETL Loading Order

The ETL loader uses this dependency-safe table order:

1. `dim_date`
2. `dim_region`
3. `dim_department`
4. `dim_customer`
5. `dim_asset`
6. `fact_finance`
7. `fact_service_requests`
8. `fact_maintenance`
9. `fact_customer_feedback`
10. `fact_esg`
11. `fact_targets`

This keeps foreign key relationships valid during append operations after the replace-mode truncate step.

## Design Notes

- Surrogate integer keys are used for business dimensions to simplify joins and future warehouse evolution.
- Check constraints are included where business-controlled value domains are already known.
- Fact tables are indexed on expected analytical filters such as date, region, department, customer, asset, and service status.
- Synthetic CSV files in `data/sample/` are treated as the source contract for ETL Loader v1.
- ETL Loader v1 truncates and reloads all tables in replace mode, then resets PostgreSQL sequences for the SERIAL-backed tables.
