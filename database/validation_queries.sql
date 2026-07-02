-- Validation queries for KPI SQL Views v1
-- These queries are non-destructive and intended for manual QA in PostgreSQL.

-- 1. Row counts for core warehouse tables.
SELECT 'dim_date' AS object_name, COUNT(*) AS row_count FROM dim_date
UNION ALL
SELECT 'dim_region', COUNT(*) FROM dim_region
UNION ALL
SELECT 'dim_department', COUNT(*) FROM dim_department
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_asset', COUNT(*) FROM dim_asset
UNION ALL
SELECT 'fact_finance', COUNT(*) FROM fact_finance
UNION ALL
SELECT 'fact_service_requests', COUNT(*) FROM fact_service_requests
UNION ALL
SELECT 'fact_maintenance', COUNT(*) FROM fact_maintenance
UNION ALL
SELECT 'fact_customer_feedback', COUNT(*) FROM fact_customer_feedback
UNION ALL
SELECT 'fact_esg', COUNT(*) FROM fact_esg
UNION ALL
SELECT 'fact_targets', COUNT(*) FROM fact_targets
ORDER BY object_name;

-- 2. Sample rows from each KPI view.
SELECT * FROM vw_finance_performance ORDER BY year, month, region_name LIMIT 5;
SELECT * FROM vw_operations_performance ORDER BY year, month, region_name LIMIT 5;
SELECT * FROM vw_asset_performance ORDER BY year, month, region_name, asset_type LIMIT 5;
SELECT * FROM vw_customer_performance ORDER BY year, month, region_name, customer_segment LIMIT 5;
SELECT * FROM vw_esg_performance ORDER BY year, month, region_name LIMIT 5;
SELECT * FROM vw_executive_kpis ORDER BY year, month, region_name LIMIT 5;
SELECT * FROM vw_decision_recommendations ORDER BY priority_score DESC LIMIT 5;

-- 3. Null KPI checks for the main analytical views.
SELECT 'vw_finance_performance.operating_margin_pct' AS check_name, COUNT(*) AS null_rows
FROM vw_finance_performance
WHERE operating_margin_pct IS NULL
UNION ALL
SELECT 'vw_operations_performance.sla_compliance_pct', COUNT(*)
FROM vw_operations_performance
WHERE sla_compliance_pct IS NULL
UNION ALL
SELECT 'vw_asset_performance.asset_risk_score', COUNT(*)
FROM vw_asset_performance
WHERE asset_risk_score IS NULL
UNION ALL
SELECT 'vw_customer_performance.avg_satisfaction_score', COUNT(*)
FROM vw_customer_performance
WHERE avg_satisfaction_score IS NULL
UNION ALL
SELECT 'vw_esg_performance.emissions_intensity_kg_per_kwh', COUNT(*)
FROM vw_esg_performance
WHERE emissions_intensity_kg_per_kwh IS NULL
UNION ALL
SELECT 'vw_executive_kpis.company_health_score', COUNT(*)
FROM vw_executive_kpis
WHERE company_health_score IS NULL
UNION ALL
SELECT 'vw_executive_kpis.risk_index', COUNT(*)
FROM vw_executive_kpis
WHERE risk_index IS NULL;

-- 4. Available year and month coverage across the KPI views.
SELECT 'vw_finance_performance' AS view_name, MIN(year) AS min_year, MAX(year) AS max_year, MIN(month) AS min_month, MAX(month) AS max_month
FROM vw_finance_performance
UNION ALL
SELECT 'vw_operations_performance', MIN(year), MAX(year), MIN(month), MAX(month)
FROM vw_operations_performance
UNION ALL
SELECT 'vw_asset_performance', MIN(year), MAX(year), MIN(month), MAX(month)
FROM vw_asset_performance
UNION ALL
SELECT 'vw_customer_performance', MIN(year), MAX(year), MIN(month), MAX(month)
FROM vw_customer_performance
UNION ALL
SELECT 'vw_esg_performance', MIN(year), MAX(year), MIN(month), MAX(month)
FROM vw_esg_performance
UNION ALL
SELECT 'vw_executive_kpis', MIN(year), MAX(year), MIN(month), MAX(month)
FROM vw_executive_kpis;

-- 5. Region coverage across the KPI views.
SELECT 'vw_finance_performance' AS view_name, COUNT(DISTINCT region_name) AS distinct_regions FROM vw_finance_performance
UNION ALL
SELECT 'vw_operations_performance', COUNT(DISTINCT region_name) FROM vw_operations_performance
UNION ALL
SELECT 'vw_asset_performance', COUNT(DISTINCT region_name) FROM vw_asset_performance
UNION ALL
SELECT 'vw_customer_performance', COUNT(DISTINCT region_name) FROM vw_customer_performance
UNION ALL
SELECT 'vw_esg_performance', COUNT(DISTINCT region_name) FROM vw_esg_performance
UNION ALL
SELECT 'vw_executive_kpis', COUNT(DISTINCT region_name) FROM vw_executive_kpis;

-- 6. Highest-risk region-month combinations.
SELECT
    year,
    month,
    region_name,
    operating_margin_pct,
    sla_compliance_pct,
    avg_satisfaction_score,
    total_downtime_hours,
    total_co2_emissions_kg,
    risk_index
FROM vw_executive_kpis
ORDER BY risk_index DESC, year DESC, month DESC
LIMIT 5;

-- 7. Top recommendations by priority.
SELECT
    year,
    month,
    region_name,
    recommendation_area,
    issue_detected,
    impact_level,
    urgency_level,
    priority_score
FROM vw_decision_recommendations
ORDER BY priority_score DESC, year DESC, month DESC
LIMIT 5;
