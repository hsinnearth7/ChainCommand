"""Logistics Coordinator Agent — Tactical Layer.

Tracks order status, optimizes transportation, manages delivery timelines.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..data.schemas import AgentAction, OrderStatus, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class LogisticsCoordinatorAgent(BaseAgent):
    name = "logistics_coordinator"
    role = "Track order status, optimize transportation, manage delivery timelines"
    layer = "tactical"

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "po_created":
            log.info("logistics_new_po", po_id=event.data.get("po_id"))
        elif event.event_type == "delivery_delayed":
            log.warning("logistics_delay", po_id=event.data.get("po_id"), days=event.data.get("delay_days"))
        elif event.event_type == "shipment_update":
            log.info("logistics_shipment", data=event.data)

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        results = {"agent": self.name, "actions": [], "shipments": [], "delays": []}

        from ..orchestrator import _runtime
        purchase_orders = _runtime.purchase_orders or []

        # Step 1: Track active orders
        active_pos = [
            po for po in purchase_orders
            if po.status in (OrderStatus.PENDING, OrderStatus.APPROVED, OrderStatus.SHIPPED)
        ]

        now = datetime.utcnow()
        for po in active_pos:
            shipment_info = {
                "po_id": po.po_id,
                "product_id": po.product_id,
                "supplier_id": po.supplier_id,
                "status": po.status.value,
                "quantity": po.quantity,
            }

            # Check for delays
            if po.expected_delivery and po.expected_delivery < now:
                delay_days = (now - po.expected_delivery).days
                shipment_info["delay_days"] = delay_days
                results["delays"].append(shipment_info)

                # Emit delay warning
                emit_action = AgentAction(
                    agent_name=self.name,
                    action_type="emit_event",
                    description=f"Delivery delay alert for PO {po.po_id}",
                    input_data={
                        "event_type": "delivery_delayed",
                        "severity": "high" if delay_days > 5 else "medium",
                        "source_agent": self.name,
                        "description": f"PO {po.po_id} delayed {delay_days} days",
                        "data": shipment_info,
                    },
                )
                await self.act(emit_action)
            else:
                results["shipments"].append(shipment_info)

            # Simulate order progression
            if po.status == OrderStatus.APPROVED:
                po.status = OrderStatus.SHIPPED
            elif po.status == OrderStatus.SHIPPED:
                if po.expected_delivery and po.expected_delivery <= now:
                    po.status = OrderStatus.DELIVERED
                    # Update product stock
                    product = next(
                        (p for p in (_runtime.products or []) if p.product_id == po.product_id),
                        None,
                    )
                    if product:
                        product.current_stock += po.quantity

        # Step 2: Inventory status check
        inv_action = AgentAction(
            agent_name=self.name,
            action_type="query_inventory_status",
            description="Check inventory for logistics planning",
            input_data={},
        )
        await self.act(inv_action)

        # Step 3: Think
        analysis = await self.think({
            "active_orders": len(active_pos),
            "delayed": len(results["delays"]),
            "in_transit": len(results["shipments"]),
        })
        results["analysis"] = analysis

        log.info(
            "logistics_cycle_complete",
            cycle=self._cycle_count,
            active=len(active_pos),
            delays=len(results["delays"]),
        )
        return results
