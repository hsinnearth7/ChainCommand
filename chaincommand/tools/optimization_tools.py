"""Optimization tools — reorder points, inventory optimization, supplier evaluation."""

from __future__ import annotations

import math
from typing import Any, Dict

from .base_tool import BaseTool


class CalculateReorderPoint(BaseTool):
    """Calculate the reorder point for a product."""

    name = "calculate_reorder_point"
    description = "Compute reorder point based on demand, lead time, and service level."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        product_id: str = kwargs.get("product_id", "")
        service_level: float = kwargs.get("service_level", 0.95)

        product = next(
            (p for p in (_runtime.products or []) if p.product_id == product_id),
            None,
        )
        if product is None:
            return {"error": f"Product {product_id} not found"}

        # z-score for service level (approximation)
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.97: 1.88, 0.99: 2.33}
        z = z_scores.get(service_level, 1.65)

        lead_time = product.lead_time_days
        safety_stock = z * product.daily_demand_std * math.sqrt(lead_time)
        reorder_point = product.daily_demand_avg * lead_time + safety_stock

        return {
            "product_id": product_id,
            "reorder_point": round(reorder_point, 1),
            "safety_stock": round(safety_stock, 1),
            "lead_time_days": lead_time,
            "service_level": service_level,
            "daily_demand_avg": product.daily_demand_avg,
        }


class OptimizeInventory(BaseTool):
    """Run inventory optimization using GA/DQN hybrid."""

    name = "optimize_inventory"
    description = "Optimize reorder point, safety stock, and order quantity for a product."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        product_id: str = kwargs.get("product_id", "")

        product = next(
            (p for p in (_runtime.products or []) if p.product_id == product_id),
            None,
        )
        if product is None:
            return {"error": f"Product {product_id} not found"}

        if _runtime.optimizer is None:
            return {"error": "Optimizer not initialized"}

        # Get forecast for optimization input
        forecast = []
        if _runtime.forecaster is not None:
            forecast = _runtime.forecaster.predict(product_id, 30)

        result = _runtime.optimizer.optimize(product, forecast)
        return {
            "product_id": product_id,
            "recommended_reorder_point": result.recommended_reorder_point,
            "recommended_safety_stock": result.recommended_safety_stock,
            "recommended_order_qty": result.recommended_order_qty,
            "expected_cost_saving": result.expected_cost_saving,
            "method": result.method,
        }


class EvaluateSupplier(BaseTool):
    """Score and rank suppliers for a product."""

    name = "evaluate_supplier"
    description = "Evaluate supplier performance using weighted scoring across reliability, cost, and quality."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        product_id: str = kwargs.get("product_id", "")
        suppliers = _runtime.suppliers or []

        candidates = [s for s in suppliers if product_id in s.products and s.is_active]
        if not candidates:
            return {"error": f"No active suppliers for {product_id}", "rankings": []}

        rankings = []
        for s in candidates:
            # Weighted composite score
            score = (
                s.reliability_score * 0.30
                + s.on_time_rate * 0.25
                + (1 - s.defect_rate) * 0.20
                + (1 / max(s.cost_multiplier, 0.5)) * 0.15
                + (1 / max(s.lead_time_mean, 1)) * 0.10
            )
            rankings.append({
                "supplier_id": s.supplier_id,
                "name": s.name,
                "composite_score": round(score, 4),
                "reliability_score": s.reliability_score,
                "on_time_rate": s.on_time_rate,
                "defect_rate": s.defect_rate,
                "cost_multiplier": s.cost_multiplier,
                "lead_time_mean": s.lead_time_mean,
            })

        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        return {
            "product_id": product_id,
            "rankings": rankings,
            "recommended": rankings[0]["supplier_id"] if rankings else None,
        }
