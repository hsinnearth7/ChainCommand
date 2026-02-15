"""Event bus — pub/sub for decoupled agent communication."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine, Dict, List

from ..data.schemas import SupplyChainEvent
from ..utils.logging_config import get_logger

log = get_logger(__name__)

Handler = Callable[[SupplyChainEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Async publish/subscribe event bus for supply chain events."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Handler]] = defaultdict(list)
        self._all_subscribers: List[Handler] = []  # subscribe to all events
        self._event_log: List[SupplyChainEvent] = []
        self._queue: asyncio.Queue[SupplyChainEvent] = asyncio.Queue()
        self._running = False
        self._task: asyncio.Task | None = None

    def subscribe(self, event_type: str, handler: Handler) -> None:
        """Subscribe a handler to a specific event type."""
        self._subscribers[event_type].append(handler)
        log.debug("event_subscribed", event_type=event_type, handler=handler.__qualname__)

    def subscribe_all(self, handler: Handler) -> None:
        """Subscribe a handler to ALL events."""
        self._all_subscribers.append(handler)

    async def publish(self, event: SupplyChainEvent) -> None:
        """Publish an event. Dispatches to matching subscribers."""
        self._event_log.append(event)
        log.info(
            "event_published",
            event_type=event.event_type,
            severity=event.severity.value,
            source=event.source_agent,
        )

        # Dispatch to type-specific subscribers
        handlers = self._subscribers.get(event.event_type, [])
        # Also dispatch to wildcard subscribers
        all_handlers = handlers + self._all_subscribers

        tasks = [self._safe_dispatch(h, event) for h in all_handlers]
        if tasks:
            await asyncio.gather(*tasks)

    async def _safe_dispatch(self, handler: Handler, event: SupplyChainEvent) -> None:
        """Dispatch with error isolation."""
        try:
            await handler(event)
        except Exception as exc:
            log.error(
                "event_handler_error",
                handler=handler.__qualname__,
                event_type=event.event_type,
                error=str(exc),
            )

    async def start(self) -> None:
        """Start the background event loop (for queued events)."""
        self._running = True
        self._task = asyncio.create_task(self._loop())
        log.info("event_bus_started")

    async def _loop(self) -> None:
        """Process queued events."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self.publish(event)
            except asyncio.TimeoutError:
                continue

    async def stop(self) -> None:
        """Stop the event loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        log.info("event_bus_stopped")

    async def enqueue(self, event: SupplyChainEvent) -> None:
        """Enqueue event for async processing."""
        await self._queue.put(event)

    @property
    def recent_events(self) -> List[SupplyChainEvent]:
        """Return the last 100 events."""
        return self._event_log[-100:]

    @property
    def event_count(self) -> int:
        return len(self._event_log)
