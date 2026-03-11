"""Prometheus metrics for ChainCommand."""
from __future__ import annotations

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        Info,
        generate_latest,
    )

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

# --- Metrics Definitions ---

if HAS_PROMETHEUS:
    REQUEST_COUNT = Counter(
        "chaincommand_http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "chaincommand_http_request_duration_seconds",
        "HTTP request latency",
        ["method", "endpoint"],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )
    ACTIVE_AGENTS = Gauge(
        "chaincommand_active_agents",
        "Number of active agents",
    )
    SIMULATION_CYCLES = Counter(
        "chaincommand_simulation_cycles_total",
        "Total simulation cycles completed",
    )
    KPI_GAUGE = Gauge(
        "chaincommand_kpi_value",
        "Current KPI metric value",
        ["metric_name"],
    )
    TOKEN_USAGE = Counter(
        "chaincommand_llm_tokens_total",
        "Total LLM tokens consumed",
        ["agent", "model"],
    )
    TOKEN_BUDGET_REMAINING = Gauge(
        "chaincommand_token_budget_remaining",
        "Remaining token budget for current cycle",
    )
    AGENT_DECISION_COUNT = Counter(
        "chaincommand_agent_decisions_total",
        "Total agent decisions made",
        ["agent_name"],
    )
    AGENT_DECISION_LATENCY = Histogram(
        "chaincommand_agent_decision_duration_seconds",
        "Agent decision latency",
        ["agent_name"],
    )
    FORECAST_MAPE = Gauge(
        "chaincommand_forecast_mape",
        "Current forecast MAPE",
        ["product_id"],
    )
    CIRCUIT_BREAKER_STATE = Gauge(
        "chaincommand_circuit_breaker_state",
        "Circuit breaker state (0=closed, 1=open, 2=half-open)",
        ["component"],
    )
    ERROR_COUNT = Counter(
        "chaincommand_errors_total",
        "Total errors",
        ["error_type", "component"],
    )
    APP_INFO = Info("chaincommand", "Application info")


def get_metrics_response() -> tuple[bytes, str]:
    """Generate Prometheus metrics response."""
    if not HAS_PROMETHEUS:
        return b"# prometheus_client not installed\n", "text/plain"
    return generate_latest(), CONTENT_TYPE_LATEST


def track_request(
    method: str, endpoint: str, status: int, duration: float
) -> None:
    """Record an HTTP request metric."""
    if not HAS_PROMETHEUS:
        return
    REQUEST_COUNT.labels(
        method=method, endpoint=endpoint, status=str(status)
    ).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)


def track_kpi(metric_name: str, value: float) -> None:
    """Update a KPI gauge."""
    if not HAS_PROMETHEUS:
        return
    KPI_GAUGE.labels(metric_name=metric_name).set(value)


def track_agent_decision(agent_name: str, duration: float) -> None:
    """Record an agent decision."""
    if not HAS_PROMETHEUS:
        return
    AGENT_DECISION_COUNT.labels(agent_name=agent_name).inc()
    AGENT_DECISION_LATENCY.labels(agent_name=agent_name).observe(duration)


def track_error(error_type: str, component: str) -> None:
    """Record an error."""
    if not HAS_PROMETHEUS:
        return
    ERROR_COUNT.labels(error_type=error_type, component=component).inc()


def set_circuit_breaker_state(component: str, state: int) -> None:
    """Update circuit breaker state gauge."""
    if not HAS_PROMETHEUS:
        return
    CIRCUIT_BREAKER_STATE.labels(component=component).set(state)


def set_app_info(
    version: str, llm_mode: str, orchestrator_mode: str
) -> None:
    """Set application info."""
    if not HAS_PROMETHEUS:
        return
    APP_INFO.info(
        {
            "version": version,
            "llm_mode": llm_mode,
            "orchestrator_mode": orchestrator_mode,
        }
    )
