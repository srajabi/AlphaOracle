#!/usr/bin/env python3
"""H10: volatility targeting - the highest-value open build.

ARCHITECTURE.md argues the system has two controls: a trend gate that
decides IN or OUT, and a volatility target that decides HOW MUCH.
Finding 4 cites vol targeting as the only leverage scheme that survived
the dot-com test, but that number predates live-warmup checking,
rate-correct financing and multi-regime reporting - the same gaps that
made finding 3's overlay claim irreproducible (finding 25).

Three questions, in order of consequence:

  1. Does vol targeting beat the trend gate at EQUAL AVERAGE LEVERAGE?
     Comparing a 3x gate against a vol target that averages 1.5x is not
     a comparison, it is a leverage difference wearing a disguise.
  2. Does gate + vol beat vol alone? Both de-risk in a crash, so they
     may be redundant. If vol alone matches, the gate should be dropped.
  3. What does it cost in TURNOVER? A continuously varying target
     rebalances constantly. Commissions are ~zero at modern retail
     brokers and spreads on liquid ETFs are 0.5-2bp, so the binding
     cost is realised capital gains in a taxable account - which scales
     with turnover, not with trade count.

Uses French daily total return from 1926 with rate-correct financing
(finding 31): levered = r*lev - (lev-1)*rf - expenses.

Writes data/vol_target_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backtesting.periods import MULTI_REGIME_WINDOWS  # noqa: E402

OUT = REPO / "data" / "vol_target_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

EXPENSE = 0.0095      # LETF expense ratio
VOL_LOOKBACK = 60     # trading days of realised vol
TARGET_VOLS = [0.10, 0.15, 0.20, 0.25, 0.30]
MAX_LEVERAGE = 3.0
DEADBANDS = [0.0, 0.10, 0.25]   # fractional change required to rebalance


def load_french():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


def trend_signal(level, band=0.05):
    sma = level.rolling(200).mean()
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


def vol_target_leverage(returns, target, deadband=0.0):
    """Leverage from realised vol, applied with a one-day lag.

    Deadband suppresses rebalancing until the target moves by more than
    `deadband` fractionally - the turnover control.
    """
    realised = returns.rolling(VOL_LOOKBACK).std() * np.sqrt(252)
    raw = (target / realised).clip(upper=MAX_LEVERAGE).shift(1)
    raw = raw.fillna(1.0)
    if deadband <= 0:
        return raw
    held, out = raw.iloc[0], []
    for value in raw:
        if held <= 0 or abs(value - held) / held > deadband:
            held = value
        out.append(held)
    return pd.Series(out, index=raw.index)


def simulate(market, rf, leverage, gate=None):
    lev = leverage.copy()
    if gate is not None:
        lev = lev.where(gate.reindex(lev.index).ffill().fillna(True), 0.0)
    lev = lev.clip(lower=0.0, upper=MAX_LEVERAGE)
    borrowed = (lev - 1).clip(lower=0)
    ret = market * lev - borrowed * rf - EXPENSE / 252 * (lev > 1)
    # Idle capital earns the risk-free rate.
    ret = ret + rf * (1 - lev).clip(lower=0)
    curve = (1 + ret).cumprod()
    years = len(ret) / 252
    turnover = float(lev.diff().abs().sum() / years)
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "terminal_x": float(curve.iloc[-1]),
        "avg_leverage": float(lev.mean()),
        "turnover_per_year": turnover,
        "years": years,
    }


def main():
    df = load_french()
    market, rf, level = df["market_return"], df["rf"], df["index_level"]
    gate = trend_signal(level)

    results = {"full_sample": {}}

    # Fixed-leverage references, gate and no-gate.
    for lev in (1.0, 2.0, 3.0):
        fixed = pd.Series(lev, index=market.index)
        results["full_sample"][f"fixed_{lev:.0f}x_buyhold"] = simulate(
            market, rf, fixed)
        results["full_sample"][f"fixed_{lev:.0f}x_gate"] = simulate(
            market, rf, fixed, gate)

    for target in TARGET_VOLS:
        lev = vol_target_leverage(market, target)
        results["full_sample"][f"voltarget_{target:.0%}"] = simulate(
            market, rf, lev)
        results["full_sample"][f"voltarget_{target:.0%}_gate"] = simulate(
            market, rf, lev, gate)

    # Turnover vs deadband at one representative target.
    results["deadband"] = {}
    for db in DEADBANDS:
        lev = vol_target_leverage(market, 0.15, db)
        results["deadband"][f"deadband_{db:.0%}"] = simulate(market, rf, lev)

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"French daily total return, {market.index.min():%Y-%m} -> "
          f"{market.index.max():%Y-%m}, rate-correct financing\n")
    print(f"{'strategy':26}{'CAGR':>8}{'maxDD':>9}{'avg lev':>9}"
          f"{'turnover/yr':>13}")
    print("-" * 65)
    for name, r in results["full_sample"].items():
        print(f"{name:26}{r['cagr_pct']:>7.2f}%{r['max_dd_pct']:>8.1f}%"
              f"{r['avg_leverage']:>8.2f}x{r['turnover_per_year']:>12.2f}x")

    print(f"\nturnover control at 15% target:")
    print(f"{'deadband':16}{'CAGR':>8}{'maxDD':>9}{'turnover/yr':>13}")
    for name, r in results["deadband"].items():
        print(f"{name:16}{r['cagr_pct']:>7.2f}%{r['max_dd_pct']:>8.1f}%"
              f"{r['turnover_per_year']:>12.2f}x")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
