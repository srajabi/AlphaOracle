"""Tests for the IPS signal feed's pure logic."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.family_signals import (
    canary_signal,
    credit_signal,
    fast_channel,
    mom_13612w,
    slow_channel,
)


def series(values, start_month=1):
    """(date, close) pairs, ~21/month across months."""
    out = []
    month, day = start_month, 1
    for v in values:
        out.append((f"2024-{month:02d}-{day:02d}", float(v)))
        day += 1
        if day > 21:
            day = 1
            month = month % 12 + 1
    return out


class TestSlowChannel:
    def test_risk_on_above_sma(self):
        closes = series([100.0] * 200 + [120.0] * 30)
        out = slow_channel(closes)
        assert out["state"] == "risk_on"
        assert out["price"] > out["sma200"]

    def test_risk_off_below_sma(self):
        closes = series([100.0] * 200 + [80.0] * 30)
        assert slow_channel(closes)["state"] == "risk_off"

    def test_uses_month_end_not_today(self):
        # rally AFTER the last month-end must not flip the state
        closes = series([100.0] * 200 + [80.0] * 21 + [200.0] * 5)
        out = slow_channel(closes)
        assert out["state"] == "risk_off"

    def test_insufficient(self):
        assert slow_channel(series([100] * 50))["state"] == "insufficient_data"


class TestFastChannel:
    def _pair(self, vix, vix3m):
        dates = [f"2024-01-{d:02d}" for d in range(1, 6)]
        return ([(d, v) for d, v in zip(dates, vix)],
                [(d, v) for d, v in zip(dates, vix3m)])

    def test_backwardation(self):
        v, v3 = self._pair([30] * 5, [25] * 5)
        assert fast_channel(v, v3)["state"] == "backwardation"

    def test_contango_clear(self):
        v, v3 = self._pair([15] * 5, [18] * 5)
        assert fast_channel(v, v3)["state"] == "clear"

    def test_median_robust_to_one_spike(self):
        v, v3 = self._pair([15, 15, 40, 15, 15], [18] * 5)
        assert fast_channel(v, v3)["state"] == "clear"


class TestCreditAndCanary:
    def test_credit_stress(self):
        hyg = series([100.0] * 40 + [90.0] * 30)   # HY selling off
        lqd = series([100.0] * 70)
        assert credit_signal(hyg, lqd)["state"] == "stress"

    def test_credit_clear(self):
        hyg = series([100.0 + i * 0.01 for i in range(70)])
        lqd = series([100.0] * 70)
        assert credit_signal(hyg, lqd)["state"] == "clear"

    def test_mom_13612w_sign(self):
        up = series([100.0 * 1.001 ** i for i in range(300)])
        down = series([100.0 * 0.999 ** i for i in range(300)])
        assert mom_13612w(up) > 0 > mom_13612w(down)

    def test_canary_states(self):
        up = series([100.0 * 1.001 ** i for i in range(300)])
        down = series([100.0 * 0.999 ** i for i in range(300)])
        assert canary_signal(up, up)["state"] == "risk_on"
        assert canary_signal(down, up)["state"] == "half_defensive"
        assert canary_signal(down, down)["state"] == "full_defensive"
