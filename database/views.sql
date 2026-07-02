-- PostgreSQL analytical KPI views for Business Intelligence Decision Hub
-- Company: NovaEnergy Services
-- Safe to rerun manually with psql because each object uses CREATE OR REPLACE VIEW.

-- vw_finance_performance
-- Monthly finance rollup by region for revenue, cost, profit, and budget control.
CREATE OR REPLACE VIEW vw_finance_performance AS
WITH finance_base AS (
    SELECT
        dd.year,
        dd.month,
        dr.region_id,
        dr.region_name,
        ff.revenue,
        ff.operating_cost,
        ff.maintenance_cost,
        ff.budgeted_cost,
        ff.profit
    FROM fact_finance AS ff
    JOIN dim_date AS dd
        ON dd.date_id = ff.date_id
    JOIN dim_region AS dr
        ON dr.region_id = ff.region_id
)
SELECT
    year,
    month,
    region_id,
    region_name,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(operating_cost), 2) AS total_operating_cost,
    ROUND(SUM(maintenance_cost), 2) AS total_maintenance_cost,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(profit) / NULLIF(SUM(revenue), 0) * 100, 2) AS operating_margin_pct,
    ROUND(SUM(budgeted_cost), 2) AS budgeted_cost,
    ROUND(SUM(operating_cost + maintenance_cost) - SUM(budgeted_cost), 2) AS budget_variance,
    ROUND(
        (SUM(operating_cost + maintenance_cost) - SUM(budgeted_cost))
        / NULLIF(SUM(budgeted_cost), 0) * 100,
        2
    ) AS budget_variance_pct
FROM finance_base
GROUP BY
    year,
    month,
    region_id,
    region_name;

-- vw_operations_performance
-- Monthly service-delivery rollup by region for SLA, backlog, and request workload.
CREATE OR REPLACE VIEW vw_operations_performance AS
SELECT
    dd.year,
    dd.month,
    dr.region_id,
    dr.region_name,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE fsr.status = 'Resolved') AS resolved_requests,
    COUNT(*) FILTER (WHERE fsr.status IN ('Open', 'In Progress')) AS open_requests,
    COUNT(*) FILTER (WHERE fsr.within_sla IS FALSE) AS delayed_requests,
    ROUND(
        COUNT(*) FILTER (WHERE fsr.status = 'Resolved' AND fsr.within_sla IS TRUE)::NUMERIC
        / NULLIF(COUNT(*) FILTER (WHERE fsr.status = 'Resolved'), 0) * 100,
        2
    ) AS sla_compliance_pct,
    ROUND(AVG(fsr.actual_resolution_hours) FILTER (WHERE fsr.status = 'Resolved'), 2) AS avg_resolution_hours,
    COUNT(*) FILTER (WHERE fsr.priority = 'Critical') AS critical_requests,
    COUNT(*) FILTER (WHERE fsr.status IN ('Open', 'In Progress')) AS backlog_volume
FROM fact_service_requests AS fsr
JOIN dim_date AS dd
    ON dd.date_id = fsr.date_id
JOIN dim_region AS dr
    ON dr.region_id = fsr.region_id
GROUP BY
    dd.year,
    dd.month,
    dr.region_id,
    dr.region_name;

