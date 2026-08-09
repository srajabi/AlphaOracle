#!/usr/bin/env python3
"""Is CAPE actionable? (TODO #25)

WHY THIS MATTERS HERE
---------------------
Finding 41c settled the band; findings 42/45 closed breadth and sector
rotation. The remaining open question blocking a GEOGRAPHY decision is
valuation: is there any evidence for over- or under-weighting a market
based on how expensive it is? CAPE is the only 150-year handle on that.

THE TRAP THIS AVOIDS
--------------------
Almost every published CAPE strategy ranks CAPE against the FULL SAMPLE
- "CAPE is in its 95th percentile historically". That is lookahead. An
investor in 1996 saw CAPE at 28 and had no way to know whether that was
the 95th percentile of a distribution ending in 2026. Ranked against
data available IN 1996 it looked different again.

So every percentile here is EXPANDING-WINDOW: at month t, CAPE is ranked
only against CAPE from the start of the sample through t. That is what
an investor could actually have computed. The full-sample version is
also reported, purely to show the size of the illusion.

Returns come from French (real total returns, 1926+). Shiller's dividend
column in our archive is corrupted (it contains the date), so Shiller is
used ONLY for the CAPE level, never for returns.

THREE QUESTIONS
1. Does CAPE predict 10-year forward returns? Reported with Newey-West
   errors (lag 120) because overlapping windows inflate naive t by ~sqrt
   of the overlap (finding 29).
2. Does a CAPE ALLOCATION RULE beat buy-hold, using honest percentiles?
3. Does CAPE add anything to the 200d/4% trend gate (finding 41c)?

Writes data/cape_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "cape_study.json"
SHILLER = REPO / "data" / "deep_history" / "shiller_monthly.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"

HORIZON_M = 120           # 10 years
MIN_HISTORY_M = 240       # 20y before the expanding percentile is usable
SMA_D, BAND = 200, 0.04


def load_cape():
    obs = json.loads(SHILLER.read_text())["observations"]
    d = pd.DataFrame(obs)
    d["date"] = pd.to_datetime(d["date"]) + pd.offsets.MonthEnd(0)
    d = d.set_index("date").sort_index()
    return pd.to_numeric(d["cape"], errors="coerce").dropna()


def load_market():
    p = json.loads(DEEP.read_text())["observations"]
    d = pd.DataFrame(p)
    d["date"] = pd.to_datetime(d["date"])
    d = d.set_index("date").sort_index()
    return d


def newey_west_t(y, x, lags):
    """OLS slope with Newey-West HAC standard error."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    S = (resid[:, None] * X).T @ (resid[:, None] * X)
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        u = (resid[:, None] * X)
        G = u[L:].T @ u[:-L]
        S += w * (G + G.T)
    XtX_inv = np.linalg.inv(X.T @ X)
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V))
    return float(beta[1]), float(beta[1] / se[1])


def daily_gate(level, band=BAND, window=SMA_D):
    sma = level.rolling(window).mean()
    lv, mv = level.values, sma.values
    out, state = np.ones(len(lv)), True
    for i in range(len(lv)):
        m = mv[i]
        if m == m:
            if state and lv[i] < m * (1 - band):
                state = False
            elif (not state) and lv[i] > m * (1 + band):
                state = True
        out[i] = 1.0 if state else 0.0
    return pd.Series(np.r_[1.0, out[:-1]], index=level.index)


def perf(r, rf, exposure):
    a = exposure.reindex(r.index).ffill().fillna(1.0).clip(0, 1)
    net = a * r + (1 - a) * rf
    c = (1 + net).cumprod()
    y = len(net) / 12
    return {"cagr_pct": float((c.iloc[-1] ** (1 / y) - 1) * 100),
            "max_dd_pct": float((c / c.cummax() - 1).min() * 100),
            "avg_exposure": float(a.mean()),
            "months": int(len(net))}


