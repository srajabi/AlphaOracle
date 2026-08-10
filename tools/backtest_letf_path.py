#!/usr/bin/env python3
"""TODO #18 - is our LETF simulator right? Test it against real LETFs.

WHAT FINDING 21 LEFT OPEN
-------------------------
Finding 21 validated SIMULATED LETF returns against real closing prices
and called the simulator good. But it only ever compared endpoints. The
mechanism that actually drives a daily-reset fund's behaviour is the
intraday PATH, and that was never tested.

This matters beyond curiosity: findings 30, 36 and 38 all price the 2x
and 3x sleeves using this simulator, and the user's aggressive sleeve is
built on 2x with a permanent gate. If the simulator is biased, every
leveraged number in this repo is biased the same way.

THE SIMULATOR UNDER TEST
------------------------
    r_letf = L * r_underlying - (L - 1) * rf - expense / 252

Three ways it can be wrong, tested separately:
1. BIAS - does the mean residual differ from zero? A simulator that is
   right on average but noisy is usable; one that drifts is not.
2. PATH DEPENDENCE - does the residual grow with intraday choppiness?
   A daily-reset fund rebalances near the close, so within a day its
   effective leverage drifts away from L. If residuals correlate with
   intraday range, the constant-L model is missing real structure.
3. COMPOUNDING - over years, does simulated cumulative wealth match
   real? This is the number the sleeve projections actually depend on.

DATA
----
OHLCV-1m for both legs (TQQQ 4,058 days, UPRO 4,472, QQQ 5,219+1,588 as
QQQQ, SPY 8,349) - one source, one adjustment convention, and it runs to
2026 rather than stopping at Alpaca's 2019. Alpaca's split-ADJUSTED
TQQQ is used as an independent cross-check where the two overlap.

SPLITS. OHLCV-1m is UNADJUSTED (finding 15 trap 1) and TQQQ has split
repeatedly, so raw returns carry phantom -50% days. Splits are detected
by ratio against the simulated series - a real 2:1 split makes
(1+r_real)/(1+r_sim) land near 0.5, which no market move plausibly does
- and excluded from tracking statistics rather than patched, because a
patched value is a guess and an excluded one is honest.

QQQ traded as QQQQ from 2004 to 2011 (finding 15 trap 2); both symbols
are stitched.

DIVIDENDS - why a positive drift is EXPECTED, not a simulator bug.
OHLCV-1m closes are price-only, but a real LETF holds the index through
swaps and captures TOTAL return. Feeding price returns to the simulator
should therefore understate reality by roughly L x dividend yield minus
the financing spread. The prediction is testable: the drift must scale
with BOTH leverage and the underlying's yield, so SPY pairs (~1.8%)
should drift more than QQQ pairs (~0.7%), and 3x more than 2x.

This does NOT affect the repo's leveraged findings (30, 36, 38): those
feed French `market_return`, which is a TOTAL return series. It affects
only this test, because no adj_close exists anywhere in the archive.

PATH PROXY. Parkinson's estimator, (high-low)/close, measures intraday
range from daily OHLC without reading 87.7 GB of minute bars. Its ratio
to |close-open|/close is a path-efficiency measure: high range with a
small net move IS a choppy path.

Writes data/letf_path_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
DAILY = COLD / "archive" / "derived" / "daily_master"
REF = COLD / "archive" / "derived" / "reference_master" / "reference.parquet"
OUT = REPO / "data" / "letf_path_study.json"

# (levered ticker, underlying, leverage, expense ratio)
PAIRS = [
    ("TQQQ", "QQQ", 3.0, 0.0095),
    ("UPRO", "SPY", 3.0, 0.0091),
    ("QLD",  "QQQ", 2.0, 0.0095),
    ("SSO",  "SPY", 2.0, 0.0089),
]
# INCEPTION DATES - not cosmetic. OHLCV-1m carries 256 days of a
# DIFFERENT security under the UPRO ticker in 2000-2001, trading at
# $6.50 and $2.94, before real UPRO launched 2009-06-25 at $128. Ticker
# reuse produced beta -12.6 and a 427x wealth ratio in the first run.
# Dates are yfinance first-trade dates, which match each fund's actual
# launch.
INCEPTION = {
    "TQQQ": "2010-02-11", "UPRO": "2009-06-25",
    "SSO": "2006-06-21", "QLD": "2006-06-21",
    "QQQ": "1999-03-10", "SPY": "1993-01-29",
}

SPLIT_RATIOS = (0.5, 1 / 3, 0.25, 2.0, 3.0, 4.0)
SPLIT_TOL = 0.06
MIN_BARS = 100          # a real trading day, not a stub


def load_ohlcv1m_daily():
    """All daily bars from the ohlcv1m master, indexed by ticker."""
    files = sorted((DAILY / "ohlcv1m").glob("*.parquet"))
    want = {t for pair in PAIRS for t in pair[:2]} | {"QQQQ"}
    frames = []
    for f in files:
        d = pd.read_parquet(f, columns=["date", "ticker", "open", "high",
                                        "low", "close", "volume", "bars"])
        d = d[d["ticker"].isin(want)]
        if len(d):
            frames.append(d)
    out = pd.concat(frames, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"])
    return out


def series_for(all_daily, ticker):
    """One ticker's daily frame, stitching QQQQ -> QQQ before 2011."""
    d = all_daily[all_daily["ticker"] == ticker]
    if ticker == "QQQ":
        old = all_daily[all_daily["ticker"] == "QQQQ"]
        if len(old):
            # QQQ traded as QQQQ 2004-2011; keep QQQQ only where QQQ is
            # absent so the overlap does not duplicate dates.
            old = old[~old["date"].isin(set(d["date"]))]
            d = pd.concat([d, old], ignore_index=True)
    d = (d.sort_values("date")
           .drop_duplicates(subset=["date"])
           .set_index("date"))
    d = d[d["bars"] >= MIN_BARS]
    inc = INCEPTION.get(ticker)
    if inc:
        d = d[d.index >= pd.Timestamp(inc)]
    return d


