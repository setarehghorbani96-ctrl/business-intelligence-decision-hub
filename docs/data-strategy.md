# Data Strategy

NovaEnergy Services uses synthetic enterprise data to demonstrate dimensional modeling, KPI design, and analytics storytelling without exposing confidential business information.

## Why Synthetic Data Is Used

- The project is a portfolio platform, so reproducibility and safety matter more than access to real operational systems.
- Synthetic data allows the warehouse model to be populated with realistic scale and business behavior.
- The same datasets can be regenerated at any time with a fixed random seed, which keeps testing and demos stable.

## Data Generation Scope

The current synthetic data generator produces CSV outputs in `data/sample/` for:

- shared dimensions: date, region, department, customer, asset
- operational facts: service requests and maintenance events
- financial facts: revenue, operating cost, maintenance cost, profit, budgeted cost
- customer facts: satisfaction, complaints, churn risk
- ESG facts: energy consumption, CO2 emissions, water, waste, renewable share
- management targets: monthly KPI targets by region and department where relevant

The generated period covers daily and monthly analytical activity from January 2024 through December 2025.

## Simulated Business Relationships

The generator is designed to preserve business logic that will matter in later analytics layers:

- Older assets create more maintenance events and more corrective work.
- Corrective maintenance creates more downtime than preventive maintenance.
- Higher downtime increases operational pressure and lowers SLA performance.
- Lower SLA performance reduces customer satisfaction and raises churn risk.
- Industrial customers carry higher contract values.
- Public Sector customers have lower churn sensitivity.
- Residential customers have lower contract value and higher churn sensitivity.
- North-West combines strong revenue with older assets, higher maintenance cost, and higher ESG pressure.
- North-East is more stable, with better asset condition and stronger SLA compliance.
- Islands operates at lower volume but with longer resolution time because of logistics complexity.
- Older assets consume more energy, which increases CO2 emissions.
- Renewable energy share improves gradually from 2024 to 2025.

## Data Quality And Validation

After generation, the workflow validates that:

- every expected CSV file is created
- primary key fields are populated and unique
- foreign key references match the dimension tables
- generated values respect major schema constraints
- Python source files compile successfully

This validation happens before any future load step into PostgreSQL.

## Refresh Approach

Synthetic data can be refreshed by rerunning:

```bash
python -m data_generation.generate_synthetic_data
```

Configuration values such as the random seed, date range, and target row counts are managed in `data_generation/config.py`.

## Governance Notes

- No real company or customer data is included.
- The generated datasets are designed for analytics development, demos, and dashboard prototyping.
- The warehouse schema remains the source-of-truth contract for column definitions and allowed value domains.
