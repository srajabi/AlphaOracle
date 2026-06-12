#!/usr/bin/env python3
"""Parameter-region stability (Peterson's curve-fitting test) for the
parameterized strategies among the lab winners.

A strategy whose Sharpe collapses one parameter step away is curve-fit;
a plateau (score near 1.0) means the result is a property of the idea,
not of the number. Run after any new parameterized strategy is added.
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.portfolio_strategies import _empty_weights, _monthly
from backtesting.run_backtests import load_price_matrix
from backtesting.validation import parameter_stability

OUT = Path("backtesting/results_validation/parameter_stability.json")


def sma_monthly_factory(prices):
    def make(window):
        weights = _empty_weights(prices)
        sma = prices["SPY"].rolling(window).mean()
        weights["SPY"] = ((prices["SPY"] > sma) & sma.notna()).astype(float)
        return _monthly(weights)
    return make


def vol_target_factory(prices):
    def make(target):
        weights = _empty_weights(prices)
        vol = prices["SPY"].pct_change().rolling(20).std() * (252 ** 0.5)
        weights["SPY"] = (target / vol).clip(0.0, 1.5).fillna(0.0)
        return weights
    return make


def changepoint_factory(prices):
    def make(multiplier):
        weights = _empty_weights(prices)
        spy = prices["SPY"]
        sma200 = spy.rolling(200).mean()
        trend = ((spy > sma200) & sma200.notna()).astype(float)
        vol_fast = spy.pct_change().rolling(20).std()
        vol_slow = vol_fast.rolling(100).median()
        cp = (vol_fast > multiplier * vol_slow).fillna(False)
        weights["SPY"] = trend.where(~cp, trend * 0.5)
        return weights
    return make


def main():
    prices = load_price_matrix(["SPY"])
    sweeps = {
        "sma200_monthly_spy(window)": (
            sma_monthly_factory(prices), [150, 175, 200, 225, 250]),
        "vol_target_spy(target)": (
            vol_target_factory(prices), [0.10, 0.125, 0.15, 0.175, 0.20]),
        "changepoint_gated(vol multiplier)": (
            changepoint_factory(prices), [1.5, 1.75, 2.0, 2.25, 2.5]),
    }

    results = {}
    for label, (factory, values) in sweeps.items():
        out = parameter_stability(factory, prices, values)
        results[label] = out
        line = "  ".join(f"{p}: {s:.2f}" for p, s in out["sharpe_by_param"].items())
        print(f"{label}\n  {line}\n  plateau_score = {out['plateau_score']:.2f}\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({k: {"sharpe_by_param": {str(p): round(s, 4) for p, s in
                                           v["sharpe_by_param"].items()},
                       "plateau_score": round(v["plateau_score"], 4)}
                   for k, v in results.items()}, f, indent=2)
    print(f"Saved to {OUT}")


if __name__ == "__main__":
    main()