-- vw_asset_performance
-- Monthly asset-performance rollup by region and asset type.
-- Asset risk score blends maintenance stress, failure frequency, downtime, and asset age,
-- then caps the indicator between 0 and 100 for a simple risk surface.
CREATE OR REPLACE VIEW vw_asset_performance AS
WITH month_calendar AS (
    SELECT DISTINCT
        year,
        month
    FROM dim_date
),
asset_inventory AS (
    SELECT
        dr.region_id,
        dr.region_name,
        da.asset_type,
        COUNT(*) AS total_assets,
        COUNT(*) FILTER (WHERE da.asset_status = 'Active') AS active_assets,
        ROUND(AVG(da.asset_age_years), 2) AS avg_asset_age
    FROM dim_asset AS da
    JOIN dim_region AS dr
        ON dr.region_id = da.region_id
    GROUP BY
        dr.region_id,
        dr.region_name,
        da.asset_type
),
maintenance_monthly AS (
    SELECT
        dd.year,
        dd.month,
        dr.region_id,
        dr.region_name,
        da.asset_type,
        COUNT(*) AS maintenance_events,
        ROUND(SUM(fm.downtime_hours), 2) AS total_downtime_hours,
        ROUND(SUM(fm.maintenance_cost), 2) AS total_maintenance_cost,
        COUNT(*) FILTER (WHERE fm.maintenance_type = 'Corrective') AS corrective_maintenance_events,
        COUNT(*) FILTER (WHERE fm.maintenance_type = 'Preventive') AS preventive_maintenance_events,
        COUNT(*) FILTER (WHERE fm.failure_detected IS TRUE) AS failure_events
    FROM fact_maintenance AS fm
    JOIN dim_date AS dd
        ON dd.date_id = fm.date_id
    JOIN dim_region AS dr
        ON dr.region_id = fm.region_id
    JOIN dim_asset AS da
        ON da.asset_id = fm.asset_id
    GROUP BY
        dd.year,
        dd.month,
        dr.region_id,
        dr.region_name,
        da.asset_type
)
SELECT
    mc.year,
    mc.month,
    ai.region_id,
    ai.region_name,
    ai.asset_type,
    ai.total_assets,
    ai.active_assets,
    COALESCE(mm.maintenance_events, 0) AS maintenance_events,
    COALESCE(mm.total_downtime_hours, 0) AS total_downtime_hours,
    COALESCE(mm.total_maintenance_cost, 0) AS total_maintenance_cost,
    COALESCE(mm.corrective_maintenance_events, 0) AS corrective_maintenance_events,
    COALESCE(mm.preventive_maintenance_events, 0) AS preventive_maintenance_events,
    COALESCE(mm.failure_events, 0) AS failure_events,
    ai.avg_asset_age,
    ROUND(
        LEAST(
            100,
            COALESCE(mm.total_downtime_hours, 0) * 0.60
            + COALESCE(mm.corrective_maintenance_events, 0) * 4.00
            + COALESCE(mm.failure_events, 0) * 6.00
            + COALESCE(ai.avg_asset_age, 0) * 2.00
        ),
        2
    ) AS asset_risk_score
FROM month_calendar AS mc
CROSS JOIN asset_inventory AS ai
LEFT JOIN maintenance_monthly AS mm
    ON mm.year = mc.year
    AND mm.month = mc.month
    AND mm.region_id = ai.region_id
    AND mm.asset_type = ai.asset_type;

-- vw_customer_performance
-- Monthly customer-experience rollup by region and segment.
CREATE OR REPLACE VIEW vw_customer_performance AS
SELECT
    dd.year,
    dd.month,
    dr.region_id,
    dr.region_name,
    dc.customer_segment,
    COUNT(*) AS total_feedback_records,
    ROUND(AVG(fcf.satisfaction_score), 2) AS avg_satisfaction_score,
    COUNT(*) FILTER (WHERE fcf.complaint_flag IS TRUE) AS complaint_count,
    ROUND(
        COUNT(*) FILTER (WHERE fcf.complaint_flag IS TRUE)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        2
    ) AS complaint_rate_pct,
    ROUND(AVG(fcf.churn_risk_score), 2) AS avg_churn_risk_score,
    COUNT(*) FILTER (WHERE fcf.churn_risk_score >= 70) AS high_churn_risk_customers
FROM fact_customer_feedback AS fcf
JOIN dim_date AS dd
    ON dd.date_id = fcf.date_id
JOIN dim_region AS dr
    ON dr.region_id = fcf.region_id
JOIN dim_customer AS dc
    ON dc.customer_id = fcf.customer_id
GROUP BY
    dd.year,
    dd.month,
    dr.region_id,
    dr.region_name,
    dc.customer_segment;

-- vw_esg_performance
-- Monthly sustainability rollup by region.
CREATE OR REPLACE VIEW vw_esg_performance AS
SELECT
    dd.year,
    dd.month,
    dr.region_id,
    dr.region_name,
    ROUND(SUM(fe.energy_consumption_kwh), 2) AS total_energy_consumption_kwh,
    ROUND(SUM(fe.co2_emissions_kg), 2) AS total_co2_emissions_kg,
    ROUND(SUM(fe.water_consumption_m3), 2) AS total_water_consumption_m3,
    ROUND(SUM(fe.waste_kg), 2) AS total_waste_kg,
    ROUND(AVG(fe.renewable_energy_share), 2) AS avg_renewable_energy_share,
    ROUND(
        SUM(fe.co2_emissions_kg) / NULLIF(SUM(fe.energy_consumption_kwh), 0),
        4
    ) AS emissions_intensity_kg_per_kwh
