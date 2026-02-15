"""CLI entry point for ChainCommand.

Usage:
    python -m chaincommand           Start API server + simulation
    python -m chaincommand --demo    Run one demo cycle and exit
"""

from __future__ import annotations

import argparse
import asyncio
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="chaincommand",
        description="ChainCommand — Autonomous Supply Chain Optimizer AI Team",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a single demo cycle (no server)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Server host (default from config)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port (default from config)",
    )
    args = parser.parse_args()

    if args.demo:
        asyncio.run(_run_demo())
    else:
        _run_server(host=args.host, port=args.port)


async def _run_demo() -> None:
    """Run one full decision cycle and print the result."""
    from .orchestrator import ChainCommandOrchestrator

    print("=" * 70)
    print("  ChainCommand — Demo Mode")
    print("  Running one full decision cycle with 10 AI agents...")
    print("=" * 70)
    print()

    orchestrator = ChainCommandOrchestrator()
    result = await orchestrator.run_demo()

    print()
    print("=" * 70)
    print("  CYCLE RESULTS")
    print("=" * 70)
    print(f"  Cycle:           {result['cycle']}")
    print(f"  KPI Violations:  {result['violations']}")
    print(f"  Report ID:       {result.get('report')}")
    print()

    kpi = result.get("kpi", {})
    print("  KPI Snapshot:")
    print(f"    OTIF:              {kpi.get('otif', 0):.1%}")
    print(f"    Fill Rate:         {kpi.get('fill_rate', 0):.1%}")
    print(f"    MAPE:              {kpi.get('mape', 0):.1f}%")
    print(f"    DSI:               {kpi.get('dsi', 0):.1f} days")
    print(f"    Stockout Count:    {kpi.get('stockout_count', 0)}")
    print(f"    Inventory Value:   ${kpi.get('total_inventory_value', 0):,.0f}")
    print(f"    Inventory Turnover:{kpi.get('inventory_turnover', 0):.1f}")
    print(f"    Perfect Order:     {kpi.get('perfect_order_rate', 0):.1%}")
    print()

    print("  Agent Summaries:")
    for agent_name, summary in result.get("agent_results", {}).items():
        short = (summary[:80] + "...") if len(summary) > 80 else summary
        print(f"    {agent_name:25s} {short}")

    print()
    print("=" * 70)
    print("  Demo complete. Run without --demo to start the API server.")
    print("=" * 70)


def _run_server(host: str | None = None, port: int | None = None) -> None:
    """Start the FastAPI server with uvicorn."""
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn required for server mode: pip install uvicorn")
        sys.exit(1)

    from .config import settings

    uvicorn.run(
        "chaincommand.api.app:app",
        host=host or settings.host,
        port=port or settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
