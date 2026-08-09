#!/usr/bin/env python3
"""Every strategy across every window, so nobody can cherry-pick one.

WHY THIS EXISTS
---------------
A trend overlay is crash insurance. It therefore wins any window
containing a crash and loses any window without one, MECHANICALLY -
before any question of skill. So a single-window result says more about
the window than the strategy, and finding 26 nearly drew the wrong
conclusion from real LETF data that happens to begin in 2010.

The fix is to stop quoting single windows. This prints a matrix:
strategies down, windows across. If a strategy only wins where crashes
live, that is now visible in the table rather than buried in prose.

Leverage uses the EMPIRICALLY CALIBRATED drag from finding 26 (~5%/yr on
3x, ~2.85% on 2x), not the 1.25% guess that inflated finding 24.

Writes data/regime_sweep.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backtesting.periods import MULTI_REGIME_WINDOWS  # noqa: E402
from tools.backtest_check_frequency import build_signal, load  # noqa: E402

OUT = REPO / "data" / "regime_sweep.json"

# Measured in finding 26 against real UPRO/TQQQ/SSO, not assumed.
DRAG_BY_LEVERAGE = {1: 0.0009, 2: 0.0285, 3: 0.0501}
CASH_ANNUAL = 0.02
WARMUP_DAYS = 400
BAND = 0.05


def levered(underlying_ret, leverage):
    drag = (1 + DRAG_BY_LEVERAGE[leverage]) ** (1 / 252) - 1
    return underlying_ret * leverage - drag


def run(returns, active):
    cash = (1 + CASH_ANNUAL) ** (1 / 252) - 1
    r = pd.Series(np.where(active.reindex(returns.index).ffill().fillna(True),
                           returns, cash), index=returns.index)
    curve = (1 + r).cumprod()
    years = len(r) / 252
    if years <= 0 or curve.iloc[-1] <= 0:
        return None
    return {
        "terminal_x": float(curve.iloc[-1]),
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "years": float(years),
    }


def main():
    prices_full = load("SPY")
    underlying_full = prices_full.pct_change().dropna()

    strategies = {}
    for lev in (1, 2, 3):
        strategies[f"{lev}x_buyhold"] = (lev, None)
        strategies[f"{lev}x_daily_band5"] = (lev, BAND)

    results = {}
    for window, (start, end, why) in MULTI_REGIME_WINDOWS.items():
        # Warmup sits BEFORE the window so the signal is live on day one.
        warm = pd.Timestamp(start) - pd.Timedelta(days=WARMUP_DAYS)
        px = prices_full.loc[warm:end]
        if len(px) < 300:
            continue
        rows = {}
        for label, (lev, band) in strategies.items():
            ret = levered(underlying_full, lev).loc[start:end]
            if len(ret) < 60:
                continue
            if band is None:
                active = pd.Series(True, index=ret.index)
            else:
                active = build_signal(px, "daily", band)
            got = run(ret, active)
            if got:
                rows[label] = got
        results[window] = {"start": start, "end": end, "why": why,
                           "strategies": rows}

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    labels = list(strategies)
    print("CAGR % by window (SPY underlying, drag calibrated to real "
          "funds)\n")
    header = f"{'window':18}{'yrs':>5}" + "".join(f"{l:>17}" for l in labels)
    print(header)
    print("-" * len(header))
    for window, block in results.items():
        rows = block["strategies"]
        if not rows:
            continue
        yrs = next(iter(rows.values()))["years"]
        line = f"{window:18}{yrs:>5.1f}"
        for label in labels:
            r = rows.get(label)
            line += f"{r['cagr_pct']:>16.1f}%" if r else f"{'-':>17}"
        print(line)

    print("\nmax drawdown % by window\n")
    print(header)
    print("-" * len(header))
    for window, block in results.items():
        rows = block["strategies"]
        if not rows:
            continue
        yrs = next(iter(rows.values()))["years"]
        line = f"{window:18}{yrs:>5.1f}"
        for label in labels:
            r = rows.get(label)
            line += f"{r['max_dd_pct']:>16.1f}%" if r else f"{'-':>17}"
        print(line)

    print("\noverlay vs buy-hold at the same leverage (CAGR difference, pp)\n")
    print(f"{'window':18}{'1x':>10}{'2x':>10}{'3x':>10}   verdict")
    for window, block in results.items():
        rows = block["strategies"]
        if not rows:
            continue
        line = f"{window:18}"
        wins = 0
        for lev in (1, 2, 3):
            bh = rows.get(f"{lev}x_buyhold")
            ov = rows.get(f"{lev}x_daily_band5")
            if bh and ov:
                gap = ov["cagr_pct"] - bh["cagr_pct"]
                wins += gap > 0
                line += f"{gap:>+9.1f}pp"
            else:
                line += f"{'-':>10}"
        line += f"   overlay wins {wins}/3"
        print(line)

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
