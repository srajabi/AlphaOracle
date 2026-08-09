#!/usr/bin/env python3
"""H11: does a Markov-switching regime model beat a trend gate?

The claim heard constantly - that people identify bull/bear regimes and
adjust within them - deserves a test rather than an argument. This is
the canonical academic version: Hamilton-style Markov switching on
returns, two states, fitted by EM.

THE DISTINCTION THAT DECIDES IT
-------------------------------
Regime DETECTION (nowcasting the current state) is achievable. Regime
PREDICTION (forecasting the transition) is what fails. The two get
conflated constantly.

And the trend gate is ITSELF a regime detector - price above its 200-day
average is a bull-state classification expressed directly as a position.
So this is not "regime model vs no regime model". It is a sophisticated
detector against a crude one.

THE TRAP THIS AVOIDS
--------------------
Fitting the model on all history and reading off the smoothed regime
probabilities is how this analysis is usually done, and it is
lookahead: the smoothed probability at time t uses data from t+1
onward. It produces a beautiful chart and an untradeable strategy.

Here the model is refit on an EXPANDING WINDOW and only the FILTERED
probability at the last observed point is used - what a real observer
could have known that day. Both variants are reported so the size of the
lookahead is visible.

Writes data/markov_regime_study.json.
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

warnings.filterwarnings("ignore")

OUT = REPO / "data" / "markov_regime_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

REFIT_EVERY = 12       # months between refits (EM is expensive)
MIN_TRAIN_MONTHS = 240  # 20y before the first out-of-sample decision
EXPENSE = 0.0095


def load_monthly():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    monthly = pd.DataFrame({
        "ret": (1 + df["market_return"]).resample("ME").prod() - 1,
        "rf": (1 + df["rf"]).resample("ME").prod() - 1,
    })
    monthly["level"] = (1 + monthly["ret"]).cumprod()
    return monthly.dropna()


def fit_markov(returns):
    from statsmodels.tsa.regime_switching.markov_regression import (
        MarkovRegression)
    model = MarkovRegression(returns.values * 100, k_regimes=2,
                             trend="c", switching_variance=True)
    return model.fit(disp=False)


def bull_state(res):
    """Index of the higher-mean regime.

    params comes back as a bare array (we fit on .values), so locate the
    per-regime constants by name rather than assuming an ordering.
    """
    names = list(res.model.param_names)
    means = []
    for i in range(2):
        idx = next((j for j, n in enumerate(names)
                    if n.startswith("const") and str(i) in n), None)
        means.append(res.params[idx] if idx is not None else 0.0)
    return int(np.argmax(means))


def in_sample_smoothed(monthly):
    """The WRONG way, included to measure the lookahead."""
    res = fit_markov(monthly["ret"])
    bull = bull_state(res)
    smoothed = np.asarray(res.smoothed_marginal_probabilities)
    if smoothed.ndim == 2 and smoothed.shape[0] != len(monthly):
        smoothed = smoothed.T
    prob = pd.Series(smoothed[:, bull], index=monthly.index)
    return (prob > 0.5).shift(1).fillna(True)


def walk_forward_filtered(monthly):
    """Honest: expanding window, filtered probability, decision lagged."""
    decisions = {}
    dates = list(monthly.index)
    res, bull = None, 0
    for i, dt in enumerate(dates):
        if i < MIN_TRAIN_MONTHS:
            decisions[dt] = True
            continue
        if (i - MIN_TRAIN_MONTHS) % REFIT_EVERY == 0 or res is None:
            try:
                res = fit_markov(monthly["ret"].iloc[:i])
                bull = bull_state(res)
            except Exception:
                pass
        if res is None:
            decisions[dt] = True
            continue
        try:
            filt = np.asarray(res.filtered_marginal_probabilities)
            if filt.ndim == 2 and filt.shape[1] != 2:
                filt = filt.T
            decisions[dt] = bool(filt[-1, bull] > 0.5)
        except Exception:
            decisions[dt] = True
    # Decision made at the close of month t governs month t+1.
    return pd.Series(decisions).shift(1).fillna(True)


def trend_gate(level, band=0.05):
    sma = level.rolling(10).mean()      # ~200 trading days at monthly
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


def simulate(monthly, active, leverage=1.0, start=None):
    m = monthly if start is None else monthly.loc[start:]
    a = active.reindex(m.index).ffill().fillna(True)
    borrowed = max(leverage - 1, 0)
    lev_ret = m["ret"] * leverage - borrowed * m["rf"]
    if leverage > 1:
        lev_ret = lev_ret - EXPENSE / 12
    r = pd.Series(np.where(a, lev_ret, m["rf"]), index=m.index)
    curve = (1 + r).cumprod()
    years = len(r) / 12
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "pct_invested": float(a.mean() * 100),
        "switches_per_year": float((a != a.shift(1)).sum() / years),
    }


def main():
    monthly = load_monthly()
    print(f"French monthly total return, {monthly.index.min():%Y-%m} -> "
          f"{monthly.index.max():%Y-%m} ({len(monthly)} months)\n")

    gate = trend_gate(monthly["level"])
    print("fitting Markov switching (in-sample, smoothed)...")
    smoothed = in_sample_smoothed(monthly)
    print("fitting Markov switching (walk-forward, filtered)... slow")
    filtered = walk_forward_filtered(monthly)

    start = monthly.index[MIN_TRAIN_MONTHS]
    variants = {
        "buy_hold": pd.Series(True, index=monthly.index),
        "trend_gate": gate,
        "markov_smoothed_LOOKAHEAD": smoothed,
        "markov_walkforward": filtered,
    }

    results = {}
    for lev in (1.0, 2.0):
        for name, active in variants.items():
            results[f"{name}_{lev:.0f}x"] = simulate(monthly, active, lev,
                                                     start)

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\nout-of-sample window {start:%Y-%m} onward "
          f"(first {MIN_TRAIN_MONTHS//12}y reserved for training)\n")
    print(f"{'variant':34}{'CAGR':>8}{'maxDD':>9}{'%in':>7}{'switch/yr':>11}")
    print("-" * 69)
    for name, r in results.items():
        print(f"{name:34}{r['cagr_pct']:>7.2f}%{r['max_dd_pct']:>8.1f}%"
              f"{r['pct_invested']:>6.0f}%{r['switches_per_year']:>10.2f}")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
