"""Tests for the attribution monitor's pure logic (no network)."""

import sys
from pathlib import Path

import math
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.attribution import (
    equity_to_returns,
    live_metrics,
    monthly_composite,
    script_status,
)


def ts(day):  # deterministic UTC timestamps, one per day
    return 1700000000 + day * 86400


class TestEquityToReturns:
    def test_simple_returns(self):
        out = equity_to_returns([ts(0), ts(1), ts(2)], [100, 110, 99])
        assert len(out) == 2
        assert out[0][1] == pytest.approx(0.10)
        assert out[1][1] == pytest.approx(-0.10)

    def test_skips_unfunded_zeros(self):
        out = equity_to_returns([ts(0), ts(1), ts(2), ts(3)],
                                [0, None, 100, 105])
        assert len(out) == 1
        assert out[0][1] == pytest.approx(0.05)


class TestLiveMetrics:
    def test_short_history_only_observations(self):
        out = live_metrics([("2026-01-01", 0.01)] * 3)
        assert out == {"observations": 3}

    def test_max_dd_and_total(self):
        daily = [("d1", 0.10), ("d2", -0.50), ("d3", 0.10)]
        daily += [("dx", 0.0)] * 10  # pad past the 5-obs minimum
        out = live_metrics(daily)
        assert out["max_dd"] == pytest.approx(-0.50)
        assert out["total_return"] == pytest.approx(1.1 * 0.5 * 1.1 - 1)

    def test_sharpe_sign(self):
        up = [(f"d{i}", 0.001 + 0.0001 * (i % 3)) for i in range(100)]
        assert live_metrics(up)["sharpe"] > 0


class TestMonthlyComposite:
    def test_geometric_within_month(self):
        daily = [("2026-01-05", 0.10), ("2026-01-06", 0.10),
                 ("2026-02-02", -0.05)]
        out = monthly_composite(daily)
        assert out["2026-01"] == pytest.approx(0.21)
        assert out["2026-02"] == pytest.approx(-0.05)

    def test_sorted_keys(self):
        daily = [("2026-03-01", 0.01), ("2026-01-01", 0.01)]
        assert list(monthly_composite(daily)) == ["2026-01", "2026-03"]


class TestScriptStatus:
    BANDS = {"sharpe_ci90_low": 0.3, "sharpe_ci90_high": 1.5,
             "max_dd_p5": -0.40}

    def _metrics(self, sharpe, max_dd, n=100):
        return {"observations": n, "sharpe": sharpe, "max_dd": max_dd,
                "total_return": 0.1, "annualized_return": 0.1,
                "current_dd": -0.01}

    def test_on_script(self):
        out = script_status(self._metrics(0.8, -0.15), self.BANDS)
        assert out["status"] == "on_script"
        assert out["breaches"] == []

    def test_watch_single_breach(self):
        out = script_status(self._metrics(0.1, -0.15), self.BANDS)
        assert out["status"] == "watch"
        assert len(out["breaches"]) == 1

    def test_off_script_double_breach(self):
        out = script_status(self._metrics(0.1, -0.55), self.BANDS)
        assert out["status"] == "off_script"
        assert len(out["breaches"]) == 2

    def test_insufficient_history(self):
        out = script_status(self._metrics(0.8, -0.15, n=30), self.BANDS)
        assert out["status"] == "insufficient_history"

    def test_no_bands_insufficient(self):
        out = script_status(self._metrics(0.8, -0.15), None)
        assert out["status"] == "insufficient_history"