def main():
    cape = load_cape()
    mkt = load_market()
    mret = (1 + mkt["market_return"]).resample("ME").prod() - 1
    rf = (1 + mkt["rf"]).resample("ME").prod() - 1
    lvl = (1 + mkt["market_return"]).cumprod()
    gate_d = daily_gate(lvl)
    gate_m = gate_d.resample("ME").last().shift(1)   # causality: prior month

    idx = cape.index.intersection(mret.index)
    cape, mret, rf = cape.loc[idx], mret.loc[idx], rf.loc[idx]
    gate_m = gate_m.reindex(idx).ffill().fillna(1.0)
    print(f"CAPE 1881-2023 joined to French returns: {len(idx)} months "
          f"{idx.min():%Y-%m} -> {idx.max():%Y-%m}")

    # ---- Q1: does CAPE predict 10y forward returns? ---------------
    fwd = ((1 + mret).rolling(HORIZON_M).apply(np.prod, raw=True)
           .shift(-HORIZON_M)) ** (12 / HORIZON_M) - 1
    ok = cape.notna() & fwd.notna()
    x, y = 1 / cape[ok], fwd[ok]              # earnings yield is the linear form
    r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
    slope, t_nw = newey_west_t(y, x, HORIZON_M)
    t_naive = stats.linregress(x, y).slope / stats.linregress(x, y).stderr
    print(f"\nQ1  10y forward return on (1/CAPE), n={ok.sum()} overlapping months")
    print(f"    R2 {r2:.3f}   naive t {t_naive:.2f}   "
          f"Newey-West t {t_nw:.2f}  (lag {HORIZON_M})")

    # non-overlapping decades - small n, but no overlap at all
    step = fwd[ok].iloc[::HORIZON_M]
    xs = (1 / cape[ok]).iloc[::HORIZON_M]
    lr = stats.linregress(xs, step)
    print(f"    NON-OVERLAPPING decades: n={len(step)}  R2 {lr.rvalue**2:.3f}  "
          f"t {lr.slope/lr.stderr:.2f}  p {lr.pvalue:.3f}")

    print(f"\n    forward 10y CAGR by CAPE quintile (expanding-window rank):")
    exp_pct = cape.expanding(MIN_HISTORY_M).apply(
        lambda s: (s.iloc[-1] >= s).mean(), raw=False)
    q = pd.qcut(exp_pct[ok & exp_pct.notna()], 5,
                labels=["cheapest", "2", "3", "4", "priciest"])
    for lab in ["cheapest", "2", "3", "4", "priciest"]:
        sel = fwd[q[q == lab].index]
        print(f"      {lab:10} n={len(sel):4}  median {sel.median()*100:5.2f}%  "
              f"mean {sel.mean()*100:5.2f}%  worst {sel.min()*100:6.2f}%")

    # ---- Q2/Q3: is it actionable? ---------------------------------
    full_pct = cape.rank(pct=True)            # LOOKAHEAD, for contrast only
    exp_pct = exp_pct.reindex(idx)

    def cape_rule(pct, hi=0.80, lo=0.20, hi_w=0.5, lo_w=1.0):
        """Scale equity weight down when CAPE is expensively ranked."""
        w = pd.Series(np.nan, index=pct.index)
        w[pct >= hi] = hi_w
        w[pct <= lo] = lo_w
        w[(pct > lo) & (pct < hi)] = 0.75
        return w.ffill().fillna(1.0)

    book = {
        "buy_hold": pd.Series(1.0, index=idx),
        "gate_only": gate_m,
        "cape_expanding": cape_rule(exp_pct),
        "cape_FULLSAMPLE_lookahead": cape_rule(full_pct),
        "cape_expanding_x_gate": cape_rule(exp_pct) * gate_m,
    }
    results = {}
    print(f"\nQ2/Q3  allocation rules  (start {idx.min():%Y-%m})")
    print(f"{'strategy':30}{'CAGR':>9}{'maxDD':>9}{'avg expo':>10}")
    print("-" * 58)
    for name, w in book.items():
        r = perf(mret, rf, w)
        results[name] = r
        print(f"{name:30}{r['cagr_pct']:>8.2f}%{r['max_dd_pct']:>8.1f}%"
              f"{r['avg_exposure']:>9.2f}")

    payload = {"q1": {"r2": r2, "t_naive": float(t_naive), "t_newey_west": t_nw,
                      "n_overlap": int(ok.sum()), "nonoverlap_n": int(len(step)),
                      "nonoverlap_t": float(lr.slope / lr.stderr),
                      "nonoverlap_p": float(lr.pvalue)},
               "rules": results}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
