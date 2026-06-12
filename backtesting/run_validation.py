#!/usr/bin/env python3
"""Run EVERY registered portfolio strategy through the validation gauntlet.

For each strategy, on one uniform universe/window (apples-to-apples):
  - point metrics (CAGR, Sharpe, maxDD, trades/yr)
  - Deflated Sharpe Ratio (trials = every strategy in this sweep)
  - stationary-bootstrap 90% CI on Sharpe + probability of negative CAGR
  - circular-shift permutation p-value (timing skill vs random alignment)
Plus, across the whole set: Probability of Backtest Overfitting (CSCV).

Universe: SPY,QQQ,TLT,GLD,XLE,XLU,EWA + 8 SPDR sectors. The joint window is
GLD-bound (2004-11 onward, ~21y) and contains the GFC, COVID, and 2022.

Usage:
    python backtesting/run_validation.py
    python backtesting/run_validation.py --n-sims 2000 --n-perms 500
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.engine import compute_weighted_returns
from backtesting.portfolio_strategies import PORTFOLIO_STRATEGIES
from backtesting.run_backtests import load_price_matrix
from backtesting.validation import (
    bootstrap_metrics,
    cagr,
    deflated_sharpe_ratio,
    max_drawdown,
    permutation_test_timing,
    probability_of_backtest_overfitting,
    sharpe_ratio,
    stationary_bootstrap_indices,
)

UNIVERSE = ["SPY", "QQQ", "TLT", "GLD", "XLE", "XLU", "EWA",
            "XLB", "XLF", "XLI", "XLK", "XLP", "XLV", "XLY"]
BASELINES = {"buy_hold_spy", "buy_hold_qqq", "equal_weight_buy_hold",
             "spy_tlt_60_40", "permanent_portfolio", "all_weather_lite"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-sims", type=int, default=1000)
    parser.add_argument("--n-perms", type=int, default=300)
    parser.add_argument("--output-dir", default="backtesting/results_validation")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    prices = load_price_matrix(UNIVERSE)
    asset_returns = prices.pct_change().fillna(0.0)
    n_days = len(prices)
    years = n_days / 252
    print(f"Universe: {len(UNIVERSE)} assets | {prices.index[0].date()} to "
          f"{prices.index[-1].date()} ({years:.1f}y, {n_days} days)")
    print(f"Strategies: {len(PORTFOLIO_STRATEGIES)} | bootstrap {args.n_sims} "
          f"sims | permutation {args.n_perms} shifts\n")

    # Shared bootstrap paths (common random numbers across strategies)
    rng = np.random.default_rng(args.seed)
    boot_indices = stationary_bootstrap_indices(n_days, args.n_sims, 21, rng)

    rows = []
    weights_by_strategy = {}
    returns_matrix = {}
    for name, fn in sorted(PORTFOLIO_STRATEGIES.items()):
        t0 = time.time()
        weights = fn(prices)
        if weights.abs().sum().sum() == 0:
            print(f"  {name}: produces no positions on this universe - skipped")
            continue
        returns = compute_weighted_returns(prices, weights, 0.0)
        weights_by_strategy[name] = weights
        returns_matrix[name] = returns

        boot = bootstrap_metrics(returns, indices=boot_indices)
        perm = permutation_test_timing(asset_returns, weights,
                                       n_perms=args.n_perms, seed=args.seed)
        rows.append({
            "strategy": name,
            "is_baseline": name in BASELINES,
            "cagr": cagr(returns),
            "sharpe": sharpe_ratio(returns),
            "max_dd": max_drawdown(returns),
            "trades_per_year": float(
                (weights.diff().abs().sum(axis=1) > 1e-9).sum() / years),
            "sharpe_ci90_low": boot["sharpe"]["p5"],
            "sharpe_ci90_high": boot["sharpe"]["p95"],
            "max_dd_p5": boot["max_dd"]["p5"],
            "prob_negative_cagr": boot["prob_negative_cagr"],
            "perm_p_value": perm["p_value"],
        })
        print(f"  {name}: sharpe {rows[-1]['sharpe']:.2f} "
              f"[{boot['sharpe']['p5']:.2f}, {boot['sharpe']['p95']:.2f}] "
              f"perm_p={perm['p_value']:.3f} ({time.time()-t0:.1f}s)")

    # Deflated Sharpe: trials = per-period sharpes of everything tested
    trial_sharpes = [sharpe_ratio(r, annualize=False)
                     for r in returns_matrix.values()]
    for row in rows:
        row["deflated_sharpe_prob"] = deflated_sharpe_ratio(
            returns_matrix[row["strategy"]], trial_sharpes)

    # PBO across the non-baseline strategy set
    active = pd.DataFrame({k: v for k, v in returns_matrix.items()
                           if k not in BASELINES})
    pbo = probability_of_backtest_overfitting(active)

    scoreboard = pd.DataFrame(rows).sort_values("sharpe", ascending=False)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scoreboard.round(4).to_csv(out_dir / "scoreboard_v2.csv", index=False)
    with open(out_dir / "summary.json", "w") as f:
        json.dump({
            "universe": UNIVERSE,
            "window": [str(prices.index[0].date()), str(prices.index[-1].date())],
            "n_strategies": len(rows),
            "pbo": pbo,
            "scoreboard": scoreboard.round(4).to_dict(orient="records"),
        }, f, indent=2)

    print(f"\nPBO across {active.shape[1]} non-baseline strategies: "
          f"{pbo['pbo']:.2f} ({pbo['n_combinations']} combinations)")
    print(f"\nTop 12 by Sharpe (with validation):")
    cols = ["strategy", "cagr", "sharpe", "sharpe_ci90_low", "max_dd",
            "deflated_sharpe_prob", "perm_p_value", "prob_negative_cagr"]
    print(scoreboard[cols].head(12).round(3).to_string(index=False))
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
