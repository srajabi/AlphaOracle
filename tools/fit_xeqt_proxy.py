#!/usr/bin/env python3
"""Fit a US-listed basket that tracks XEQT.TO, for paper/live parity.

Why this exists: the live account can hold XEQT.TO (TSX, CAD), but Alpaca
is US-only, so the paper account has to hold a proxy. This finds the
basket and, more importantly, reports how closely it actually tracks.

Two methodology points, both load-bearing:

1. MONTHLY, not daily. XEQT.TO carries 88 zero-return days over the
   window (thin early trading), which damps its measured daily vol below
   VT's and caps daily correlation near 0.92 regardless of basket - a
   daily fit puts EWC at 0%, which is an artefact. Month-end sampling
   washes the stale prints out, and month-end is the cadence the
   slow-channel rule trades at anyway.

2. FX-neutralised. XEQT.TO is CAD-denominated; the basket is USD. We
   convert XEQT to USD before fitting so this measures ALLOCATION
   tracking rather than accidentally fitting CAD/USD. The residual FX
   difference is real and is reported, not engineered away - the live
   position earns in CAD and the paper position in USD.

Usage: python tools/fit_xeqt_proxy.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

DATA = Path(__file__).resolve().parent.parent / "data" / "historical_long"
CANDIDATES = ["VT", "VTI", "VXUS", "EWC"]
COMBOS = [["VT", "EWC"], ["VTI", "VXUS", "EWC"], ["VT", "VTI", "VXUS", "EWC"]]


def series(ticker):
    d = json.loads((DATA / f"{ticker}.json").read_text())
    s = pd.Series({p["date"]: p["close"] for p in d["prices"]}, name=ticker)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def usdcad(start="2019-08-01", end="2026-07-01"):
    """CAD=X is CAD per 1 USD."""
    fx = yf.download("CAD=X", start=start, end=end, progress=False,
                     auto_adjust=True)["Close"]
    if isinstance(fx, pd.DataFrame):
        fx = fx.iloc[:, 0]
    fx.index = pd.to_datetime(fx.index).tz_localize(None)
    return fx.rename("USDCAD")


def monthly_returns():
    df = pd.concat(
        [series("XEQT.TO").rename("XEQT_CAD")]
        + [series(t) for t in CANDIDATES]
        + [usdcad()],
        axis=1, sort=True).dropna()
    df["XEQT_USD"] = df["XEQT_CAD"] / df["USDCAD"]
    monthly = df.resample("ME").last()
    return monthly, monthly[["XEQT_USD"] + CANDIDATES].pct_change().dropna()


def score(target, basket):
    diff = basket - target
    return {
        "te_pct_yr": float(np.std(diff, ddof=1) * np.sqrt(12) * 100),
        "corr": float(np.corrcoef(target, basket)[0, 1]),
        "cum_drift_pp": float((np.prod(1 + basket) - np.prod(1 + target)) * 100),
    }


def fit(X, target, tickers, all_tickers):
    cols = [all_tickers.index(t) for t in tickers]
    Xs = X[:, cols]

    def sse(w):
        return float(np.sum((Xs @ w - target) ** 2))

    res = minimize(sse, np.full(len(cols), 1 / len(cols)), method="SLSQP",
                   bounds=[(0.0, 1.0)] * len(cols),
                   constraints=[{"type": "eq",
                                 "fun": lambda w: w.sum() - 1}])
    return dict(zip(tickers, res.x)), Xs @ res.x


def main():
    monthly, rets = monthly_returns()
    target = rets["XEQT_USD"].values
    X = rets[CANDIDATES].values
    print(f"{len(rets)} monthly observations, "
          f"{rets.index.min().date()} -> {rets.index.max().date()}\n")

    print("single-ticker baselines")
    for t in CANDIDATES:
        s = score(target, rets[t].values)
        print(f"  {t + ' alone':26} TE={s['te_pct_yr']:5.2f}%/yr  "
              f"corr={s['corr']:.4f}  drift={s['cum_drift_pp']:+6.1f}pp")

    print("\nfitted baskets (long-only, weights sum to 1)")
    for combo in COMBOS:
        weights, basket = fit(X, target, combo, CANDIDATES)
        s = score(target, basket)
        print(f"  {'+'.join(combo):26} TE={s['te_pct_yr']:5.2f}%/yr  "
              f"corr={s['corr']:.4f}  drift={s['cum_drift_pp']:+6.1f}pp")
        print("      " + "  ".join(f"{k} {v * 100:.1f}%"
                                   for k, v in weights.items() if v > 0.005))

    fx_vol = float(monthly["USDCAD"].pct_change().dropna().std()
                   * np.sqrt(12) * 100)
    print(f"\nCAD/USD annualised vol {fx_vol:.2f}%/yr - the live-vs-paper "
          "gap that no basket can remove")


if __name__ == "__main__":
    main()
