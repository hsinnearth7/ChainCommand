"""Role-Based Access Control (RBAC) for ChainCommand."""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles with increasing privilege levels."""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


class Permission(str, Enum):
    """Granular permissions for API access control."""
    READ_KPI = "read:kpi"
    READ_INVENTORY = "read:inventory"
    READ_AGENTS = "read:agents"
    READ_EVENTS = "read:events"
    READ_SIMULATION = "read:simulation"
    TRIGGER_AGENT = "trigger:agent"
    TRIGGER_SIMULATION = "trigger:simulation"
    MANAGE_SIMULATION = "manage:simulation"
    MANAGE_USERS = "manage:users"
    MANAGE_CONFIG = "manage:config"
    MANAGE_MODELS = "manage:models"


# Role-to-permission mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.VIEWER: {
        Permission.READ_KPI,
        Permission.READ_INVENTORY,
        Permission.READ_AGENTS,
        Permission.READ_EVENTS,
        Permission.READ_SIMULATION,
    },
    Role.OPERATOR: {
        Permission.READ_KPI,
        Permission.READ_INVENTORY,
        Permission.READ_AGENTS,
        Permission.READ_EVENTS,
        Permission.READ_SIMULATION,
        Permission.TRIGGER_AGENT,
        Permission.TRIGGER_SIMULATION,
        Permission.MANAGE_SIMULATION,
        Permission.MANAGE_MODELS,
    },
    Role.ADMIN: set(Permission),  # All permissions
}

# Endpoint-to-permission mapping (method, path_prefix) -> required permission
ENDPOINT_PERMISSIONS: dict[tuple[str, str], Permission] = {
    ("GET", "/api/kpi"): Permission.READ_KPI,
    ("GET", "/api/inventory"): Permission.READ_INVENTORY,
    ("GET", "/api/agents"): Permission.READ_AGENTS,
    ("GET", "/api/events"): Permission.READ_EVENTS,
    ("GET", "/api/simulation"): Permission.READ_SIMULATION,
    ("POST", "/api/agents"): Permission.TRIGGER_AGENT,
    ("POST", "/api/simulation"): Permission.TRIGGER_SIMULATION,
    ("PUT", "/api/simulation"): Permission.MANAGE_SIMULATION,
    ("DELETE", "/api/simulation"): Permission.MANAGE_SIMULATION,
    ("POST", "/api/users"): Permission.MANAGE_USERS,
    ("PUT", "/api/users"): Permission.MANAGE_USERS,
    ("DELETE", "/api/users"): Permission.MANAGE_USERS,
    ("PUT", "/api/config"): Permission.MANAGE_CONFIG,
    ("POST", "/api/models"): Permission.MANAGE_MODELS,
}


class User(BaseModel):
    """User model with role assignment."""
    id: str
    username: str
    email: str = ""
    role: Role = Role.VIEWER
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def permissions(self) -> set[Permission]:
        """Get all permissions for this user's role."""
        return ROLE_PERMISSIONS.get(self.role, set())

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions

    def has_any_permission(self, *permissions: Permission) -> bool:
        """Check if user has any of the specified permissions."""
        return bool(self.permissions & set(permissions))


def _resolve_permission(method: str, path: str) -> Permission | None:
    """Resolve the required permission for a given HTTP method and path."""
    for (m, prefix), perm in ENDPOINT_PERMISSIONS.items():
        if method.upper() == m and path.startswith(prefix):
            return perm
    return None


class RBACMiddleware:
    """FastAPI middleware that enforces RBAC on protected endpoints.

    Usage:
        app = FastAPI()
        app.add_middleware(RBACMiddleware, user_resolver=my_resolver)
    """

    UNPROTECTED_PATHS = frozenset({"/api/health", "/metrics", "/docs", "/openapi.json", "/redoc"})

    def __init__(self, app: Any, user_resolver: Any = None) -> None:
        self.app = app
        self._user_resolver = user_resolver or self._default_resolver

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "GET")

        # Skip unprotected paths
        if any(path.startswith(p) for p in self.UNPROTECTED_PATHS):
            await self.app(scope, receive, send)
            return

        # Resolve required permission
        required = _resolve_permission(method, path)
        if required is None:
            # No explicit mapping — allow through (defense in depth at handler level)
            await self.app(scope, receive, send)
            return

        # Resolve user from request headers
        headers = dict(scope.get("headers", []))
        api_key = None
        for key, value in headers.items():
            if key == b"x-api-key":
                api_key = value.decode("utf-8")
                break

        user = await self._user_resolver(api_key)
        if user is None:
            await self._send_error(send, 401, "Authentication required")
            return

        if not user.is_active:
            await self._send_error(send, 403, "Account is deactivated")
            return

        if not user.has_permission(required):
            logger.warning(
                "access denied: user=%s role=%s required=%s path=%s",
                user.username, user.role.value, required.value, path,
            )
            await self._send_error(send, 403, f"Permission denied: requires {required.value}")
            return

        # Attach user to scope for downstream handlers
        scope["user"] = user
        await self.app(scope, receive, send)

    @staticmethod
    async def _default_resolver(api_key: str | None) -> User | None:
        """Default resolver: treats any non-empty API key as admin (dev only)."""
        if not api_key:
            return None
        return User(id="default", username="dev-user", role=Role.ADMIN)

    @staticmethod
    async def _send_error(send: Any, status: int, message: str) -> None:
        """Send an HTTP error response."""
        import json
        body = json.dumps({"error": message}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(body)).encode()],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
