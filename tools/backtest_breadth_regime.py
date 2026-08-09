#!/usr/bin/env python3
"""Is BREADTH a faster regime detector than index price?

WHY THIS AND NOT ANOTHER ADAPTIVE BAND
--------------------------------------
Five detectors have now failed: Markov switching (finding 33),
volatility-scaled bands (34), credit confirmation (H9), macro/recession
indicators (19, 20) and efficiency-ratio bands (this session).

They share a defect. Every one of them consumes the index return series
or something that lags it - Markov states are fit on returns, volatility
is computed from returns, the efficiency ratio is computed from returns,
credit and macro publish after the market moves. No transform of a slow
signal yields a fast one.

Breadth is different in kind. It asks how many COMPONENTS are
individually holding up. A 3% index fall with 45 of 49 industries down
is not the same event as a 3% fall driven by two megacaps, and the index
level cannot tell them apart. That is new information, not a
rearrangement of old information.

THE QUESTION, STATED SO IT CAN FAIL
-----------------------------------
1. LEAD/LAG: on the drawdowns that matter, does breadth cross its
   threshold BEFORE price crosses its 200-day trend? Measured in trading
   days, per episode. If the median lead is <= 0, breadth is price in
   disguise and everything below is noise.

2. Does a breadth gate, or breadth AND price, beat price alone?

Deliberately parameter-light. One breadth threshold (50%), one lookback
(200d, matching the price gate), one band (2%, finding 41). A tuned
grid over ~30 independent US drawdowns would be fitted (finding 29).

Writes data/breadth_regime_study.json.
"""
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "breadth_regime_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"
URL = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
       "49_Industry_Portfolios_Daily_CSV.zip")

SMA_WINDOW = 200
BAND = 0.02
BREADTH_LEVELS = (0.40, 0.50, 0.60)
DD_THRESHOLD = -0.20          # episodes worth detecting


def load_market():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    df["index_level"] = (1 + df["market_return"]).cumprod()
    return df[["market_return", "rf", "index_level"]]


def fetch_industries():
    """49 daily industry portfolios, 1926-. Returns a wide frame of returns."""
    raw = subprocess.run(
        ["curl", "-sS", "-L", "-m", "300", "--retry", "3",
         "-A", "Mozilla/5.0", URL], capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")

    header, rows = None, []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if header is None:
            # First row whose leading cell is blank and which has many
            # columns is the industry-name header.
            if len(parts) > 40 and parts[0] == "":
                header = ["date"] + parts[1:]
            continue
        if len(parts[0]) == 8 and parts[0].isdigit():
            try:
                rows.append([parts[0]] + [float(v) for v in parts[1:]])
            except ValueError:
                continue
        elif rows:
            break          # value-weighted block ends; ignore the rest

    width = len(header)
    df = pd.DataFrame([r for r in rows if len(r) == width], columns=header)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.set_index("date").sort_index()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df.loc[df[c] <= -99.99, c] = np.nan     # French missing-data code
        df[c] = df[c] / 100.0
    return df


def breadth_series(industry_returns, window=SMA_WINDOW):
    """Fraction of industries trading above their OWN trailing SMA."""
    levels = (1 + industry_returns.fillna(0.0)).cumprod()
    levels = levels.where(industry_returns.notna())
    sma = levels.rolling(window, min_periods=window).mean()
    above = (levels > sma)
    valid = sma.notna() & levels.notna()
    return (above & valid).sum(axis=1) / valid.sum(axis=1).replace(0, np.nan)


def gate_from(series, threshold, band, invert_band=True):
    """Hysteresis gate on any series against a threshold.

    Exits below threshold*(1-band), re-enters above threshold*(1+band).
    Shifted one day: the state acting on day T uses data through T-1.
    """
    state, out = True, {}
    for dt, v in series.items():
        if pd.notna(v):
            if state and v < threshold * (1 - band):
                state = False
            elif (not state) and v > threshold * (1 + band):
                state = True
        out[dt] = 1.0 if state else 0.0
    return pd.Series(out).shift(1).fillna(1.0)


def price_gate(level, band=BAND, window=SMA_WINDOW):
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


def perf(ret, rf, exposure):
    a = exposure.reindex(ret.index).ffill().fillna(1.0)
    r = pd.Series(np.where(a > 0, ret, rf), index=ret.index)
    curve = (1 + r).cumprod()
    years = len(r) / 252
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "switches_per_year": float((a != a.shift(1)).sum() / years),
        "pct_in_market": float(a.mean() * 100),
    }


def drawdown_episodes(level, threshold=DD_THRESHOLD):
    """Peak-to-trough episodes worse than `threshold`, as (peak, trough)."""
    dd = level / level.cummax() - 1
    episodes, in_ep, peak_i = [], False, None
    running_peak = level.iloc[0]
    for i, (dt, v) in enumerate(level.items()):
        if v >= running_peak:
            if in_ep:
                in_ep = False
            running_peak, peak_i = v, i
        elif not in_ep and dd.iloc[i] <= threshold:
            in_ep = True
            trough_i = int(dd.iloc[i:].idxmin() == dd.index[i:])
            seg = dd.iloc[i:]
            end = seg.index.get_loc(seg.idxmin())
            episodes.append((peak_i, i, i + end))
    return episodes


