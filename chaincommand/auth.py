"""API key authentication for ChainCommand."""

from __future__ import annotations

import hmac

from fastapi import HTTPException, Request, WebSocket

from .config import settings


def require_api_key(request: Request) -> None:
    """FastAPI dependency that validates the X-API-Key header."""
    key = request.headers.get("X-API-Key", "")
    if not hmac.compare_digest(key, settings.api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


async def require_ws_api_key(websocket: WebSocket) -> None:
    """Validate API key for WebSocket connections via query param."""
    key = websocket.query_params.get("api_key", "")
    if not hmac.compare_digest(key, settings.api_key):
        await websocket.close(code=4001, reason="Invalid API key")
        raise HTTPException(status_code=401, detail="Invalid API key")
