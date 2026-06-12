"""Statistical validation toolkit for backtested strategies.

Implements the methods our papers library prescribes:

- Probabilistic / Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014,
  papers/deflated_sharpe.md): corrects an observed Sharpe for track length,
  non-normality, and the number of strategies tried.
- Stationary block bootstrap Monte Carlo (Politis & Romano 1994): resamples
  return paths preserving autocorrelation -> confidence intervals on Sharpe,
  CAGR, and max drawdown instead of point estimates.
- Circular-shift permutation test: does the strategy's TIMING add value over
  random alignment of the same exposure profile? (Preserves both series'
  autocorrelation; destroys only the alignment.)
- Probability of Backtest Overfitting via CSCV (Bailey, Borwein,
  Lopez de Prado & Zhu 2017): how often does the in-sample winner of a
  strategy set underperform out-of-sample?

All functions take plain daily return Series/DataFrames (see
engine.compute_weighted_returns) and are deterministic given a seed.
"""

import math
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, norm, skew

TRADING_DAYS = 252
EULER_MASCHERONI = 0.5772156649015329


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------

def sharpe_ratio(returns: pd.Series, annualize: bool = True) -> float:
    """Sharpe ratio of a daily return series (0% risk-free, like the engine)."""
    r = np.asarray(returns, dtype=float)
    if len(r) < 2 or np.std(r, ddof=0) == 0:
        return 0.0
    sr = np.mean(r) / np.std(r, ddof=0)
    return float(sr * math.sqrt(TRADING_DAYS)) if annualize else float(sr)


def cagr(returns: pd.Series) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) == 0:
        return 0.0
    terminal = float(np.prod(1.0 + r))
    if terminal <= 0:
        return -1.0
    return terminal ** (TRADING_DAYS / len(r)) - 1.0


def _equity_curve(returns) -> np.ndarray:
    """Equity including the 1.0 starting point, so a first-day loss counts
    as a drawdown (an investor's actual experience)."""
    r = np.asarray(returns, dtype=float)
    return np.concatenate([[1.0], np.cumprod(1.0 + r)])


def max_drawdown(returns: pd.Series) -> float:
    equity = _equity_curve(returns)
    running_max = np.maximum.accumulate(equity)
    return float(np.min(equity / running_max - 1.0))


# ---------------------------------------------------------------------------
# Tail-risk metrics (beyond Sharpe/maxDD)
# ---------------------------------------------------------------------------

def sortino_ratio(returns: pd.Series) -> float:
    """Like Sharpe but penalizes only downside deviation (0% MAR)."""
    r = np.asarray(returns, dtype=float)
    downside = r[r < 0]
    if len(r) < 2 or len(downside) == 0:
        return 0.0
    downside_dev = math.sqrt(np.mean(downside ** 2))
    if downside_dev == 0:
        return 0.0
    return float(np.mean(r) / downside_dev * math.sqrt(TRADING_DAYS))


def calmar_ratio(returns: pd.Series) -> float:
    """CAGR / |max drawdown| - return earned per unit of worst pain."""
    dd = max_drawdown(returns)
    if dd == 0:
        return 0.0
    return float(cagr(returns) / abs(dd))


def cvar(returns: pd.Series, alpha: float = 0.95) -> float:
    """Conditional VaR / Expected Shortfall: mean DAILY return of the worst
    (1-alpha) tail. Rockafellar & Uryasev (2000) - what you lose on a bad
    day GIVEN it's a bad day (negative number)."""
    r = np.sort(np.asarray(returns, dtype=float))
    n_tail = max(1, int(math.floor(len(r) * (1.0 - alpha))))
    return float(r[:n_tail].mean())


def ulcer_index(returns: pd.Series) -> float:
    """RMS of the drawdown series - measures DEPTH x DURATION of pain,
    unlike maxDD which only sees the single worst point."""
    equity = _equity_curve(returns)
    running_max = np.maximum.accumulate(equity)
    dd = equity / running_max - 1.0
    return float(math.sqrt(np.mean(dd ** 2)))


