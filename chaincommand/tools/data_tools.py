"""Data query tools — access demand history, inventory, suppliers, KPIs."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict

from .base_tool import BaseTool


class QueryDemandHistory(BaseTool):
    """Query historical demand data for a product."""

    name = "query_demand_history"
    description = "Retrieve historical demand records for a given product and date range."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime  # deferred to avoid circular imports

        product_id: str = kwargs.get("product_id", "")
        days: int = kwargs.get("days", 90)

        if _runtime.demand_df is None:
            return {"error": "No demand data loaded"}

        df = _runtime.demand_df
        if product_id:
            df = df[df["product_id"] == product_id]

        cutoff = datetime.utcnow() - timedelta(days=days)
        df = df[df["date"] >= cutoff]

        records = df.tail(200).to_dict(orient="records")
        return {
            "product_id": product_id,
            "record_count": len(records),
            "records": records,
            "avg_demand": float(df["quantity"].mean()) if len(df) else 0.0,
            "std_demand": float(df["quantity"].std()) if len(df) else 0.0,
        }


class QueryInventoryStatus(BaseTool):
    """Query current inventory status for products."""

    name = "query_inventory_status"
    description = "Get current inventory snapshot for one or all products."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        product_id: str = kwargs.get("product_id", "")
        products = _runtime.products or []

        if product_id:
            products = [p for p in products if p.product_id == product_id]

        snapshots = []
        for p in products:
            snapshots.append({
                "product_id": p.product_id,
                "name": p.name,
                "current_stock": p.current_stock,
                "reorder_point": p.reorder_point,
                "safety_stock": p.safety_stock,
                "daily_demand_avg": p.daily_demand_avg,
                "days_of_supply": (
                    p.current_stock / p.daily_demand_avg
                    if p.daily_demand_avg > 0 else 999
                ),
                "status": (
                    "critical" if p.current_stock < p.safety_stock
                    else "low" if p.current_stock < p.reorder_point
                    else "healthy"
                ),
            })
        return {"products": snapshots, "count": len(snapshots)}


class QuerySupplierInfo(BaseTool):
    """Query supplier information and performance metrics."""

    name = "query_supplier_info"
    description = "Get supplier details including reliability, lead time, and defect rate."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        supplier_id: str = kwargs.get("supplier_id", "")
        product_id: str = kwargs.get("product_id", "")
        suppliers = _runtime.suppliers or []

        if supplier_id:
            suppliers = [s for s in suppliers if s.supplier_id == supplier_id]
        elif product_id:
            suppliers = [s for s in suppliers if product_id in s.products]

        results = []
        for s in suppliers:
            results.append({
                "supplier_id": s.supplier_id,
                "name": s.name,
                "reliability_score": s.reliability_score,
                "lead_time_mean": s.lead_time_mean,
                "lead_time_std": s.lead_time_std,
                "cost_multiplier": s.cost_multiplier,
                "defect_rate": s.defect_rate,
                "on_time_rate": s.on_time_rate,
                "capacity": s.capacity,
                "is_active": s.is_active,
                "products": s.products,
            })
        return {"suppliers": results, "count": len(results)}


class QueryKPIHistory(BaseTool):
    """Query historical KPI snapshots."""

    name = "query_kpi_history"
    description = "Retrieve recent KPI snapshots for trend analysis."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        periods: int = kwargs.get("periods", 30)
        history = _runtime.kpi_engine.history if _runtime.kpi_engine else []
        snapshots = list(history[-periods:])

        return {
            "snapshots": [s.model_dump() for s in snapshots],
            "count": len(snapshots),
        }
