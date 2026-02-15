"""Anomaly Detector Agent — Operational Layer.

Real-time detection of demand anomalies, cost anomalies, and quality issues.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..data.schemas import AgentAction, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class AnomalyDetectorAgent(BaseAgent):
    name = "anomaly_detector"
    role = "Real-time detection of demand anomalies, cost anomalies, and quality issues"
    layer = "operational"

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "new_data_point":
            log.debug("anomaly_new_data", product=event.data.get("product_id"))
        elif event.event_type == "tick":
            pass  # Handled in run_cycle

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        results = {"agent": self.name, "anomalies_found": [], "products_scanned": 0}

        products = context.get("products", [])
        results["products_scanned"] = len(products)

        # Step 1: Run anomaly detection on each product
        for product in products[:10]:  # Scan top 10 per cycle
            detect_action = AgentAction(
                agent_name=self.name,
                action_type="detect_anomalies",
                description=f"Detect anomalies for {product.product_id}",
                input_data={"product_id": product.product_id},
            )
            detect_result = await self.act(detect_action)

            anomalies = detect_result.get("anomalies", [])
            if anomalies:
                results["anomalies_found"].extend(anomalies)

                # Emit anomaly events
                for anomaly in anomalies:
                    emit_action = AgentAction(
                        agent_name=self.name,
                        action_type="emit_event",
                        description=f"Alert: {anomaly.get('anomaly_type', 'unknown')}",
                        input_data={
                            "event_type": "anomaly_detected",
                            "severity": anomaly.get("severity", "medium"),
                            "source_agent": self.name,
                            "description": anomaly.get("description", "Anomaly detected"),
                            "data": anomaly,
                        },
                    )
                    await self.act(emit_action)

        # Step 2: Query demand history for pattern analysis
        history_action = AgentAction(
            agent_name=self.name,
            action_type="query_demand_history",
            description="Get recent demand data for pattern analysis",
            input_data={"days": 14},
        )
        await self.act(history_action)

        # Step 3: Think and assess
        analysis = await self.think({
            "products_scanned": results["products_scanned"],
            "anomalies_found": len(results["anomalies_found"]),
            "cycle": self._cycle_count,
        })
        results["analysis"] = analysis

        log.info(
            "anomaly_cycle_complete",
            cycle=self._cycle_count,
            anomalies=len(results["anomalies_found"]),
        )
        return results
