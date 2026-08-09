#!/usr/bin/env python3
"""When is the trend gate worth having - early, late, or always?

The proposal: use the gate for the first 2-3 years to cushion entry,
then hold unhedged forever.

The intuition behind it is sound for a RETIREE, and probably inverted
for this mandate. With 800k deployed and ~2.2M of future contributions,
most of the capital is not yet invested, so an early crash is a discount
on the majority of the money. A crash at year 25 - 5M deployed, two
years of contributions left to average in - is the one that does damage.

That argues the gate is worth MORE later. Testing it rather than
asserting it.

Four policies, identical contributions, rolling 27-year starts across a
century:

  always_hold     never gate
  always_gate     gate throughout
  gate_early      gate for the first N years, then hold
  gate_late       hold, then gate for the LAST N years

Judged on TERMINAL WEALTH, per MANIFESTO.md, plus the worst drawdown
experienced in the first three years - the behavioural risk that makes
people abandon a strategy, which the terminal number cannot see.

Writes data/entry_phase_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "entry_phase_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

INITIAL = 800_000
ANNUAL_CONTRIB = 80_000
HORIZON_Y = 27
PHASE_Y = 3


def load_monthly():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    monthly = pd.DataFrame({
        "ret": (1 + df["market_return"]).resample("ME").prod() - 1,
        "rf": (1 + df["rf"]).resample("ME").prod() - 1,
    }).dropna()
    monthly["level"] = (1 + monthly["ret"]).cumprod()
    return monthly


def gate_signal(level, window=10, band=0.05):
    """~200 trading days at monthly resolution."""
    sma = level.rolling(window).mean()
    state, out = True, {}
    for dt in level.index:
        p, m = level.loc[dt], sma.loc[dt]
        if pd.notna(m):
            if state and p < m * (1 - band):
                state = False
            elif (not state) and p > m * (1 + band):
                state = True
        out[dt] = state
    return pd.Series(out).shift(1).fillna(True)


def simulate(rets, rfs, gates, policy):
    n = len(rets)
    phase = PHASE_Y * 12
    wealth, contributed = INITIAL, INITIAL
    path = []
    for i in range(n):
        if policy == "always_hold":
            on = False
        elif policy == "always_gate":
            on = True
        elif policy == "gate_early":
            on = i < phase
        else:                       # gate_late
            on = i >= n - phase
        wealth += ANNUAL_CONTRIB / 12
        contributed += ANNUAL_CONTRIB / 12
        invested = (not on) or gates[i]
        wealth *= (1 + (rets[i] if invested else rfs[i]))
        path.append(wealth)
    series = pd.Series(path)
    dd = (series / series.cummax() - 1)
    early = dd.iloc[:phase].min() if len(series) > phase else dd.min()
    return {
        "terminal": float(series.iloc[-1]),
        "contributed": float(contributed),
        "max_dd_pct": float(dd.min() * 100),
        "first3y_dd_pct": float(early * 100),
    }


def main():
    monthly = load_monthly()
    gate = gate_signal(monthly["level"])
    months = HORIZON_Y * 12
    policies = ["always_hold", "always_gate", "gate_early", "gate_late"]

    starts = range(0, len(monthly) - months, 12)   # yearly rolling starts
    collected = {p: [] for p in policies}
    for s in starts:
        rets = monthly["ret"].iloc[s:s + months].values
        rfs = monthly["rf"].iloc[s:s + months].values
        gates = gate.iloc[s:s + months].values
        for p in policies:
            collected[p].append(simulate(rets, rfs, gates, p))

    results = {}
    for p in policies:
        term = np.array([r["terminal"] for r in collected[p]])
        results[p] = {
            "n_windows": len(term),
            "median_terminal": float(np.median(term)),
            "p10_terminal": float(np.percentile(term, 10)),
            "p90_terminal": float(np.percentile(term, 90)),
            "worst_terminal": float(term.min()),
            "median_max_dd_pct": float(np.median(
                [r["max_dd_pct"] for r in collected[p]])),
            "median_first3y_dd_pct": float(np.median(
                [r["first3y_dd_pct"] for r in collected[p]])),
            "worst_first3y_dd_pct": float(np.min(
                [r["first3y_dd_pct"] for r in collected[p]])),
        }

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    base = results["always_hold"]["median_terminal"]
    print(f"{HORIZON_Y}y horizon, {INITIAL:,} initial + "
          f"{ANNUAL_CONTRIB:,}/yr, {results['always_hold']['n_windows']} "
          f"rolling starts 1926-2026\n")
    print(f"{'policy':14}{'median':>13}{'vs hold':>10}{'p10':>13}"
          f"{'med maxDD':>11}{'first-3y DD':>13}{'worst 3y':>11}")
    print("-" * 85)
    for p in policies:
        r = results[p]
        print(f"{p:14}{r['median_terminal']:>12,.0f}"
              f"{(r['median_terminal'] / base - 1) * 100:>+9.1f}%"
              f"{r['p10_terminal']:>12,.0f}"
              f"{r['median_max_dd_pct']:>10.1f}%"
              f"{r['median_first3y_dd_pct']:>12.1f}%"
              f"{r['worst_first3y_dd_pct']:>10.1f}%")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
