#!/usr/bin/env python3
"""H7: does modelling contributions change the strategy ranking?

Every backtest in this repo is lump-sum. Both mandates contribute ~80k
CAD/yr. For the son, ~73% of the capital that will ever be invested
arrives AFTER t0, which changes what a drawdown is: a discount on the
majority of the money rather than a loss on all of it.

The mechanism that should hurt overlays: a trend overlay sits in cash
during exactly the months when contributions would buy cheapest. Under
lump-sum accounting that is pure benefit (missed drawdown). Under
contribution accounting it also carries a cost (missed cheap shares).

Everything is in CAD, because that is what these people spend, and
finding 21 shows unhedged USD exposure is a material part of the CAD
return.

Strategies compared, deliberately few and all already in the registry:
  buy_hold          - the benchmark from MANIFESTO.md
  sma200            - monthly 200-day trend overlay, cash when below
  sma200_bands      - same with +/-5% hysteresis (the "reddit" variant)

Writes data/contribution_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path("data/historical_long")
OUT = Path("data/contribution_study.json")

# Long enough to contain dot-com, GFC, COVID and 2022.
START, END = "1995-01-31", "2026-03-31"
WARMUP_DAYS = 300      # signal must be live from the first test day
ANNUAL_CONTRIB = 80_000
INITIAL = 800_000
CASH_YIELD = 0.02      # conservative flat short-rate assumption


def load(ticker):
    payload = json.loads((DATA / f"{ticker}.json").read_text())
    s = pd.Series({p["date"]: p["close"] for p in payload["prices"]},
                  dtype=float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def cad_series():
    """SPY expressed in CAD - what a Canadian actually experiences."""
    spy, fx = load("SPY"), load("CAD=X")
    df = pd.concat([spy.rename("spy"), fx.rename("usdcad")], axis=1,
                   sort=True).dropna()
    return (df["spy"] * df["usdcad"]).rename("SPY_CAD")


def signals(prices):
    """Monthly in/out signals with the warmup live before the test window."""
    sma = prices.rolling(200).mean()
    month_end = prices.resample("ME").last().index

    plain, banded = {}, {}
    state = True                       # hysteresis needs a starting state
    for date in month_end:
        px = prices.asof(date)
        ma = sma.asof(date)
        if pd.isna(px) or pd.isna(ma):
            plain[date], banded[date] = np.nan, np.nan
            continue
        plain[date] = px > ma
        # +/-5% bands: only flip once price clears the far side.
        if state and px < ma * 0.95:
            state = False
        elif (not state) and px > ma * 1.05:
            state = True
        banded[date] = state
    return pd.Series(plain), pd.Series(banded)


def simulate(returns, in_market, contrib_per_year):
    """Wealth path with monthly contributions.

    Contributions arrive at the START of each month and are invested
    according to that month's signal, which is what actually happens:
    you deposit and the rule tells you where it goes.
    """
    monthly_contrib = contrib_per_year / 12.0
    cash_monthly = (1 + CASH_YIELD) ** (1 / 12) - 1

    wealth = INITIAL
    path = {}
    for date, ret in returns.items():
        wealth += monthly_contrib
        invested = bool(in_market.get(date, True))
        wealth *= (1 + (ret if invested else cash_monthly))
        path[date] = wealth
    return pd.Series(path)


def stats(path, contributed, label):
    curve = path / path.cummax()
    total_in = INITIAL + contributed
    years = len(path) / 12.0
    return {
        "strategy": label,
        "terminal_cad": float(path.iloc[-1]),
        "total_contributed_cad": float(total_in),
        "multiple_on_money_in": float(path.iloc[-1] / total_in),
        "max_drawdown_pct": float((curve.min() - 1) * 100),
        "years": years,
    }


def main():
    prices = cad_series()
    warm_start = pd.Timestamp(START) - pd.Timedelta(days=WARMUP_DAYS)
    prices = prices.loc[warm_start:END]

    plain, banded = signals(prices)

    monthly = prices.resample("ME").last()
    returns = monthly.pct_change().dropna()
    returns = returns.loc[START:END]

    # CAUSALITY: returns[T] is the return from T-1 to T, so it must be
    # governed by the signal observed at T-1. Aligning signal[T] with
    # returns[T] lets the rule see the month it is trading - which
    # produced +271% over buy-hold at -8% maxDD across 2008, a number
    # impossible for a monthly trend rule and the giveaway that this was
    # wrong.
    always = pd.Series(True, index=returns.index)
    strategies = {
        "buy_hold": always,
        "sma200": plain.shift(1).reindex(returns.index).ffill().fillna(True),
        "sma200_bands": banded.shift(1).reindex(returns.index).ffill()
                              .fillna(True),
    }

    results = {"window": {"start": str(returns.index.min().date()),
                          "end": str(returns.index.max().date())},
               "lump_sum": [], "with_contributions": []}

    for label, sig in strategies.items():
        lump = simulate(returns, sig, 0)
        contrib = simulate(returns, sig, ANNUAL_CONTRIB)
        results["lump_sum"].append(stats(lump, 0, label))
        results["with_contributions"].append(
            stats(contrib, ANNUAL_CONTRIB * len(returns) / 12.0, label))

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"SPY in CAD, {results['window']['start']} -> "
          f"{results['window']['end']}, signal live from day one")
    print(f"initial {INITIAL:,}   contributions {ANNUAL_CONTRIB:,}/yr\n")

    for mode in ("lump_sum", "with_contributions"):
        print(f"--- {mode.replace('_', ' ').upper()} ---")
        print(f"{'strategy':16}{'terminal':>16}{'x money in':>13}"
              f"{'maxDD':>10}")
        base = None
        for row in results[mode]:
            if base is None:
                base = row["terminal_cad"]
            print(f"{row['strategy']:16}{row['terminal_cad']:>15,.0f}"
                  f"{row['multiple_on_money_in']:>12.2f}x"
                  f"{row['max_drawdown_pct']:>9.1f}%")
        print()

    # The question H7 exists to answer.
    print("overlay cost vs buy_hold, by accounting method:")
    for mode in ("lump_sum", "with_contributions"):
        rows = {r["strategy"]: r["terminal_cad"] for r in results[mode]}
        for name in ("sma200", "sma200_bands"):
            gap = (rows[name] / rows["buy_hold"] - 1) * 100
            print(f"  {mode:20} {name:14} {gap:+7.1f}%")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