def max_drawdown_duration(returns: pd.Series) -> int:
    """Longest stretch (in trading days) below a prior equity peak -
    'how long were you underwater', the metric retirees actually feel."""
    equity = _equity_curve(returns)
    running_max = np.maximum.accumulate(equity)
    underwater = equity < running_max
    longest = current = 0
    for u in underwater:
        current = current + 1 if u else 0
        longest = max(longest, current)
    return int(longest)


def tail_ratio(returns: pd.Series) -> float:
    """|95th percentile| / |5th percentile| of daily returns. > 1 means the
    right tail is fatter than the left (you want this above ~0.9)."""
    r = np.asarray(returns, dtype=float)
    p5 = np.percentile(r, 5)
    p95 = np.percentile(r, 95)
    if p5 == 0:
        return 0.0
    return float(abs(p95) / abs(p5))


def cdar(returns: pd.Series, alpha: float = 0.95) -> float:
    """Conditional Drawdown at Risk (Riskfolio-style): mean of the worst
    (1-alpha) of DAILY drawdown observations. Where CVaR sees bad days,
    CDaR sees bad sustained periods."""
    equity = _equity_curve(returns)
    running_max = np.maximum.accumulate(equity)
    dd = np.sort(equity / running_max - 1.0)
    n_tail = max(1, int(math.floor(len(dd) * (1.0 - alpha))))
    return float(dd[:n_tail].mean())


# ---------------------------------------------------------------------------
# Execution-realism tests (Carver / pysystemtrade-inspired)
# ---------------------------------------------------------------------------

def cost_sensitivity(prices: pd.DataFrame, weights: pd.DataFrame,
                     bps_levels=(0.0, 2.0, 5.0, 10.0)) -> dict:
    """Sharpe at several one-way cost levels + the breakeven cost.

    Costs scale linearly with turnover, so the breakeven (Sharpe = 0) cost
    solves mean_gross = c * mean_turnover. A strategy whose breakeven is
    under ~20bps has no real-world margin for error."""
    from backtesting.engine import compute_weighted_returns

    out = {}
    for bps in bps_levels:
        r = compute_weighted_returns(prices, weights, bps)
        out[f"sharpe_at_{int(bps)}bps"] = sharpe_ratio(r)

    gross = compute_weighted_returns(prices, weights, 0.0)
    w = weights.reindex(prices.index).fillna(0.0)
    turnover = w.diff().abs().sum(axis=1, min_count=1).fillna(
        w.abs().sum(axis=1))
    mean_turnover = float(turnover.mean())
    if mean_turnover > 1e-12:
        out["breakeven_cost_bps"] = float(gross.mean() / mean_turnover * 1e4)
    else:
        out["breakeven_cost_bps"] = float("inf")
    return out


def lag_sensitivity(prices: pd.DataFrame, weights: pd.DataFrame) -> dict:
    """Sharpe with the normal 1-day execution lag vs an EXTRA day of delay.

    A robust monthly signal barely notices T+2; a fragile timing edge
    collapses. Large drops flag strategies that depend on executing the
    instant the signal fires."""
    from backtesting.engine import compute_weighted_returns

    base = sharpe_ratio(compute_weighted_returns(prices, weights, 0.0))
    delayed = sharpe_ratio(
        compute_weighted_returns(prices, weights.shift(1), 0.0))
    return {
        "sharpe_lag1": base,
        "sharpe_lag2": delayed,
        "lag_sharpe_drop": base - delayed,
    }


def gap_risk(weights: pd.DataFrame, shock: float = 0.15) -> float:
    """Worst-case overnight gap loss: max gross applied exposure x shock.

    Monthly/trend signals cannot react to a gap - this is the loss if every
    held asset gapped down `shock` on the strategy's most-exposed day.
    For a 3x levered sleeve this is 3 x shock; cash-heavy overlays score
    well here. Returns a negative number."""
    applied = weights.shift(1).fillna(0.0)
    max_gross = float(applied.abs().sum(axis=1).max())
    return -max_gross * shock


