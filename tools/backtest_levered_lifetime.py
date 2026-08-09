#!/usr/bin/env python3
"""Gate + 2x for the whole portfolio, for life. Does it dominate?

Finding 36 established that for a 1x portfolio the gate earns its keep
only during the entry phase. The natural next question: what if the
ENTIRE portfolio runs 2x with a permanent gate?

This is not a small change. MANIFESTO.md calls sleeve 1 the "I will be
fine" money, and levering all of it makes the whole plan contingent on
the gate working. So the interesting number is not the median - it is
the LEFT TAIL, and specifically whether the bad outcomes still clear the
bar the money exists to clear.

73 rolling 27-year windows, 1926-2026, 800k initial + 80k/yr,
rate-correct financing (finding 31), monthly gate.

Reported: median, p10, and worst terminal wealth; median and worst
maximum drawdown; and the worst drawdown in the first three years, which
finding 36 identified as the behavioural crux.

Writes data/levered_lifetime_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "levered_lifetime_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

INITIAL = 800_000
ANNUAL_CONTRIB = 80_000
HORIZON_Y = 27
ENTRY_Y = 3
EXPENSE = 0.0095


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


POLICIES = {
    "1x_hold":            dict(lev=1.0, gate="never"),
    "1x_gate_entry":      dict(lev=1.0, gate="entry"),
    "2x_gate_always":     dict(lev=2.0, gate="always"),
    "2x_gate_entry":      dict(lev=2.0, gate="entry"),
    "2x_hold_ungated":    dict(lev=2.0, gate="never"),
    "3x_gate_always":     dict(lev=3.0, gate="always"),
}


def simulate(rets, rfs, gates, lev, gate_mode):
    entry = ENTRY_Y * 12
    wealth = INITIAL
    path = []
    for i in range(len(rets)):
        wealth += ANNUAL_CONTRIB / 12
        if gate_mode == "always":
            active = gates[i]
        elif gate_mode == "entry":
            active = gates[i] if i < entry else True
        else:
            active = True
        if active:
            borrowed = max(lev - 1, 0)
            r = rets[i] * lev - borrowed * rfs[i]
            if lev > 1:
                r -= EXPENSE / 12
        else:
            r = rfs[i]
        wealth *= (1 + r)
        wealth = max(wealth, 1.0)      # wiped out stays wiped out
        path.append(wealth)
    s = pd.Series(path)
    dd = s / s.cummax() - 1
    return {
        "terminal": float(s.iloc[-1]),
        "max_dd_pct": float(dd.min() * 100),
        "first3y_dd_pct": float(dd.iloc[:entry].min() * 100),
    }


def main():
    m = load_monthly()
    gate = gate_signal(m["level"])
    months = HORIZON_Y * 12
    starts = range(0, len(m) - months, 12)

    collected = {p: [] for p in POLICIES}
    for s in starts:
        rets = m["ret"].iloc[s:s + months].values
        rfs = m["rf"].iloc[s:s + months].values
        gates = gate.iloc[s:s + months].values
        for name, cfg in POLICIES.items():
            collected[name].append(
                simulate(rets, rfs, gates, cfg["lev"], cfg["gate"]))

    contributed = INITIAL + ANNUAL_CONTRIB * HORIZON_Y
    results = {}
    for name, rows in collected.items():
        term = np.array([r["terminal"] for r in rows])
        results[name] = {
            "n_windows": len(term),
            "median": float(np.median(term)),
            "p10": float(np.percentile(term, 10)),
            "worst": float(term.min()),
            "pct_below_contributed": float((term < contributed).mean() * 100),
            "median_max_dd_pct": float(np.median(
                [r["max_dd_pct"] for r in rows])),
            "worst_max_dd_pct": float(np.min(
                [r["max_dd_pct"] for r in rows])),
            "worst_first3y_dd_pct": float(np.min(
                [r["first3y_dd_pct"] for r in rows])),
        }

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"{HORIZON_Y}y, {INITIAL:,} + {ANNUAL_CONTRIB:,}/yr, "
          f"{len(list(starts))} rolling starts 1926-2026")
    print(f"total contributed over the horizon: {contributed:,}\n")
    print(f"{'policy':18}{'median':>13}{'p10':>13}{'worst':>13}"
          f"{'<paid in':>10}{'med DD':>9}{'worst DD':>10}{'worst 3y':>10}")
    print("-" * 96)
    for name in POLICIES:
        r = results[name]
        print(f"{name:18}{r['median']:>12,.0f}{r['p10']:>12,.0f}"
              f"{r['worst']:>12,.0f}{r['pct_below_contributed']:>9.0f}%"
              f"{r['median_max_dd_pct']:>8.1f}%{r['worst_max_dd_pct']:>9.1f}%"
              f"{r['worst_first3y_dd_pct']:>9.1f}%")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