FROM fact_esg AS fe
JOIN dim_date AS dd
    ON dd.date_id = fe.date_id
JOIN dim_region AS dr
    ON dr.region_id = fe.region_id
GROUP BY
    dd.year,
    dd.month,
    dr.region_id,
    dr.region_name;

-- vw_executive_kpis
-- Monthly executive rollup by region. The health score uses simple weighted sub-scores:
-- finance 30%, operations 25%, customer 20%, asset 15%, ESG 10%.
-- Risk rises when margin, SLA, and satisfaction weaken, and when downtime or emissions rise.
CREATE OR REPLACE VIEW vw_executive_kpis AS
WITH asset_region_month AS (
    SELECT
        year,
        month,
        region_id,
        region_name,
        ROUND(SUM(total_downtime_hours), 2) AS total_downtime_hours,
        ROUND(AVG(asset_risk_score), 2) AS avg_asset_risk_score
    FROM vw_asset_performance
    GROUP BY
        year,
        month,
        region_id,
        region_name
),
customer_region_month AS (
    SELECT
        year,
        month,
        region_id,
        region_name,
        ROUND(AVG(avg_satisfaction_score), 2) AS avg_satisfaction_score,
        ROUND(AVG(avg_churn_risk_score), 2) AS avg_churn_risk_score,
        SUM(high_churn_risk_customers) AS high_churn_risk_customers
    FROM vw_customer_performance
    GROUP BY
        year,
        month,
        region_id,
        region_name
),
view_keys AS (
    SELECT year, month, region_id, region_name FROM vw_finance_performance
    UNION
    SELECT year, month, region_id, region_name FROM vw_operations_performance
    UNION
    SELECT year, month, region_id, region_name FROM asset_region_month
    UNION
    SELECT year, month, region_id, region_name FROM customer_region_month
    UNION
    SELECT year, month, region_id, region_name FROM vw_esg_performance
)
SELECT
    vk.year,
    vk.month,
    vk.region_id,
    vk.region_name,
    fp.total_revenue,
    fp.operating_margin_pct,
    op.sla_compliance_pct,
    crm.avg_satisfaction_score,
    arm.total_downtime_hours,
    ep.total_co2_emissions_kg,
    ROUND(
        LEAST(
            100,
            GREATEST(
                0,
                COALESCE(LEAST(fp.operating_margin_pct * 4, 100), 0) * 0.30
                + COALESCE(op.sla_compliance_pct, 0) * 0.25
                + COALESCE(LEAST(crm.avg_satisfaction_score / 5 * 100, 100), 0) * 0.20
                + COALESCE(GREATEST(0, 100 - arm.avg_asset_risk_score), 0) * 0.15
                + COALESCE(
                    LEAST(
                        100,
                        COALESCE(ep.avg_renewable_energy_share, 0) * 2
                        + GREATEST(0, 1 - COALESCE(ep.emissions_intensity_kg_per_kwh, 0)) * 40
                    ),
                    0
                ) * 0.10
            )
        ),
        2
    ) AS company_health_score,
    ROUND(
        LEAST(
            100,
            GREATEST(0, 20 - COALESCE(fp.operating_margin_pct, 0)) * 2.00
            + GREATEST(0, 90 - COALESCE(op.sla_compliance_pct, 0)) * 0.80
            + GREATEST(0, 4.20 - COALESCE(crm.avg_satisfaction_score, 0)) * 18.00
            + LEAST(COALESCE(arm.total_downtime_hours, 0) / 25.00, 20)
            + LEAST(COALESCE(ep.total_co2_emissions_kg, 0) / 2000.00, 15)
        ),
        2
    ) AS risk_index
FROM view_keys AS vk
LEFT JOIN vw_finance_performance AS fp
    ON fp.year = vk.year
    AND fp.month = vk.month
    AND fp.region_id = vk.region_id
LEFT JOIN vw_operations_performance AS op
    ON op.year = vk.year
    AND op.month = vk.month
    AND op.region_id = vk.region_id
LEFT JOIN asset_region_month AS arm
    ON arm.year = vk.year
    AND arm.month = vk.month
    AND arm.region_id = vk.region_id
