"""Rich terminal UI for ChainCommand demo mode."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.tree import Tree

from .theme import (
    AGENT_ICONS,
    AGENT_LAYER,
    CHAINCOMMAND_THEME,
    CYCLE_STEPS,
    INIT_PHASES,
    KPI_BAD,
    KPI_GOOD,
    KPI_WARN,
    LAYER_BADGES,
    LAYER_COLORS,
    SEVERITY_STYLES,
)


class ChainCommandUI:
    """Observer-pattern UI that renders Rich output driven by orchestrator callbacks."""

    def __init__(self) -> None:
        self.console = Console(theme=CHAINCOMMAND_THEME)
        self._event_buffer: List[Dict[str, Any]] = []
        self._init_timings: List[float] = [0.0] * len(INIT_PHASES)
        self._cycle_timings: List[float] = [0.0] * len(CYCLE_STEPS)
        self._phase_start: float = 0.0
        self._step_start: float = 0.0
        self._demo_start: float = 0.0

        # Progress bar references (set inside context managers)
        self._init_progress: Optional[Progress] = None
        self._init_task_id: Optional[int] = None
        self._cycle_progress: Optional[Progress] = None
        self._cycle_task_id: Optional[int] = None

    # ── Header / Footer ─────────────────────────────────────

    def print_header(self) -> None:
        """Print startup banner with system info."""
        self._demo_start = time.time()

        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="bold cyan", justify="right")
        info_table.add_column()
        info_table.add_row("System",  "ChainCommand v1.0.0")
        info_table.add_row("Mode",    "Demo -- Single Decision Cycle")
        info_table.add_row("Agents",  "10 AI Agents across 4 layers")
        info_table.add_row("ML",      "LSTM + XGBoost | Isolation Forest | GA + DQN")

        self.console.print()
        self.console.print(
            Panel(
                info_table,
                title="[bold white]ChainCommand[/bold white]",
                subtitle="[dim]Autonomous Supply Chain Optimizer[/dim]",
                border_style="cyan",
                padding=(1, 3),
            )
        )
        self.console.print()

    def print_footer(self) -> None:
        """Print completion banner with total elapsed time."""
        elapsed = time.time() - self._demo_start
        self.console.print()
        self.console.print(
            Panel(
                f"[bold green]Demo complete[/bold green] in [bold]{elapsed:.1f}s[/bold]\n"
                f"[dim]Run without --demo to start the API server.[/dim]",
                border_style="green",
                padding=(1, 3),
            )
        )
        self.console.print()

    # ── Initialization Progress ──────────────────────────────

    @contextmanager
    def init_progress(self):
        """Context manager wrapping the initialization phase with a progress bar."""
        self.console.print("[bold cyan]Initializing system...[/bold cyan]")
        self.console.print()
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        with progress:
            task_id = progress.add_task(
                INIT_PHASES[0]["desc"],
                total=len(INIT_PHASES),
            )
            self._init_progress = progress
            self._init_task_id = task_id
            yield
        self._init_progress = None
        self._init_task_id = None
        self.console.print()

    def start_init_phase(self, index: int) -> None:
        """Mark the start of initialization phase *index*."""
        self._phase_start = time.time()
        if self._init_progress and self._init_task_id is not None:
            phase = INIT_PHASES[index]
            self._init_progress.update(
                self._init_task_id,
                description=f"{phase['name']}: {phase['desc']}",
            )

    def complete_init_phase(self, index: int) -> None:
        """Mark completion of initialization phase *index*."""
        self._init_timings[index] = time.time() - self._phase_start
        if self._init_progress and self._init_task_id is not None:
            self._init_progress.advance(self._init_task_id)

    def print_init_complete(self) -> None:
        """Print a summary table showing time spent in each init phase."""
        table = Table(title="Initialization Complete", border_style="cyan")
        table.add_column("Phase", style="bold")
        table.add_column("Description")
        table.add_column("Time", justify="right", style="green")

        total = 0.0
        for i, phase in enumerate(INIT_PHASES):
            t = self._init_timings[i]
            total += t
            table.add_row(phase["name"], phase["desc"], f"{t:.2f}s")
        table.add_row("[bold]Total[/bold]", "", f"[bold]{total:.2f}s[/bold]")

        self.console.print(table)
        self.console.print()

    # ── Decision Cycle Progress ──────────────────────────────

    @contextmanager
    def cycle_progress(self):
        """Context manager wrapping one decision cycle with a progress bar."""
        self.console.print("[bold magenta]Running decision cycle...[/bold magenta]")
        self.console.print()
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        with progress:
            task_id = progress.add_task(
                CYCLE_STEPS[0]["desc"],
                total=len(CYCLE_STEPS),
            )
            self._cycle_progress = progress
            self._cycle_task_id = task_id
            yield
        self._cycle_progress = None
        self._cycle_task_id = None
        self.console.print()

    def start_cycle_step(self, index: int) -> None:
        """Mark the start of decision cycle step *index*."""
        self._step_start = time.time()
        if self._cycle_progress and self._cycle_task_id is not None:
            step = CYCLE_STEPS[index]
            layer_color = LAYER_COLORS.get(step["layer"], "white")
            self._cycle_progress.update(
                self._cycle_task_id,
                description=f"[{layer_color}]{step['name']}[/{layer_color}]: {step['desc']}",
            )

    def complete_cycle_step(self, index: int) -> None:
        """Mark completion of decision cycle step *index*."""
        self._cycle_timings[index] = time.time() - self._step_start
        if self._cycle_progress and self._cycle_task_id is not None:
            self._cycle_progress.advance(self._cycle_task_id)

    # ── Event Notifications ──────────────────────────────────

    def notify_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
    ) -> None:
        """Buffer an event; immediately print if HIGH or CRITICAL."""
        entry = {
            "event_type": event_type,
            "severity": severity,
            "source": source,
            "description": description,
            "time": time.time(),
        }
        self._event_buffer.append(entry)

        if severity in ("high", "critical"):
            style = SEVERITY_STYLES.get(severity, "white")
            self.console.print(
                f"  [{style}][{severity.upper()}][/{style}] "
                f"{event_type} -- {description}"
            )

    # ── KPI Dashboard ────────────────────────────────────────

    def print_kpi_dashboard(self, kpi: Dict[str, Any]) -> None:
        """Render a colour-coded KPI table with PASS/FAIL markers."""
        table = Table(title="KPI Dashboard", border_style="blue")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        table.add_column("Status", justify="center")

        rows: list[tuple[str, str, str]] = [
            ("OTIF",               f"{kpi.get('otif', 0):.1%}",
             self._kpi_status(kpi.get("otif", 0), 0.95, 0.85)),
            ("Fill Rate",          f"{kpi.get('fill_rate', 0):.1%}",
             self._kpi_status(kpi.get("fill_rate", 0), 0.97, 0.90)),
            ("MAPE",               f"{kpi.get('mape', 0):.1f}%",
             self._kpi_status_inverse(kpi.get("mape", 0), 15, 25)),
            ("Days Supply (DSI)",  f"{kpi.get('dsi', 0):.1f} days",
             self._kpi_status_range(kpi.get("dsi", 0), 10, 60)),
            ("Stockout Count",     f"{kpi.get('stockout_count', 0)}",
             self._kpi_status_inverse(kpi.get("stockout_count", 0), 3, 8)),
            ("Inventory Value",    f"${kpi.get('total_inventory_value', 0):,.0f}",
             ""),
            ("Carrying Cost",      f"${kpi.get('carrying_cost', 0):,.0f}",
             ""),
            ("Inventory Turnover", f"{kpi.get('inventory_turnover', 0):.1f}",
             self._kpi_status(kpi.get("inventory_turnover", 0), 6, 3)),
            ("Perfect Order Rate", f"{kpi.get('perfect_order_rate', 0):.1%}",
             self._kpi_status(kpi.get("perfect_order_rate", 0), 0.95, 0.85)),
            ("Backorder Rate",     f"{kpi.get('backorder_rate', 0):.1%}",
             self._kpi_status_inverse(kpi.get("backorder_rate", 0), 0.05, 0.15)),
            ("Supplier Defect",    f"{kpi.get('supplier_defect_rate', 0):.1%}",
             self._kpi_status_inverse(kpi.get("supplier_defect_rate", 0), 0.02, 0.05)),
            ("Order Cycle Time",   f"{kpi.get('order_cycle_time', 0):.1f} days",
             ""),
        ]

        for metric, value, status in rows:
            table.add_row(metric, value, status)

        self.console.print(table)
        self.console.print()

    @staticmethod
    def _kpi_status(value: float, good_thresh: float, warn_thresh: float) -> str:
        """Higher-is-better metric."""
        if value >= good_thresh:
            return f"[{KPI_GOOD}]PASS[/{KPI_GOOD}]"
        if value >= warn_thresh:
            return f"[{KPI_WARN}]WARN[/{KPI_WARN}]"
        return f"[{KPI_BAD}]FAIL[/{KPI_BAD}]"

    @staticmethod
    def _kpi_status_inverse(value: float, good_thresh: float, warn_thresh: float) -> str:
        """Lower-is-better metric."""
        if value <= good_thresh:
            return f"[{KPI_GOOD}]PASS[/{KPI_GOOD}]"
        if value <= warn_thresh:
            return f"[{KPI_WARN}]WARN[/{KPI_WARN}]"
        return f"[{KPI_BAD}]FAIL[/{KPI_BAD}]"

    @staticmethod
    def _kpi_status_range(value: float, low: float, high: float) -> str:
        """In-range metric (value should be between low and high)."""
        if low <= value <= high:
            return f"[{KPI_GOOD}]PASS[/{KPI_GOOD}]"
        return f"[{KPI_BAD}]FAIL[/{KPI_BAD}]"

    # ── Agent Summary Tree ───────────────────────────────────

    def print_agent_summary_tree(self, results: Dict[str, str]) -> None:
        """Render a layered tree of agent results."""
        tree = Tree("[bold]Agent Results by Layer[/bold]")

        layers: dict[str, list[str]] = {}
        for agent_name in results:
            layer = AGENT_LAYER.get(agent_name, "unknown")
            layers.setdefault(layer, []).append(agent_name)

        layer_order = ["strategic", "tactical", "operational", "orchestration"]
        for layer in layer_order:
            agents = layers.get(layer, [])
            if not agents:
                continue
            badge = LAYER_BADGES.get(layer, layer)
            color = LAYER_COLORS.get(layer, "white")
            branch = tree.add(f"{badge} [{color}]{layer.title()} Layer[/{color}]")
            for agent_name in agents:
                icon = AGENT_ICONS.get(agent_name, " - ")
                summary = results.get(agent_name, "")
                short = (summary[:90] + "...") if len(summary) > 90 else summary
                branch.add(f"[dim]{icon}[/dim] [bold]{agent_name}[/bold]: {short}")

        self.console.print(tree)
        self.console.print()

    # ── Event Log ────────────────────────────────────────────

    def print_event_log(self) -> None:
        """Render buffered events as a table sorted by time."""
        if not self._event_buffer:
            self.console.print("[dim]No events recorded during this cycle.[/dim]")
            self.console.print()
            return

        table = Table(title="Event Log", border_style="yellow")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Severity", justify="center")
        table.add_column("Type")
        table.add_column("Source")
        table.add_column("Description", max_width=60)

        for i, evt in enumerate(self._event_buffer, 1):
            sev = evt["severity"]
            style = SEVERITY_STYLES.get(sev, "white")
            table.add_row(
                str(i),
                f"[{style}]{sev.upper()}[/{style}]",
                evt["event_type"],
                evt["source"],
                evt["description"],
            )

        self.console.print(table)
        self.console.print()

    # ── Cycle Timing Bar Chart ───────────────────────────────

    def print_cycle_timing(self) -> None:
        """Render a horizontal bar chart of step durations."""
        table = Table(title="Cycle Step Timing", border_style="magenta")
        table.add_column("Step", style="bold", min_width=18)
        table.add_column("Layer", justify="center")
        table.add_column("Time", justify="right", min_width=7)
        table.add_column("Bar", min_width=30)

        max_time = max(self._cycle_timings) if any(self._cycle_timings) else 1.0
        for i, step in enumerate(CYCLE_STEPS):
            t = self._cycle_timings[i]
            bar_len = int((t / max_time) * 25) if max_time > 0 else 0
            color = LAYER_COLORS.get(step["layer"], "white")
            bar = f"[{color}]{'=' * bar_len}[/{color}]"
            badge = LAYER_BADGES.get(step["layer"], "")
            table.add_row(step["name"], badge, f"{t:.2f}s", bar)

        total = sum(self._cycle_timings)
        table.add_row("[bold]Total[/bold]", "", f"[bold]{total:.2f}s[/bold]", "")
        self.console.print(table)
        self.console.print()

    # ── Callback Bridge Methods ──────────────────────────────
    # These are invoked by the Orchestrator via ui_callback.

    def on_init_phase_start(self, index: int) -> None:
        self.start_init_phase(index)

    def on_init_phase_complete(self, index: int) -> None:
        self.complete_init_phase(index)

    def on_cycle_step_start(self, index: int) -> None:
        self.start_cycle_step(index)

    def on_cycle_step_complete(self, index: int) -> None:
        self.complete_cycle_step(index)

    def on_event(
        self,
        event_type: str,
        severity: str,
        source: str,
        description: str,
    ) -> None:
        self.notify_event(event_type, severity, source, description)
