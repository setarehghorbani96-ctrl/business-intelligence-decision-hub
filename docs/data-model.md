# Data Model

Business Intelligence Decision Hub uses a star-schema-inspired PostgreSQL design to support recruiter-friendly analytics storytelling and future dashboard performance. The model keeps business dimensions stable and reusable while allowing fact tables to capture measurable events at clear analytical grain.

## Why This Model

- It separates descriptive business context from measurable activity.
- It supports predictable joins for BI tools, SQL analysis, and semantic-layer views.
- It keeps the initial implementation focused on clean structure before synthetic data, ETL logic, or AI recommendations are introduced.
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

Future KPI usage: trend reporting for revenue growth, downtime hours, SLA compliance, emissions, and target progress.

### `dim_region`

Business purpose: defines NovaEnergy's operating footprint and provides the geographic lens used across the platform.

Future KPI usage: regional comparisons for revenue, service backlog, maintenance costs, customer satisfaction, and ESG performance.

### `dim_department`

Business purpose: represents organizational ownership for budget, cost, and target accountability.

Future KPI usage: operating margin, budget variance, and KPI target ownership by function.

### `dim_customer`

Business purpose: stores customer master data, segmentation, contract context, and account status.

Future KPI usage: contract-value analysis, service-demand patterns, churn risk, and customer satisfaction tracking.

### `dim_asset`

Business purpose: stores asset inventory and operational classification details across the regional footprint.

Future KPI usage: asset availability, downtime analysis, maintenance cost tracking, and asset-level ESG performance.

## Fact Tables

### `fact_finance`

Business purpose: captures financial performance by date, region, and department.

Analytical grain: one finance record per date, region, and department combination as defined by future source processes.

Future KPI usage: revenue growth, operating margin, cost mix, and budget variance.

### `fact_service_requests`

Business purpose: captures customer service activity and operational response performance.

Analytical grain: one service request event per request.

Future KPI usage: SLA compliance, average resolution time, request backlog volume, and priority analysis.

### `fact_maintenance`

Business purpose: records asset maintenance activity and related operational impact.

Analytical grain: one maintenance event per asset/date occurrence.

Future KPI usage: downtime hours, maintenance cost, failure rates, and preventive-versus-corrective mix.

### `fact_customer_feedback`

Business purpose: captures customer sentiment and retention-risk indicators.

Analytical grain: one feedback event per customer/date occurrence.

Future KPI usage: customer satisfaction, complaint incidence, and churn risk monitoring.

### `fact_esg`

Business purpose: records environmental performance measures across regions and assets.

Analytical grain: one ESG measurement record per date, region, and optional asset context.

Future KPI usage: energy consumption, CO2 emissions, water consumption, waste generation, and renewable energy share.

### `fact_targets`

Business purpose: stores KPI targets for planned-versus-actual comparison.

Analytical grain: one target definition per date, KPI, and optional regional or departmental scope.

Future KPI usage: target attainment, ESG goal progress, and management scorecard reporting.

## Design Notes

- Surrogate integer keys are used for business dimensions to simplify joins and future warehouse evolution.
- Check constraints are included where business-controlled value domains are already known.
- Fact tables are indexed on expected analytical filters such as date, region, department, customer, asset, and service status.
- The schema is intentionally versioned as a foundation model so that future ETL, synthetic data generation, KPI views, and dashboard layers can build on a stable contract.