LEFT JOIN customer_region_month AS crm
    ON crm.year = vk.year
    AND crm.month = vk.month
    AND crm.region_id = vk.region_id
LEFT JOIN vw_esg_performance AS ep
    ON ep.year = vk.year
    AND ep.month = vk.month
    AND ep.region_id = vk.region_id;

-- vw_decision_recommendations
-- Rule-based monthly management recommendations derived from the executive KPI surface.
CREATE OR REPLACE VIEW vw_decision_recommendations AS
SELECT
    year,
    month,
    region_name,
    'Operations' AS recommendation_area,
    'SLA compliance below 85 percent' AS issue_detected,
    'Increase dispatch coverage, review backlog drivers, and strengthen SLA recovery actions.' AS recommended_action,
    CASE
        WHEN sla_compliance_pct < 75 THEN 'High'
        ELSE 'Medium'
    END AS impact_level,
    CASE
        WHEN sla_compliance_pct < 80 THEN 'High'
        ELSE 'Medium'
    END AS urgency_level,
    ROUND((85 - sla_compliance_pct) * 1.50 + COALESCE(risk_index, 0) * 0.20, 2) AS priority_score
FROM vw_executive_kpis
WHERE sla_compliance_pct < 85

UNION ALL

SELECT
    year,
    month,
    region_name,
    'Finance' AS recommendation_area,
    'Operating margin below 15 percent' AS issue_detected,
    'Review regional cost structure, maintenance burden, and budget discipline.' AS recommended_action,
    CASE
        WHEN operating_margin_pct < 10 THEN 'High'
        ELSE 'Medium'
    END AS impact_level,
    CASE
        WHEN operating_margin_pct < 12 THEN 'High'
        ELSE 'Medium'
    END AS urgency_level,
    ROUND((15 - operating_margin_pct) * 3.00 + COALESCE(risk_index, 0) * 0.25, 2) AS priority_score
FROM vw_executive_kpis
WHERE operating_margin_pct < 15

UNION ALL

SELECT
    year,
    month,
    region_name,
    'Customer Experience' AS recommendation_area,
    'Average satisfaction below 3.5' AS issue_detected,
    'Escalate customer-service recovery plans and address the root causes behind complaints.' AS recommended_action,
    CASE
        WHEN avg_satisfaction_score < 3.0 THEN 'High'
        ELSE 'Medium'
    END AS impact_level,
    CASE
        WHEN avg_satisfaction_score < 3.2 THEN 'High'
        ELSE 'Medium'
    END AS urgency_level,
    ROUND((3.5 - avg_satisfaction_score) * 25.00 + COALESCE(risk_index, 0) * 0.20, 2) AS priority_score
FROM vw_executive_kpis
WHERE avg_satisfaction_score < 3.5

UNION ALL

SELECT
    year,
    month,
    region_name,
    'Asset Reliability' AS recommendation_area,
    'Downtime materially above expected monthly threshold' AS issue_detected,
    'Prioritize preventive maintenance, review failure hotspots, and stabilize critical assets.' AS recommended_action,
    CASE
        WHEN total_downtime_hours > 800 THEN 'High'
        ELSE 'Medium'
    END AS impact_level,
    CASE
        WHEN total_downtime_hours > 700 THEN 'High'
        ELSE 'Medium'
    END AS urgency_level,
    ROUND((total_downtime_hours - 500) * 0.08 + COALESCE(risk_index, 0) * 0.20, 2) AS priority_score
FROM vw_executive_kpis
WHERE total_downtime_hours > 500

UNION ALL

SELECT
    year,
    month,
    region_name,
    'ESG Efficiency' AS recommendation_area,
    'CO2 emissions above expected monthly threshold' AS issue_detected,
    'Launch energy-efficiency actions, inspect high-consumption assets, and improve renewable mix.' AS recommended_action,
    CASE
        WHEN total_co2_emissions_kg > 30000 THEN 'High'
        ELSE 'Medium'
    END AS impact_level,
    CASE
        WHEN total_co2_emissions_kg > 25000 THEN 'High'
        ELSE 'Medium'
    END AS urgency_level,
    ROUND((total_co2_emissions_kg - 20000) / 750.00 + COALESCE(risk_index, 0) * 0.15, 2) AS priority_score
FROM vw_executive_kpis
WHERE total_co2_emissions_kg > 20000;
