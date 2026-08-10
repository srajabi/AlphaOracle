#!/usr/bin/env python3
"""Build ONE daily master bar table across every source, with provenance.

WHY DAILY AND NOT MINUTE
------------------------
All 48 findings in this repo are computed on daily or monthly bars. A
minute-level union of OHLCV-1m (87.7 GB, 31k tickers) with the Alpaca
dump would land near 150 GB and serve only TODO #16 and #18, which
between them need about thirty instruments. Reduced to daily, all
sources together are ~5 GB - small enough to query interactively and
broad enough to cover the whole research surface.

Minute data stays curated at the instruments actually tested intraday.

LONG FORMAT, NOT RESOLVED
-------------------------
One row per (date, ticker, SOURCE). The table deliberately keeps every
source's opinion rather than silently electing a winner, because finding
48 established that NEITHER source is authoritative - Alpaca carried the
bad CSCO print (23.000 when CSCO traded ~19.70), OHLCV-1m carried the bad
INTC one (20.000 when INTC traded ~21.17). Resolution is a query-time
decision with the evidence visible, not a build-time guess.

REGULAR HOURS ONLY
------------------
Finding 48: every material cross-source disagreement (>1%) fell OUTSIDE
09:30-16:00 ET. Session filtering is done by converting to
America/New_York rather than by a fixed UTC window, because the UTC
offset of the US session changes with DST (13:30-20:00 in summer,
14:30-21:00 in winter). A fixed UTC window silently drops or admits an
hour for half the year.

QUALITY COLUMN
--------------
`bars` counts the minute bars behind each daily aggregate. The session
filter is INCLUSIVE of the 16:00 bar so that `close` captures the
closing auction print, which makes a full session 391 rather than 390.
Low counts flag half-days, illiquid names and partial data - which
finding 44 needed and had to infer by proxy. In 1992 the median
ticker-day has just 14 bars against INTC's ~350, so this column is the
liquidity filter the archive never had.

Writes E:/ColdStorage/AlphaOracle-data/daily_master/<source>/*.parquet
"""
import io
import json
import sys
import tarfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
OHLCV = COLD / "OHLCV-1m" / "data"
TARS = {"alpaca": COLD / "market-data-7859.tar.pigz"}
HIST = REPO / "data" / "historical_long"
# Lives under archive/derived/ alongside the other derived sets so
# package_archive.py finds it. A run already in flight writes to the
# old AlphaOracle-data/daily_master path; move it, do not rebuild.
OUTROOT = COLD / "archive" / "derived" / "daily_master"

ET = "America/New_York"
SESSION_START, SESSION_END = "09:30", "16:00"
AGG = {"open": "first", "high": "max", "low": "min",
       "close": "last", "volume": "sum"}


def to_daily(df, tcol="timestamp"):
    """Minute bars (UTC) -> daily regular-session OHLCV + bar count."""
    ts = pd.to_datetime(df[tcol], utc=True).dt.tz_convert(ET)
    df = df.assign(_et=ts)
    # DST-correct session filter: wall-clock ET, not a fixed UTC window.
    t = df["_et"].dt.time
    lo = pd.Timestamp(SESSION_START).time()
    hi = pd.Timestamp(SESSION_END).time()
    df = df[(t >= lo) & (t <= hi)]
    if df.empty:
        return None
    df = df.assign(date=df["_et"].dt.date)
    keys = ["date", "ticker"] if "ticker" in df.columns else ["date"]
    g = df.groupby(keys, observed=True)
    out = g.agg(AGG)
    out["bars"] = g.size()
    return out.reset_index()