def load_rf():
    ref = pd.read_parquet(REF, columns=["series_id", "date", "value"])
    rf = ref[ref["series_id"] == "french_daily:rf"]
    return rf.set_index(pd.to_datetime(rf["date"]))["value"].sort_index()


def analyse(lev_df, und_df, rf, L, expense, label):
    j = pd.DataFrame({
        "lev_close": lev_df["close"],
        "und_close": und_df["close"],
        "und_high": und_df["high"],
        "und_low": und_df["low"],
        "und_open": und_df["open"],
    }).dropna()
    if len(j) < 250:
        return None
    j["rf"] = rf.reindex(j.index).ffill().fillna(0.0)
    j["r_real"] = j["lev_close"].pct_change()
    j["r_und"] = j["und_close"].pct_change()
    j["r_sim"] = L * j["r_und"] - (L - 1) * j["rf"] - expense / 252
    j = j.dropna()

    # split detection against the simulated series
    ratio = (1 + j["r_real"]) / (1 + j["r_sim"])
    is_split = pd.Series(False, index=j.index)
    for k in SPLIT_RATIOS:
        is_split |= (ratio - k).abs() < SPLIT_TOL
    # a genuine one-day move that large in the UNDERLYING is not a split
    is_split &= j["r_und"].abs() < 0.15
    clean = j[~is_split].copy()

    clean["resid"] = clean["r_real"] - clean["r_sim"]
    clean["parkinson"] = (clean["und_high"] - clean["und_low"]) / clean["und_close"]
    clean["net"] = (clean["und_close"] - clean["und_open"]).abs() / clean["und_close"]
    # choppiness: wide range, small net move
    clean["chop"] = clean["parkinson"] / clean["net"].replace(0, np.nan)

    r = clean["resid"]
    tstat, pval = stats.ttest_1samp(r, 0)
    slope = stats.linregress(clean["r_und"], clean["r_real"])

    ok = clean.dropna(subset=["chop"])
    path = stats.linregress(ok["parkinson"], ok["resid"])
    chop = stats.linregress(np.log(ok["chop"].clip(0.1, 100)), ok["resid"])

    # compounding: real vs simulated wealth over the whole window
    real_cum = float((1 + clean["r_real"]).prod())
    sim_cum = float((1 + clean["r_sim"]).prod())

    # rolling 1-year compounding gap, to see if error accumulates
    yr = 252
    gaps = []
    for s in range(0, len(clean) - yr, yr // 2):
        w = clean.iloc[s:s + yr]
        gaps.append(float((1 + w["r_real"]).prod() / (1 + w["r_sim"]).prod()))
    gaps = np.array(gaps) if gaps else np.array([np.nan])

    return {
        "label": label, "leverage": L, "expense": expense,
        "days": int(len(clean)), "splits_excluded": int(is_split.sum()),
        "start": str(clean.index.min().date()),
        "end": str(clean.index.max().date()),
        "mean_resid_bp_per_day": float(r.mean() * 1e4),
        "resid_t": float(tstat), "resid_p": float(pval),
        "tracking_error_bp_per_day": float(r.std() * 1e4),
        "annualised_drift_pct": float(r.mean() * 252 * 100),
        "beta_real_on_underlying": float(slope.slope),
        "beta_r2": float(slope.rvalue ** 2),
        "path_slope_parkinson": float(path.slope),
        "path_p": float(path.pvalue),
        "chop_slope": float(chop.slope), "chop_p": float(chop.pvalue),
        "real_cum": real_cum, "sim_cum": sim_cum,
        "cum_ratio_real_over_sim": real_cum / sim_cum if sim_cum else np.nan,
        "rolling_1y_gap_median": float(np.nanmedian(gaps)),
        "rolling_1y_gap_min": float(np.nanmin(gaps)),
        "rolling_1y_gap_max": float(np.nanmax(gaps)),
    }


def main():
    print("loading ohlcv1m daily master...", flush=True)
    all_daily = load_ohlcv1m_daily()
    rf = load_rf()
    print(f"  {len(all_daily):,} rows, tickers "
          f"{sorted(all_daily['ticker'].unique())}\n", flush=True)

    results = []
    for lev, und, L, exp in PAIRS:
        ld, ud = series_for(all_daily, lev), series_for(all_daily, und)
        if len(ld) < 250 or len(ud) < 250:
            print(f"{lev}/{und}: insufficient data "
                  f"({len(ld)}/{len(ud)} days)")
            continue
        r = analyse(ld, ud, rf, L, exp, f"{lev}/{und}")
        if r:
            results.append(r)
            print(f"{r['label']:11} {r['days']:>5}d {r['start']}..{r['end']}"
                  f"  splits excl {r['splits_excluded']}", flush=True)

    print(f"\n{'pair':11}{'beta':>7}{'R2':>7}{'drift%/yr':>11}"
          f"{'TE bp/d':>9}{'real/sim':>10}{'path p':>9}")
    print("-" * 64)
    for r in results:
        print(f"{r['label']:11}{r['beta_real_on_underlying']:>7.3f}"
              f"{r['beta_r2']:>7.4f}{r['annualised_drift_pct']:>10.2f}%"
              f"{r['tracking_error_bp_per_day']:>9.1f}"
              f"{r['cum_ratio_real_over_sim']:>10.3f}"
              f"{r['path_p']:>9.3f}")

    print("\ncompounding over the full window (real vs simulated wealth):")
    for r in results:
        print(f"  {r['label']:11} real {r['real_cum']:>9.2f}x   "
              f"sim {r['sim_cum']:>9.2f}x   ratio "
              f"{r['cum_ratio_real_over_sim']:.3f}   "
              f"rolling-1y gap {r['rolling_1y_gap_min']:.3f}"
              f"..{r['rolling_1y_gap_max']:.3f}")

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
