"""Tests for action tools — input validation, PO creation, safety stock."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from chaincommand.tools.action_tools import (
    AdjustSafetyStock,
    CreatePurchaseOrder,
    EmitEvent,
    RequestHumanApproval,
)


@pytest.fixture
def mock_runtime(mock_runtime):
    """Extend conftest mock_runtime for action tool tests."""
    return mock_runtime


class TestCreatePurchaseOrder:
    @pytest.mark.asyncio
    async def test_negative_quantity_rejected(self, mock_runtime):
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = CreatePurchaseOrder()
            result = await tool.execute(
                supplier_id="SUP-test01",
                product_id="PRD-test01",
                quantity=-10,
                unit_cost=5.0,
            )
            assert "error" in result
            assert "positive" in result["error"]

    @pytest.mark.asyncio
    async def test_zero_quantity_rejected(self, mock_runtime):
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = CreatePurchaseOrder()
            result = await tool.execute(
                supplier_id="SUP-test01",
                product_id="PRD-test01",
                quantity=0,
                unit_cost=5.0,
            )
            assert "error" in result

    @pytest.mark.asyncio
    async def test_negative_unit_cost_rejected(self, mock_runtime):
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = CreatePurchaseOrder()
            result = await tool.execute(
                supplier_id="SUP-test01",
                product_id="PRD-test01",
                quantity=10,
                unit_cost=-1.0,
            )
            assert "error" in result
            assert "non-negative" in result["error"]

    @pytest.mark.asyncio
    async def test_valid_po_auto_approved(self, mock_runtime):
        """Small PO should be auto-approved."""
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = CreatePurchaseOrder()
            result = await tool.execute(
                supplier_id="SUP-test01",
                product_id="PRD-test01",
                quantity=5,
                unit_cost=10.0,
            )
            assert "po_id" in result
            assert result["approval_status"] == "auto_approved"
            assert result["total_cost"] == 50.0

    @pytest.mark.asyncio
    async def test_expensive_po_needs_approval(self, mock_runtime):
        """Large PO should require human approval."""
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = CreatePurchaseOrder()
            result = await tool.execute(
                supplier_id="SUP-test01",
                product_id="PRD-test01",
                quantity=10000,
                unit_cost=10.0,
            )
            assert result["approval_status"] == "pending"
            assert len(mock_runtime.pending_approvals) > 0


class TestAdjustSafetyStock:
    @pytest.mark.asyncio
    async def test_negative_safety_stock_rejected(self, mock_runtime):
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = AdjustSafetyStock()
            result = await tool.execute(
                product_id="PRD-test01",
                new_safety_stock=-10.0,
            )
            assert "error" in result
            assert "non-negative" in result["error"]

    @pytest.mark.asyncio
    async def test_small_change_auto_applied(self, mock_runtime):
        """Small safety stock change should auto-apply."""
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = AdjustSafetyStock()
            result = await tool.execute(
                product_id="PRD-test01",
                new_safety_stock=52.0,  # ~4% change from 50
            )
            assert result["status"] == "applied"
            assert result["new_safety_stock"] == 52.0

    @pytest.mark.asyncio
    async def test_large_change_needs_approval(self, mock_runtime):
        """Large safety stock change (>25%) should need approval."""
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = AdjustSafetyStock()
            result = await tool.execute(
                product_id="PRD-test01",
                new_safety_stock=100.0,  # 100% change from 50
            )
            assert result["status"] == "pending_approval"
            assert "request_id" in result

    @pytest.mark.asyncio
    async def test_product_not_found(self, mock_runtime):
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = AdjustSafetyStock()
            result = await tool.execute(
                product_id="NONEXISTENT",
                new_safety_stock=100.0,
            )
            assert "error" in result


class TestRequestHumanApproval:
    @pytest.mark.asyncio
    async def test_valid_approval_request(self, mock_runtime):
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = RequestHumanApproval()
            result = await tool.execute(
                request_type="general",
                description="Test approval",
                estimated_cost=1000.0,
                risk_level="high",
            )
            assert result["status"] == "pending"
            assert "request_id" in result

    @pytest.mark.asyncio
    async def test_invalid_severity_handled(self, mock_runtime):
        """Invalid severity should gracefully fallback to MEDIUM."""
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = RequestHumanApproval()
            result = await tool.execute(
                request_type="general",
                description="Test with bad severity",
                risk_level="nonexistent_severity",
            )
            assert result["status"] == "pending"  # should not crash


class TestEmitEvent:
    @pytest.mark.asyncio
    async def test_emit_without_event_bus(self, mock_runtime):
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = EmitEvent()
            result = await tool.execute(
                event_type="test_event",
                severity="low",
                source_agent="test",
                description="test event",
            )
            assert result["published"] is False

    @pytest.mark.asyncio
    async def test_invalid_severity_in_emit(self, mock_runtime):
        """Invalid severity should gracefully fallback to MEDIUM."""
        with patch("chaincommand.orchestrator._runtime", mock_runtime):
            tool = EmitEvent()
            result = await tool.execute(
                event_type="test_event",
                severity="bogus",
            )
            assert "event_id" in result
