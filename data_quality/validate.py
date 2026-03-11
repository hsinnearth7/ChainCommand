"""Data quality validation using Great Expectations."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import great_expectations as gx

    HAS_GX = True
except ImportError:
    HAS_GX = False

EXPECTATIONS_DIR = Path(__file__).parent / "expectations"


def validate_dataframe(df: Any, expectation_suite: str) -> dict[str, Any]:
    """Validate a pandas DataFrame against an expectation suite."""
    if not HAS_GX:
        logger.warning("great_expectations not installed — skipping validation")
        return {
            "success": True,
            "skipped": True,
            "reason": "great_expectations not installed",
        }

    suite_path = EXPECTATIONS_DIR / f"{expectation_suite}.json"
    if not suite_path.exists():
        return {"success": False, "error": f"Suite not found: {expectation_suite}"}

    context = gx.get_context()
    datasource = context.sources.add_or_update_pandas("pandas_source")
    asset = datasource.add_dataframe_asset(name="validation_asset")
    batch = asset.build_batch_request(dataframe=df)

    suite = context.get_expectation_suite(expectation_suite)
    results = context.run_validation_operator(
        "action_list_operator",
        assets_to_validate=[(batch, suite)],
    )

    return {
        "success": results["success"],
        "statistics": results.statistics if hasattr(results, "statistics") else {},
        "suite": expectation_suite,
    }


def validate_demand_history(df: Any) -> dict[str, Any]:
    """Validate demand history data."""
    return validate_dataframe(df, "demand_history")


def validate_inventory_status(df: Any) -> dict[str, Any]:
    """Validate inventory status data."""
    return validate_dataframe(df, "inventory_status")
