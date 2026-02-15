"""Central configuration using Pydantic Settings."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class LLMMode(str, Enum):
    MOCK = "mock"
    OPENAI = "openai"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    """Application-wide settings loaded from env / .env file."""

    model_config = {"env_file": ".env", "env_prefix": "CC_"}

    # ── LLM ──────────────────────────────────────────────
    llm_mode: LLMMode = LLMMode.MOCK
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ── Simulation ───────────────────────────────────────
    num_products: int = 50
    num_suppliers: int = 20
    history_days: int = 365
    simulation_speed: float = 1.0  # multiplier for event tick rate

    # ── Event engine ─────────────────────────────────────
    event_tick_seconds: float = 5.0
    enable_proactive_monitoring: bool = True

    # ── KPI thresholds (defaults overridable) ────────────
    otif_target: float = 0.95
    fill_rate_target: float = 0.97
    mape_threshold: float = 15.0  # percent
    dsi_max: float = 60.0  # days of supply
    dsi_min: float = 10.0
    stockout_tolerance: int = 3  # max concurrent stockouts

    # ── Escalation / HITL ────────────────────────────────
    cost_escalation_threshold: float = 50_000.0  # USD — needs human approval
    inventory_change_pct_threshold: float = 25.0  # >25% change needs approval
    auto_approve_below: float = 10_000.0

    # ── Server ───────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # ── ML model params ──────────────────────────────────
    lstm_hidden_size: int = 64
    lstm_num_layers: int = 2
    lstm_seq_length: int = 30
    lstm_epochs: int = 50
    xgb_n_estimators: int = 100
    xgb_max_depth: int = 6
    isolation_contamination: float = 0.05
    ga_population_size: int = 50
    ga_generations: int = 100
    dqn_hidden_size: int = 128
    dqn_episodes: int = 200
    dqn_epsilon_start: float = 1.0
    dqn_epsilon_end: float = 0.01
    dqn_epsilon_decay: float = 0.995


settings = Settings()
