"""BentoML service for ChainCommand ML model serving."""
from __future__ import annotations

import bentoml
import numpy as np
import pandas as pd
from typing import Any


@bentoml.service(
    name="chaincommand-forecast",
    traffic={"timeout": 30},
    resources={"cpu": "1", "memory": "512Mi"},
)
class ChainCommandService:
    """Unified ML serving endpoint for supply chain models."""

    def __init__(self) -> None:
        # Lazy import to avoid circular deps at module level
        from chaincommand.models.forecaster import EnsembleForecaster
        from chaincommand.models.anomaly_detector import AnomalyDetector
        from chaincommand.models.optimizer import HybridOptimizer

        self.forecaster = EnsembleForecaster()
        self.anomaly_detector = AnomalyDetector()
        self.optimizer = HybridOptimizer()

    @bentoml.api
    async def forecast(
        self, product_id: str, history: list[float], horizon: int = 30
    ) -> dict[str, Any]:
        """Demand forecast for a product."""
        series = pd.Series(history)
        try:
            self.forecaster.fit(series)
            predictions = self.forecaster.predict(horizon)
            return {
                "product_id": product_id,
                "horizon": horizon,
                "predictions": predictions.tolist(),
                "status": "ok",
            }
        except Exception as e:
            return {
                "product_id": product_id,
                "error": str(e),
                "status": "fallback",
                "predictions": [float(series.mean())] * horizon,
            }

    @bentoml.api
    async def detect_anomalies(self, data: list[list[float]]) -> dict[str, Any]:
        """Anomaly detection on supply chain metrics."""
        arr = np.array(data)
        try:
            labels = self.anomaly_detector.predict(arr)
            return {
                "anomalies": labels.tolist(),
                "count": int((labels == -1).sum()),
                "status": "ok",
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}

    @bentoml.api
    async def optimize(
        self, products: list[dict], constraints: dict | None = None
    ) -> dict[str, Any]:
        """Inventory optimization."""
        try:
            result = self.optimizer.optimize(products, constraints or {})
            return {"recommendations": result, "status": "ok"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
