"""ChainCommand Orchestrator — system coordinator and runtime state."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from .config import settings
from .data.schemas import (
    HumanApprovalRequest,
    KPISnapshot,
    PurchaseOrder,
    Product,
    Supplier,
)
from .utils.logging_config import get_logger, setup_logging

log = get_logger(__name__)


# ── Runtime state (singleton) ───────────────────────────────

@dataclass
class _RuntimeState:
    """Mutable global state shared across agents, tools, and API."""

    products: Optional[List[Product]] = None
    suppliers: Optional[List[Supplier]] = None
    demand_df: Optional[pd.DataFrame] = None

    # ML models
    forecaster: Any = None
    anomaly_detector: Any = None
    optimizer: Any = None

    # Engines
    kpi_engine: Any = None
    event_bus: Any = None
    monitor: Any = None

    # Agent registry
    agents: Dict[str, Any] = field(default_factory=dict)

    # Transaction state
    purchase_orders: List[PurchaseOrder] = field(default_factory=list)
    pending_approvals: Dict[str, HumanApprovalRequest] = field(default_factory=dict)
    kpi_history: List[KPISnapshot] = field(default_factory=list)


_runtime = _RuntimeState()


# ── Orchestrator ────────────────────────────────────────────

class ChainCommandOrchestrator:
    """Main orchestrator that initializes, runs cycles, and shuts down."""

    def __init__(self) -> None:
        self._running = False
        self._cycle_count = 0
        self._loop_task: Optional[asyncio.Task] = None

    @property
    def running(self) -> bool:
        return self._running

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    async def initialize(self) -> None:
        """Bootstrap the entire system."""
        setup_logging()
        log.info("initializing", llm_mode=settings.llm_mode.value)

        # 1. Generate synthetic data
        from .data.generator import generate_all

        log.info("generating_data")
        products, suppliers, demand_df = generate_all()
        _runtime.products = products
        _runtime.suppliers = suppliers
        _runtime.demand_df = demand_df
        log.info("data_generated", products=len(products), suppliers=len(suppliers))

        # 2. Train ML models
        from .models.forecaster import EnsembleForecaster
        from .models.anomaly_detector import AnomalyDetector
        from .models.optimizer import HybridOptimizer

        log.info("training_models")

        _runtime.forecaster = EnsembleForecaster()
        product_ids = [p.product_id for p in products[:20]]  # Train on first 20 for speed
        _runtime.forecaster.train_all(demand_df, product_ids)

        _runtime.anomaly_detector = AnomalyDetector()
        _runtime.anomaly_detector.train(demand_df)

        _runtime.optimizer = HybridOptimizer()
        log.info("models_trained")

        # 3. Initialize engines
        from .kpi.engine import KPIEngine
        from .events.bus import EventBus
        from .events.monitor import ProactiveMonitor

        _runtime.kpi_engine = KPIEngine()
        _runtime.event_bus = EventBus()
        _runtime.monitor = ProactiveMonitor(
            _runtime.event_bus, _runtime.kpi_engine, _runtime.anomaly_detector
        )

        # 4. Initialize agents
        from .llm.factory import create_llm
        from .tools import (
            QueryDemandHistory, QueryInventoryStatus, QuerySupplierInfo,
            QueryKPIHistory, RunDemandForecast, GetForecastAccuracy,
            CalculateReorderPoint, OptimizeInventory, EvaluateSupplier,
            DetectAnomalies, AssessSupplyRisk, ScanMarketIntelligence,
            CreatePurchaseOrder, RequestHumanApproval, AdjustSafetyStock,
            EmitEvent,
        )
        from .agents import (
            DemandForecasterAgent, StrategicPlannerAgent,
            InventoryOptimizerAgent, SupplierManagerAgent,
            LogisticsCoordinatorAgent, AnomalyDetectorAgent,
            RiskAssessorAgent, MarketIntelligenceAgent,
            CoordinatorAgent, ReporterAgent,
        )

        llm = create_llm()
        log.info("llm_created", mode=settings.llm_mode.value)

        _runtime.agents = {
            "demand_forecaster": DemandForecasterAgent(
                llm=llm,
                tools=[QueryDemandHistory(), RunDemandForecast(), GetForecastAccuracy(), ScanMarketIntelligence(), EmitEvent()],
            ),
            "strategic_planner": StrategicPlannerAgent(
                llm=llm,
                tools=[QueryKPIHistory(), OptimizeInventory(), QueryInventoryStatus(), EmitEvent()],
            ),
            "inventory_optimizer": InventoryOptimizerAgent(
                llm=llm,
                tools=[QueryInventoryStatus(), CalculateReorderPoint(), AdjustSafetyStock(), OptimizeInventory(), EmitEvent()],
            ),
            "supplier_manager": SupplierManagerAgent(
                llm=llm,
                tools=[QuerySupplierInfo(), EvaluateSupplier(), CreatePurchaseOrder(), RequestHumanApproval(), EmitEvent()],
            ),
            "logistics_coordinator": LogisticsCoordinatorAgent(
                llm=llm,
                tools=[QueryInventoryStatus(), EmitEvent()],
            ),
            "anomaly_detector": AnomalyDetectorAgent(
                llm=llm,
                tools=[DetectAnomalies(), QueryDemandHistory(), QueryInventoryStatus(), EmitEvent()],
            ),
            "risk_assessor": RiskAssessorAgent(
                llm=llm,
                tools=[AssessSupplyRisk(), ScanMarketIntelligence(), QuerySupplierInfo(), EmitEvent()],
            ),
            "market_intelligence": MarketIntelligenceAgent(
                llm=llm,
                tools=[ScanMarketIntelligence(), EmitEvent()],
            ),
            "coordinator": CoordinatorAgent(
                llm=llm,
                tools=[
                    QueryKPIHistory(), QueryInventoryStatus(), QuerySupplierInfo(),
                    QueryDemandHistory(), RequestHumanApproval(), EmitEvent(),
                ],
            ),
            "reporter": ReporterAgent(
                llm=llm,
                tools=[QueryKPIHistory(), QueryInventoryStatus(), EmitEvent()],
            ),
        }

        # 5. Set up event subscriptions
        bus = _runtime.event_bus
        agents = _runtime.agents

        bus.subscribe("kpi_threshold_violated", agents["demand_forecaster"].handle_event)
        bus.subscribe("new_market_intel", agents["demand_forecaster"].handle_event)
        bus.subscribe("forecast_updated", agents["strategic_planner"].handle_event)
        bus.subscribe("kpi_trend_alert", agents["strategic_planner"].handle_event)
        bus.subscribe("low_stock_alert", agents["inventory_optimizer"].handle_event)
        bus.subscribe("overstock_alert", agents["inventory_optimizer"].handle_event)
        bus.subscribe("stockout_alert", agents["inventory_optimizer"].handle_event)
        bus.subscribe("forecast_updated", agents["inventory_optimizer"].handle_event)
        bus.subscribe("reorder_triggered", agents["supplier_manager"].handle_event)
        bus.subscribe("supplier_issue", agents["supplier_manager"].handle_event)
        bus.subscribe("quality_alert", agents["supplier_manager"].handle_event)
        bus.subscribe("po_created", agents["logistics_coordinator"].handle_event)
        bus.subscribe("delivery_delayed", agents["logistics_coordinator"].handle_event)
        bus.subscribe("anomaly_detected", agents["risk_assessor"].handle_event)
        bus.subscribe("supply_risk_alert", agents["risk_assessor"].handle_event)
        bus.subscribe("cycle_complete", agents["reporter"].handle_event)
        bus.subscribe("kpi_snapshot_created", agents["reporter"].handle_event)

        # Coordinator listens to everything
        bus.subscribe_all(agents["coordinator"].handle_event)

        log.info("agents_initialized", count=len(_runtime.agents))

        # 6. Compute initial KPI snapshot (stored in kpi_engine.history automatically)
        _runtime.kpi_engine.calculate_snapshot(
            products, _runtime.purchase_orders, suppliers
        )

        log.info("system_ready")

    async def run_cycle(self) -> Dict[str, Any]:
        """Execute one full decision cycle across all agent layers."""
        self._cycle_count += 1
        log.info("cycle_start", cycle=self._cycle_count)

        products = _runtime.products or []
        context = {"products": products, "cycle": self._cycle_count}
        agent_results: Dict[str, Any] = {}

        agents = _runtime.agents

        # Step 1: Operational layer — Market Intelligence + Anomaly Detection
        log.info("cycle_step", step=1, description="Operational layer scan")
        market_result = await agents["market_intelligence"].run_cycle(context)
        anomaly_result = await agents["anomaly_detector"].run_cycle(context)
        agent_results["market_intelligence"] = market_result
        agent_results["anomaly_detector"] = anomaly_result

        # Step 2: Strategic layer — Demand Forecasting
        log.info("cycle_step", step=2, description="Strategic forecasting")
        forecast_result = await agents["demand_forecaster"].run_cycle(context)
        agent_results["demand_forecaster"] = forecast_result

        # Step 3: Tactical + Operational — Inventory + Risk
        log.info("cycle_step", step=3, description="Inventory check + Risk assessment")
        inv_result = await agents["inventory_optimizer"].run_cycle(context)
        risk_result = await agents["risk_assessor"].run_cycle(context)
        agent_results["inventory_optimizer"] = inv_result
        agent_results["risk_assessor"] = risk_result

        # Step 4: Tactical — Supplier selection + Procurement
        log.info("cycle_step", step=4, description="Supplier management")
        supplier_result = await agents["supplier_manager"].run_cycle(context)
        agent_results["supplier_manager"] = supplier_result

        # Step 5: Tactical — Logistics coordination
        log.info("cycle_step", step=5, description="Logistics coordination")
        logistics_result = await agents["logistics_coordinator"].run_cycle(context)
        agent_results["logistics_coordinator"] = logistics_result

        # Step 6: Strategic — Strategic planning
        log.info("cycle_step", step=6, description="Strategic planning")
        planner_result = await agents["strategic_planner"].run_cycle(context)
        agent_results["strategic_planner"] = planner_result

        # Step 7: Orchestration — Coordinator summarizes + resolves conflicts
        log.info("cycle_step", step=7, description="Coordinator arbitration")
        coord_context = {**context, "agent_results": agent_results}
        coord_result = await agents["coordinator"].run_cycle(coord_context)
        agent_results["coordinator"] = coord_result

        # Step 8: Orchestration — Reporter generates summary
        log.info("cycle_step", step=8, description="Report generation")
        report_context = {
            **context,
            "agent_results": agent_results,
            "coordinator_summary": coord_result.get("executive_summary", ""),
        }
        report_result = await agents["reporter"].run_cycle(report_context)
        agent_results["reporter"] = report_result

        # Step 9: KPI update (stored in kpi_engine.history automatically)
        snapshot = _runtime.kpi_engine.calculate_snapshot(
            products, _runtime.purchase_orders, _runtime.suppliers or [],
        )
        violations = _runtime.kpi_engine.check_thresholds(snapshot)
        for event in violations:
            if _runtime.event_bus:
                await _runtime.event_bus.publish(event)

        # Simulate demand consumption
        import random
        for p in products:
            consumed = max(0, random.gauss(p.daily_demand_avg, p.daily_demand_std))
            p.current_stock = max(0, p.current_stock - consumed)

        log.info(
            "cycle_complete",
            cycle=self._cycle_count,
            agents_run=len(agent_results),
            kpi_violations=len(violations),
        )

        return {
            "cycle": self._cycle_count,
            "agent_results": {k: v.get("analysis", "") if isinstance(v, dict) else "" for k, v in agent_results.items()},
            "kpi": snapshot.model_dump(),
            "violations": len(violations),
            "report": report_result.get("report", {}).get("report_id"),
        }

    async def run_loop(self) -> None:
        """Run continuous simulation cycles."""
        self._running = True

        # Start proactive monitor
        if _runtime.monitor:
            await _runtime.monitor.start()

        log.info("simulation_loop_started")
        while self._running:
            try:
                await self.run_cycle()
                interval = settings.event_tick_seconds * 2 / max(settings.simulation_speed, 0.1)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.error("cycle_error", error=str(exc))
                await asyncio.sleep(5)

    async def stop_loop(self) -> None:
        """Stop the simulation loop."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
        log.info("simulation_loop_stopped")

    async def run_demo(self) -> Dict[str, Any]:
        """Run a single demo cycle and print results."""
        await self.initialize()
        result = await self.run_cycle()
        await self.shutdown()
        return result

    async def shutdown(self) -> None:
        """Clean shutdown of all components."""
        self._running = False
        if _runtime.monitor:
            await _runtime.monitor.stop()
        if _runtime.event_bus:
            await _runtime.event_bus.stop()
        log.info("system_shutdown")


# ── Singleton ───────────────────────────────────────────────

_orchestrator: Optional[ChainCommandOrchestrator] = None


def get_orchestrator() -> ChainCommandOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ChainCommandOrchestrator()
    return _orchestrator
