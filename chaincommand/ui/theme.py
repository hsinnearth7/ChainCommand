"""Visual constants and theme definitions for ChainCommand terminal UI."""

from __future__ import annotations

from rich.theme import Theme

# ── Agent Layer Colors & Badges ─────────────────────────────

LAYER_COLORS = {
    "strategic":     "bold cyan",
    "tactical":      "bold yellow",
    "operational":   "bold green",
    "orchestration": "bold magenta",
}

LAYER_BADGES = {
    "strategic":     "[cyan]STRAT[/cyan]",
    "tactical":      "[yellow]TACT[/yellow]",
    "operational":   "[green]OPS[/green]",
    "orchestration": "[magenta]ORCH[/magenta]",
}

# ── Agent Icons & Layer Mapping ─────────────────────────────

AGENT_ICONS: dict[str, str] = {
    "demand_forecaster":     ">>>",
    "strategic_planner":     "***",
    "inventory_optimizer":   "###",
    "supplier_manager":      "$$$",
    "logistics_coordinator": "~~~",
    "anomaly_detector":      "!!!",
    "risk_assessor":         "???",
    "market_intelligence":   "@@@",
    "coordinator":           "+++",
    "reporter":              "---",
}

AGENT_LAYER: dict[str, str] = {
    "demand_forecaster":     "strategic",
    "strategic_planner":     "strategic",
    "inventory_optimizer":   "tactical",
    "supplier_manager":      "tactical",
    "logistics_coordinator": "tactical",
    "anomaly_detector":      "operational",
    "risk_assessor":         "operational",
    "market_intelligence":   "operational",
    "coordinator":           "orchestration",
    "reporter":              "orchestration",
}

# ── Event Severity Styles ───────────────────────────────────

SEVERITY_STYLES: dict[str, str] = {
    "low":      "dim green",
    "medium":   "yellow",
    "high":     "bold red",
    "critical": "bold white on red",
}

# ── KPI Threshold Colors ────────────────────────────────────

KPI_GOOD = "green"
KPI_WARN = "yellow"
KPI_BAD  = "red"

# ── Rich Theme Object ───────────────────────────────────────

CHAINCOMMAND_THEME = Theme({
    "info":        "cyan",
    "warning":     "yellow",
    "error":       "bold red",
    "success":     "bold green",
    "header":      "bold white",
    "layer.strategic":     "cyan",
    "layer.tactical":      "yellow",
    "layer.operational":   "green",
    "layer.orchestration": "magenta",
})

# ── Initialization Phases (6) ───────────────────────────────

INIT_PHASES: list[dict[str, str]] = [
    {"name": "Synthetic Data",    "desc": "Generating products, suppliers & demand history"},
    {"name": "Forecaster",        "desc": "Training LSTM + XGBoost ensemble model"},
    {"name": "Anomaly Detector",  "desc": "Training Isolation Forest model"},
    {"name": "Engines",           "desc": "Initializing KPI engine, event bus & monitor"},
    {"name": "Agents",            "desc": "Creating 10 AI agents with LLM & tools"},
    {"name": "KPI Baseline",      "desc": "Computing initial KPI snapshot"},
]

# ── Decision Cycle Steps (8) ────────────────────────────────

CYCLE_STEPS: list[dict[str, str]] = [
    {"name": "Market Scan",        "desc": "Market Intelligence + Anomaly Detection", "layer": "operational"},
    {"name": "Forecasting",        "desc": "Demand Forecasting",                      "layer": "strategic"},
    {"name": "Inventory & Risk",   "desc": "Inventory Optimization + Risk Assessment", "layer": "tactical"},
    {"name": "Procurement",        "desc": "Supplier Selection & Purchase Orders",     "layer": "tactical"},
    {"name": "Logistics",          "desc": "Logistics Coordination",                   "layer": "tactical"},
    {"name": "Strategy",           "desc": "Strategic Planning",                        "layer": "strategic"},
    {"name": "Coordination",       "desc": "Coordinator Arbitration & Conflict Res.",   "layer": "orchestration"},
    {"name": "Reporting",          "desc": "Summary Report Generation",                 "layer": "orchestration"},
]
