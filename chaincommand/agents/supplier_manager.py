"""Supplier Manager Agent — Tactical Layer.

Evaluates supplier performance, selects optimal suppliers, manages procurement.
HITL gate: >$50k requires human approval, <$10k auto-approved.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..config import settings
from ..data.schemas import AgentAction, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class SupplierManagerAgent(BaseAgent):
    name = "supplier_manager"
    role = (
        "Evaluate supplier performance, select optimal suppliers, manage procurement. "
        "Enforce HITL approval gates for high-cost orders."
    )
    layer = "tactical"

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "reorder_triggered":
            product_id = event.data.get("product_id", "")
            log.info("supplier_reorder_received", product=product_id)
        elif event.event_type == "supplier_issue":
            log.warning("supplier_issue_event", data=event.data)
        elif event.event_type == "quality_alert":
            log.warning("supplier_quality_alert", data=event.data)

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        results = {"agent": self.name, "actions": [], "orders_created": [], "evaluations": []}

        products = context.get("products", [])

        # Step 1: Evaluate suppliers for products needing reorder
        reorder_products = [
            p for p in products if p.current_stock < p.reorder_point
        ]

        for product in reorder_products[:5]:
            # Evaluate suppliers
            eval_action = AgentAction(
                agent_name=self.name,
                action_type="evaluate_supplier",
                description=f"Evaluate suppliers for {product.product_id}",
                input_data={"product_id": product.product_id},
            )
            eval_result = await self.act(eval_action)
            results["evaluations"].append(eval_result)

            recommended = eval_result.get("recommended")
            if not recommended:
                continue

            # Calculate order quantity
            order_qty = max(
                product.min_order_qty,
                product.reorder_point - product.current_stock + product.safety_stock,
            )

            total_cost = order_qty * product.unit_cost

            # HITL gate check
            if total_cost >= settings.cost_escalation_threshold:
                # Request human approval
                approval_action = AgentAction(
                    agent_name=self.name,
                    action_type="request_human_approval",
                    description=f"High-cost PO requires approval: ${total_cost:,.0f}",
                    input_data={
                        "request_type": "purchase_order",
                        "description": (
                            f"PO for {product.name}: {order_qty:.0f} units "
                            f"from {recommended} at ${total_cost:,.0f}"
                        ),
                        "estimated_cost": total_cost,
                        "risk_level": "high",
                        "data": {
                            "product_id": product.product_id,
                            "supplier_id": recommended,
                            "quantity": order_qty,
                        },
                    },
                )
                await self.act(approval_action)
                log.info("supplier_approval_requested", cost=total_cost)
            else:
                # Create PO (auto-approve if below threshold)
                po_action = AgentAction(
                    agent_name=self.name,
                    action_type="create_purchase_order",
                    description=f"Create PO for {product.product_id}",
                    input_data={
                        "supplier_id": recommended,
                        "product_id": product.product_id,
                        "quantity": order_qty,
                        "unit_cost": product.unit_cost,
                    },
                )
                po_result = await self.act(po_action)
                results["orders_created"].append(po_result)

                # Emit PO created event
                emit_action = AgentAction(
                    agent_name=self.name,
                    action_type="emit_event",
                    description="Notify PO creation",
                    input_data={
                        "event_type": "po_created",
                        "severity": "low",
                        "source_agent": self.name,
                        "description": f"PO created: {po_result.get('po_id', 'unknown')}",
                        "data": po_result,
                    },
                )
                await self.act(emit_action)

        # Step 2: Get supplier info for reporting
        supplier_action = AgentAction(
            agent_name=self.name,
            action_type="query_supplier_info",
            description="Query all supplier status",
            input_data={},
        )
        supplier_data = await self.act(supplier_action)

        # Step 3: Think
        analysis = await self.think({
            "reorder_products": len(reorder_products),
            "orders_created": len(results["orders_created"]),
            "suppliers": supplier_data.get("count", 0),
        })
        results["analysis"] = analysis

        log.info(
            "supplier_cycle_complete",
            cycle=self._cycle_count,
            orders=len(results["orders_created"]),
        )
        return results
