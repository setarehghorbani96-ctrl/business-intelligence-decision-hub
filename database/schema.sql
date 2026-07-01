-- PostgreSQL Schema v1 for Business Intelligence Decision Hub
-- Company: NovaEnergy Services
-- Scope: dimensional model foundation for future analytics workloads

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL CHECK (week BETWEEN 1 AND 53),
    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 31)
);

COMMENT ON TABLE dim_date IS 'Calendar dimension used to align all analytical facts at daily grain.';
COMMENT ON COLUMN dim_date.date_id IS 'Surrogate-style integer key, typically represented as YYYYMMDD.';

CREATE TABLE IF NOT EXISTS dim_region (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL,
    area_manager VARCHAR(100),
    region_profile TEXT
);

COMMENT ON TABLE dim_region IS 'Reference list of NovaEnergy operating regions used for geographic slicing.';

CREATE TABLE IF NOT EXISTS dim_department (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_type VARCHAR(100)
);

COMMENT ON TABLE dim_department IS 'Corporate and operational departments used for budget and performance reporting.';

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    contract_type VARCHAR(50),
    start_date DATE,
    status VARCHAR(50) NOT NULL,
    annual_contract_value NUMERIC(14,2),
    CONSTRAINT chk_dim_customer_segment
        CHECK (customer_segment IN ('Industrial', 'Commercial', 'Public Sector', 'Residential')),
    CONSTRAINT chk_dim_customer_status
        CHECK (status IN ('Active', 'Lost', 'Suspended')),
    CONSTRAINT chk_dim_customer_acv
        CHECK (annual_contract_value IS NULL OR annual_contract_value >= 0)
);

COMMENT ON TABLE dim_customer IS 'Customer master data used for customer analytics, service demand, and retention KPIs.';

CREATE TABLE IF NOT EXISTS dim_asset (
    asset_id SERIAL PRIMARY KEY,
    asset_name VARCHAR(150) NOT NULL,
    asset_type VARCHAR(100) NOT NULL,
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    installation_date DATE,
    asset_age_years INTEGER,
    criticality_level VARCHAR(50) NOT NULL,
    asset_status VARCHAR(50) NOT NULL,
    CONSTRAINT chk_dim_asset_type
        CHECK (asset_type IN ('Energy Unit', 'HVAC System', 'Smart Meter', 'Charging Station', 'Industrial Equipment')),
    CONSTRAINT chk_dim_asset_criticality
        CHECK (criticality_level IN ('Low', 'Medium', 'High', 'Critical')),
    CONSTRAINT chk_dim_asset_status
        CHECK (asset_status IN ('Active', 'Maintenance', 'Retired')),
    CONSTRAINT chk_dim_asset_age
        CHECK (asset_age_years IS NULL OR asset_age_years >= 0)
);

COMMENT ON TABLE dim_asset IS 'Asset inventory dimension supporting maintenance, availability, and ESG analysis.';

CREATE TABLE IF NOT EXISTS fact_finance (
    finance_id SERIAL PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    department_id INTEGER NOT NULL REFERENCES dim_department(department_id),
    revenue NUMERIC(14,2) NOT NULL DEFAULT 0,
    operating_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    maintenance_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    budgeted_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    profit NUMERIC(14,2),
    CONSTRAINT chk_fact_finance_revenue
        CHECK (revenue >= 0),
    CONSTRAINT chk_fact_finance_operating_cost
        CHECK (operating_cost >= 0),
    CONSTRAINT chk_fact_finance_maintenance_cost
        CHECK (maintenance_cost >= 0),
    CONSTRAINT chk_fact_finance_budgeted_cost
        CHECK (budgeted_cost >= 0),
    CONSTRAINT chk_fact_finance_profit_consistency
        CHECK (profit IS NULL OR profit = revenue - operating_cost - maintenance_cost)
);

COMMENT ON TABLE fact_finance IS 'Financial fact table at date-region-department grain for revenue, cost, and margin analysis.';

CREATE TABLE IF NOT EXISTS fact_service_requests (
    request_id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    customer_id INTEGER NOT NULL REFERENCES dim_customer(customer_id),
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    asset_id INTEGER REFERENCES dim_asset(asset_id),
    request_type VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    sla_target_hours NUMERIC(10,2) NOT NULL,
    actual_resolution_hours NUMERIC(10,2),
    within_sla BOOLEAN,
    CONSTRAINT chk_fact_service_requests_priority
        CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    CONSTRAINT chk_fact_service_requests_status
        CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Cancelled')),
    CONSTRAINT chk_fact_service_requests_sla_target
        CHECK (sla_target_hours >= 0),
    CONSTRAINT chk_fact_service_requests_resolution_hours
        CHECK (actual_resolution_hours IS NULL OR actual_resolution_hours >= 0),
    CONSTRAINT chk_fact_service_requests_resolved_after_created
        CHECK (resolved_at IS NULL OR resolved_at >= created_at),
    CONSTRAINT chk_fact_service_requests_sla_flag
        CHECK (within_sla IS NULL OR actual_resolution_hours IS NOT NULL)
);

COMMENT ON TABLE fact_service_requests IS 'Service operations fact table used for SLA, backlog, and resolution-time performance analysis.';

CREATE TABLE IF NOT EXISTS fact_maintenance (
    maintenance_id SERIAL PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    asset_id INTEGER NOT NULL REFERENCES dim_asset(asset_id),
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    maintenance_type VARCHAR(50) NOT NULL,
    downtime_hours NUMERIC(10,2) NOT NULL DEFAULT 0,
    maintenance_cost NUMERIC(14,2) NOT NULL DEFAULT 0,
    failure_detected BOOLEAN NOT NULL DEFAULT false,
    technician_team VARCHAR(100),
    CONSTRAINT chk_fact_maintenance_type
        CHECK (maintenance_type IN ('Preventive', 'Corrective', 'Inspection', 'Upgrade')),
    CONSTRAINT chk_fact_maintenance_downtime
        CHECK (downtime_hours >= 0),
    CONSTRAINT chk_fact_maintenance_cost
        CHECK (maintenance_cost >= 0)
);

