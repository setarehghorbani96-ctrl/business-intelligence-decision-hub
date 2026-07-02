# KPI Dictionary

KPI SQL Views v1 adds a reusable semantic layer on top of the NovaEnergy warehouse tables. These PostgreSQL views are designed to support future dashboards, FastAPI endpoints, AI-assisted insights, and executive decision support.

## Implemented Views

### `vw_finance_performance`

Purpose: monthly finance rollup by region.

Main outputs:
- `total_revenue`
- `total_operating_cost`
- `total_maintenance_cost`
- `total_profit`
- `operating_margin_pct`
- `budgeted_cost`
- `budget_variance`
- `budget_variance_pct`

Key formulas:
- `total_profit = SUM(profit)`
- `operating_margin_pct = SUM(profit) / NULLIF(SUM(revenue), 0) * 100`
- `budget_variance = SUM(operating_cost + maintenance_cost) - SUM(budgeted_cost)`
- `budget_variance_pct = budget_variance / NULLIF(SUM(budgeted_cost), 0) * 100`

### `vw_operations_performance`

Purpose: monthly service-delivery rollup by region.

Main outputs:
- `total_requests`
- `resolved_requests`
- `open_requests`
- `delayed_requests`
- `sla_compliance_pct`
- `avg_resolution_hours`
- `critical_requests`
- `backlog_volume`

Key formulas:
- `resolved_requests = COUNT(*) FILTER (WHERE status = 'Resolved')`
- `open_requests = COUNT(*) FILTER (WHERE status IN ('Open', 'In Progress'))`
- `delayed_requests = COUNT(*) FILTER (WHERE within_sla IS FALSE)`
- `sla_compliance_pct = resolved within SLA / resolved requests * 100`
- `backlog_volume = Open + In Progress`

### `vw_asset_performance`

Purpose: monthly asset reliability rollup by region and asset type.

Main outputs:
- `total_assets`
- `active_assets`
- `maintenance_events`
- `total_downtime_hours`
- `total_maintenance_cost`
- `corrective_maintenance_events`
- `preventive_maintenance_events`
- `failure_events`
- `avg_asset_age`
- `asset_risk_score`

Key formula:
- `asset_risk_score` is a capped 0-100 indicator built from downtime, corrective maintenance volume, failure volume, and average asset age.

### `vw_customer_performance`

Purpose: monthly customer-experience rollup by region and customer segment.

Main outputs:
- `total_feedback_records`
- `avg_satisfaction_score`
- `complaint_count`
- `complaint_rate_pct`
- `avg_churn_risk_score`
- `high_churn_risk_customers`

Key formulas:
- `complaint_rate_pct = complaint_count / total_feedback_records * 100`
- `high_churn_risk_customers = COUNT(*) FILTER (WHERE churn_risk_score >= 70)`

### `vw_esg_performance`

Purpose: monthly ESG rollup by region.

Main outputs:
- `total_energy_consumption_kwh`
- `total_co2_emissions_kg`
- `total_water_consumption_m3`
- `total_waste_kg`
- `avg_renewable_energy_share`
- `emissions_intensity_kg_per_kwh`

Key formula:
- `emissions_intensity_kg_per_kwh = total_co2_emissions_kg / NULLIF(total_energy_consumption_kwh, 0)`

### `vw_executive_kpis`

Purpose: monthly executive scorecard by region.

Main outputs:
- `total_revenue`
- `operating_margin_pct`
- `sla_compliance_pct`
- `avg_satisfaction_score`
- `total_downtime_hours`
- `total_co2_emissions_kg`
- `company_health_score`
- `risk_index`

Key formulas:
- `company_health_score` is a weighted score using finance, operations, customer, asset, and ESG sub-scores.
- `risk_index` rises when margin weakens, SLA drops, satisfaction falls, downtime increases, or emissions increase.

### `vw_decision_recommendations`

Purpose: monthly rule-based management recommendations by region.

Main outputs:
- `recommendation_area`
- `issue_detected`
- `recommended_action`
- `impact_level`
- `urgency_level`
- `priority_score`

Rule examples:
- low SLA compliance triggers operational intervention
- low operating margin triggers cost review
- low customer satisfaction triggers service recovery action
- high downtime triggers preventive-maintenance action
- high CO2 emissions trigger energy-efficiency action

## How These Views Support Future Work

- Dashboards can read pre-aggregated KPI views instead of rebuilding business logic in the BI layer.
- FastAPI endpoints can expose stable analytical surfaces to the frontend.
- AI insight workflows can reason from consistent business metrics rather than raw fact tables.
- Validation and QA become easier because KPI definitions are centralized in SQL.

## Validation Queries

Use [validation_queries.sql](/C:/Users/Setareh/Documents/business-intelligence-decision-hub/database/validation_queries.sql) to inspect:

- row counts for main tables
- sample rows from each KPI view
- null KPI checks
- year and month coverage
- region coverage
- highest-risk region-month combinations
- highest-priority recommendations
