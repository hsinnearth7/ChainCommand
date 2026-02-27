"""Shared test fixtures for ChainCommand."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pytest

from chaincommand.data.schemas import (
    HumanApprovalRequest,
    KPISnapshot,
    Product,
    ProductCategory,
    PurchaseOrder,
    Supplier,
)


@dataclass
class MockRuntime:
    """Lightweight mock of _RuntimeState for testing."""

    products: Optional[List[Product]] = None
    suppliers: Optional[List[Supplier]] = None
    demand_df: Any = None
    forecaster: Any = None
    anomaly_detector: Any = None
    optimizer: Any = None
    kpi_engine: Any = None
    event_bus: Any = None
    monitor: Any = None
    agents: Dict[str, Any] = field(default_factory=dict)
    purchase_orders: List[PurchaseOrder] = field(default_factory=list)
    pending_approvals: Dict[str, HumanApprovalRequest] = field(default_factory=dict)
    kpi_history: List[KPISnapshot] = field(default_factory=list)
    backend: Any = None


@pytest.fixture
def mock_runtime():
    """Provide a mock runtime with sample products and suppliers."""
    rt = MockRuntime()
    rt.products = [
        Product(
            product_id="PRD-test01",
            name="Test Widget",
            category=ProductCategory.ELECTRONICS,
            unit_cost=10.0,
            selling_price=25.0,
            current_stock=500.0,
            reorder_point=100.0,
            safety_stock=50.0,
            daily_demand_avg=20.0,
            daily_demand_std=5.0,
        ),
    ]
    rt.suppliers = [
        Supplier(
            supplier_id="SUP-test01",
            name="Test Supplier",
            lead_time_mean=5.0,
        ),
    ]
    return rt


@pytest.fixture
def app_no_lifespan():
    """Create a FastAPI test app without the real lifespan (no orchestrator init)."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from chaincommand.auth import require_api_key, require_ws_api_key
    from chaincommand.config import settings

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    app = FastAPI(lifespan=noop_lifespan)

    # Mirror CORS config
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["X-API-Key", "Content-Type"],
    )

    # Import and include routers
    from chaincommand.api.routes.dashboard import router as dashboard_router
    from chaincommand.api.routes.control import router as control_router

    app.include_router(dashboard_router, prefix="/api")
    app.include_router(control_router, prefix="/api")

    @app.get("/")
    async def root():
        return {
            "name": "ChainCommand",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
        }

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok", "name": "ChainCommand", "version": "1.0.0"}

    return app


@pytest.fixture
def client(app_no_lifespan):
    """HTTPX async test client for the FastAPI app."""
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app_no_lifespan)
    return AsyncClient(transport=transport, base_url="http://test")
