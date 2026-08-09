#!/usr/bin/env python3
"""Band width on US data specifically - upside, not just average CAGR.

Finding 41 chose 2% on a 5-market vote. But the money is going into a
US-heavy portfolio, and the US row of that table is a near-tie: 2% at
10.65% against 4% at 10.58%, a 7bp gap across a century. A 7bp gap does
not select a parameter.

So ask the question that actually matters for a 27-year accumulation:
what is the DISTRIBUTION of outcomes per band - the upside (p90), the
downside (p10), and the drawdown you have to sit through - on the real
US path rather than on a single full-sample CAGR.

Method: 27-year windows over 1926-2026 daily, started every 12 months.
Real contributions (800k initial + 80k/yr) so the sequence-of-returns
effect is present. The gate is computed ONCE on the full series and then
sliced, so each window inherits genuine trend structure - block
bootstrapping returns would destroy exactly the autocorrelation the gate
exploits and is the wrong tool here.

Overlapping windows are NOT independent. Treat the spread as
descriptive, not as a significance test (finding 29).

Writes data/band_upside_us.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "band_upside_us.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

INITIAL = 800_000
ANNUAL_CONTRIB = 80_000
HORIZON_Y = 27
BANDS = (0.02, 0.03, 0.04, 0.05)
SMA = 200


def load():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    df["level"] = (1 + df["market_return"]).cumprod()
    return df


def gate(level, band, window=SMA):
    sma = level.rolling(window).mean()
    state, out = True, {}
    for dt in level.index:
        p, m = level.loc[dt], sma.loc[dt]
        if pd.notna(m):
            if state and p < m * (1 - band):
                state = False
            elif (not state) and p > m * (1 + band):
                state = True
        out[dt] = 1.0 if state else 0.0
    return pd.Series(out).shift(1).fillna(1.0)


def simulate(ret, rf, exposure, contrib_days):
    """Daily wealth path with contributions on the first day of each month."""
    wealth = INITIAL
    peak, maxdd = INITIAL, 0.0
    path_end = None
    a = exposure.values
    r_mkt, r_rf = ret.values, rf.values
    for i in range(len(ret)):
        if contrib_days[i]:
            wealth += ANNUAL_CONTRIB / 12
        r = r_mkt[i] if a[i] > 0 else r_rf[i]
        wealth = max(wealth * (1 + r), 1.0)
        peak = max(peak, wealth)
        maxdd = min(maxdd, wealth / peak - 1)
    path_end = wealth
    return path_end, maxdd


def main():
    df = load()
    ret, rf, level = df["market_return"], df["rf"], df["level"]

    gates = {b: gate(level, b) for b in BANDS}
    gates["buy_hold"] = pd.Series(1.0, index=level.index)

    # contribution flag: first trading day of each month
    month_id = level.index.to_period("M")
    contrib = np.r_[True, month_id[1:] != month_id[:-1]]

    days = HORIZON_Y * 252
    starts = range(SMA + 10, len(df) - days, 252)
    starts = list(starts)

    results = {}
    for name, g in gates.items():
        terms, dds = [], []
        for s in starts:
            sl = slice(s, s + days)
            t, d = simulate(ret.iloc[sl], rf.iloc[sl],
                            g.iloc[sl], contrib[sl])
            terms.append(t)
            dds.append(d * 100)
        terms = np.array(terms)
        key = name if isinstance(name, str) else f"{name:.0%}"
        results[key if isinstance(name, str) else f"band_{name:.0%}"] = {
            "p10": float(np.percentile(terms, 10)),
            "median": float(np.median(terms)),
            "p90": float(np.percentile(terms, 90)),
            "best": float(terms.max()),
            "worst": float(terms.min()),
            "median_max_dd_pct": float(np.median(dds)),
            "worst_max_dd_pct": float(np.min(dds)),
            "switches_per_year": float(
                (g != g.shift(1)).sum() / (len(g) / 252)),
        }

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"US 1926-2026, {HORIZON_Y}y windows, {len(starts)} annual starts")
    print(f"{INITIAL:,} initial + {ANNUAL_CONTRIB:,}/yr\n")
    hdr = (f"{'variant':12}{'p10':>13}{'median':>13}{'p90':>13}"
           f"{'worst':>13}{'medDD':>9}{'worstDD':>9}{'sw/yr':>7}")
    print(hdr)
    print("-" * len(hdr))
    for name, r in results.items():
        print(f"{name:12}{r['p10']:>12,.0f}{r['median']:>12,.0f}"
              f"{r['p90']:>12,.0f}{r['worst']:>12,.0f}"
              f"{r['median_max_dd_pct']:>8.1f}%{r['worst_max_dd_pct']:>8.1f}%"
              f"{r['switches_per_year']:>7.2f}")

    print("\nvs buy_hold:")
    bh = results["buy_hold"]
    for name, r in results.items():
        if name == "buy_hold":
            continue
        print(f"  {name:12} median {r['median']/bh['median']:6.3f}x   "
              f"p90 {r['p90']/bh['p90']:6.3f}x   "
              f"p10 {r['p10']/bh['p10']:6.3f}x   "
              f"worst {r['worst']/bh['worst']:6.3f}x")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
