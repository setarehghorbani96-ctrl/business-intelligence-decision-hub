-- Starter reference seed data for Business Intelligence Decision Hub
-- Scope limited to shared dimensions required for schema v1 initialization.

INSERT INTO dim_region (region_name, country, area_manager, region_profile)
VALUES
    ('North-West', 'Italy', NULL, 'Mature industrial territory with high-density service coverage.'),
    ('North-East', 'Italy', NULL, 'Growth-oriented region with manufacturing and infrastructure demand.'),
    ('Central', 'Italy', NULL, 'Balanced portfolio across public sector, commercial, and mixed-use assets.'),
    ('South', 'Italy', NULL, 'Operationally diverse region with service expansion opportunities.'),
    ('Islands', 'Italy', NULL, 'Distributed regional footprint with higher logistical complexity.')
ON CONFLICT (region_name) DO NOTHING;

INSERT INTO dim_department (department_name, department_type)
VALUES
    ('Executive', 'Leadership'),
    ('Finance', 'Corporate'),
    ('Sales', 'Commercial'),
    ('Operations', 'Operational'),
    ('Assets', 'Operational'),
    ('ESG', 'Sustainability'),
    ('Customer Service', 'Support'),
    ('Digital Transformation', 'Strategic Enablement')
ON CONFLICT (department_name) DO NOTHING;
