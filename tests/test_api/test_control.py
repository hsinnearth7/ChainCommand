"""Control endpoint tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def api_key():
    from chaincommand.config import settings
    return settings.api_key


@pytest.fixture
def auth_headers(api_key):
    return {"X-API-Key": api_key}


class TestSimulationControl:
    @pytest.mark.asyncio
    async def test_simulation_status(self, client, auth_headers, mock_runtime):
        mock_orch = MagicMock()
        mock_orch.running = False
        mock_orch.cycle_count = 0

        with patch("chaincommand.orchestrator._runtime", mock_runtime), \
             patch("chaincommand.orchestrator.get_orchestrator", return_value=mock_orch):
            resp = await client.get("/api/simulation/status", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["running"] is False

    @pytest.mark.asyncio
    async def test_simulation_speed_invalid(self, client, auth_headers):
        resp = await client.post(
            "/api/simulation/speed?speed=0.01",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert "error" in resp.json()

    @pytest.mark.asyncio
    async def test_simulation_speed_valid(self, client, auth_headers):
        resp = await client.post(
            "/api/simulation/speed?speed=2.0",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["speed"] == 2.0

    @pytest.mark.asyncio
    async def test_simulation_stop(self, client, auth_headers):
        mock_orch = MagicMock()
        mock_orch.stop_loop = MagicMock(return_value=None)
        # Make stop_loop an async mock
        import asyncio
        mock_orch.stop_loop = lambda: asyncio.sleep(0)

        with patch("chaincommand.orchestrator.get_orchestrator", return_value=mock_orch):
            resp = await client.post("/api/simulation/stop", headers=auth_headers)
            assert resp.status_code == 200
