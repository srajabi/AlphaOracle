#!/usr/bin/env python3
"""Rule slate v2 - fixes the defects in v1.

v1 (tools/backtest_rule_slate.py) concluded that nothing beats SMA200
with 5% bands. That conclusion may still hold, but v1 could not support
it. The defects, and what v2 does instead:

  DEFECT 1  Unequal average exposure. Rules were invested different
            fractions of the time (0.59x to 0.74x), so comparing raw
            CAGR compared RISK LEVELS, not rules. This is the exact
            error called out in finding 32.
      FIX   Scale each rule's leverage so every variant carries the same
            average exposure, then compare.

  DEFECT 2  One number per rule. Finding 27's own rule is never to quote
            a single window, and v1's docstring claimed multi-window
            reporting that the code did not do.
      FIX   Report across every MULTI_REGIME_WINDOW.

  DEFECT 3  The baseline had been tuned on this data (finding 24 swept
            the band and found 2-6% works) while challengers each got
            one arbitrary parameter. That is a rigged fight.
      FIX   Sweep every rule over a small grid and report the MEDIAN of
            its grid, not its best. Best-of-grid is what overfitting
            looks like; median is what a naive user would get.

  DEFECT 4  No confidence interval on the differences.
      FIX   Stationary block bootstrap on returns, 500 resamples, to
            report whether gaps are distinguishable from noise.

Remaining and NOT fixed here, recorded honestly: single asset (US), no
transaction or tax cost, and the 200-day window is itself folklore
fitted to this same history so nothing here is truly out-of-sample.

Writes data/rule_slate_v2.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backtesting.periods import MULTI_REGIME_WINDOWS  # noqa: E402
from tools.backtest_rule_slate import (  # noqa: E402
    load, rule_abs_momentum, rule_drawdown, rule_sma_band,
    rule_sma_ensemble, rule_sma_volband,
)

OUT = REPO / "data" / "rule_slate_v2.json"
EXPENSE = 0.0095
TARGET_EXPOSURE = 1.0     # every rule normalised to this average
N_BOOT = 500
BLOCK = 63                # ~quarter, preserves autocorrelation
RNG = np.random.default_rng(20260809)

# Small grid per rule so none is judged on a single lucky parameter.
GRIDS = {
    "sma200_band5": [lambda lv, r, b=b: rule_sma_band(lv, 200, b)
                     for b in (0.02, 0.03, 0.05, 0.07)],
    "sma_window": [lambda lv, r, w=w: rule_sma_band(lv, w, 0.05)
                   for w in (100, 150, 200, 250)],
    "sma_volband": [lambda lv, r, k=k: rule_sma_volband(lv, r, 200, k)
                    for k in (1.0, 1.5, 2.0, 2.5)],
    "sma_ensemble": [lambda lv, r, b=b: rule_sma_ensemble(
        lv, (50, 100, 200), b) for b in (0.02, 0.03, 0.05, 0.07)],
    "abs_momentum": [lambda lv, r, m=m: rule_abs_momentum(lv, m)
                     for m in (6, 9, 12, 15)],
    "drawdown": [lambda lv, r, d=d: rule_drawdown(lv, d, d / 3)
                 for d in (0.10, 0.15, 0.20, 0.25)],
}


def normalise(exposure, target=TARGET_EXPOSURE):
    """Scale so average exposure matches across rules."""
    mean = exposure.mean()
    return exposure * (target / mean) if mean > 0 else exposure


def perf(market, rf, exposure, cap=3.0):
    lev = exposure.reindex(market.index).ffill().fillna(1.0).clip(0, cap)
    borrowed = (lev - 1).clip(lower=0)
    ret = market * lev - borrowed * rf - EXPENSE / 252 * (lev > 1)
    ret = ret + rf * (1 - lev).clip(lower=0)
    return ret


def summarise(ret):
    curve = (1 + ret).cumprod()
    years = len(ret) / 252
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
    }


def block_bootstrap_cagr(ret, n=N_BOOT, block=BLOCK):
    vals = ret.values
    n_obs = len(vals)
    n_blocks = int(np.ceil(n_obs / block))
    out = []
    for _ in range(n):
        starts = RNG.integers(0, n_obs - block, size=n_blocks)
        sample = np.concatenate([vals[s:s + block] for s in starts])[:n_obs]
        growth = np.prod(1 + sample)
        if growth > 0:
            out.append(growth ** (252 / n_obs) - 1)
    return np.percentile(out, [5, 50, 95]) * 100 if out else [np.nan] * 3


def main():
    df = load()
    market, rf, level = df["market_return"], df["rf"], df["index_level"]

    print("building rule grids (median of grid, not best of grid)\n")
    exposures = {"buy_hold": pd.Series(1.0, index=level.index)}
    for name, grid in GRIDS.items():
        variants = [normalise(fn(level, market)) for fn in grid]
        # Median exposure across the grid at each date = the typical
        # member, rather than the luckiest.
        exposures[name] = pd.concat(variants, axis=1).median(axis=1)

    results = {"full_sample": {}, "windows": {}, "bootstrap": {}}

    for name, exposure in exposures.items():
        ret = perf(market, rf, exposure)
        results["full_sample"][name] = summarise(ret)
        results["full_sample"][name]["avg_exposure"] = float(
            exposure.reindex(market.index).ffill().fillna(1.0).mean())
        lo, mid, hi = block_bootstrap_cagr(ret)
        results["bootstrap"][name] = {"p5": float(lo), "p50": float(mid),
                                      "p95": float(hi)}

    for window, (start, end, _why) in MULTI_REGIME_WINDOWS.items():
        rows = {}
        for name, exposure in exposures.items():
            seg = perf(market, rf, exposure).loc[start:end]
            if len(seg) > 250:
                rows[name] = summarise(seg)
        if rows:
            results["windows"][window] = rows

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"ALL RULES NORMALISED TO {TARGET_EXPOSURE:.2f}x AVERAGE EXPOSURE")
    print(f"{'rule':18}{'CAGR':>8}{'maxDD':>9}{'avg exp':>9}"
          f"{'bootstrap 5-95%':>22}")
    print("-" * 66)
    for name, r in results["full_sample"].items():
        b = results["bootstrap"][name]
        print(f"{name:18}{r['cagr_pct']:>7.2f}%{r['max_dd_pct']:>8.1f}%"
              f"{r['avg_exposure']:>8.2f}x"
              f"{b['p5']:>12.2f}%-{b['p95']:.2f}%")

    print("\nCAGR by window (finding 27: never quote one window)\n")
    names = list(exposures)
    hdr = f"{'window':18}" + "".join(f"{n[:11]:>12}" for n in names)
    print(hdr)
    print("-" * len(hdr))
    for window, rows in results["windows"].items():
        line = f"{window:18}"
        for n in names:
            line += (f"{rows[n]['cagr_pct']:>11.1f}%" if n in rows
                     else f"{'-':>12}")
        print(line)

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
