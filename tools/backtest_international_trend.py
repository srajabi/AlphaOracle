#!/usr/bin/env python3
"""The out-of-sample test: does trend following work outside the US?

This is the defect finding 34 could not fix. The 200-day convention was
fitted to US history by decades of practitioners before we ever ran it,
so every US result - however carefully bootstrapped - may be one large
in-sample selection. No amount of care on US data can detect that.

JST Macrohistory gives 18 countries of annual equity total returns,
1870-2020, 2,263 country-years. The US is the CONTAMINATED sample; the
other 17 are clean. If trend following only works in the US, it is a
well-documented coincidence.

DESIGN NOTES

Annual data forces a coarse rule: absolute momentum over the prior N
years, decided at year end, held for the next year. That is the same
FAMILY as the 200-day gate (slow-lookback trend following) and was one
of the rules tested in finding 34, where it was statistically
indistinguishable from the SMA variants. It is not the same rule, and a
null result here would be weaker evidence than a positive one.

REAL returns throughout, deflated by each country's CPI. Nominal
comparison across countries with Weimar Germany in the sample is
meaningless.

Cash leg earns the bill rate, also deflated.

Writes data/international_trend_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "international_trend_study.json"
JST = REPO / "data" / "deep_history" / "jst_macrohistory.json"
LOOKBACKS = (1, 2, 3)
MIN_YEARS = 60


def load():
    payload = json.loads(JST.read_text())
    df = pd.DataFrame(payload["observations"])
    keep = ["year", "country", "eq_tr", "bill_rate", "cpi"]
    df = df[[c for c in keep if c in df.columns]].copy()
    for c in ("year", "eq_tr", "bill_rate", "cpi"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["year", "country", "eq_tr"])


def real_returns(g):
    """Deflate nominal equity and bill returns by CPI inflation."""
    g = g.sort_values("year").copy()
    infl = g["cpi"].pct_change()
    g["eq_real"] = (1 + g["eq_tr"]) / (1 + infl) - 1
    bill = g["bill_rate"].fillna(0.0)
    g["cash_real"] = (1 + bill) / (1 + infl) - 1
    return g.dropna(subset=["eq_real"])


def stats(returns):
    r = pd.Series(returns).dropna()
    if len(r) < 10:
        return None
    curve = (1 + r).cumprod()
    years = len(r)
    if curve.iloc[-1] <= 0:
        return None
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "years": int(years),
    }


def run_country(g, lookback):
    """Absolute momentum: hold equity next year if trailing return > 0."""
    eq = g["eq_real"].reset_index(drop=True)
    cash = g["cash_real"].fillna(0.0).reset_index(drop=True)

    level = (1 + eq).cumprod()
    trailing = level / level.shift(lookback) - 1
    # Decision at end of year t governs year t+1.
    invested = (trailing > 0).shift(1).fillna(True)

    strat = pd.Series(np.where(invested, eq, cash))
    return stats(eq), stats(strat), float(invested.mean() * 100)


def main():
    df = load()
    results = {}

    for lookback in LOOKBACKS:
        rows = {}
        for country, g in df.groupby("country"):
            g = real_returns(g)
            if len(g) < MIN_YEARS:
                continue
            bh, st, pct_in = run_country(g, lookback)
            if not bh or not st:
                continue
            rows[country] = {
                "buy_hold": bh, "trend": st, "pct_invested": pct_in,
                "edge_pp": st["cagr_pct"] - bh["cagr_pct"],
                "dd_improvement_pp": st["max_dd_pct"] - bh["max_dd_pct"],
            }
        results[f"lookback_{lookback}y"] = rows

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    for lookback in LOOKBACKS:
        rows = results[f"lookback_{lookback}y"]
        print(f"\n=== {lookback}-year absolute momentum, REAL returns ===")
        print(f"{'country':14}{'yrs':>5}{'B&H CAGR':>10}{'trend':>9}"
              f"{'edge':>9}{'B&H maxDD':>11}{'trend maxDD':>13}")
        for country in sorted(rows):
            r = rows[country]
            print(f"{country:14}{r['buy_hold']['years']:>5}"
                  f"{r['buy_hold']['cagr_pct']:>9.2f}%"
                  f"{r['trend']['cagr_pct']:>8.2f}%"
                  f"{r['edge_pp']:>+8.2f}"
                  f"{r['buy_hold']['max_dd_pct']:>10.1f}%"
                  f"{r['trend']['max_dd_pct']:>12.1f}%")

        edges = {c: r["edge_pp"] for c, r in rows.items()}
        non_us = {c: e for c, e in edges.items() if c != "USA"}
        wins = sum(1 for e in non_us.values() if e > 0)
        print(f"\n  USA edge:            {edges.get('USA', float('nan')):+.2f}pp")
        print(f"  non-US countries:    {len(non_us)}")
        print(f"  trend wins in:       {wins}/{len(non_us)}")
        print(f"  median non-US edge:  {np.median(list(non_us.values())):+.2f}pp")
        print(f"  mean non-US edge:    {np.mean(list(non_us.values())):+.2f}pp")
        dd = [r["dd_improvement_pp"] for c, r in rows.items() if c != "USA"]
        print(f"  median drawdown improvement: {np.median(dd):+.1f}pp")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
