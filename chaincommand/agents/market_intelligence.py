"""Market Intelligence Agent — Operational Layer.

Monitors market dynamics, identifies trends, detects emerging opportunities.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..data.schemas import AgentAction, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class MarketIntelligenceAgent(BaseAgent):
    name = "market_intelligence"
    role = "Monitor market dynamics, identify trends, detect emerging product opportunities"
    layer = "operational"

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "tick":
            pass  # Periodic scan handled in run_cycle

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        results = {"agent": self.name, "intel_items": [], "alerts": []}

        # Step 1: Scan market intelligence
        scan_action = AgentAction(
            agent_name=self.name,
            action_type="scan_market_intelligence",
            description="Periodic market intelligence scan",
            input_data={},
        )
        scan_result = await self.act(scan_action)

        items = scan_result.get("items", [])
        results["intel_items"] = items

        # Step 2: Evaluate and emit significant findings
        for item in items:
            impact = item.get("impact_score", 0)
            if abs(impact) > 0.3:
                severity = "high" if abs(impact) > 0.5 else "medium"
                emit_action = AgentAction(
                    agent_name=self.name,
                    action_type="emit_event",
                    description=f"Market intel: {item.get('topic', 'unknown')}",
                    input_data={
                        "event_type": "new_market_intel",
                        "severity": severity,
                        "source_agent": self.name,
                        "description": item.get("summary", ""),
                        "data": item,
                    },
                )
                await self.act(emit_action)
                results["alerts"].append(item)

        # Step 3: Think about market trends
        analysis = await self.think({
            "intel_items": len(items),
            "significant_alerts": len(results["alerts"]),
            "cycle": self._cycle_count,
        })
        results["analysis"] = analysis

        log.info(
            "market_intel_cycle_complete",
            cycle=self._cycle_count,
            items=len(items),
            alerts=len(results["alerts"]),
        )
        return results
