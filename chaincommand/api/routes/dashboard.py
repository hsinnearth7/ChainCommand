"""Dashboard routes — KPI, inventory, agents, events, forecasts, approvals."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from ...data.schemas import ApprovalStatus
from ...utils.logging_config import get_logger

log = get_logger(__name__)
router = APIRouter(tags=["dashboard"])


# ── KPI ──────────────────────────────────────────────────────

@router.get("/kpi/current")
async def get_current_kpi():
    """Get the latest KPI snapshot."""
    from ...orchestrator import _runtime

    if not _runtime.kpi_engine or not _runtime.kpi_engine.history:
        return {"error": "No KPI data available yet"}
    snapshot = _runtime.kpi_engine.history[-1]
    return snapshot.model_dump()


@router.get("/kpi/history")
async def get_kpi_history(periods: int = Query(default=30, ge=1, le=365)):
    """Get KPI history for trend analysis."""
    from ...orchestrator import _runtime

    if not _runtime.kpi_engine:
        return {"snapshots": [], "count": 0}
    snapshots = _runtime.kpi_engine.history[-periods:]
    return {
        "snapshots": [s.model_dump() for s in snapshots],
        "count": len(snapshots),
    }


# ── Inventory ────────────────────────────────────────────────

@router.get("/inventory/status")
async def get_inventory_status(product_id: Optional[str] = None):
    """Get inventory status for all or a specific product."""
    from ...orchestrator import _runtime

    products = _runtime.products or []
    if product_id:
        products = [p for p in products if p.product_id == product_id]

    items = []
    for p in products:
        dsi = p.current_stock / p.daily_demand_avg if p.daily_demand_avg > 0 else 999
        items.append({
            "product_id": p.product_id,
            "name": p.name,
            "category": p.category.value,
            "current_stock": p.current_stock,
            "reorder_point": p.reorder_point,
            "safety_stock": p.safety_stock,
            "daily_demand_avg": p.daily_demand_avg,
            "days_of_supply": round(dsi, 1),
            "unit_cost": p.unit_cost,
            "status": (
                "critical" if p.current_stock < p.safety_stock
                else "low" if p.current_stock < p.reorder_point
                else "healthy"
            ),
        })

    return {"products": items, "count": len(items)}


# ── Agents ───────────────────────────────────────────────────

@router.get("/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    from ...orchestrator import _runtime

    agents = _runtime.agents or {}
    return {
        "agents": {name: agent.get_status() for name, agent in agents.items()},
        "count": len(agents),
    }


# ── Events ───────────────────────────────────────────────────

@router.get("/events/recent")
async def get_recent_events(limit: int = Query(default=50, ge=1, le=200)):
    """Get recent supply chain events."""
    from ...orchestrator import _runtime

    if not _runtime.event_bus:
        return {"events": [], "count": 0}
    events = _runtime.event_bus.recent_events[-limit:]
    return {
        "events": [e.model_dump() for e in reversed(events)],
        "count": len(events),
    }


def _get_recent_events(limit: int = 20) -> list[dict]:
    """Helper for WebSocket: return recent events as dicts."""
    from ...orchestrator import _runtime

    if not _runtime.event_bus:
        return []
    events = _runtime.event_bus.recent_events[-limit:]
    return [e.model_dump() for e in events]


# ── Forecast ─────────────────────────────────────────────────

@router.get("/forecast/{product_id}")
async def get_forecast(product_id: str, horizon: int = Query(default=30, ge=1, le=90)):
    """Get demand forecast for a product."""
    from ...orchestrator import _runtime

    if not _runtime.forecaster:
        return {"error": "Forecaster not initialized"}

    results = _runtime.forecaster.predict(product_id, horizon)
    return {
        "product_id": product_id,
        "horizon": horizon,
        "forecasts": [r.model_dump() for r in results],
        "accuracy": _runtime.forecaster.get_accuracy(product_id),
    }


# ── Human Approval ───────────────────────────────────────────

@router.get("/approvals/pending")
async def get_pending_approvals():
    """List all pending approval requests."""
    from ...orchestrator import _runtime

    pending = {
        k: v.model_dump()
        for k, v in _runtime.pending_approvals.items()
        if v.status == ApprovalStatus.PENDING
    }
    return {"approvals": pending, "count": len(pending)}


@router.post("/approval/{request_id}/decide")
async def decide_approval(request_id: str, approved: bool, reason: str = ""):
    """Human decision on an approval request."""
    from ...orchestrator import _runtime

    approval = _runtime.pending_approvals.get(request_id)
    if not approval:
        return {"error": f"Approval request {request_id} not found"}

    approval.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
    approval.decided_at = datetime.utcnow()
    approval.decided_by = "human"
    approval.reason = reason

    log.info("approval_decided", request_id=request_id, approved=approved)
    return {"request_id": request_id, "status": approval.status.value, "reason": reason}


# ── WebSocket — Live Events ──────────────────────────────────

_ws_clients: list[WebSocket] = []


@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """Live event stream via WebSocket."""
    await websocket.accept()
    _ws_clients.append(websocket)
    log.info("ws_client_connected", total=len(_ws_clients))

    try:
        seen_ids: set[str] = set()
        while True:
            # Keep connection alive; push events from event bus
            await asyncio.sleep(1)
            from ...orchestrator import _runtime

            if _runtime.event_bus:
                events = _runtime.event_bus.recent_events[-20:]
                for evt in events:
                    if evt.event_id not in seen_ids:
                        seen_ids.add(evt.event_id)
                        await websocket.send_json(evt.model_dump())
                # Cap memory
                if len(seen_ids) > 5000:
                    seen_ids = set(list(seen_ids)[-2000:])
    except WebSocketDisconnect:
        _ws_clients.remove(websocket)
        log.info("ws_client_disconnected", total=len(_ws_clients))
    except Exception:
        if websocket in _ws_clients:
            _ws_clients.remove(websocket)
