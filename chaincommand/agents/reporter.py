"""Reporter Agent — Orchestration Layer.

Aggregates all agent outputs into structured reports and dashboard data.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..data.schemas import AgentAction, SupplyChainEvent
from ..utils.logging_config import get_logger
from .base_agent import BaseAgent

log = get_logger(__name__)


class ReporterAgent(BaseAgent):
    name = "reporter"
    role = "Aggregate agent outputs into structured reports and dashboard data"
    layer = "orchestration"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._reports: list[Dict[str, Any]] = []

    async def handle_event(self, event: SupplyChainEvent) -> None:
        if event.event_type == "cycle_complete":
            log.info("reporter_cycle_triggered", cycle=event.data.get("cycle"))
        elif event.event_type == "kpi_snapshot_created":
            log.debug("reporter_kpi_received")

    async def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._last_run = datetime.utcnow()

        agent_results = context.get("agent_results", {})
        coordinator_summary = context.get("coordinator_summary", "")

        # Step 1: Gather KPI data
        kpi_action = AgentAction(
            agent_name=self.name,
            action_type="query_kpi_history",
            description="Get KPI data for report",
            input_data={"periods": 10},
        )
        kpi_data = await self.act(kpi_action)

        # Step 2: Gather inventory data
        inv_action = AgentAction(
            agent_name=self.name,
            action_type="query_inventory_status",
            description="Get inventory status for report",
            input_data={},
        )
        inv_data = await self.act(inv_action)

        # Step 3: Build structured report
        report = {
            "report_id": f"RPT-{self._cycle_count:04d}",
            "timestamp": datetime.utcnow().isoformat(),
            "cycle": self._cycle_count,
            "executive_summary": coordinator_summary,
            "kpi": {
                "snapshot_count": kpi_data.get("count", 0),
                "latest": kpi_data.get("snapshots", [{}])[-1] if kpi_data.get("snapshots") else {},
            },
            "inventory": {
                "total_products": inv_data.get("count", 0),
                "critical": len([
                    p for p in inv_data.get("products", [])
                    if p.get("status") == "critical"
                ]),
                "low": len([
                    p for p in inv_data.get("products", [])
                    if p.get("status") == "low"
                ]),
                "healthy": len([
                    p for p in inv_data.get("products", [])
                    if p.get("status") == "healthy"
                ]),
            },
            "agent_summaries": {},
        }

        # Step 4: Summarize each agent's results
        for agent_name, result in agent_results.items():
            if isinstance(result, dict):
                report["agent_summaries"][agent_name] = {
                    "analysis": result.get("analysis", ""),
                    "actions_count": len(result.get("actions", [])),
                }

        # Step 5: LLM-generated narrative summary
        narrative = await self.think({
            "cycle": self._cycle_count,
            "kpi_count": report["kpi"]["snapshot_count"],
            "critical_products": report["inventory"]["critical"],
            "low_products": report["inventory"]["low"],
            "agents_reporting": len(agent_results),
        })
        report["narrative"] = narrative

        self._reports.append(report)

        log.info(
            "reporter_cycle_complete",
            cycle=self._cycle_count,
            report_id=report["report_id"],
        )

        return {"agent": self.name, "report": report}

    @property
    def latest_report(self) -> Dict[str, Any] | None:
        return self._reports[-1] if self._reports else None

    @property
    def all_reports(self) -> list[Dict[str, Any]]:
        return self._reports