def build_ohlcv1m(limit=None):
    outdir = OUTROOT / "ohlcv1m"
    outdir.mkdir(parents=True, exist_ok=True)
    files = sorted(OHLCV.glob("ohlcv_*.parquet"))
    if limit:
        files = files[:limit]
    t0, done = time.time(), 0
    for f in files:
        dest = outdir / f"daily_{f.stem.split('_')[1]}.parquet"
        if dest.exists():
            done += 1
            continue
        tab = pq.read_table(f, columns=["timestamp", "ticker", "open",
                                        "high", "low", "close", "volume"])
        df = tab.to_pandas()
        del tab
        daily = to_daily(df)
        del df
        if daily is None or daily.empty:
            continue
        daily["source"] = "ohlcv1m"
        daily.to_parquet(dest, index=False)
        done += 1
        el = time.time() - t0
        print(f"  [ohlcv1m] {done}/{len(files)} {f.stem} -> "
              f"{len(daily):,} rows  ({el:.0f}s)", flush=True)
    return outdir


def build_alpaca():
    """Derive Alpaca daily from the MINUTE MASTER, not from the tar.

    The first version streamed the tar a second time and accumulated
    ~900,000 small DataFrames before concatenating - unbounded memory for
    no benefit. tools/build_minute_master.py already pays the one
    expensive tar pass and writes per-ticker parquet; daily is then a
    cheap aggregation over that, and memory is bounded by one ticker.

    Run build_minute_master.py FIRST.
    """
    src = COLD / "archive" / "derived" / "minute_master" / "alpaca"
    outdir = OUTROOT / "alpaca"
    outdir.mkdir(parents=True, exist_ok=True)
    dest = outdir / "daily_all.parquet"
    if not src.exists():
        print(f"  [alpaca] minute master missing at {src}")
        print("           run tools/build_minute_master.py first")
        return outdir
    if dest.exists():
        print(f"  [alpaca] {dest.name} exists, skipping")
        return outdir

    files = sorted(src.glob("*.parquet"))
    chunks, t0 = [], time.time()
    for i, f in enumerate(files, 1):
        df = pd.read_parquet(f)
        if df.empty:
            continue
        df["ticker"] = f.stem
        d = to_daily(df)
        if d is not None and not d.empty:
            chunks.append(d)
        if i % 1000 == 0:
            print(f"  [alpaca] {i}/{len(files)} tickers, "
                  f"{time.time()-t0:.0f}s", flush=True)
    if not chunks:
        return outdir
    out = pd.concat(chunks, ignore_index=True)
    out["source"] = "alpaca"
    out.to_parquet(dest, index=False, compression="zstd")
    print(f"  [alpaca] wrote {len(out):,} daily rows from "
          f"{len(files):,} tickers", flush=True)
    return outdir


def build_yfinance():
    outdir = OUTROOT / "yfinance"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in sorted(HIST.glob("*.json")):
        if f.stem.startswith("FRED_"):
            continue
        try:
            payload = json.loads(f.read_text())
        except Exception:
            continue
        prices = payload.get("prices")
        if not prices:
            continue
        df = pd.DataFrame(prices)
        dcol = next((c for c in ("date", "Date") if c in df), None)
        if dcol is None:
            continue
        df = df.rename(columns={dcol: "date"})
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        df["ticker"] = payload.get("ticker", f.stem)
        keep = [c for c in ("date", "ticker", "open", "high", "low",
                            "close", "adj_close", "volume") if c in df]
        rows.append(df[keep])
    if not rows:
        return outdir
    out = pd.concat(rows, ignore_index=True).dropna(subset=["date"])
    out["source"] = "yfinance"
    out["bars"] = np.nan
    out.to_parquet(outdir / "daily_all.parquet", index=False)
    print(f"  [yfinance] wrote {len(out):,} rows, "
          f"{out['ticker'].nunique()} tickers", flush=True)
    return outdir


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    OUTROOT.mkdir(parents=True, exist_ok=True)
    if which in ("all", "yfinance"):
        print("building yfinance daily...")
        build_yfinance()
    if which in ("all", "alpaca"):
        print("building alpaca daily (streams 38.9 GB)...")
        build_alpaca()
    if which in ("all", "ohlcv1m"):
        print("building ohlcv1m daily (reads 87.7 GB)...")
        build_ohlcv1m(limit)
    print("\ndone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
