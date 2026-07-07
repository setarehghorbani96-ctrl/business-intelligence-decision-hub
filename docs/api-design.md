# API Design

Business Intelligence Decision Hub exposes read-only KPI endpoints for the NovaEnergy Services decision-support workflow. The SQL view layer remains the source of truth, and the FastAPI layer packages those views into a stable JSON contract that a future Streamlit dashboard can consume without embedding business logic in the UI.

## Design Goals

- Expose approved PostgreSQL KPI views through clean, business-readable endpoints
- Keep route handlers thin by delegating database access to a service layer
- Support optional dashboard filters for year, month, region, and limit
- Return a consistent response envelope across KPI and recommendation endpoints
- Prevent arbitrary table access by whitelisting view names in the query service

## Endpoints

### Health

- `GET /health`
- `GET /health/database`

`/health` confirms the API process is running.

Example response:

```json
{
  "status": "ok",
  "service": "Business Intelligence Decision Hub API"
}
```

`/health/database` verifies PostgreSQL connectivity. If the database is unavailable, the API returns HTTP `503` with a clear error message.

Successful response:

```json
{
  "status": "ok",
  "database": "connected"
}
```

### KPI Views

- `GET /kpis/executive` -> `vw_executive_kpis`
- `GET /kpis/finance` -> `vw_finance_performance`
- `GET /kpis/operations` -> `vw_operations_performance`
- `GET /kpis/assets` -> `vw_asset_performance`
- `GET /kpis/customers` -> `vw_customer_performance`
- `GET /kpis/esg` -> `vw_esg_performance`

### Recommendations

- `GET /recommendations/actions` -> `vw_decision_recommendations`

Recommendation rows are ordered by `priority_score DESC` by default so the highest-priority actions appear first.

## Query Parameters

All KPI and recommendation endpoints support the same optional filters:

- `year`: integer year filter
- `month`: integer month filter from `1` to `12`
- `region`: exact region name filter such as `North-West`
- `limit`: maximum number of rows to return, default `100`, maximum `1000`

Example URLs:

- `GET /kpis/executive?year=2025&region=North-West`
- `GET /kpis/finance?year=2025&month=6`
- `GET /recommendations/actions?region=Islands&limit=10`

## Response Format

Each endpoint returns the same dashboard-ready envelope:

```json
{
  "view": "vw_executive_kpis",
  "filters": {
    "year": 2025,
    "month": null,
    "region": "North-West",
    "limit": 100
  },
  "row_count": 1,
  "data": [
    {
      "year": 2025,
      "month": 1,
      "region_name": "North-West",
      "total_revenue": 1234567.89
    }
  ]
}
```

If no rows match the filter, the API still returns a successful response with:

```json
{
  "row_count": 0,
  "data": []
}
```

## Implementation Notes

- SQLAlchemy manages the PostgreSQL connection and engine reuse
- The API reads database settings from environment variables
- The query service uses parameterized SQL for filters and limit values
- Only approved view names can be queried by the service layer
- Decimal and date-like database values are normalized into JSON-safe response values

## Streamlit Readiness

This API design keeps future dashboard pages simple:

- Streamlit can request already-modeled KPI datasets instead of rebuilding metrics in Python
- Shared filters can be passed directly from dashboard controls to the API
- Recommendation results are already prioritized for executive action panels
- A stable response wrapper makes it easier to reuse generic data-fetch and rendering helpers
