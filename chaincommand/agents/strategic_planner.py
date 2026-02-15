"""Strategic Planner Agent — Strategic Layer.

Develops inventory policies, production plans, and distribution strategies.
Uses beer game consensus mechanism to reduce bullwhip effect.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..data.schemas import AgentAction, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class StrategicPlannerAgent(BaseAgent):
    name = "strategic_planner"
    role = (
        "Develop inventory policies, production plans, and distribution strategies. "
        "Apply consensus mechanism to reduce bullwhip effect."
    )
    layer = "strategic"

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "forecast_updated":
            log.info("planner_forecast_received", product=event.data.get("product_id"))
        elif event.event_type == "kpi_trend_alert":
            log.info("planner_kpi_trend", metric=event.data.get("metric"))

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        results = {"agent": self.name, "actions": [], "recommendations": []}

        # Step 1: Review KPI history
        kpi_action = AgentAction(
            agent_name=self.name,
            action_type="query_kpi_history",
            description="Review KPI trends for strategic planning",
            input_data={"periods": 10},
        )
        kpi_data = await self.act(kpi_action)
        results["actions"].append(kpi_action.model_dump())

        # Step 2: Assess inventory status
        inv_action = AgentAction(
            agent_name=self.name,
            action_type="query_inventory_status",
            description="Review overall inventory health",
            input_data={},
        )
        inv_data = await self.act(inv_action)

        # Step 3: Think strategically
        think_context = {
            "kpi_snapshots": kpi_data.get("count", 0),
            "inventory_products": inv_data.get("count", 0),
            "cycle": self._cycle_count,
        }
        strategy = await self.think(think_context)
        results["strategy"] = strategy

        # Step 4: Consensus mechanism — smooth demand signals
        # Beer game insight: share information to prevent bullwhip effect
        products = context.get("products", [])
        for product in products[:3]:
            optimize_action = AgentAction(
                agent_name=self.name,
                action_type="optimize_inventory",
                description=f"Strategic optimization for {product.product_id}",
                input_data={"product_id": product.product_id},
            )
            opt_result = await self.act(optimize_action)
            results["recommendations"].append(opt_result)

        # Step 5: Emit strategy update
        emit_action = AgentAction(
            agent_name=self.name,
            action_type="emit_event",
            description="Publish strategy update",
            input_data={
                "event_type": "strategy_updated",
                "severity": "low",
                "source_agent": self.name,
                "description": f"Strategic plan updated (cycle {self._cycle_count})",
                "data": {"recommendations_count": len(results["recommendations"])},
            },
        )
        await self.act(emit_action)

        log.info("planner_cycle_complete", cycle=self._cycle_count)
        return results
