"""Tests for backtesting/validation.py."""

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.validation import (
    TRADING_DAYS,
    bootstrap_metrics,
    cagr,
    calmar_ratio,
    cvar,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    max_drawdown,
    max_drawdown_duration,
    permutation_test_timing,
    probabilistic_sharpe_ratio,
    probability_of_backtest_overfitting,
    risk_report,
    sharpe_ratio,
    sortino_ratio,
    stationary_bootstrap_indices,
    tail_ratio,
    ulcer_index,
)


@pytest.fixture
def rng():
    return np.random.default_rng(7)


def _standardized_normal(rng, n, mean, std):
    """Normal draws rescaled so the SAMPLE mean/std are exact - makes
    Sharpe-based assertions deterministic instead of draw-dependent."""
    raw = rng.normal(0, 1, n)
    raw = (raw - raw.mean()) / raw.std(ddof=0)
    return pd.Series(raw * std + mean)


@pytest.fixture
def good_returns(rng):
    """Exactly Sharpe 1.0 (annualized) daily series, 8 years."""
    n = 8 * TRADING_DAYS
    daily_mu = 1.0 / math.sqrt(TRADING_DAYS) * 0.01
    return _standardized_normal(rng, n, daily_mu, 0.01)


@pytest.fixture
def flat_returns(rng):
    """Exactly zero-mean daily series, 8 years."""
    return _standardized_normal(rng, 8 * TRADING_DAYS, 0.0, 0.01)


class TestCoreMetrics:
    def test_sharpe_known_value(self):
        r = pd.Series([0.01, -0.01] * 500)
        assert abs(sharpe_ratio(r)) < 1e-9  # zero mean

    def test_sharpe_constant_series_is_zero(self):
        assert sharpe_ratio(pd.Series([0.0] * 100)) == 0.0

    def test_cagr_doubling(self):
        # exactly doubles over one trading year
        daily = 2.0 ** (1.0 / TRADING_DAYS) - 1.0
        r = pd.Series([daily] * TRADING_DAYS)
        assert cagr(r) == pytest.approx(1.0, rel=1e-6)

    def test_max_drawdown_simple(self):
        # +10% then -50%: max DD is exactly -50%
        r = pd.Series([0.10, -0.50])
        assert max_drawdown(r) == pytest.approx(-0.50)

    def test_max_drawdown_monotonic_up_is_zero(self):
        r = pd.Series([0.01] * 50)
        assert max_drawdown(r) == 0.0


class TestRiskMetrics:
    def test_sortino_ignores_upside_vol(self):
        # same downside, but B has huge upside spikes: Sortino should not
        # punish B the way Sharpe does
        a = pd.Series([0.001, -0.005] * 250)
        b = pd.Series([0.02, -0.005] * 250)
        assert sortino_ratio(b) > sortino_ratio(a)

    def test_sortino_no_losses_returns_zero(self):
        assert sortino_ratio(pd.Series([0.01] * 100)) == 0.0

    def test_calmar_known_value(self):
        # +10% then -50%: CAGR over 2 days annualizes hugely negative;
        # just verify sign and the dd denominator
        r = pd.Series([0.10, -0.50])
        assert calmar_ratio(r) == pytest.approx(cagr(r) / 0.50)

    def test_cvar_is_tail_mean(self):
        r = pd.Series([-0.10] * 5 + [0.001] * 95)
        # worst 5% of 100 days = 5 days, all -10%
        assert cvar(r, alpha=0.95) == pytest.approx(-0.10)

    def test_cvar_more_negative_than_var_level(self):
        rng = np.random.default_rng(3)
        r = pd.Series(rng.normal(0, 0.01, 5000))
        assert cvar(r, 0.95) < np.percentile(r, 5)

    def test_ulcer_zero_for_monotonic_up(self):
        assert ulcer_index(pd.Series([0.01] * 100)) == 0.0

    def test_ulcer_increases_with_time_underwater(self):
        # same maxDD, but B stays underwater longer
        a = pd.Series([-0.10] + [0.12] + [0.0] * 98)
        b = pd.Series([-0.10] + [0.0] * 98 + [0.12])
        assert ulcer_index(b) > ulcer_index(a)
        assert max_drawdown(a) == pytest.approx(max_drawdown(b))

    def test_dd_duration_simple(self):
        # drop on day 1, recover on day 4: underwater days 1,2,3 = 3
        r = pd.Series([-0.10, 0.0, 0.0, 0.20])
        assert max_drawdown_duration(r) == 3

    def test_dd_duration_zero_when_always_at_high(self):
        assert max_drawdown_duration(pd.Series([0.01] * 50)) == 0

    def test_tail_ratio_symmetric_near_one(self):
        rng = np.random.default_rng(4)
        r = pd.Series(rng.normal(0, 0.01, 20000))
        assert 0.9 < tail_ratio(r) < 1.1

    def test_risk_report_keys_complete(self):
        r = pd.Series(np.random.default_rng(5).normal(0.0003, 0.01, 1000))
        report = risk_report(r)
        expected = {"sharpe", "sortino", "calmar", "cagr", "max_dd",
                    "max_dd_duration_days", "ulcer_index", "cvar_95",
                    "cdar_95", "tail_ratio"}
        assert set(report) == expected
        assert all(np.isfinite(v) for v in report.values())


