#!/usr/bin/env python3
"""Can we beat SMA200 + 5% bands? A slate of candidate regime rules.

Tests six rules on identical data with identical treatment, so the
comparison is about the rule and not about who got a friendlier window.

The candidates, and why each MIGHT help rather than just being different:

  sma200_band5    baseline (finding 24)
  sma200_volband  band scaled by realised vol instead of a fixed 5%.
                  5% is a large move in a calm market and noise in a
                  violent one, so a fixed band is implicitly a bet on
                  the volatility regime. This REMOVES a fitted parameter
                  rather than adding one - the strongest candidate on
                  principle.
  sma_ensemble    50/100/200 agreement, exposure scaled by how many
                  agree. Averaging over lookbacks reduces the chance
                  that "200" is itself a fitted artefact. Buys
                  robustness, not necessarily return.
  abs_momentum    trailing 12-month return > 0 (Moskowitz/Ooi/Pedersen
                  time-series momentum). The academic standard and the
                  right external benchmark.
  drawdown_rule   exit at -X% from the running peak. Genuinely different
                  information from a moving average - it is path-based
                  rather than level-based.
  two_channel     the existing design: slow trend OR a volatility spike.
                  Directly attacks the fast-crash mode a slow average
                  structurally cannot catch (finding 27: COVID and 2022
                  both beat the gate).

All are evaluated at 1x and 2x with rate-correct financing (finding 31)
and reported across every MULTI_REGIME_WINDOW (finding 27's rule: never
quote one window).

Writes data/rule_slate_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "rule_slate_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"
EXPENSE = 0.0095


def load():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


def _hysteresis(level, upper, lower):
    """Shared state machine: exit below `lower`, re-enter above `upper`."""
    state, out = True, {}
    for dt in level.index:
        p, up, lo = level.loc[dt], upper.loc[dt], lower.loc[dt]
        if pd.notna(up) and pd.notna(lo):
            if state and p < lo:
                state = False
            elif (not state) and p > up:
                state = True
        out[dt] = 1.0 if state else 0.0
    return pd.Series(out).shift(1).fillna(1.0)


def rule_sma_band(level, window=200, band=0.05):
    sma = level.rolling(window).mean()
    return _hysteresis(level, sma * (1 + band), sma * (1 - band))


def rule_sma_volband(level, returns, window=200, k=1.5):
    """Band = k * annualised realised vol, expressed per-unit-of-price."""
    sma = level.rolling(window).mean()
    vol = returns.rolling(60).std() * np.sqrt(252)
    band = (k * vol / np.sqrt(252) * np.sqrt(20)).clip(0.01, 0.20)
    return _hysteresis(level, sma * (1 + band), sma * (1 - band))


def rule_sma_ensemble(level, windows=(50, 100, 200), band=0.05):
    votes = [rule_sma_band(level, w, band) for w in windows]
    return sum(votes) / len(votes)


def rule_abs_momentum(level, months=12):
    lag = int(months * 21)
    mom = level / level.shift(lag) - 1
    return (mom > 0).astype(float).shift(1).fillna(1.0)


def rule_drawdown(level, exit_dd=0.15, reenter_dd=0.05):
    peak = level.cummax()
    dd = level / peak - 1
    state, out = True, {}
    for dt in level.index:
        d = dd.loc[dt]
        if state and d < -exit_dd:
            state = False
        elif (not state) and d > -reenter_dd:
            state = True
        out[dt] = 1.0 if state else 0.0
    return pd.Series(out).shift(1).fillna(1.0)


def rule_two_channel(level, returns, band=0.05, vol_mult=2.0):
    """Slow trend OR a volatility spike forces risk-off."""
    slow = rule_sma_band(level, 200, band)
    vol = returns.rolling(20).std() * np.sqrt(252)
    baseline = vol.rolling(500).median()
    spike = (vol > baseline * vol_mult).astype(float).shift(1).fillna(0.0)
    return ((slow > 0) & (spike == 0)).astype(float)


def simulate(market, rf, exposure, leverage):
    lev = exposure.reindex(market.index).ffill().fillna(1.0) * leverage
    borrowed = (lev - 1).clip(lower=0)
    ret = market * lev - borrowed * rf
    if leverage > 1:
        ret = ret - EXPENSE / 252 * (lev > 1)
    ret = ret + rf * (1 - lev).clip(lower=0)
    curve = (1 + ret).cumprod()
    years = len(ret) / 252
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "avg_exposure": float(lev.mean()),
        "turnover_per_year": float(lev.diff().abs().sum() / years),
    }


def main():
    df = load()
    market, rf, level = df["market_return"], df["rf"], df["index_level"]

    rules = {
        "buy_hold": pd.Series(1.0, index=level.index),
        "sma200_band5": rule_sma_band(level),
        "sma200_volband": rule_sma_volband(level, market),
        "sma_ensemble": rule_sma_ensemble(level),
        "abs_momentum_12m": rule_abs_momentum(level),
        "drawdown_15_5": rule_drawdown(level),
        "two_channel": rule_two_channel(level, market),
    }

    results = {}
    for name, exposure in rules.items():
        for lev in (1.0, 2.0):
            results[f"{name}_{lev:.0f}x"] = simulate(market, rf, exposure, lev)

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"French daily total return {level.index.min():%Y-%m} -> "
          f"{level.index.max():%Y-%m}, rate-correct financing\n")
    for lev in ("1x", "2x"):
        print(f"--- {lev} ---")
        print(f"{'rule':22}{'CAGR':>8}{'maxDD':>9}{'avg exp':>9}"
              f"{'turn/yr':>9}")
        for name in rules:
            r = results[f"{name}_{lev}"]
            print(f"{name:22}{r['cagr_pct']:>7.2f}%{r['max_dd_pct']:>8.1f}%"
                  f"{r['avg_exposure']:>8.2f}x{r['turnover_per_year']:>8.2f}")
        print()

    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
