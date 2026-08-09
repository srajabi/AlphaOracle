#!/usr/bin/env python3
"""Glide paths: does the SHAPE of leverage-over-time matter?

The user proposed a hump - de-risked years 1-3, maximum leverage 3-20,
de-risked 20-30. The intuition is "do not blow up before you have
accumulated, protect what you have built at the end, compound hard in
the middle".

The contribution math argues the opposite for the early years. At year 1
the base is ~800k with 2.2M of contributions still to come, so a
drawdown is cheap and partly self-repairing. By year 25 the base is
10-60M and contributions round to nothing, so a drawdown is permanent.
That implies MOST risk early, LEAST late - monotonically decreasing.

Against that, finding 36 showed a -75% first-three-year drawdown is the
behavioural failure mode that ends strategies, which is a real argument
for de-risking early that the wealth math cannot see.

Shapes tested (leverage multiplier by year, gate always on):

  flat_1x            1.0 throughout
  flat_2x            2.0 throughout                    (finding 37 winner)
  user_hump          1.2 / 2.0 / 2.0 / 1.2            (the proposal)
  decreasing         2.0 / 2.0 / 1.5 / 1.0            (what the math says)
  increasing         1.0 / 1.5 / 2.0 / 2.0
  decreasing_soft    1.8 / 1.8 / 1.5 / 1.2

Segments are years 0-3, 3-10, 10-20, 20-27.

Writes data/glide_path_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "glide_path_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

INITIAL = 800_000
ANNUAL_CONTRIB = 80_000
HORIZON_Y = 27
EXPENSE = 0.0095
BOUNDS_Y = (3, 10, 20)

SHAPES = {
    "flat_1x": (1.0, 1.0, 1.0, 1.0),
    "flat_2x": (2.0, 2.0, 2.0, 2.0),
    "user_hump": (1.2, 2.0, 2.0, 1.2),
    "decreasing": (2.0, 2.0, 1.5, 1.0),
    "increasing": (1.0, 1.5, 2.0, 2.0),
    "decreasing_soft": (1.8, 1.8, 1.5, 1.2),
}


def load_monthly():
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


def gate_signal(level, window=10, band=0.05):
    sma = level.rolling(window).mean()
    state, out = True, {}
    for dt in level.index:
        p, mm = level.loc[dt], sma.loc[dt]
        if pd.notna(mm):
            if state and p < mm * (1 - band):
                state = False
            elif (not state) and p > mm * (1 + band):
                state = True
        out[dt] = state
    return pd.Series(out).shift(1).fillna(True)


def leverage_at(month, shape):
    year = month / 12.0
    a, b, c = BOUNDS_Y
    if year < a:
        return shape[0]
    if year < b:
        return shape[1]
    if year < c:
        return shape[2]
    return shape[3]


def simulate(rets, rfs, gates, shape):
    wealth = INITIAL
    path = []
    for i in range(len(rets)):
        wealth += ANNUAL_CONTRIB / 12
        lev = leverage_at(i, shape)
        if gates[i]:
            borrowed = max(lev - 1, 0)
            r = rets[i] * lev - borrowed * rfs[i]
            if lev > 1:
                r -= EXPENSE / 12      # charged once, not twice
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
        "last7y_dd_pct": float(dd.iloc[-84:].min() * 100),
    }


def main():
    m = load_monthly()
    gate = gate_signal(m["level"])
    months = HORIZON_Y * 12
    starts = range(0, len(m) - months, 12)

    collected = {k: [] for k in SHAPES}
    for s in starts:
        rets = m["ret"].iloc[s:s + months].values
        rfs = m["rf"].iloc[s:s + months].values
        gates = gate.iloc[s:s + months].values
        for name, shape in SHAPES.items():
            collected[name].append(simulate(rets, rfs, gates, shape))

    results = {}
    for name, rows in collected.items():
        term = np.array([r["terminal"] for r in rows])
        results[name] = {
            "shape": SHAPES[name],
            "median": float(np.median(term)),
            "p10": float(np.percentile(term, 10)),
            "worst": float(term.min()),
            "median_max_dd_pct": float(np.median(
                [r["max_dd_pct"] for r in rows])),
            "worst_max_dd_pct": float(np.min([r["max_dd_pct"] for r in rows])),
            "worst_first3y_dd_pct": float(np.min(
                [r["first3y_dd_pct"] for r in rows])),
            "worst_last7y_dd_pct": float(np.min(
                [r["last7y_dd_pct"] for r in rows])),
        }

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"{HORIZON_Y}y, {INITIAL:,} + {ANNUAL_CONTRIB:,}/yr, "
          f"{len(list(starts))} rolling starts, gate always on")
    print("segments: y0-3 / y3-10 / y10-20 / y20-27\n")
    print(f"{'shape':18}{'leverage':22}{'median':>12}{'p10':>12}"
          f"{'worst':>12}{'worst DD':>10}{'worst 3y':>10}{'worst last7y':>14}")
    print("-" * 110)
    for name, r in results.items():
        lev = "/".join(f"{x:.1f}" for x in r["shape"])
        print(f"{name:18}{lev:22}{r['median']:>11,.0f}{r['p10']:>11,.0f}"
              f"{r['worst']:>11,.0f}{r['worst_max_dd_pct']:>9.1f}%"
              f"{r['worst_first3y_dd_pct']:>9.1f}%"
              f"{r['worst_last7y_dd_pct']:>13.1f}%")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