COMMENT ON TABLE fact_maintenance IS 'Maintenance event fact table supporting downtime, failure, and cost tracking by asset and region.';

CREATE TABLE IF NOT EXISTS fact_customer_feedback (
    feedback_id SERIAL PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    customer_id INTEGER NOT NULL REFERENCES dim_customer(customer_id),
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    satisfaction_score NUMERIC(3,2) NOT NULL,
    complaint_flag BOOLEAN NOT NULL DEFAULT false,
    churn_risk_score NUMERIC(5,2) NOT NULL,
    CONSTRAINT chk_fact_customer_feedback_satisfaction
        CHECK (satisfaction_score BETWEEN 1 AND 5),
    CONSTRAINT chk_fact_customer_feedback_churn
        CHECK (churn_risk_score BETWEEN 0 AND 100)
);

COMMENT ON TABLE fact_customer_feedback IS 'Customer experience fact table for satisfaction, complaint, and churn-risk monitoring.';

CREATE TABLE IF NOT EXISTS fact_esg (
    esg_id SERIAL PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    asset_id INTEGER REFERENCES dim_asset(asset_id),
    energy_consumption_kwh NUMERIC(14,2) NOT NULL DEFAULT 0,
    co2_emissions_kg NUMERIC(14,2) NOT NULL DEFAULT 0,
    water_consumption_m3 NUMERIC(14,2) NOT NULL DEFAULT 0,
    waste_kg NUMERIC(14,2) NOT NULL DEFAULT 0,
    renewable_energy_share NUMERIC(5,2),
    CONSTRAINT chk_fact_esg_energy
        CHECK (energy_consumption_kwh >= 0),
    CONSTRAINT chk_fact_esg_co2
        CHECK (co2_emissions_kg >= 0),
    CONSTRAINT chk_fact_esg_water
        CHECK (water_consumption_m3 >= 0),
    CONSTRAINT chk_fact_esg_waste
        CHECK (waste_kg >= 0),
    CONSTRAINT chk_fact_esg_renewable_share
        CHECK (renewable_energy_share IS NULL OR renewable_energy_share BETWEEN 0 AND 100)
);

COMMENT ON TABLE fact_esg IS 'ESG and sustainability fact table for environmental-performance KPI tracking.';

CREATE TABLE IF NOT EXISTS fact_targets (
    target_id SERIAL PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    region_id INTEGER REFERENCES dim_region(region_id),
    department_id INTEGER REFERENCES dim_department(department_id),
    kpi_name VARCHAR(150) NOT NULL,
    target_value NUMERIC(14,2) NOT NULL,
    target_unit VARCHAR(50),
    target_period VARCHAR(50)
);

COMMENT ON TABLE fact_targets IS 'Target-setting fact table used to compare actual KPI results with business goals.';

CREATE INDEX IF NOT EXISTS idx_dim_customer_customer_segment
    ON dim_customer (customer_segment);

CREATE INDEX IF NOT EXISTS idx_dim_asset_asset_type
    ON dim_asset (asset_type);

CREATE INDEX IF NOT EXISTS idx_fact_finance_date_id
    ON fact_finance (date_id);

CREATE INDEX IF NOT EXISTS idx_fact_finance_region_id
    ON fact_finance (region_id);

CREATE INDEX IF NOT EXISTS idx_fact_finance_department_id
    ON fact_finance (department_id);

CREATE INDEX IF NOT EXISTS idx_fact_service_requests_date_id
    ON fact_service_requests (date_id);

CREATE INDEX IF NOT EXISTS idx_fact_service_requests_region_id
    ON fact_service_requests (region_id);

CREATE INDEX IF NOT EXISTS idx_fact_service_requests_customer_id
    ON fact_service_requests (customer_id);

CREATE INDEX IF NOT EXISTS idx_fact_service_requests_asset_id
    ON fact_service_requests (asset_id);

CREATE INDEX IF NOT EXISTS idx_fact_service_requests_status
    ON fact_service_requests (status);

CREATE INDEX IF NOT EXISTS idx_fact_maintenance_date_id
    ON fact_maintenance (date_id);

CREATE INDEX IF NOT EXISTS idx_fact_maintenance_region_id
    ON fact_maintenance (region_id);

CREATE INDEX IF NOT EXISTS idx_fact_maintenance_asset_id
    ON fact_maintenance (asset_id);

CREATE INDEX IF NOT EXISTS idx_fact_customer_feedback_date_id
    ON fact_customer_feedback (date_id);

CREATE INDEX IF NOT EXISTS idx_fact_customer_feedback_region_id
    ON fact_customer_feedback (region_id);

CREATE INDEX IF NOT EXISTS idx_fact_customer_feedback_customer_id
    ON fact_customer_feedback (customer_id);

CREATE INDEX IF NOT EXISTS idx_fact_esg_date_id
    ON fact_esg (date_id);

CREATE INDEX IF NOT EXISTS idx_fact_esg_region_id
    ON fact_esg (region_id);

CREATE INDEX IF NOT EXISTS idx_fact_esg_asset_id
    ON fact_esg (asset_id);

CREATE INDEX IF NOT EXISTS idx_fact_targets_date_id
    ON fact_targets (date_id);

CREATE INDEX IF NOT EXISTS idx_fact_targets_region_id
    ON fact_targets (region_id);

CREATE INDEX IF NOT EXISTS idx_fact_targets_department_id
    ON fact_targets (department_id);