class TestProbabilisticSharpe:
    def test_positive_sharpe_high_psr(self, good_returns):
        assert probabilistic_sharpe_ratio(good_returns) > 0.95

    def test_flat_returns_psr_near_half(self, flat_returns):
        assert 0.4 < probabilistic_sharpe_ratio(flat_returns) < 0.6

    def test_benchmark_above_sr_lowers_psr(self, good_returns):
        sr = sharpe_ratio(good_returns, annualize=False)
        assert probabilistic_sharpe_ratio(good_returns, sr_benchmark=sr * 2) < 0.5

    def test_short_series_returns_zero(self):
        assert probabilistic_sharpe_ratio(pd.Series([0.01, 0.02])) == 0.0


class TestDeflatedSharpe:
    def test_more_trials_more_deflation(self, good_returns, rng):
        few = rng.normal(0, 0.02, 3)
        many = rng.normal(0, 0.02, 200)
        dsr_few = deflated_sharpe_ratio(good_returns, few)
        dsr_many = deflated_sharpe_ratio(good_returns, many)
        assert dsr_many <= dsr_few

    def test_deflation_never_exceeds_raw_psr(self, good_returns, rng):
        trials = rng.normal(0, 0.02, 50)
        assert (deflated_sharpe_ratio(good_returns, trials)
                <= probabilistic_sharpe_ratio(good_returns) + 1e-12)

    def test_expected_max_sharpe_grows_with_trials(self):
        assert (expected_max_sharpe(100, 0.01)
                > expected_max_sharpe(10, 0.01)
                > expected_max_sharpe(2, 0.01)
                > 0.0)

    def test_expected_max_sharpe_degenerate_cases(self):
        assert expected_max_sharpe(1, 0.01) == 0.0
        assert expected_max_sharpe(10, 0.0) == 0.0


class TestBootstrap:
    def test_indices_shape_and_range(self, rng):
        idx = stationary_bootstrap_indices(100, 20, 10, rng)
        assert idx.shape == (20, 100)
        assert idx.min() >= 0 and idx.max() < 100

    def test_reproducible_with_seed(self, good_returns):
        a = bootstrap_metrics(good_returns, n_sims=50, seed=1)
        b = bootstrap_metrics(good_returns, n_sims=50, seed=1)
        assert a == b

    def test_distribution_brackets_observed(self, good_returns):
        m = bootstrap_metrics(good_returns, n_sims=300, seed=3)
        assert m["sharpe"]["p5"] < m["observed_sharpe"] < m["sharpe"]["p95"]
        assert m["cagr"]["p5"] < m["observed_cagr"] < m["cagr"]["p95"]

    def test_negative_cagr_prob_sane(self, good_returns, flat_returns):
        good = bootstrap_metrics(good_returns, n_sims=300, seed=3)
        flat = bootstrap_metrics(flat_returns, n_sims=300, seed=3)
        assert good["prob_negative_cagr"] < 0.10
        assert 0.2 < flat["prob_negative_cagr"] < 0.8


class TestPermutationTest:
    def _make_market(self, rng, n=2000):
        # deterministic alternating regimes (250d blocks) + noise: a
        # detectable but realistic trend structure
        regime = np.sign(np.sin(np.arange(n) * np.pi / 250) + 1e-9)
        r = 0.002 * regime + rng.normal(0, 0.01, n)
        return pd.DataFrame({"SPY": r}), regime

    def test_skilled_timing_beats_null(self, rng):
        market, regime = self._make_market(rng)
        # detector: rolling-60 mean sign - reliably tracks the regime with lag
        detected = np.sign(market["SPY"].rolling(60).mean()).fillna(0)
        weights = pd.DataFrame({"SPY": (detected > 0).astype(float)})
        result = permutation_test_timing(market, weights, n_perms=200, seed=5)
        assert result["p_value"] < 0.10

    def test_random_timing_not_significant(self, rng):
        market, _ = self._make_market(rng)
        weights = pd.DataFrame(
            {"SPY": rng.integers(0, 2, len(market)).astype(float)},
            index=market.index,
        )
        result = permutation_test_timing(market, weights, n_perms=200, seed=5)
        assert result["p_value"] > 0.05

    def test_too_short_raises(self):
        market = pd.DataFrame({"SPY": [0.01] * 100})
        weights = pd.DataFrame({"SPY": [1.0] * 100})
        with pytest.raises(ValueError):
            permutation_test_timing(market, weights, min_shift=63)


class TestPBO:
    def test_pure_noise_pbo_near_half(self, rng):
        noise = pd.DataFrame(rng.normal(0, 0.01, (2000, 10)))
        result = probability_of_backtest_overfitting(noise)
        assert 0.2 < result["pbo"] < 0.8

    def test_dominant_strategy_low_pbo(self, rng):
        noise = pd.DataFrame(rng.normal(0, 0.01, (2000, 10)))
        noise[0] = rng.normal(0.002, 0.01, 2000)  # genuinely better
        result = probability_of_backtest_overfitting(noise)
        assert result["pbo"] < 0.2

    def test_odd_blocks_raises(self, rng):
        noise = pd.DataFrame(rng.normal(0, 0.01, (500, 3)))
        with pytest.raises(ValueError):
            probability_of_backtest_overfitting(noise, n_blocks=7)
