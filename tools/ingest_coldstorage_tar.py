#!/usr/bin/env python3
"""One-pass inventory + targeted extraction of the ColdStorage Alpaca tars.

WHAT THESE ARCHIVES ARE
-----------------------
E:/ColdStorage holds two 2019 Alpaca minute-data dumps laid out as
alpaca-market-data/<TICKER>/<TICKER>_minute_data_<YYYY-MM-01>.csv - one
small CSV per ticker per month, so there are MILLIONS of entries. Files
whose name ends _EMPTY.csv are 35-byte placeholders (header only).

  market-data.tar            25.8 GB, tarred 2019-09-19 - BZIP2 despite
                             the extension (magic BZh9)
  market-data-7859.tar.pigz  38.9 GB gzipped, tarred 2019-09-23

The first 40 entries of each are byte-identical including sizes, and
bzip2 compresses CSV harder than gzip, so these are probably the SAME
dataset stored twice - bzip2 first, then re-done with pigz for faster
decompression. This script settles that empirically instead of assuming.

WHY STREAMING, NOT EXTRACTION
-----------------------------
Extracting in full would create millions of tiny files, which NTFS
handles badly, and the plain tar alone would land ~2M inodes for data we
mostly do not need. The disk sustains 625 MB/s, so a full sequential
pass is ~40s of I/O; the cost is per-entry Python overhead, which one
pass amortises.

tarfile is opened in STREAM mode with compression sniffing ('r|*').
Random-access mode ('r:') builds a full member index first and is far
slower here. Note "r|" alone FAILS on market-data.tar with "invalid
header" because that file is bzip2 - only GNU tar auto-detects.

So: one pass that simultaneously
  1. inventories every ticker (file count, byte total, date range), and
  2. materialises the TARGET tickers straight to parquet.

TARGETS AND WHY
---------------
- LETFs (TQQQ/UPRO/SSO/SQQQ/SPXU/UDOW): TODO #18, LETF path-dependency
  from real intraday paths, still untouched. Simulated LETF returns were
  validated against real prices in finding 21 but never against the
  intraday PATH, which is what actually drives the daily-reset drag.
- SPY/QQQ/DIA/IWM: TODO #16, stop-loss behaviour on the true intraday
  path rather than on close-to-close bars.
- Sector ETFs: an INDEPENDENT second source for the same bars already in
  OHLCV-1m, which is the cross-source validator the archive has never
  had. Two sources disagreeing localises bad prints.

Writes data/coldstorage_inventory.json and
E:/ColdStorage/AlphaOracle-data/alpaca_minute/<TICKER>.parquet
"""
import io
import json
import sys
import tarfile
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
OUTDIR = COLD / "AlphaOracle-data" / "alpaca_minute"
INVENTORY = REPO / "data" / "coldstorage_inventory.json"

TARGETS = {
    # levered - TODO #18
    "TQQQ", "SQQQ", "UPRO", "SPXU", "SSO", "SDS", "UDOW", "SDOW", "QLD",
    # broad - TODO #16
    "SPY", "QQQ", "DIA", "IWM", "VTI",
    # sectors - cross-source validation vs OHLCV-1m
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLU", "XLY", "XLB",
    # names that mattered in finding 44
    "AAPL", "MSFT", "NVDA", "CSCO", "INTC", "YHOO", "AOL", "WCOM", "SUNW",
}

# Both are COMPRESSED despite appearances. market-data.tar starts with
# BZh9 - it is bzip2, not an uncompressed tar; GNU tar auto-detects this
# but Python's "r|" does not and raises "invalid header". "r|*" lets
# tarfile sniff the compression, which is why both entries use it.
#
# bzip2 decompresses at ~30 MB/s against gzip's ~300 MB/s, so prefer the
# pigz archive for any full pass.
ARCHIVES = [
    ("bz2", COLD / "market-data.tar", "r|*"),
    ("pigz", COLD / "market-data-7859.tar.pigz", "r|*"),
]


def parse_member(name):
    """alpaca-market-data/WINA/WINA_minute_data_2013-03-01.csv -> (WINA, 2013-03)."""
    parts = name.split("/")
    if len(parts) < 3 or not parts[2].endswith(".csv"):
        return None, None, False
    ticker = parts[1]
    stem = parts[2][:-4]
    empty = stem.endswith("_EMPTY")
    if empty:
        stem = stem[:-6]
    month = stem.rsplit("_", 1)[-1][:7] if "_" in stem else None
    return ticker, month, empty


