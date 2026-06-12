#!/usr/bin/env python3
"""Overnight vs intraday return decomposition (Lou, Polk & Skouras 2019,
papers/tug_of_war_overnight.md).

Splits each session into overnight (prev close -> open) and intraday
(open -> close) legs and compares three holdings:
  - overnight_only: hold close->open, flat during the day
  - intraday_only: hold open->close, flat overnight
  - buy_hold: continuous (close->close)

The honest version includes a per-switch cost (half-spread paid twice a day),
which is what kills most retail implementations of this effect.

Usage:
    python backtesting/overnight_decomposition.py --tickers SPY,QQQ
    python backtesting/overnight_decomposition.py --tickers QQQ --cost-bps 1
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.run_backtests import load_history
from backtesting.validation import bootstrap_metrics, cagr, max_drawdown, sharpe_ratio


def decompose(ticker: str, cost_bps: float):
    df = load_history(ticker)
    close = df["close"].astype(float)
    open_ = df["open"].astype(float)

    overnight = (open_ / close.shift(1) - 1.0).fillna(0.0)
    intraday = (close / open_ - 1.0).fillna(0.0)
    full = close.pct_change().fillna(0.0)

    cost = cost_bps / 10000.0
    legs = {
        "overnight_only": overnight - 2 * cost,   # buy at close, sell at open
        "intraday_only": intraday - 2 * cost,     # buy at open, sell at close
        "buy_hold": full,
    }
    rows = []
    for name, r in legs.items():
        boot = bootstrap_metrics(r, n_sims=500, seed=11)
        rows.append({
            "ticker": ticker,
            "leg": name,
            "cagr": round(cagr(r), 4),
            "sharpe": round(sharpe_ratio(r), 3),
            "sharpe_ci90": [round(boot["sharpe"]["p5"], 3),
                            round(boot["sharpe"]["p95"], 3)],
            "max_dd": round(max_drawdown(r), 4),
            "cost_bps_per_leg": cost_bps,
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tickers", default="SPY,QQQ")
    parser.add_argument("--cost-bps", type=float, default=0.0,
                        help="One-way half-spread cost in bps per switch")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    results = []
    for ticker in [t.strip() for t in args.tickers.split(",") if t.strip()]:
        results.extend(decompose(ticker, args.cost_bps))

    out = pd.DataFrame(results)
    print(out.to_string(index=False))
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