def apply_buffer(weights: pd.DataFrame, buffer: float = 0.05) -> pd.DataFrame:
    """Carver-style position buffering: only trade when the target weight
    drifts more than `buffer` from the current position; otherwise hold.
    Cuts turnover (and so costs/taxes) with minimal signal loss."""
    out = weights.copy()
    values = weights.to_numpy()
    buffered = np.empty_like(values)
    cur = values[0].copy()
    buffered[0] = cur
    for i in range(1, len(values)):
        target = values[i]
        move = np.abs(target - cur) > buffer
        cur = np.where(move, target, cur)
        buffered[i] = cur
    out.iloc[:, :] = buffered
    return out


def parameter_stability(strategy_factory, prices: pd.DataFrame,
                        param_values, transaction_cost_bps: float = 0.0) -> dict:
    """Sharpe across a parameter sweep + a plateau score.

    strategy_factory(param) -> weights DataFrame. plateau_score =
    min(sharpe)/max(sharpe) over the sweep (1.0 = totally flat surface;
    low values = the headline number lives on a knife's edge - Peterson's
    curve-fitting tell)."""
    from backtesting.engine import compute_weighted_returns

    sharpes = {}
    for p in param_values:
        weights = strategy_factory(p)
        r = compute_weighted_returns(prices, weights, transaction_cost_bps)
        sharpes[p] = sharpe_ratio(r)
    vals = np.array(list(sharpes.values()))
    plateau = float(vals.min() / vals.max()) if vals.max() > 0 else 0.0
    return {"sharpe_by_param": sharpes, "plateau_score": plateau}


def risk_report(returns: pd.Series) -> dict:
    """All risk metrics for one return series in a single dict."""
    return {
        "sharpe": sharpe_ratio(returns),
        "sortino": sortino_ratio(returns),
        "calmar": calmar_ratio(returns),
        "cagr": cagr(returns),
        "max_dd": max_drawdown(returns),
        "max_dd_duration_days": max_drawdown_duration(returns),
        "ulcer_index": ulcer_index(returns),
        "cvar_95": cvar(returns, 0.95),
        "cdar_95": cdar(returns, 0.95),
        "tail_ratio": tail_ratio(returns),
    }


# ---------------------------------------------------------------------------
# Probabilistic / Deflated Sharpe (Bailey & Lopez de Prado 2014)
# ---------------------------------------------------------------------------

def probabilistic_sharpe_ratio(returns: pd.Series, sr_benchmark: float = 0.0) -> float:
    """P(true Sharpe > sr_benchmark) given the observed track record.

    sr_benchmark is a NON-annualized (per-period) Sharpe. Accounts for track
    length, skewness and kurtosis of the return series.
    """
    r = np.asarray(returns, dtype=float)
    n = len(r)
    if n < 3 or np.std(r, ddof=0) == 0:
        return 0.0
    sr = sharpe_ratio(returns, annualize=False)
    g3 = float(skew(r))
    g4 = float(kurtosis(r, fisher=False))  # raw kurtosis (normal = 3)
    denom = 1.0 - g3 * sr + (g4 - 1.0) / 4.0 * sr ** 2
    if denom <= 0:
        return 0.0
    z = (sr - sr_benchmark) * math.sqrt(n - 1) / math.sqrt(denom)
    return float(norm.cdf(z))


def expected_max_sharpe(n_trials: int, var_trial_sharpes: float) -> float:
    """Expected maximum per-period Sharpe across n_trials skill-less
    strategies whose Sharpe estimates have the given variance."""
    if n_trials <= 1 or var_trial_sharpes <= 0:
        return 0.0
    e = math.e
    return math.sqrt(var_trial_sharpes) * (
        (1.0 - EULER_MASCHERONI) * norm.ppf(1.0 - 1.0 / n_trials)
        + EULER_MASCHERONI * norm.ppf(1.0 - 1.0 / (n_trials * e))
    )


