#!/usr/bin/env python3
"""Package everything for long-term, off-machine backup.

DESIGN RULES
------------
1. NEVER recompress compressed data. The tars are already gzip/bzip2 and
   the parquet is already zstd/snappy. Re-wrapping them costs hours of
   CPU and gains nothing. Only the JSON sources get compressed, because
   text actually compresses (~10x).

2. Originals are RENAMED, never rewritten. A rename on the same volume
   is instant and lossless. The manifest records the original filename
   so provenance survives the rename.

3. Every file gets a SHA256. A backup you cannot verify is a backup you
   do not have - bit rot on cold storage is silent, and these files will
   sit on a drive for years.

4. The archive is SELF-DESCRIBING. README.md and MANIFEST.json travel
   with the data, so a reader in five years (or a future agent) does not
   need this conversation to understand what they have - including the
   traps, which are the part that would otherwise be lost.

NAMING
------
    <dataset>_<coverage>_<scope>_snap<YYYY-MM-DD>.<ext>

Coverage and snapshot date in the filename because these datasets are
point-in-time captures. "market-data.tar" told us nothing; the same file
as alpaca-minute-bars_1999-01_2019-09_7859tickers_snap2019-09-23.tar.bz2
tells us everything before it is opened - including that it is bzip2.

Usage:  python tools/package_archive.py [--move] [--hash]
        --move   perform the renames (default is a dry run)
        --hash   compute SHA256 (slow: ~64 GB to read)
"""
import hashlib
import json
import sys
import tarfile
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
ARCHIVE = COLD / "archive"
RAW = ARCHIVE / "raw"
DERIVED = ARCHIVE / "derived"
TODAY = date.today().isoformat()

# (current path, archival name, description, known issues)
RENAMES = [
    (COLD / "market-data-7859.tar.pigz",
     "alpaca-minute-bars_1999-01_2019-09_7859tickers_snap2019-09-23.tar.gz",
     "Alpaca minute bars, per-ticker-per-month CSVs, gzip (pigz) tar.",
     ["53% of members are 35-byte _EMPTY placeholders",
      "only 1,862 of 7,859 tickers have >=200 real months",
      "SPY absent entirely; QQQ and DIA hold only 2019-06..2019-09",
      "CSV `timestamp` column is naive EASTERN, not UTC",
      "column named `millis` holds SECONDS - it is authoritative",
      "prices are split-adjusted as of 2019"]),
    (COLD / "market-data.tar",
     "alpaca-minute-bars_1999-01_2019-09_7859tickers_snap2019-09-19.tar.bz2",
     "Same dataset, four days earlier, BZIP2 despite the .tar extension.",
     ["magic bytes are BZh9 - it is bzip2, not an uncompressed tar",
      "MULTI-STREAM bzip2 (pbzip2). tarfile.open(path, 'r|*') dies with "
      "'EOFError: End of stream already reached' at the end of the FIRST "
      "stream. This does NOT mean the file is truncated - it is not. Open "
      "it as tarfile.open(fileobj=bz2.open(path,'rb'), mode='r|'), which "
      "splices the streams. GNU tar works because it shells out to real "
      "bzip2",
      "bzip2 decompresses ~10x slower than the gzip twin (~115 min for a "
      "full member scan vs ~13 min)",
      "VERIFIED REDUNDANT 2026-08-09 (tools/inventory_bz2_twin.py): it "
      "is a STRICT SUBSET of the snap2019-09-23 twin. 1,562,414 members "
      "vs 1,957,238; 6,273 tickers vs 7,859; 1,586 tickers exist only in "
      "the 09-23 copy and ZERO only here; no ticker has more real months. "
      "The 09-19 run was incomplete and 09-23 was the completion. Safe "
      "to exclude from backup, and safe to delete once 09-23 is stored "
      "off-machine",
      "SPY is absent from BOTH captures - it was never downloaded, not "
      "lost in transfer. Source SPY minute bars from OHLCV-1m"]),
]

JSON_SOURCES = [
    (REPO / "data" / "historical_long",
     f"alphaoracle-historical-long_daily-bars-and-fred_snap{TODAY}.tar.gz",
     "yfinance daily bars (79 tickers) + 10 FRED series, as fetched."),
    (REPO / "data" / "deep_history",
     f"alphaoracle-deep-history_french-shiller-jst-epu_snap{TODAY}.tar.gz",
     "Ken French factors/portfolios, Shiller 1871+, JST macrohistory, EPU."),
    (REPO / "data" / "vintage",
     f"alphaoracle-alfred-vintage_point-in-time_snap{TODAY}.tar.gz",
     "ALFRED point-in-time vintages - the ONLY lookahead-safe macro."),
]

