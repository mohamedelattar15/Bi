"""Grocery Sales Dashboard API - FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import (
    dashboard,
    sales,
    products,
    customers,
    employees,
    basket,
    filters,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for Grocery Sales Dashboard - Power BI migration",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(sales.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(employees.router)
app.include_router(basket.router)
app.include_router(filters.router)


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}
