"""Demand Forecaster Agent — Strategic Layer.

Analyzes sales patterns, seasonality, and market trends to produce demand forecasts.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..data.schemas import AgentAction, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class DemandForecasterAgent(BaseAgent):
    name = "demand_forecaster"
    role = "Analyze sales patterns, seasonality, and market trends to produce demand forecasts"
    layer = "strategic"

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "kpi_threshold_violated":
            metric = event.data.get("metric")
            if metric == "mape":
                log.info("forecaster_mape_alert", mape=event.data.get("value"))
                # Re-run forecast for affected products
        elif event.event_type == "new_market_intel":
            log.info("forecaster_market_intel", topic=event.data.get("topic"))

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        results = {"agent": self.name, "actions": [], "forecasts": []}

        # Step 1: Query demand history for context
        history_action = AgentAction(
            agent_name=self.name,
            action_type="query_demand_history",
            description="Query recent demand data for analysis",
            input_data={"days": 90},
        )
        history = await self.act(history_action)
        results["actions"].append(history_action.model_dump())

        # Step 2: Think about the data
        think_context = {
            "demand_summary": f"Avg demand: {history.get('avg_demand', 0):.1f}",
            "record_count": history.get("record_count", 0),
            "cycle": self._cycle_count,
        }
        analysis = await self.think(think_context)
        results["analysis"] = analysis

        # Step 3: Run forecast for key products
        products = context.get("products", [])
        for product in products[:5]:  # Top 5 products per cycle
            forecast_action = AgentAction(
                agent_name=self.name,
                action_type="run_demand_forecast",
                description=f"Forecast demand for {product.product_id}",
                input_data={"product_id": product.product_id, "horizon": 30},
            )
            forecast_result = await self.act(forecast_action)
            results["forecasts"].append(forecast_result)

            # Emit forecast update event
            emit_action = AgentAction(
                agent_name=self.name,
                action_type="emit_event",
                description="Publish forecast update",
                input_data={
                    "event_type": "forecast_updated",
                    "severity": "low",
                    "source_agent": self.name,
                    "description": f"Forecast updated for {product.product_id}",
                    "data": {"product_id": product.product_id},
                },
            )
            await self.act(emit_action)

        # Step 4: Check accuracy
        accuracy_action = AgentAction(
            agent_name=self.name,
            action_type="get_forecast_accuracy",
            description="Check forecast accuracy metrics",
            input_data={"product_id": products[0].product_id if products else ""},
        )
        accuracy = await self.act(accuracy_action)
        results["accuracy"] = accuracy

        log.info("forecaster_cycle_complete", cycle=self._cycle_count, forecasts=len(results["forecasts"]))
        return results
