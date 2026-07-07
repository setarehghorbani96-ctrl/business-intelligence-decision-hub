"""FastAPI application entrypoint for the KPI backend."""

from fastapi import FastAPI

from api.routers.health import router as health_router
from api.routers.kpis import router as kpis_router
from api.routers.recommendations import router as recommendations_router


app = FastAPI(
    title="Business Intelligence Decision Hub API",
    description="Dashboard-ready KPI endpoints for NovaEnergy Services.",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(kpis_router)
app.include_router(recommendations_router)
