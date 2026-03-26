"""BentoML service for ChainCommand ML model serving."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import bentoml
import numpy as np
import pandas as pd


@dataclass
class _ProductSnapshot:
    """Lightweight product-like object for detect_batch().

    AnomalyDetector.detect_batch() expects objects with .product_id,
    .daily_demand_avg, and .current_stock attributes.
    """
    product_id: str
    daily_demand_avg: float
    current_stock: float


@bentoml.service(
    name="chaincommand-forecast",
    traffic={"timeout": 30},
    resources={"cpu": "1", "memory": "512Mi"},
)
class ChainCommandService:
    """Unified ML serving endpoint for supply chain models."""

    def __init__(self) -> None:
        from chaincommand.models.anomaly_detector import AnomalyDetector
        from chaincommand.models.forecaster import EnsembleForecaster
        from chaincommand.models.optimizer import HybridOptimizer

        self.forecaster = EnsembleForecaster()
        self.anomaly_detector = AnomalyDetector()
        self.optimizer = HybridOptimizer()

    @bentoml.api
    async def forecast(
        self, product_id: str, history: list[float], horizon: int = 30
    ) -> dict[str, Any]:
        """Demand forecast for a product."""
        try:
            # Build a DataFrame matching the expected train() signature:
            #   train(history: pd.DataFrame, product_id: str)
            # The DataFrame needs 'product_id', 'quantity', and 'day_of_week' columns.
            # Generate synthetic dates so XGB features (day_of_week) are available.
            dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=len(history), freq="D")
            df = pd.DataFrame({
                "product_id": [product_id] * len(history),
                "quantity": history,
                "day_of_week": dates.dayofweek,
            })
            self.forecaster.train(df, product_id)
            # predict() signature: predict(product_id: str, horizon: int)
            results = self.forecaster.predict(product_id, horizon)
            predictions = [r.predicted_demand for r in results]
            return {
                "product_id": product_id,
                "horizon": horizon,
                "predictions": predictions,
                "status": "ok",
            }
        except Exception as e:
            series = pd.Series(history)
            return {
                "product_id": product_id,
                "error": str(e),
                "status": "fallback",
                "predictions": [float(series.mean())] * horizon,
            }

    @bentoml.api
    async def detect_anomalies(self, data: list[list[float]]) -> dict[str, Any]:
        """Anomaly detection on supply chain metrics.

        Each row in `data` is [daily_demand_avg, current_stock, ...].
        Optionally, a third element can provide a product_id string.
        """
        try:
            # detect_batch() expects a list of product-like objects with
            # .product_id, .daily_demand_avg, and .current_stock attributes.
            snapshots = []
            for idx, row in enumerate(data):
                product_id = row[2] if len(row) > 2 and isinstance(row[2], str) else f"row-{idx}"
                snapshots.append(_ProductSnapshot(
                    product_id=product_id,
                    daily_demand_avg=row[0] if len(row) > 0 else 0.0,
                    current_stock=row[1] if len(row) > 1 else 0.0,
                ))
            anomalies = self.anomaly_detector.detect_batch(snapshots)
            return {
                "anomalies": [
                    {
                        "type": a.anomaly_type,
                        "product_id": a.product_id,
                        "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
                        "score": a.score,
                        "description": a.description,
                    }
                    for a in anomalies
                ],
                "count": len(anomalies),
                "status": "ok",
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}

    @bentoml.api
    async def optimize(
        self, products: list[dict], constraints: dict | None = None
    ) -> dict[str, Any]:
        """Inventory optimization."""
        from chaincommand.data.schemas import Product

        try:
            # HybridOptimizer.optimize() signature:
            #   optimize(product: Product, demand_forecast: List[ForecastResult])
            # Process each product individually.
            recommendations = []
            for prod_dict in products:
                product = Product(**prod_dict)
                result = self.optimizer.optimize(product, [])
                recommendations.append({
                    "product_id": result.product_id,
                    "reorder_point": result.recommended_reorder_point,
                    "safety_stock": result.recommended_safety_stock,
                    "order_qty": result.recommended_order_qty,
                    "cost_saving": result.expected_cost_saving,
                    "method": result.method,
                })
            return {"recommendations": recommendations, "status": "ok"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