def deflated_sharpe_ratio(returns: pd.Series, trial_sharpes) -> float:
    """DSR: probability the strategy's Sharpe is real, given how many
    strategies were tried.

    trial_sharpes: per-period (non-annualized) Sharpe of EVERY strategy in
    the experiment, including this one. The benchmark becomes the expected
    max Sharpe of that many skill-less trials.
    """
    trial_sharpes = np.asarray(trial_sharpes, dtype=float)
    sr0 = expected_max_sharpe(len(trial_sharpes), float(np.var(trial_sharpes)))
    return probabilistic_sharpe_ratio(returns, sr_benchmark=sr0)


# ---------------------------------------------------------------------------
# Stationary block bootstrap Monte Carlo (Politis & Romano 1994)
# ---------------------------------------------------------------------------

def stationary_bootstrap_indices(n: int, n_sims: int, avg_block: int,
                                 rng: np.random.Generator) -> np.ndarray:
    """(n_sims, n) index matrix. Blocks have geometric length (mean
    avg_block) and wrap circularly, preserving local autocorrelation."""
    p = 1.0 / avg_block
    # For each position, decide whether a new block starts (prob p)
    new_block = rng.random((n_sims, n)) < p
    new_block[:, 0] = True
    starts = rng.integers(0, n, size=(n_sims, n))
    indices = np.zeros((n_sims, n), dtype=np.int64)
    for sim in range(n_sims):
        idx = 0
        for t in range(n):
            if new_block[sim, t]:
                idx = starts[sim, t]
            else:
                idx = (idx + 1) % n
            indices[sim, t] = idx
    return indices


def bootstrap_metrics(returns: pd.Series, n_sims: int = 1000,
                      avg_block: int = 21, seed: int = 42,
                      indices: np.ndarray = None) -> dict:
    """Monte Carlo distribution of Sharpe/CAGR/maxDD via stationary bootstrap.

    Returns point estimates plus 5th/50th/95th percentiles and the
    probability of a negative CAGR over a same-length path.

    Pass a precomputed `indices` matrix (from stationary_bootstrap_indices)
    to share the same resampled paths across many strategies - common random
    numbers make cross-strategy comparisons less noisy and much faster.
    """
    r = np.asarray(returns, dtype=float)
    n = len(r)
    if indices is None:
        rng = np.random.default_rng(seed)
        indices = stationary_bootstrap_indices(n, n_sims, avg_block, rng)
    else:
        if indices.shape[1] != n:
            raise ValueError("Precomputed indices length mismatch")
        n_sims = indices.shape[0]
    paths = r[indices]  # (n_sims, n)

    means = paths.mean(axis=1)
    stds = paths.std(axis=1, ddof=0)
    sharpes = np.where(stds > 0, means / stds * math.sqrt(TRADING_DAYS), 0.0)

    log_growth = np.log1p(paths).sum(axis=1)
    cagrs = np.expm1(log_growth * (TRADING_DAYS / n))

    equity = np.cumprod(1.0 + paths, axis=1)
    running_max = np.maximum.accumulate(equity, axis=1)
    maxdds = (equity / running_max - 1.0).min(axis=1)

    def pct(a):
        return {
            "p5": float(np.percentile(a, 5)),
            "p50": float(np.percentile(a, 50)),
            "p95": float(np.percentile(a, 95)),
        }

    return {
        "observed_sharpe": sharpe_ratio(returns),
        "observed_cagr": cagr(returns),
        "observed_max_dd": max_drawdown(returns),
        "sharpe": pct(sharpes),
        "cagr": pct(cagrs),
        "max_dd": pct(maxdds),
        "prob_negative_cagr": float((cagrs < 0).mean()),
        "n_sims": n_sims,
        "avg_block": avg_block,
    }