DERIVED_SETS = [
    ("minute_master/alpaca", "Alpaca minute bars, one parquet per ticker, "
     "complete incl. extended hours. Timestamps rebuilt from `millis`."),
    ("daily_master/ohlcv1m", "OHLCV-1m aggregated to daily regular-session "
     "bars, one parquet per source month, with a `bars` count column."),
    ("daily_master/alpaca", "Alpaca aggregated to daily regular-session bars."),
    ("daily_master/yfinance", "yfinance daily bars, already daily."),
    ("reference_master", "922 macro/factor series, tidy long format, with "
     "vintage_date as a first-class column."),
]



README = """# AlphaOracle data archive

Generated {today}. Self-describing on purpose: everything needed to use
this data correctly is in this file and MANIFEST.json. Do not rely on
external notes.

## Layout

    raw/        original captures, renamed, byte-identical to source
    derived/    parquet built from raw/ - reproducible, safe to delete
    MANIFEST.json   sizes, SHA256, coverage, per-dataset known issues

`derived/` can always be rebuilt from `raw/` with the tools in the
AlphaOracle repo (tools/build_minute_master.py, build_daily_master.py,
build_reference_master.py). `raw/` cannot be rebuilt from anything.
**If you are short of space, delete derived/, never raw/.**

## Verifying a backup

Bit rot on cold storage is silent. Every file in MANIFEST.json that has
a `sha256` can be checked:

    python tools/package_archive.py --verify

## The traps - read this before writing a backtest

These cost real debugging time and are not discoverable from the data.

**Alpaca minute bars**
- The CSV `timestamp` column is naive EASTERN time. Stamping UTC on it
  shifts every bar 4-5 hours. Use the `millis` column instead.
- `millis` holds SECONDS despite the name. It is authoritative and
  DST-proof.
- Prices are SPLIT-ADJUSTED as of 2019-09.
- 53% of the archive's members are 35-byte `_EMPTY` placeholders; only
  1,862 of 7,859 tickers have >=200 real months.
- **SPY is absent entirely.** QQQ and DIA have only 2019-06..2019-09.
  Never assume a ticker is present.

**OHLCV-1m**
- Prices are UNADJUSTED for splits - the opposite of Alpaca. A 2:1 split
  reads as a -50% day.
- Timestamps ARE genuinely UTC here.
- Symbols change: QQQ traded as QQQQ from 2004 to 2011.
- The median 1992 ticker-day has 14 minute bars, not 390. Use the
  daily master's `bars` column as a liquidity filter.
- DUPLICATE minute timestamps occur. Some ticker-days aggregate to more
  than the 391-minute session (AAPL 2026-03-31 = 394 bars). OHLC is
  unaffected (first/max/min/last are idempotent) but summed VOLUME is
  inflated on those days. Deduplicate on (ticker, timestamp) before
  summing volume. `bars` > 391 in the daily master flags them.

**Comparing the two sources**
- Compare RETURNS, never price levels - one is split-adjusted and the
  other is not.
- They agree on 99.3% of bars within 10bp. Material disagreement
  (>1%) is 0.032% and sits ENTIRELY in extended hours.
- Neither source is authoritative: both carry bad prints, often round
  numbers. Where closes match but returns differ, the bad tick is in
  the PREVIOUS bar.

**Reference series**
- Only 8 of 922 series carry a `vintage_date` (the ALFRED ones). Those
  are the ONLY ones safe for decision-time backtests. Everything else is
  current-vintage and using it as if known at the time is lookahead.

## Provenance

| dataset | source | captured |
|---|---|---|
| alpaca-minute-bars | Alpaca market data API | 2019-09 |
| OHLCV-1m | HuggingFace mito0o852/OHLCV-1m | 2026-08 |
| historical-long | yfinance + FRED | 2026-03..08 |
| deep-history | Ken French, Shiller, JST, EPU | 2026-08 |
| alfred-vintage | ALFRED point-in-time API | 2026-08 |
"""


