"""Forecasting tools — demand prediction and accuracy tracking."""

from __future__ import annotations

from typing import Any, Dict

from .base_tool import BaseTool


class RunDemandForecast(BaseTool):
    """Trigger demand forecasting for a product."""

    name = "run_demand_forecast"
    description = "Run the ensemble forecaster to predict future demand for a product."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        product_id: str = kwargs.get("product_id", "")
        horizon: int = kwargs.get("horizon", 30)

        if _runtime.forecaster is None or _runtime.demand_df is None:
            return {"error": "Forecaster not initialized"}

        product_df = _runtime.demand_df[
            _runtime.demand_df["product_id"] == product_id
        ]
        if product_df.empty:
            return {"error": f"No data for product {product_id}"}

        results = _runtime.forecaster.predict(product_id, horizon)
        forecast_data = [
            {
                "date": r.forecast_date.isoformat(),
                "predicted_demand": r.predicted_demand,
                "confidence_lower": r.confidence_lower,
                "confidence_upper": r.confidence_upper,
                "model_used": r.model_used,
            }
            for r in results
        ]
        return {
            "product_id": product_id,
            "horizon": horizon,
            "forecasts": forecast_data,
        }


class GetForecastAccuracy(BaseTool):
    """Get forecast accuracy metrics."""

    name = "get_forecast_accuracy"
    description = "Retrieve MAPE and other accuracy metrics for recent forecasts."

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        from ..orchestrator import _runtime

        product_id: str = kwargs.get("product_id", "")

        if _runtime.forecaster is None:
            return {"error": "Forecaster not initialized"}

        accuracy = _runtime.forecaster.get_accuracy(product_id)
        return {
            "product_id": product_id,
            **accuracy,
        }
