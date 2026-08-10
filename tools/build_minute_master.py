#!/usr/bin/env python3
"""Convert the Alpaca tar to parquet - the complete minute master.

COMPLETE, NOT CURATED
---------------------
Every bar, every ticker, including extended hours. Filtering is a
QUERY-TIME decision: finding 48 showed extended-hours bars are where
cross-source disagreement lives, but that is a reason to flag them, not
to discard them. TODO #16 (overnight gaps) and finding 14 need exactly
those bars.

PARTITIONING - and why it differs from OHLCV-1m
-----------------------------------------------
The tar is ordered BY TICKER (all of WINA's months, then the next
ticker), so a single streaming pass can only partition by ticker without
buffering the whole archive. That is also the better layout here: one
parquet per ticker mirrors the source, yields 7,859 files instead of
1.96 million, and matches the per-ticker time-series access every
backtest actually uses.

OHLCV-1m stays partitioned BY MONTH, which suits cross-sectional queries
(finding 44's "rank every ticker in this month"). Neither is wrong; a
pyarrow dataset reads both. The manifest records which is which.

Memory is bounded by the largest single ticker (AAPL, ~185 MB of CSV):
rows accumulate for the current ticker and flush when the ticker changes.

TIMESTAMPS
----------
Built from `millis` (SECONDS despite the name - finding 47), which is
authoritative and DST-proof. The CSV `timestamp` column is naive EASTERN
and stamping UTC on it shifts every bar 4-5 hours. The raw `timestamp`
is dropped rather than kept, because keeping a column that looks like a
timestamp but silently lies is worse than not having it.

Writes E:/ColdStorage/archive/derived/minute_master/alpaca/<TICKER>.parquet
"""
import io
import json
import sys
import tarfile
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
SRC = COLD / "market-data-7859.tar.pigz"
OUT = COLD / "archive" / "derived" / "minute_master" / "alpaca"
STATS = REPO / "data" / "minute_master_alpaca.json"

COLS = ["timestamp", "open", "high", "low", "close", "volume"]


def flush(ticker, chunks, stats):
    """Parse ONE csv per ticker, not one per ticker-month.

    A ticker has ~115-250 monthly CSVs and there are ~900,000 in total.
    Calling read_csv on each costs milliseconds of pandas setup per file
    and extrapolated to ~19 hours. Every monthly CSV for a ticker shares
    the same header, so the raw bytes can be concatenated - header once,
    then each file's body - and parsed in a single call. Headers are
    grouped rather than assumed identical, so a ticker whose schema
    changed mid-history still parses correctly instead of silently
    mis-aligning columns.
    """
    if not chunks:
        return
    groups = {}
    for raw in chunks:
        nl = raw.find(b"\n")
        if nl < 0:
            continue
        header, body = raw[:nl + 1], raw[nl + 1:]
        if not body.strip():
            continue
        groups.setdefault(header, []).append(body)

    frames = []
    for header, bodies in groups.items():
        blob = header + b"".join(bodies)
        try:
            df = pd.read_csv(io.BytesIO(blob))
        except Exception:
            continue
        if df.empty or "millis" not in df.columns:
            continue
        ms = pd.to_numeric(df["millis"], errors="coerce")
        df = df[ms.notna()]
        if df.empty:
            continue
        df = df.assign(timestamp=pd.to_datetime(
            ms[ms.notna()].astype("int64"), unit="s", utc=True))
        frames.append(df[[c for c in COLS if c in df.columns]])
    if not frames:
        return

    out = (pd.concat(frames, ignore_index=True)
             .sort_values("timestamp")
             .drop_duplicates(subset=["timestamp"])
             .reset_index(drop=True))
    if out.empty:
        return
    out.to_parquet(OUT / f"{ticker}.parquet", index=False,
                   compression="zstd")
    stats[ticker] = {
        "rows": int(len(out)),
        "first": str(out["timestamp"].iloc[0]),
        "last": str(out["timestamp"].iloc[-1]),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stats = {}
    cur, chunks = None, []
    n = kept = 0
    t0 = time.time()
    with tarfile.open(SRC, "r|*") as tf:
        for m in tf:
            if not m.isfile():
                continue
            n += 1
            parts = m.name.split("/")
            if len(parts) < 3 or not parts[2].endswith(".csv"):
                continue
            ticker = parts[1]
            if ticker != cur:
                flush(cur, chunks, stats)
                cur, chunks = ticker, []
            if "_EMPTY" in parts[2] or m.size < 100:
                continue
            fh = tf.extractfile(m)
            if fh is not None:
                chunks.append(fh.read())
                kept += 1
            if n % 100_000 == 0:
                el = time.time() - t0
                print(f"  {n:,} members, {len(stats):,} tickers written, "
                      f"{el:.0f}s", flush=True)
    flush(cur, chunks, stats)

    total = sum(v["rows"] for v in stats.values())
    size = sum(p.stat().st_size for p in OUT.glob("*.parquet"))
    STATS.write_text(json.dumps(
        {"tickers": len(stats), "total_rows": total,
         "parquet_bytes": size, "source_members": n,
         "nonempty_members": kept, "per_ticker": stats}, indent=2),
        encoding="utf-8")
    print(f"\n{len(stats):,} tickers, {total:,} minute bars, "
          f"{size/1e9:.1f} GB parquet (from {n:,} tar members)")
    print(f"wrote {OUT}")
    print(f"wrote {STATS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