def lead_lag(level, breadth, threshold=0.50):
    """Trading days by which breadth crosses BEFORE price, per episode.

    Positive = breadth is faster. This is the whole test; if the median
    is <= 0 there is no case for breadth as a detector.
    """
    sma = level.rolling(SMA_WINDOW).mean()
    price_below = (level < sma * (1 - BAND)).values
    breadth_below = (breadth.reindex(level.index) < threshold).values
    dd = (level / level.cummax() - 1).values

    rows, i, n = [], 0, len(level)
    while i < n:
        if dd[i] <= DD_THRESHOLD:
            # walk back to the peak that started it
            j = i
            while j > 0 and dd[j] < 0:
                j -= 1
            # first crossing of each signal at or after the peak
            p = next((k for k in range(j, n) if price_below[k]), None)
            b = next((k for k in range(j, n) if breadth_below[k]), None)
            trough = j + int(np.nanargmin(dd[j:min(n, j + 1500)]))
            if p is not None and b is not None:
                rows.append({
                    "peak": str(level.index[j].date()),
                    "trough": str(level.index[trough].date()),
                    "depth_pct": float(dd[trough] * 100),
                    "price_signal": str(level.index[p].date()),
                    "breadth_signal": str(level.index[b].date()),
                    "breadth_lead_days": int(p - b),
                })
            # skip past this episode's recovery
            k = trough
            while k < n and dd[k] < -0.02:
                k += 1
            i = k
        i += 1
    return rows


def main():
    mkt = load_market()
    ind = fetch_industries()
    print(f"industries: {ind.shape[1]} cols, "
          f"{ind.index.min():%Y-%m-%d} -> {ind.index.max():%Y-%m-%d}")

    breadth = breadth_series(ind)
    joined = mkt.join(breadth.rename("breadth"), how="inner").dropna()
    level, ret, rf = (joined["index_level"], joined["market_return"],
                      joined["rf"])
    print(f"joined sample: {joined.index.min():%Y-%m-%d} -> "
          f"{joined.index.max():%Y-%m-%d}  ({len(joined)} days)")
    print(f"breadth mean {joined['breadth'].mean():.3f}  "
          f"p5 {joined['breadth'].quantile(.05):.3f}  "
          f"p95 {joined['breadth'].quantile(.95):.3f}\n")

    # ---- Q1: does breadth lead price? -------------------------------
    episodes = lead_lag(level, joined["breadth"])
    print("=" * 78)
    print("Q1  LEAD/LAG - breadth vs price signal, per >20% drawdown")
    print("=" * 78)
    print(f"{'peak':12}{'trough':12}{'depth':>8}{'price sig':>13}"
          f"{'breadth sig':>13}{'lead(d)':>9}")
    for e in episodes:
        print(f"{e['peak']:12}{e['trough']:12}{e['depth_pct']:>7.1f}%"
              f"{e['price_signal']:>13}{e['breadth_signal']:>13}"
              f"{e['breadth_lead_days']:>9}")
    leads = [e["breadth_lead_days"] for e in episodes]
    if leads:
        print(f"\n  n={len(leads)}  median lead {np.median(leads):.0f} days  "
              f"mean {np.mean(leads):.0f}  "
              f"breadth first in {sum(l > 0 for l in leads)}/{len(leads)}")
        print("  (positive = breadth crossed first)")

    # ---- Q2: does it trade better? ----------------------------------
    start = level.index[SMA_WINDOW + 10]
    seg = slice(start, None)
    pg = price_gate(level)
    rows = {"buy_hold": perf(ret.loc[seg], rf.loc[seg],
                             pd.Series(1.0, index=level.index)),
            "price_gate_2%": perf(ret.loc[seg], rf.loc[seg], pg)}

    for lvl in BREADTH_LEVELS:
        bg = gate_from(joined["breadth"], lvl, BAND)
        rows[f"breadth_{lvl:.0%}"] = perf(ret.loc[seg], rf.loc[seg], bg)
        # AND: both must be risk-off to exit (fewer exits, less whipsaw)
        rows[f"price_AND_breadth_{lvl:.0%}"] = perf(
            ret.loc[seg], rf.loc[seg],
            ((pg > 0) | (bg > 0)).astype(float))
        # OR: either signal exits (faster, more whipsaw)
        rows[f"price_OR_breadth_{lvl:.0%}"] = perf(
            ret.loc[seg], rf.loc[seg],
            ((pg > 0) & (bg > 0)).astype(float))

    print("\n" + "=" * 78)
    print("Q2  DOES IT TRADE BETTER?")
    print("=" * 78)
    print(f"{'variant':26}{'CAGR':>8}{'maxDD':>9}{'sw/yr':>8}{'in mkt':>9}")
    print("-" * 78)
    for name, r in rows.items():
        print(f"{name:26}{r['cagr_pct']:>7.2f}%{r['max_dd_pct']:>8.1f}%"
              f"{r['switches_per_year']:>7.2f}{r['pct_in_market']:>8.1f}%")

    payload = {"episodes": episodes, "performance": rows,
               "sample": {"start": str(joined.index.min().date()),
                          "end": str(joined.index.max().date()),
                          "n_industries": int(ind.shape[1])}}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
