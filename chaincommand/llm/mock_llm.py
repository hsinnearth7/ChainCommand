"""Rule-based mock LLM for development and testing (no API key needed)."""

from __future__ import annotations

import random
import re
from typing import TypeVar

from pydantic import BaseModel

from .base import BaseLLM

T = TypeVar("T", bound=BaseModel)

# ── Pre-defined response templates ──────────────────────

_DEMAND_KEYWORDS = re.compile(
    r"demand|forecast|predict|sales|trend", re.IGNORECASE
)
_RISK_KEYWORDS = re.compile(
    r"risk|disrupt|shortage|delay|threat|vulnerability", re.IGNORECASE
)
_INVENTORY_KEYWORDS = re.compile(
    r"inventory|stock|reorder|safety.?stock|warehouse", re.IGNORECASE
)
_SUPPLIER_KEYWORDS = re.compile(
    r"supplier|vendor|procurement|purchase|sourcing", re.IGNORECASE
)
_ANOMALY_KEYWORDS = re.compile(
    r"anomal|outlier|unusual|spike|abnormal", re.IGNORECASE
)
_LOGISTICS_KEYWORDS = re.compile(
    r"logistics|shipping|delivery|transport|route", re.IGNORECASE
)
_MARKET_KEYWORDS = re.compile(
    r"market|intelligence|news|economic|industry", re.IGNORECASE
)
_REPORT_KEYWORDS = re.compile(
    r"report|summary|dashboard|executive|overview", re.IGNORECASE
)
_COORDINATE_KEYWORDS = re.compile(
    r"coordinate|conflict|priorit|arbitrat|consensus", re.IGNORECASE
)
_OPTIMIZE_KEYWORDS = re.compile(
    r"optimi|improve|efficien|reduce.?cost|saving", re.IGNORECASE
)


def _mock_response(prompt: str) -> str:
    """Match intent from prompt and return a plausible mock response."""

    if _DEMAND_KEYWORDS.search(prompt):
        trend = random.choice(["upward", "stable", "seasonal spike"])
        return (
            f"Based on analysis, demand shows a {trend} pattern. "
            f"Recommended forecast adjustment: {random.uniform(-5, 15):.1f}%. "
            f"Confidence: {random.uniform(0.7, 0.95):.0%}. "
            "Key drivers: seasonal effects and recent promotional activity."
        )

    if _RISK_KEYWORDS.search(prompt):
        level = random.choice(["low", "medium", "high"])
        return (
            f"Risk assessment: overall supply risk is {level}. "
            f"Top concern: lead-time variability (score {random.uniform(0.2, 0.9):.2f}). "
            "Mitigation: consider dual-sourcing for critical SKUs and increasing safety stock by 10-15%."
        )

    if _INVENTORY_KEYWORDS.search(prompt):
        action = random.choice([
            "increase safety stock by 12%",
            "reduce reorder point by 8%",
            "maintain current levels",
            "trigger emergency replenishment",
        ])
        return (
            f"Inventory recommendation: {action}. "
            f"Current DSI: {random.uniform(15, 55):.1f} days. "
            f"Estimated cost impact: ${random.uniform(-5000, 10000):.0f}."
        )

    if _SUPPLIER_KEYWORDS.search(prompt):
        supplier = random.choice([
            "GlobalTech Supply", "Pacific Rim Trading", "EuroLogistics",
        ])
        return (
            f"Recommended supplier: {supplier} "
            f"(reliability: {random.uniform(0.8, 0.98):.0%}, "
            f"cost multiplier: {random.uniform(0.9, 1.15):.2f}). "
            "Alternative suppliers identified as backup options."
        )

    if _ANOMALY_KEYWORDS.search(prompt):
        atype = random.choice(["demand spike", "cost anomaly", "lead-time anomaly"])
        return (
            f"Anomaly detected: {atype} with score {random.uniform(0.6, 0.99):.2f}. "
            "Recommend investigation and potential corrective action."
        )

    if _LOGISTICS_KEYWORDS.search(prompt):
        return (
            f"Logistics status: {random.randint(2, 8)} shipments in transit. "
            f"Average delivery time: {random.uniform(3, 12):.1f} days. "
            f"On-time rate: {random.uniform(0.82, 0.97):.0%}."
        )

    if _MARKET_KEYWORDS.search(prompt):
        topic = random.choice([
            "raw material price increase",
            "new competitor entry",
            "regulatory change",
            "seasonal demand shift",
        ])
        return (
            f"Market intelligence: {topic} detected. "
            f"Estimated impact: {random.choice(['positive', 'negative', 'neutral'])}. "
            "Recommend monitoring over next 2 weeks."
        )

    if _REPORT_KEYWORDS.search(prompt):
        return (
            "Executive Summary: System operating within normal parameters. "
            f"OTIF: {random.uniform(0.88, 0.98):.0%}, "
            f"Fill Rate: {random.uniform(0.92, 0.99):.0%}, "
            f"Active alerts: {random.randint(0, 5)}. "
            "No critical issues requiring immediate attention."
        )

    if _COORDINATE_KEYWORDS.search(prompt):
        return (
            "Coordination assessment: all agents aligned. "
            f"Resolved {random.randint(0, 3)} minor conflicts. "
            "Priority actions queued for execution. "
            "No escalation required this cycle."
        )

    if _OPTIMIZE_KEYWORDS.search(prompt):
        return (
            f"Optimization complete. Estimated savings: ${random.uniform(1000, 25000):.0f}. "
            f"Efficiency gain: {random.uniform(2, 12):.1f}%. "
            "Recommended changes applied to reorder parameters."
        )

    # Fallback
    return (
        "Analysis complete. Current supply chain status is stable. "
        "No immediate actions required. Continuing monitoring."
    )


class MockLLM(BaseLLM):
    """Rule-based mock that matches intent via regex and returns canned responses."""

    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
    ) -> str:
        return _mock_response(prompt)

    async def generate_json(
        self,
        prompt: str,
        schema: type[T],
        system: str = "",
        temperature: float = 0.1,
    ) -> T:
        # Build a minimal valid instance by inspecting schema fields
        from pydantic_core import PydanticUndefined

        fields = schema.model_fields
        data: dict = {}
        for name, info in fields.items():
            if info.default is not PydanticUndefined:
                continue  # let Pydantic use its default
            annotation = info.annotation
            if annotation is str or (hasattr(annotation, "__origin__") is False and annotation is str):
                data[name] = _mock_response(prompt)[:120]
            elif annotation is float:
                data[name] = round(random.uniform(0.1, 100.0), 2)
            elif annotation is int:
                data[name] = random.randint(1, 500)
            elif annotation is bool:
                data[name] = True
        try:
            return schema(**data)
        except Exception:
            # Fallback: try constructing with model_construct
            return schema.model_construct(**data)
