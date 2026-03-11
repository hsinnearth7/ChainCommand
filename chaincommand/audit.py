"""Audit logging for ChainCommand.

Provides structured audit trail for all significant operations including
user actions, system events, and API access patterns.
"""
from __future__ import annotations

import json
import logging
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False

logger = logging.getLogger(__name__)


class AuditEvent:
    """Represents a single audit log entry."""

    __slots__ = (
        "timestamp", "user", "action", "resource", "result",
        "ip_address", "user_agent", "details", "duration_ms",
    )

    def __init__(
        self,
        user: str,
        action: str,
        resource: str,
        result: str = "success",
        ip_address: str = "",
        user_agent: str = "",
        details: dict[str, Any] | None = None,
        duration_ms: float = 0.0,
    ) -> None:
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.user = user
        self.action = action
        self.resource = resource
        self.result = result
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.details = details or {}
        self.duration_ms = duration_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "user": self.user,
            "action": self.action,
            "resource": self.resource,
            "result": self.result,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.details,
            "duration_ms": self.duration_ms,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class AuditLogger:
    """Structured audit logger with in-memory trail and optional structlog integration."""

    def __init__(self, max_trail_size: int = 10000) -> None:
        self._trail: deque[dict[str, Any]] = deque(maxlen=max_trail_size)
        if HAS_STRUCTLOG:
            self._log = structlog.get_logger("chaincommand.audit")
        else:
            self._log = logging.getLogger("chaincommand.audit")

    def log(
        self,
        user: str,
        action: str,
        resource: str,
        result: str = "success",
        ip_address: str = "",
        user_agent: str = "",
        details: dict[str, Any] | None = None,
        duration_ms: float = 0.0,
    ) -> AuditEvent:
        """Record an audit event."""
        event = AuditEvent(
            user=user,
            action=action,
            resource=resource,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            duration_ms=duration_ms,
        )
        entry = event.to_dict()
        self._trail.append(entry)

        if HAS_STRUCTLOG:
            self._log.info(
                "audit_event",
                user=user,
                action=action,
                resource=resource,
                result=result,
                ip_address=ip_address,
                duration_ms=duration_ms,
            )
        else:
            self._log.info(
                "audit: user=%s action=%s resource=%s result=%s ip=%s duration=%.1fms",
                user, action, resource, result, ip_address, duration_ms,
            )

        return event

    def query(
        self,
        user: str | None = None,
        action: str | None = None,
        resource: str | None = None,
        result: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Query the audit trail with optional filters."""
        results = []
        for entry in reversed(self._trail):
            if user and entry["user"] != user:
                continue
            if action and entry["action"] != action:
                continue
            if resource and not entry["resource"].startswith(resource):
                continue
            if result and entry["result"] != result:
                continue
            results.append(entry)
            if len(results) >= offset + limit:
                break
        return results[offset : offset + limit]

    @property
    def trail_size(self) -> int:
        return len(self._trail)


# Global audit logger instance
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


class AuditMiddleware:
    """FastAPI ASGI middleware that automatically logs API access.

    Usage:
        app = FastAPI()
        app.add_middleware(AuditMiddleware)
    """

    SKIP_PATHS = frozenset({"/metrics", "/api/health"})

    def __init__(self, app: Any, audit_logger: AuditLogger | None = None) -> None:
        self.app = app
        self._audit = audit_logger or get_audit_logger()

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in self.SKIP_PATHS:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        start_time = time.monotonic()

        # Extract client info from scope
        client = scope.get("client", ("", 0))
        ip_address = client[0] if client else ""

        # Extract headers
        headers = dict(scope.get("headers", []))
        user_agent = ""
        username = "anonymous"
        for key, value in headers.items():
            if key == b"user-agent":
                user_agent = value.decode("utf-8", errors="replace")
            elif key == b"x-api-key":
                # Mask API key in audit
                username = f"api-key:***{value.decode()[-4:]}" if len(value) > 4 else "api-key:***"

        # Get user from scope (set by RBAC middleware)
        user = scope.get("user")
        if user is not None:
            username = user.username

        # Capture response status
        response_status = [0]

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                response_status[0] = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
            duration_ms = (time.monotonic() - start_time) * 1000
            result = "success" if response_status[0] < 400 else "failure"
        except Exception as exc:
            duration_ms = (time.monotonic() - start_time) * 1000
            result = "error"
            self._audit.log(
                user=username,
                action=f"{method} {path}",
                resource=path,
                result=result,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"error": str(exc), "status": 500},
                duration_ms=duration_ms,
            )
            raise

        self._audit.log(
            user=username,
            action=f"{method} {path}",
            resource=path,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"status": response_status[0]},
            duration_ms=duration_ms,
        )
