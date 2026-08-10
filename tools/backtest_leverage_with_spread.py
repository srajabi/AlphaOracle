#!/usr/bin/env python3
"""What does finding 51's missing financing spread do to the sleeves?

Finding 51 showed the LETF simulator charges (L-1) x rf and no spread,
while real funds finance via swaps at rf PLUS roughly 0.5-1.5%/yr per
unit of borrowed exposure. Every leveraged projection in this repo
(findings 30, 36, 38) omits that.

This re-prices the sleeve decisions with the spread charged, at 0 /
50 / 100 / 150bp, so the question is answered as a RANGE rather than a
point - the spread is bounded by finding 51, not measured, because no
adj_close exists in the archive to pin the dividend yields.

The question is NOT "does the ordering change" - it cannot, since the
cost applies uniformly to every levered variant and not at all to 1x.
The question is whether 2x still clears 1x by enough to be worth the
drawdown, once financing is charged honestly.

Setup matches finding 38 so the numbers are comparable: French monthly
TOTAL returns 1926-2026, 27-year windows started every 12 months,
800k initial + 80k/yr contributions, permanent 10-month/5% gate once
levered (finding 30 - the gate must never be removed after leverage).

Writes data/leverage_spread_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "leverage_spread_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

INITIAL = 800_000
ANNUAL_CONTRIB = 80_000
HORIZON_Y = 27
EXPENSE = 0.0095          # LETF expense ratio, already in the repo's sims
SPREADS = (0.0, 0.005, 0.010, 0.015)
RAMP_BOUNDS = (3, 10, 20)
RAMP = (1.0, 1.5, 2.0, 2.0)


def load_monthly():
    d = pd.DataFrame(json.loads(DEEP.read_text())["observations"])
    d["date"] = pd.to_datetime(d["date"])
    d = d.set_index("date").sort_index()
    m = pd.DataFrame({
        "ret": (1 + d["market_return"]).resample("ME").prod() - 1,
        "rf": (1 + d["rf"]).resample("ME").prod() - 1,
    }).dropna()
    m["level"] = (1 + m["ret"]).cumprod()
    return m


def gate(level, window=10, band=0.05):
    sma = level.rolling(window).mean()
    lv, mv = level.values, sma.values
    out, state = np.ones(len(lv)), True
    for i in range(len(lv)):
        q = mv[i]
        if q == q:
            if state and lv[i] < q * (1 - band):
                state = False
            elif (not state) and lv[i] > q * (1 + band):
                state = True
        out[i] = 1.0 if state else 0.0
    return np.r_[1.0, out[:-1]]          # act on last month's state


def leverage_at(month, mode):
    if mode == "1x":
        return 1.0
    if mode == "2x":
        return 2.0
    if mode == "3x":
        return 3.0
    year = month / 12.0
    a, b, c = RAMP_BOUNDS
    if year < a:
        return RAMP[0]
    if year < b:
        return RAMP[1]
    if year < c:
        return RAMP[2]
    return RAMP[3]


def simulate(rets, rfs, gates, mode, spread, gated=True):
    wealth = INITIAL
    path = []
    for i in range(len(rets)):
        wealth += ANNUAL_CONTRIB / 12
        lev = leverage_at(i, mode)
        active = gates[i] > 0 if gated else True
        if active:
            borrowed = max(lev - 1.0, 0.0)
            # THE CORRECTION: financing is rf + spread, not rf.
            r = rets[i] * lev - borrowed * (rfs[i] + spread / 12)
            if lev > 1:
                r -= EXPENSE / 12
        else:
            r = rfs[i]
        wealth = max(wealth * (1 + r), 1.0)
        path.append(wealth)
    s = pd.Series(path)
    dd = s / s.cummax() - 1
    return float(s.iloc[-1]), float(dd.min() * 100)


POLICIES = [("1x_nogate", "1x", False), ("1x_gated", "1x", True),
            ("2x_gated", "2x", True), ("3x_gated", "3x", True),
            ("ramp_gated", "ramp", True)]


def main():
    m = load_monthly()
    g = gate(m["level"])
    months = HORIZON_Y * 12
    starts = list(range(0, len(m) - months, 12))
    print(f"{HORIZON_Y}y windows, {len(starts)} starts, "
          f"{m.index.min():%Y-%m}..{m.index.max():%Y-%m}")
    print(f"{INITIAL:,} + {ANNUAL_CONTRIB:,}/yr, expense {EXPENSE:.2%}\n")

    results = {}
    for spread in SPREADS:
        for name, mode, gated in POLICIES:
            if mode == "1x" and spread > 0:
                pass          # 1x borrows nothing; spread is a no-op
            terms, dds = [], []
            for s in starts:
                sl = slice(s, s + months)
                t, d = simulate(m["ret"].values[sl], m["rf"].values[sl],
                                g[sl], mode, spread, gated)
                terms.append(t)
                dds.append(d)
            terms = np.array(terms)
            results.setdefault(name, {})[f"{spread:.3f}"] = {
                "p10": float(np.percentile(terms, 10)),
                "median": float(np.median(terms)),
                "p90": float(np.percentile(terms, 90)),
                "worst": float(terms.min()),
                "worst_dd_pct": float(np.min(dds)),
            }

    # .0% rounds 0.005 to "0%" and collides with the zero column
    hdr = (f"{'policy':12}" + "".join(f"{f'{s * 100:.1f}bp/100':>16}"
                                      for s in SPREADS))
    hdr = (f"{'policy':12}" + "".join(f"{f'spread {s:.2%}':>16}"
                                      for s in SPREADS))
    print("MEDIAN terminal wealth")
    print(hdr)
    print("-" * len(hdr))
    for name, _, _ in POLICIES:
        row = f"{name:12}"
        for s in SPREADS:
            row += f"{results[name][f'{s:.3f}']['median']:>15,.0f} "
        print(row)

    print("\nWORST-CASE terminal wealth")
    print(hdr)
    print("-" * len(hdr))
    for name, _, _ in POLICIES:
        row = f"{name:12}"
        for s in SPREADS:
            row += f"{results[name][f'{s:.3f}']['worst']:>15,.0f} "
        print(row)

    print("\ncost of the spread, as a % of median terminal wealth:")
    for name, mode, _ in POLICIES:
        base = results[name]["0.000"]["median"]
        hi = results[name]["0.015"]["median"]
        print(f"  {name:12} 0 -> 150bp: {base:>13,.0f} -> {hi:>13,.0f}"
              f"   ({(hi/base - 1) * 100:+.1f}%)")

    print("\n2x vs 1x advantage as financing gets charged honestly:")
    for s in SPREADS:
        k = f"{s:.3f}"
        two = results["2x_gated"][k]["median"]
        one = results["1x_gated"][k]["median"]
        tw = results["2x_gated"][k]["worst"]
        ow = results["1x_gated"][k]["worst"]
        print(f"  spread {s:.2%}: median {two/one:.2f}x   worst {tw/ow:.2f}x")

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
