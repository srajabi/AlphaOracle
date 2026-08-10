#!/usr/bin/env python3
"""Fix Alpaca timestamps, then cross-validate against the OHLCV-1m archive.

TWO TIMESTAMP TRAPS IN THE ALPACA DUMP
--------------------------------------
1. The CSV `timestamp` column is NAIVE EASTERN time, not UTC. AAPL's
   first bar reads 2000-01-03 09:30:00 - but 09:30 UTC is 04:30 ET,
   which is not a market open. Stamping UTC on it (as the first ingest
   did) shifts every bar by 4-5 hours and silently destroys any
   session-aware analysis.

2. The column named `millis` holds SECONDS, not milliseconds:
   946909800 -> 2000-01-03 14:30:00 UTC = 09:30 ET. Read as
   milliseconds it decodes to January 1970.

`millis` is unambiguous and DST-proof, so it is treated as the
authoritative clock and `timestamp` is rebuilt from it. No re-scan of
the 38.9 GB archive is needed because millis is already in the parquet.

WHY CROSS-VALIDATION MATTERS
----------------------------
The OHLCV-1m archive has never had an independent check. Finding 15
guarded five traps by reasoning about single-source data; two sources
let us LOCALISE disagreements instead of arguing about them.

Prices cannot be compared directly - Alpaca is split-adjusted as of
2019, OHLCV-1m is unadjusted (finding 15 trap 1). RETURNS are
split-invariant except on the split date itself, so the comparison is
on minute returns.

Writes data/cross_source_validation.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent
ALPACA = Path("E:/ColdStorage/AlphaOracle-data/alpaca_minute")
OHLCV = Path("E:/ColdStorage/OHLCV-1m/data")
OUT = REPO / "data" / "cross_source_validation.json"

CHECK_TICKERS = ["AAPL", "MSFT", "INTC", "CSCO", "NVDA", "XLK", "IWM"]
CHECK_MONTHS = ["2005-06", "2010-06", "2015-06", "2018-06"]
TOL = 1e-4          # returns agreeing to 1bp are "the same bar"


def fix_timestamps():
    """Rebuild timestamp from the authoritative `millis` (seconds) column."""
    fixed = {}
    for path in sorted(ALPACA.glob("*.parquet")):
        df = pd.read_parquet(path)
        if "millis" not in df.columns:
            continue
        before = df["timestamp"].min() if "timestamp" in df else None
        ms = pd.to_numeric(df["millis"], errors="coerce")
        df = df[ms.notna()].copy()
        df["timestamp"] = pd.to_datetime(ms[ms.notna()].astype("int64"),
                                         unit="s", utc=True)
        df = (df.sort_values("timestamp")
                .drop_duplicates(subset=["timestamp"])
                .reset_index(drop=True))
        df.to_parquet(path, index=False)
        fixed[path.stem] = {
            "rows": int(len(df)),
            "was_first": str(before),
            "now_first": str(df["timestamp"].iloc[0]) if len(df) else None,
            "now_last": str(df["timestamp"].iloc[-1]) if len(df) else None,
        }
    return fixed


def session_hist(ts):
    """Distribution of bars by UTC hour - sanity check on the clock."""
    return ts.dt.hour.value_counts().sort_index().to_dict()


def compare(ticker, month):
    apath = ALPACA / f"{ticker}.parquet"
    opath = OHLCV / f"ohlcv_{month}.parquet"
    if not apath.exists() or not opath.exists():
        return None

    a = pd.read_parquet(apath, columns=["timestamp", "close", "volume"])
    a = a[(a["timestamp"] >= f"{month}-01") &
          (a["timestamp"] < (pd.Timestamp(f"{month}-01", tz="UTC")
                             + pd.offsets.MonthBegin(1)))]
    if len(a) < 100:
        return None

    t = pq.read_table(opath, columns=["ticker", "timestamp", "close", "volume"])
    o = t.to_pandas()
    o = o[o["ticker"] == ticker]
    if len(o) < 100:
        return None
    o["timestamp"] = pd.to_datetime(o["timestamp"], utc=True)

    a = a.set_index("timestamp").sort_index()
    o = o.set_index("timestamp").sort_index()
    common = a.index.intersection(o.index)
    if len(common) < 100:
        return {"ticker": ticker, "month": month, "overlap_bars": len(common),
                "note": "insufficient timestamp overlap"}

    ar = a.loc[common, "close"].pct_change()
    orr = o.loc[common, "close"].pct_change()
    both = pd.DataFrame({"a": ar, "o": orr}).dropna()
    diff = (both["a"] - both["o"]).abs()
    agree = float((diff <= TOL).mean())

    # volume is NOT split-adjusted the same way; compare correlation only
    av, ov = a.loc[common, "volume"], o.loc[common, "volume"]
    vol_corr = float(np.corrcoef(av.fillna(0), ov.fillna(0))[0, 1])

    return {
        "ticker": ticker, "month": month,
        "alpaca_bars": int(len(a)), "ohlcv_bars": int(len(o)),
        "overlap_bars": int(len(common)),
        "overlap_pct_of_alpaca": round(100 * len(common) / len(a), 1),
        "return_agreement_pct": round(100 * agree, 2),
        "median_abs_return_diff": float(diff.median()),
        "p99_abs_return_diff": float(diff.quantile(0.99)),
        "max_abs_return_diff": float(diff.max()),
        "volume_corr": round(vol_corr, 4),
    }


def main():
    print("rebuilding timestamps from `millis` (seconds, UTC)...")
    fixed = fix_timestamps()
    for t in ["AAPL", "TQQQ"]:
        if t in fixed:
            f = fixed[t]
            print(f"  {t}: {f['was_first']}  ->  {f['now_first']}")

    a = pd.read_parquet(ALPACA / "AAPL.parquet", columns=["timestamp"])
    print(f"\nAAPL bars by UTC hour after fix (13-20 = US session):")
    h = session_hist(a["timestamp"])
    print("  " + "  ".join(f"{k}h:{v//1000}k" for k, v in sorted(h.items())))

    print(f"\ncross-source comparison (returns, split-invariant):")
    hdr = (f"{'ticker':7}{'month':9}{'alpaca':>8}{'ohlcv':>8}{'overlap':>9}"
           f"{'agree%':>8}{'medDiff':>10}{'maxDiff':>9}{'volCorr':>9}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for ticker in CHECK_TICKERS:
        for month in CHECK_MONTHS:
            r = compare(ticker, month)
            if r is None:
                continue
            rows.append(r)
            if "note" in r:
                print(f"{ticker:7}{month:9}  {r['note']} "
                      f"(overlap {r['overlap_bars']})")
                continue
            print(f"{r['ticker']:7}{r['month']:9}{r['alpaca_bars']:>8}"
                  f"{r['ohlcv_bars']:>8}{r['overlap_bars']:>9}"
                  f"{r['return_agreement_pct']:>7.1f}%"
                  f"{r['median_abs_return_diff']:>10.2e}"
                  f"{r['max_abs_return_diff']:>9.3f}"
                  f"{r['volume_corr']:>9.3f}")

    OUT.write_text(json.dumps({"timestamp_fix": fixed, "comparisons": rows},
                              indent=2), encoding="utf-8")
    good = [r for r in rows if "return_agreement_pct" in r]
    if good:
        ag = np.mean([r["return_agreement_pct"] for r in good])
        print(f"\nmean return agreement across {len(good)} ticker-months: "
              f"{ag:.1f}%")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
