"""Structural tests for every registered portfolio strategy.

The big one is the causality (no-lookahead) test: a strategy's weights up to
date t must not change when future data is removed. This catches the most
common and most expensive backtesting bug class.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.engine import compute_weighted_returns
from backtesting.portfolio_strategies import PORTFOLIO_STRATEGIES

# Strategies that read aux data files (e.g. ^VIX) need the repo data dir;
# they're tested too, but skipped gracefully if data is missing.
N_DAYS = 1400
TICKERS = ["SPY", "QQQ", "TLT", "GLD", "XLE", "XLU", "EWA", "VGK",
           "XLB", "XLF", "XLI", "XLK", "XLP", "XLV", "XLY"]


@pytest.fixture(scope="module")
def prices():
    """Synthetic but realistic price matrix: correlated GBM with regimes."""
    rng = np.random.default_rng(99)
    dates = pd.bdate_range("2015-01-02", periods=N_DAYS)
    base = rng.normal(0.0003, 0.01, (N_DAYS, len(TICKERS)))
    common = rng.normal(0.0002, 0.008, (N_DAYS, 1))
    rets = base * 0.6 + common * 0.4
    prices = 100 * np.cumprod(1 + rets, axis=0)
    return pd.DataFrame(prices, index=dates, columns=TICKERS)


def _run(strategy_fn, prices):
    try:
        return strategy_fn(prices)
    except FileNotFoundError:
        pytest.skip("strategy needs repo data files (e.g. ^VIX) not present")


@pytest.mark.parametrize("name", sorted(PORTFOLIO_STRATEGIES))
class TestStrategyContract:
    def test_shape_and_alignment(self, name, prices):
        weights = _run(PORTFOLIO_STRATEGIES[name], prices)
        assert isinstance(weights, pd.DataFrame)
        assert weights.index.equals(prices.index)
        assert list(weights.columns) == list(prices.columns)

    def test_no_nan_or_inf(self, name, prices):
        weights = _run(PORTFOLIO_STRATEGIES[name], prices)
        assert np.isfinite(weights.to_numpy()).all(), f"{name} produced NaN/inf"

    def test_leverage_bounded(self, name, prices):
        weights = _run(PORTFOLIO_STRATEGIES[name], prices)
        gross = weights.abs().sum(axis=1).max()
        assert gross <= 3.5 + 1e-9, f"{name} gross leverage {gross:.2f} > 3.5"

    def test_no_lookahead(self, name, prices):
        """Weights through day t must be identical when days after t are
        unknown. Allow a tail window for month-end-evaluation strategies."""
        weights_full = _run(PORTFOLIO_STRATEGIES[name], prices)
        cut = N_DAYS - 200
        weights_cut = PORTFOLIO_STRATEGIES[name](prices.iloc[:cut])
        # compare up to 45 days before the cut (covers monthly resampling)
        compare_to = cut - 45
        a = weights_full.iloc[:compare_to]
        b = weights_cut.iloc[:compare_to]
        pd.testing.assert_frame_equal(a, b, check_exact=False, atol=1e-12,
                                      obj=f"{name} lookahead check")


class TestEngineReturns:
    def test_weights_applied_next_day(self, prices):
        """A weight set on day t earns day t+1's return, not day t's."""
        weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
        # bet everything on SPY for exactly one day
        t = 100
        weights.iloc[t, 0] = 1.0
        returns = compute_weighted_returns(prices, weights, 0.0)
        spy_next = prices.iloc[t + 1, 0] / prices.iloc[t, 0] - 1.0
        assert returns.iloc[t + 1] == pytest.approx(spy_next)
        assert returns.iloc[t] == 0.0

    def test_transaction_costs_reduce_returns(self, prices):
        weights = pd.DataFrame(1.0 / len(TICKERS), index=prices.index,
                               columns=prices.columns)
        free = compute_weighted_returns(prices, weights, 0.0)
        costly = compute_weighted_returns(prices, weights, 10.0)
        assert costly.sum() < free.sum()
