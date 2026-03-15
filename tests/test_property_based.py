"""Property-based tests using Hypothesis."""

from __future__ import annotations

import pytest

try:
    from hypothesis import given, settings
    from hypothesis import strategies as st

    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

pytestmark = pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")


if HAS_HYPOTHESIS:

    class TestKPIRanges:
        @given(
            otif=st.floats(min_value=0, max_value=1),
            fill_rate=st.floats(min_value=0, max_value=1),
            mape=st.floats(min_value=0, max_value=100),
            dsi=st.floats(min_value=0, max_value=365),
        )
        @settings(max_examples=50)
        def test_kpi_snapshot_valid_ranges(self, otif, fill_rate, mape, dsi):
            from chaincommand.data.schemas import KPISnapshot

            snap = KPISnapshot(otif=otif, fill_rate=fill_rate, mape=mape, dsi=dsi)
            assert 0 <= snap.otif <= 1
            assert 0 <= snap.fill_rate <= 1
            assert 0 <= snap.mape <= 100
            assert 0 <= snap.dsi <= 365

        @given(
            unit_cost=st.floats(min_value=0.01, max_value=1000),
            risk_score=st.floats(min_value=0, max_value=1),
            capacity=st.floats(min_value=1, max_value=100000),
        )
        @settings(max_examples=30)
        def test_supplier_candidate_valid(self, unit_cost, risk_score, capacity):
            from chaincommand.optimization.cpsat_optimizer import SupplierCandidate

            sc = SupplierCandidate(
                supplier_id="TEST",
                unit_cost=unit_cost,
                risk_score=risk_score,
                capacity=capacity,
            )
            assert sc.unit_cost > 0
            assert 0 <= sc.risk_score <= 1

        @given(demand=st.floats(min_value=100, max_value=10000))
        @settings(max_examples=20)
        def test_optimizer_satisfies_demand(self, demand):
            from chaincommand.optimization.cpsat_optimizer import (
                SupplierAllocationOptimizer,
                SupplierCandidate,
            )

            candidates = [
                SupplierCandidate(
                    supplier_id="S1", unit_cost=10.0, risk_score=0.1, capacity=50000,
                ),
                SupplierCandidate(
                    supplier_id="S2", unit_cost=12.0, risk_score=0.05, capacity=50000,
                ),
            ]
            opt = SupplierAllocationOptimizer()
            result = opt.optimize(candidates, demand=demand)
            total = sum(result.allocations.values())
            assert total >= demand * 0.99  # allow tiny rounding

        @given(
            on_time=st.floats(min_value=0.5, max_value=0.99),
            defect=st.floats(min_value=0.001, max_value=0.1),
        )
        @settings(max_examples=20)
        def test_risk_score_in_range(self, on_time, defect):
            from chaincommand.risk.scorer import SupplierMetrics, SupplierRiskScorer

            scorer = SupplierRiskScorer()
            metrics = SupplierMetrics(supplier_id="TEST", on_time_rate=on_time, defect_rate=defect)
            score = scorer.score_supplier(metrics)
            assert 0 <= score.overall_score <= 1
            assert score.risk_level in ("low", "medium", "high", "critical")

        @given(n=st.integers(min_value=1, max_value=10))
        @settings(max_examples=10)
        def test_bom_synthetic_generation(self, n):
            from chaincommand.bom.manager import BOMManager

            mgr = BOMManager()
            trees = mgr.generate_synthetic_boms(n_assemblies=n)
            assert len(trees) == n
            for tree in trees:
                assert len(tree.root_items) == 1