# ---------------------------------------------------------------------------
# Circular-shift permutation test for timing skill
# ---------------------------------------------------------------------------

def permutation_test_timing(asset_returns: pd.DataFrame, weights: pd.DataFrame,
                            n_perms: int = 500, seed: int = 42,
                            min_shift: int = 63) -> dict:
    """Does the strategy's timing beat random alignment of the same weights?

    Circularly shifts the weight matrix by random offsets (>= min_shift days)
    against the SAME asset returns: exposure profile, turnover and leverage
    are preserved; only the alignment with returns is destroyed. The p-value
    is the fraction of shifted variants whose Sharpe >= observed.
    """
    asset_returns = asset_returns.fillna(0.0)
    weights = weights.reindex(asset_returns.index).fillna(0.0)
    n = len(asset_returns)
    if n <= 2 * min_shift:
        raise ValueError("Series too short for a meaningful permutation test")

    applied = weights.shift(1).fillna(0.0).to_numpy()
    ret = asset_returns.to_numpy()
    observed = ret * applied
    observed_sr = sharpe_ratio(pd.Series(observed.sum(axis=1)))

    rng = np.random.default_rng(seed)
    shifts = rng.integers(min_shift, n - min_shift, size=n_perms)
    null_sharpes = np.empty(n_perms)
    for i, s in enumerate(shifts):
        shifted = np.roll(applied, s, axis=0)
        null_sharpes[i] = sharpe_ratio(pd.Series((ret * shifted).sum(axis=1)))

    p_value = float((null_sharpes >= observed_sr).mean())
    return {
        "observed_sharpe": observed_sr,
        "null_sharpe_mean": float(null_sharpes.mean()),
        "null_sharpe_p95": float(np.percentile(null_sharpes, 95)),
        "p_value": p_value,
        "n_perms": n_perms,
    }


# ---------------------------------------------------------------------------
# Probability of Backtest Overfitting (CSCV, Bailey et al. 2017)
# ---------------------------------------------------------------------------

def probability_of_backtest_overfitting(returns_matrix: pd.DataFrame,
                                        n_blocks: int = 8) -> dict:
    """CSCV estimate of PBO for a SET of strategies.

    Splits time into n_blocks contiguous blocks; for every half/half
    combination, picks the in-sample Sharpe winner and finds its
    out-of-sample rank. PBO = fraction of combinations where the IS winner
    is below the OOS median. ~0.5 means rankings are noise; near 0 means
    the winner genuinely generalizes.
    """
    if n_blocks % 2 != 0:
        raise ValueError("n_blocks must be even")
    data = returns_matrix.dropna(how="any").to_numpy()
    n, n_strats = data.shape
    if n_strats < 2:
        raise ValueError("Need at least 2 strategies")
    blocks = np.array_split(np.arange(n), n_blocks)

    logits = []
    for is_blocks in combinations(range(n_blocks), n_blocks // 2):
        is_idx = np.concatenate([blocks[b] for b in is_blocks])
        oos_idx = np.concatenate([blocks[b] for b in range(n_blocks)
                                  if b not in is_blocks])
        def sharpes(idx):
            sub = data[idx]
            mu = sub.mean(axis=0)
            sd = sub.std(axis=0, ddof=0)
            return np.where(sd > 0, mu / sd, 0.0)
        winner = int(np.argmax(sharpes(is_idx)))
        oos = sharpes(oos_idx)
        # relative rank of the IS winner out-of-sample, in (0, 1)
        rank = (oos < oos[winner]).sum() / (n_strats - 1) if n_strats > 1 else 0.5
        rank = min(max(rank, 1e-6), 1 - 1e-6)
        logits.append(math.log(rank / (1.0 - rank)))

    logits = np.array(logits)
    return {
        "pbo": float((logits < 0).mean()),
        "n_combinations": len(logits),
        "median_oos_rank_logit": float(np.median(logits)),
    }
