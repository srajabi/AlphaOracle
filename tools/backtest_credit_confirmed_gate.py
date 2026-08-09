#!/usr/bin/env python3
"""H9 - does credit confirmation cut whipsaw? Plus the increasing ramp.

TWO QUESTIONS

1. The increasing leverage ramp (1.0/1.5/2.0/2.0) with a permanent gate.
   Finding 38's glide test found this captures 81% of flat-2x's median
   while giving the same gentle first-three-years as unlevered 1x. This
   re-runs it head to head with the alternatives so the trade is
   explicit.

2. H9 - credit confirmation. The gate's expensive failure is whipsaw:
   price dips below trend, you exit, it recovers, you re-enter, and you
   pay on both sides. 2018, 2015-16 and much of 2022. Finding 31 ranked
   this the top threat to a leveraged sleeve.

   Hypothesis: real bears carry credit stress; chop does not. In 2000
   and 2008 corporate borrowing costs blew out alongside equities; in
   the 2018 and 2015-16 selloffs they largely did not. So require BOTH
   price-below-trend AND widening credit before exiting.

   Credit measure: the Moody's Baa-Aaa spread, monthly from 1919 -
   chosen over HYG/LQD (2007+) because a century test needs a century of
   data, and this one covers 1929.

   "Widening" = the spread is above its own trailing 12-month median.
   That is a deliberately crude, parameter-light definition; a tuned
   threshold on a series with ~30 independent credit cycles would be
   fitted (finding 29).

Writes data/credit_gate_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "credit_gate_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

INITIAL = 800_000
ANNUAL_CONTRIB = 80_000
HORIZON_Y = 27
EXPENSE = 0.0095
CREDIT_LOOKBACK = 12
BOUNDS_Y = (3, 10, 20)


def load_market():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    m = pd.DataFrame({
        "ret": (1 + df["market_return"]).resample("ME").prod() - 1,
        "rf": (1 + df["rf"]).resample("ME").prod() - 1,
    }).dropna()
    m["level"] = (1 + m["ret"]).cumprod()
    return m


def load_credit():
    baa = pd.read_csv(REPO / "data" / "_BAA.csv")
    aaa = pd.read_csv(REPO / "data" / "_AAA.csv")
    for d in (baa, aaa):
        d.columns = ["date", "value"]
        d["date"] = pd.to_datetime(d["date"]) + pd.offsets.MonthEnd(0)
    spread = (baa.set_index("date")["value"]
              - aaa.set_index("date")["value"]).dropna()
    # Stressed when the spread sits above its own trailing median.
    baseline = spread.rolling(CREDIT_LOOKBACK).median()
    stressed = (spread > baseline).shift(1).fillna(False)
    return spread, stressed


def trend_gate(level, window=10, band=0.05):
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


RAMP = {"y0_3": 1.0, "y3_10": 1.5, "y10_20": 2.0, "y20_27": 2.0}


def leverage_at(month, mode):
    if mode == "flat1":
        return 1.0
    if mode == "flat2":
        return 2.0
    year = month / 12.0
    a, b, c = BOUNDS_Y
    if year < a:
        return RAMP["y0_3"]
    if year < b:
        return RAMP["y3_10"]
    if year < c:
        return RAMP["y10_20"]
    return RAMP["y20_27"]


def simulate(rets, rfs, gates, credit, lev_mode, gate_mode):
    wealth = INITIAL
    path, switches = [], 0
    prev = True
    for i in range(len(rets)):
        wealth += ANNUAL_CONTRIB / 12
        lev = leverage_at(i, lev_mode)
        if gate_mode == "none":
            active = True
        elif gate_mode == "trend":
            active = gates[i]
        else:                       # trend AND credit stress to exit
            active = gates[i] or (not credit[i])
        if active != prev:
            switches += 1
        prev = active
        if active:
            borrowed = max(lev - 1, 0)
            r = rets[i] * lev - borrowed * rfs[i]
            if lev > 1:
                r -= EXPENSE / 12
        else:
            r = rfs[i]
        wealth = max(wealth * (1 + r), 1.0)
        path.append(wealth)
    s = pd.Series(path)
    dd = s / s.cummax() - 1
    return {
        "terminal": float(s.iloc[-1]),
        "max_dd_pct": float(dd.min() * 100),
        "first3y_dd_pct": float(dd.iloc[:36].min() * 100),
        "switches": switches,
    }


POLICIES = {
    "1x_no_gate":         ("flat1", "none"),
    "1x_trend":           ("flat1", "trend"),
    "2x_trend":           ("flat2", "trend"),
    "2x_trend_credit":    ("flat2", "credit"),
    "ramp_trend":         ("ramp", "trend"),
    "ramp_trend_credit":  ("ramp", "credit"),
}


def main():
    m = load_market()
    spread, stressed = load_credit()
    joined = pd.concat([m, stressed.rename("stress")], axis=1,
                       join="inner").dropna()
    gate = trend_gate(joined["level"])

    months = HORIZON_Y * 12
    starts = range(0, len(joined) - months, 12)
    collected = {k: [] for k in POLICIES}
    for s in starts:
        rets = joined["ret"].iloc[s:s + months].values
        rfs = joined["rf"].iloc[s:s + months].values
        gates = gate.iloc[s:s + months].values
        credit = joined["stress"].iloc[s:s + months].values
        for name, (lev_mode, gate_mode) in POLICIES.items():
            collected[name].append(
                simulate(rets, rfs, gates, credit, lev_mode, gate_mode))

    results = {}
    for name, rows in collected.items():
        term = np.array([r["terminal"] for r in rows])
        results[name] = {
            "median": float(np.median(term)),
            "p10": float(np.percentile(term, 10)),
            "worst": float(term.min()),
            "median_max_dd_pct": float(np.median(
                [r["max_dd_pct"] for r in rows])),
            "worst_max_dd_pct": float(np.min([r["max_dd_pct"] for r in rows])),
            "worst_first3y_dd_pct": float(np.min(
                [r["first3y_dd_pct"] for r in rows])),
            "median_switches": float(np.median(
                [r["switches"] for r in rows])),
        }

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"{HORIZON_Y}y, {INITIAL:,} + {ANNUAL_CONTRIB:,}/yr, "
          f"{len(list(starts))} rolling starts")
    print(f"window {joined.index.min():%Y-%m} -> {joined.index.max():%Y-%m}")
    print(f"ramp = {RAMP}\n")
    print(f"{'policy':20}{'median':>13}{'p10':>13}{'worst':>13}"
          f"{'worstDD':>9}{'worst3y':>9}{'switches':>10}")
    print("-" * 88)
    for name in POLICIES:
        r = results[name]
        print(f"{name:20}{r['median']:>12,.0f}{r['p10']:>12,.0f}"
              f"{r['worst']:>12,.0f}{r['worst_max_dd_pct']:>8.1f}%"
              f"{r['worst_first3y_dd_pct']:>8.1f}%"
              f"{r['median_switches']:>9.0f}")

    print("\ncredit confirmation effect (same leverage):")
    for lev, a, b in (("2x", "2x_trend", "2x_trend_credit"),
                      ("ramp", "ramp_trend", "ramp_trend_credit")):
        ra, rb = results[a], results[b]
        print(f"  {lev:5} median {ra['median']:>12,.0f} -> {rb['median']:>12,.0f}"
              f"   worstDD {ra['worst_max_dd_pct']:6.1f}% -> "
              f"{rb['worst_max_dd_pct']:6.1f}%"
              f"   switches {ra['median_switches']:.0f} -> "
              f"{rb['median_switches']:.0f}")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