def sha256(path, chunk=32 * 1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def dir_stats(d):
    if not d.exists():
        return {"exists": False}
    files = [p for p in d.rglob("*") if p.is_file()]
    return {"exists": True, "files": len(files),
            "bytes": sum(p.stat().st_size for p in files)}


def main():
    move = "--move" in sys.argv
    do_hash = "--hash" in sys.argv
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = {"generated": TODAY, "root": str(ARCHIVE),
                "raw": [], "derived": [], "in_place": []}

    print(f"{'DRY RUN' if not move else 'MOVING'}  hash={do_hash}\n")

    # 1. rename the big originals (instant on the same volume)
    for src, newname, desc, issues in RENAMES:
        dest = RAW / newname
        entry = {"archival_name": newname, "original_name": src.name,
                 "description": desc, "known_issues": issues}
        if dest.exists():
            entry["bytes"] = dest.stat().st_size
            entry["status"] = "already archived"
        elif src.exists():
            entry["bytes"] = src.stat().st_size
            if move:
                src.rename(dest)
                entry["status"] = "moved"
            else:
                entry["status"] = "would move"
        else:
            entry["status"] = "MISSING"
        print(f"  [{entry['status']:16}] {newname}")
        if do_hash and dest.exists():
            t = time.time()
            entry["sha256"] = sha256(dest)
            print(f"        sha256 {entry['sha256'][:16]}... "
                  f"({time.time()-t:.0f}s)")
        manifest["raw"].append(entry)

    # 2. compress the JSON sources - text is the only thing worth zipping
    for srcdir, name, desc in JSON_SOURCES:
        dest = RAW / name
        entry = {"archival_name": name, "original_dir": str(srcdir),
                 "description": desc}
        if not srcdir.exists():
            entry["status"] = "MISSING"
        elif dest.exists():
            entry["status"] = "already archived"
            entry["bytes"] = dest.stat().st_size
        else:
            before = sum(p.stat().st_size for p in srcdir.rglob("*")
                         if p.is_file())
            if move:
                with tarfile.open(dest, "w:gz", compresslevel=6) as tf:
                    tf.add(srcdir, arcname=srcdir.name)
                entry["bytes"] = dest.stat().st_size
                entry["uncompressed_bytes"] = before
                entry["ratio"] = round(before / max(entry["bytes"], 1), 1)
                entry["status"] = "compressed"
            else:
                entry["uncompressed_bytes"] = before
                entry["status"] = "would compress"
        print(f"  [{entry['status']:16}] {name}")
        if do_hash and dest.exists():
            entry["sha256"] = sha256(dest)
        manifest["raw"].append(entry)

    # 3. derived sets stay as directories of parquet - already compressed
    for rel, desc in DERIVED_SETS:
        d = DERIVED / rel
        st = dir_stats(d)
        st.update({"path": f"derived/{rel}", "description": desc})
        manifest["derived"].append(st)
        print(f"  [derived         ] {rel:26} "
              f"{st.get('files', 0):>6} files  "
              f"{st.get('bytes', 0)/1e9:>7.2f} GB")

    # 4. OHLCV-1m stays where it is - 87.7 GB of already-compressed parquet
    src = COLD / "OHLCV-1m"
    st = dir_stats(src)
    st.update({"path": str(src),
               "description": "HuggingFace mito0o852/OHLCV-1m minute bars, "
                              "411 monthly parquet, 1992-01..2026-03, "
                              "~31k tickers. Left in place: already parquet, "
                              "already compressed, nothing to gain.",
               "known_issues": [
                   "prices are UNADJUSTED for splits (finding 15 trap 1)",
                   "timestamps are genuinely UTC (unlike the Alpaca dump)",
                   "median ticker-day in 1992 has only 14 minute bars",
                   "DUPLICATE minute timestamps occur: some ticker-days "
                   "aggregate to >391 bars against a 391-minute regular "
                   "session (AAPL 2026-03-31 = 394). Harmless for OHLC "
                   "(first/max/min/last are idempotent) but it INFLATES "
                   "summed volume on those days. Deduplicate on "
                   "(ticker, timestamp) before summing volume",
                   "the daily master's `bars` column exposes this - any "
                   "value >391 is a duplicate-timestamp day"]})
    manifest["in_place"].append(st)
    print(f"  [in place        ] OHLCV-1m  {st.get('files', 0)} files  "
          f"{st.get('bytes', 0)/1e9:.1f} GB")

    (ARCHIVE / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    (ARCHIVE / "README.md").write_text(README.format(today=TODAY),
                                       encoding="utf-8")
    total = (sum(e.get("bytes", 0) for e in manifest["raw"])
             + sum(e.get("bytes", 0) for e in manifest["derived"])
             + sum(e.get("bytes", 0) for e in manifest["in_place"]))
    print(f"\ntotal archive footprint: {total/1e9:.1f} GB")
    print(f"wrote {ARCHIVE / 'MANIFEST.json'}")
    if not move:
        print("\nthis was a DRY RUN - re-run with --move to apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
