"""Risk Assessor Agent — Operational Layer.

Quantifies supply risk across depth, breadth, and criticality dimensions.
Triggers mitigation workflows when risk exceeds thresholds.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..data.schemas import AgentAction, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class RiskAssessorAgent(BaseAgent):
    name = "risk_assessor"
    role = (
        "Quantify supply risk (depth/breadth/criticality), "
        "trigger mitigation for high-risk scenarios"
    )
    layer = "operational"

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "anomaly_detected":
            log.info("risk_anomaly_received", anomaly=event.data.get("anomaly_type"))
        elif event.event_type == "market_disruption":
            log.warning("risk_market_disruption", data=event.data)
        elif event.event_type == "supplier_issue":
            log.warning("risk_supplier_issue", supplier=event.data.get("supplier_id"))

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        results = {"agent": self.name, "risk_assessments": [], "mitigations": []}

        products = context.get("products", [])

        # Step 1: Assess supply risk for key products
        for product in products[:5]:
            risk_action = AgentAction(
                agent_name=self.name,
                action_type="assess_supply_risk",
                description=f"Assess supply risk for {product.product_id}",
                input_data={"product_id": product.product_id},
            )
            risk_result = await self.act(risk_action)
            results["risk_assessments"].append(risk_result)

            # Check if highest risk is critical/high
            highest = risk_result.get("highest_risk", {})
            if highest and highest.get("level") in ("critical", "high"):
                # Emit risk alert
                emit_action = AgentAction(
                    agent_name=self.name,
                    action_type="emit_event",
                    description=f"High supply risk for {product.product_id}",
                    input_data={
                        "event_type": "supply_risk_alert",
                        "severity": "critical" if highest["level"] == "critical" else "high",
                        "source_agent": self.name,
                        "description": (
                            f"High supply risk for {product.name}: "
                            f"overall={highest['overall_risk']:.3f} ({highest['level']})"
                        ),
                        "data": {
                            "product_id": product.product_id,
                            "risk": highest,
                        },
                    },
                )
                await self.act(emit_action)
                results["mitigations"].append({
                    "product_id": product.product_id,
                    "risk_level": highest["level"],
                    "recommendation": "Consider dual-sourcing or safety stock increase",
                })

        # Step 2: Scan market intelligence
        intel_action = AgentAction(
            agent_name=self.name,
            action_type="scan_market_intelligence",
            description="Scan for market risk signals",
            input_data={},
        )
        intel_result = await self.act(intel_action)
        results["market_intel"] = intel_result

        # Step 3: Think
        analysis = await self.think({
            "assessments": len(results["risk_assessments"]),
            "high_risk_products": len(results["mitigations"]),
            "market_signals": intel_result.get("intel_count", 0),
        })
        results["analysis"] = analysis

        log.info(
            "risk_cycle_complete",
            cycle=self._cycle_count,
            high_risk=len(results["mitigations"]),
        )
        return results