def scan(label, path, mode, collect):
    """Stream one archive. Returns inventory dict; fills `collect` for targets."""
    inv = defaultdict(lambda: {"files": 0, "empty": 0, "bytes": 0,
                               "min_month": None, "max_month": None})
    t0 = time.time()
    n = 0
    with tarfile.open(path, mode) as tf:
        for m in tf:
            if not m.isfile():
                continue
            n += 1
            ticker, month, empty = parse_member(m.name)
            if ticker is None:
                continue
            e = inv[ticker]
            e["files"] += 1
            e["bytes"] += m.size
            if empty:
                e["empty"] += 1
            elif month:
                if e["min_month"] is None or month < e["min_month"]:
                    e["min_month"] = month
                if e["max_month"] is None or month > e["max_month"]:
                    e["max_month"] = month
            if ticker in TARGETS and not empty and m.size > 100:
                data = tf.extractfile(m)
                if data is not None:
                    collect[ticker].append(data.read())
            if n % 250_000 == 0:
                el = time.time() - t0
                print(f"  [{label}] {n:,} files, {len(inv):,} tickers, "
                      f"{el:.0f}s ({n/el:,.0f}/s)", flush=True)
    el = time.time() - t0
    print(f"  [{label}] DONE {n:,} files, {len(inv):,} tickers, {el:.0f}s",
          flush=True)
    return dict(inv), n


def write_targets(collect, source):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    written = {}
    for ticker, chunks in sorted(collect.items()):
        if not chunks:
            continue
        frames = []
        for raw in chunks:
            try:
                df = pd.read_csv(io.BytesIO(raw))
            except Exception:
                continue
            if len(df):
                frames.append(df)
        if not frames:
            continue
        out = pd.concat(frames, ignore_index=True)
        # normalise the timestamp column whatever it is called
        tcol = next((c for c in out.columns
                     if c.lower() in ("timestamp", "time", "date", "datetime",
                                      "t", "unnamed: 0")), out.columns[0])
        out = out.rename(columns={tcol: "timestamp"})
        try:
            out["timestamp"] = pd.to_datetime(out["timestamp"],
                                              errors="coerce", utc=True)
            out = out.dropna(subset=["timestamp"]).sort_values("timestamp")
            out = out.drop_duplicates(subset=["timestamp"])
        except Exception:
            pass
        path = OUTDIR / f"{ticker}.parquet"
        out.to_parquet(path, index=False)
        written[ticker] = {"rows": int(len(out)), "source": source,
                           "cols": list(out.columns)[:10]}
        print(f"    wrote {ticker}: {len(out):,} rows", flush=True)
    return written


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "pigz"
    sel = [a for a in ARCHIVES if a[0] == which]
    if not sel:
        raise SystemExit(f"unknown archive {which}; use bz2|pigz")
    label, path, mode = sel[0]
    if not path.exists():
        raise SystemExit(f"missing {path}")
    print(f"streaming {label}: {path.name} ({path.stat().st_size/1e9:.1f} GB)")

    collect = defaultdict(list)
    inv, total = scan(label, path, mode, collect)

    print(f"\nmaterialising {len(collect)} target tickers...")
    written = write_targets(collect, label)

    payload = {}
    if INVENTORY.exists():
        payload = json.loads(INVENTORY.read_text())
    payload[label] = {
        "archive": path.name,
        "size_gb": round(path.stat().st_size / 1e9, 2),
        "total_files": total,
        "n_tickers": len(inv),
        "targets_written": written,
        "tickers": inv,
    }
    INVENTORY.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    real = {t: v for t, v in inv.items() if v["files"] > v["empty"]}
    months = [v["min_month"] for v in real.values() if v["min_month"]]
    maxs = [v["max_month"] for v in real.values() if v["max_month"]]
    print(f"\n=== {label} ===")
    print(f"  files       {total:,}")
    print(f"  tickers     {len(inv):,}  ({len(real):,} with any real data)")
    if months:
        print(f"  coverage    {min(months)} -> {max(maxs)}")
    print(f"  empty files {sum(v['empty'] for v in inv.values()):,}")
    print(f"  targets     {len(written)} written to {OUTDIR}")
    print(f"\nwrote {INVENTORY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
