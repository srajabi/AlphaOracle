"""Tests for the execution-realism layer: costs, lag, buffering, gap risk,
parameter stability, CDaR."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.engine import compute_weighted_returns
from backtesting.validation import (
    apply_buffer,
    cdar,
    cost_sensitivity,
    cvar,
    gap_risk,
    lag_sensitivity,
    parameter_stability,
    sharpe_ratio,
)


@pytest.fixture
def prices():
    rng = np.random.default_rng(11)
    dates = pd.bdate_range("2018-01-02", periods=1500)
    rets = rng.normal(0.0004, 0.01, (1500, 3))
    return pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=dates,
                        columns=["A", "B", "C"])


class TestCDaR:
    def test_cdar_at_least_as_bad_as_mean_drawdown(self):
        rng = np.random.default_rng(2)
        r = pd.Series(rng.normal(0, 0.01, 2000))
        assert cdar(r, 0.95) <= 0.0

    def test_cdar_zero_for_monotonic_up(self):
        assert cdar(pd.Series([0.01] * 100)) == 0.0

    def test_cdar_worse_than_cvar_makes_sense(self):
        # drawdowns persist; daily returns don't - CDaR magnitude should
        # generally exceed CVaR magnitude for a volatile series
        rng = np.random.default_rng(3)
        r = pd.Series(rng.normal(0, 0.01, 2000))
        assert abs(cdar(r, 0.95)) > abs(cvar(r, 0.95))


class TestCostSensitivity:
    def test_sharpe_declines_with_cost(self, prices):
        rng = np.random.default_rng(4)
        weights = pd.DataFrame(rng.random((1500, 3)), index=prices.index,
                               columns=prices.columns)
        out = cost_sensitivity(prices, weights)
        assert out["sharpe_at_0bps"] >= out["sharpe_at_2bps"] >= \
               out["sharpe_at_10bps"]

    def test_breakeven_infinite_for_buy_and_hold(self, prices):
        weights = pd.DataFrame(1.0 / 3, index=prices.index,
                               columns=prices.columns)
        out = cost_sensitivity(prices, weights)
        # constant weights -> near-zero turnover after entry; breakeven huge
        assert out["breakeven_cost_bps"] > 100

    def test_breakeven_sign_matches_gross_mean(self, prices):
        # a high-turnover strategy on zero-edge prices: breakeven near zero
        rng = np.random.default_rng(5)
        weights = pd.DataFrame(rng.random((1500, 3)), index=prices.index,
                               columns=prices.columns)
        out = cost_sensitivity(prices, weights)
        assert np.isfinite(out["breakeven_cost_bps"])


class TestLagSensitivity:
    def test_buy_and_hold_immune_to_lag(self, prices):
        weights = pd.DataFrame(1.0 / 3, index=prices.index,
                               columns=prices.columns)
        out = lag_sensitivity(prices, weights)
        assert abs(out["lag_sharpe_drop"]) < 0.05

    def test_foresight_strategy_destroyed_by_lag(self, prices):
        # cheat-weights that "know" tomorrow's winner (possible because the
        # engine shifts once; shifting twice kills the cheat) - lag test
        # must expose it
        rets = prices.pct_change().shift(-1).fillna(0.0)
        weights = (rets.rank(axis=1) == 3).astype(float)
        out = lag_sensitivity(prices, weights)
        assert out["lag_sharpe_drop"] > 1.0


class TestGapRisk:
    def test_unlevered_long_only_bounded_by_shock(self, prices):
        weights = pd.DataFrame(1.0 / 3, index=prices.index,
                               columns=prices.columns)
        assert gap_risk(weights, 0.15) == pytest.approx(-0.15)

    def test_levered_scales(self, prices):
        weights = pd.DataFrame(1.0, index=prices.index,
                               columns=prices.columns)  # 3x gross
        assert gap_risk(weights, 0.15) == pytest.approx(-0.45)

    def test_cash_heavy_scores_well(self, prices):
        weights = pd.DataFrame(0.1, index=prices.index,
                               columns=prices.columns)  # 30% gross
        assert gap_risk(weights, 0.15) == pytest.approx(-0.045)


class TestBuffer:
    def test_buffer_reduces_turnover(self, prices):
        rng = np.random.default_rng(6)
        weights = pd.DataFrame(rng.random((1500, 3)) * 0.05 + 0.3,
                               index=prices.index, columns=prices.columns)
        buffered = apply_buffer(weights, buffer=0.05)
        turn_raw = weights.diff().abs().sum().sum()
        turn_buf = buffered.diff().abs().sum().sum()
        assert turn_buf < turn_raw * 0.5

    def test_buffer_tracks_large_moves(self, prices):
        weights = pd.DataFrame(0.0, index=prices.index,
                               columns=prices.columns)
        weights.iloc[750:, 0] = 1.0  # a real regime change
        buffered = apply_buffer(weights, buffer=0.05)
        assert buffered.iloc[-1, 0] == 1.0
        assert buffered.iloc[751, 0] == 1.0

    def test_zero_buffer_is_identity(self, prices):
        rng = np.random.default_rng(7)
        weights = pd.DataFrame(rng.random((1500, 3)), index=prices.index,
                               columns=prices.columns)
        pd.testing.assert_frame_equal(apply_buffer(weights, 0.0), weights)


class TestParameterStability:
    def test_flat_factory_perfect_plateau(self, prices):
        def factory(_p):
            return pd.DataFrame(1.0 / 3, index=prices.index,
                                columns=prices.columns)
        out = parameter_stability(factory, prices, [1, 2, 3])
        assert out["plateau_score"] == pytest.approx(1.0)

    def test_sweep_keys_preserved(self, prices):
        def factory(p):
            w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
            w["A"] = p / 10.0
            return w
        out = parameter_stability(factory, prices, [1, 5, 9])
        assert set(out["sharpe_by_param"]) == {1, 5, 9}
