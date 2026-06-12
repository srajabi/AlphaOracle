"""Tests for distribution-shape, consistency, and benchmark-relative metrics."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.validation import (
    capture_ratios,
    downside_correlation,
    gain_to_pain,
    k_ratio,
    martin_ratio,
    omega_ratio,
    risk_report,
    rolling_sharpe_consistency,
)


class TestOmega:
    def test_symmetric_zero_mean_near_one(self):
        rng = np.random.default_rng(1)
        raw = rng.normal(0, 0.01, 50000)
        r = pd.Series(raw - raw.mean())
        assert 0.95 < omega_ratio(r) < 1.05

    def test_positive_mean_above_one(self):
        rng = np.random.default_rng(2)
        r = pd.Series(rng.normal(0.001, 0.01, 5000))
        assert omega_ratio(r) > 1.0

    def test_threshold_raises_bar(self):
        rng = np.random.default_rng(3)
        r = pd.Series(rng.normal(0.001, 0.01, 5000))
        assert omega_ratio(r, threshold=0.002) < omega_ratio(r, threshold=0.0)


class TestMartinAndGPR:
    def test_martin_prefers_shallow_drawdowns(self):
        # identical except for one dip: deeper dip = lower CAGR AND higher
        # ulcer, so Martin must rank A strictly above B
        a = pd.Series([0.001] * 250 + [-0.005] + [0.001] * 249)
        b = pd.Series([0.001] * 250 + [-0.10] + [0.001] * 249)
        assert martin_ratio(a) > martin_ratio(b) > 0.0

    def test_martin_zero_guard_for_no_drawdown(self):
        assert martin_ratio(pd.Series([0.001] * 500)) == 0.0

    def test_gpr_no_losing_months_is_zero_guard(self):
        r = pd.Series([0.001] * 252)
        assert gain_to_pain(r) == 0.0  # no pain -> guarded

    def test_gpr_positive_for_profitable_series(self):
        rng = np.random.default_rng(4)
        r = pd.Series(rng.normal(0.0008, 0.01, 2520))
        assert gain_to_pain(r) > 1.0


class TestKRatio:
    def test_straight_line_growth_beats_lumpy(self):
        rng = np.random.default_rng(5)
        smooth = pd.Series([0.0005] * 1000)
        lumpy = pd.Series(rng.normal(0.0005, 0.02, 1000))
        assert k_ratio(smooth) > k_ratio(lumpy)

    def test_short_series_zero(self):
        assert k_ratio(pd.Series([0.01] * 5)) == 0.0


class TestRollingConsistency:
    def test_always_up_is_one(self):
        r = pd.Series([0.001] * 1000)
        assert rolling_sharpe_consistency(r) == 1.0

    def test_too_short_zero(self):
        assert rolling_sharpe_consistency(pd.Series([0.01] * 100)) == 0.0


class TestCaptureRatios:
    def test_half_exposure_half_capture(self):
        rng = np.random.default_rng(6)
        bench = pd.Series(rng.normal(0.0003, 0.01, 5000))
        strat = bench * 0.5
        out = capture_ratios(strat, bench)
        assert out["up_capture"] == pytest.approx(0.5)
        assert out["down_capture"] == pytest.approx(0.5)

    def test_convex_strategy_asymmetric(self):
        rng = np.random.default_rng(7)
        bench = pd.Series(rng.normal(0.0, 0.01, 5000))
        # long benchmark on up days only (perfect-foresight convexity for
        # the metric's sake)
        strat = bench.where(bench > 0, 0.0)
        out = capture_ratios(strat, bench)
        assert out["up_capture"] == pytest.approx(1.0)
        assert out["down_capture"] == pytest.approx(0.0)


class TestDownsideCorrelation:
    def test_hedged_strategy_low_downside_corr(self):
        rng = np.random.default_rng(8)
        bench = pd.Series(rng.normal(0.0, 0.01, 5000))
        hedged = pd.Series(rng.normal(0.0, 0.005, 5000))  # independent
        long = bench * 1.0
        assert abs(downside_correlation(hedged, bench)) < 0.1
        assert downside_correlation(long, bench) > 0.95

    def test_insufficient_down_days_guard(self):
        bench = pd.Series([0.01] * 100)
        strat = pd.Series([0.005] * 100)
        assert downside_correlation(strat, bench) == 0.0


class TestRiskReportWithBenchmark:
    def test_benchmark_keys_present(self):
        rng = np.random.default_rng(9)
        r = pd.Series(rng.normal(0.0004, 0.01, 2000))
        b = pd.Series(rng.normal(0.0004, 0.012, 2000))
        report = risk_report(r, benchmark=b)
        for key in ("up_capture", "down_capture", "downside_corr",
                    "omega", "martin", "gain_to_pain", "k_ratio",
                    "skew", "kurtosis", "rolling_1y_sharpe_pos"):
            assert key in report
        assert all(np.isfinite(v) for v in report.values())
