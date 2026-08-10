#!/usr/bin/env python3
"""Does the earlier bzip2 capture hold what the gzip one is missing?

THE QUESTION
------------
The gzip capture (snap 2019-09-23) is missing SPY, XLE, XLF, YHOO, AOL
and WCOM entirely, and holds only 2019-06..2019-09 for QQQ and DIA
(finding 47). The bzip2 capture (snap 2019-09-19) is four days older.
Does it have them?

PRIOR - and it points the other way
-----------------------------------
bzip2 beats gzip on text by 10-20%. Identical content would put the
bzip2 copy near 31-35 GB against the gzip's 38.9 GB. It is 25.8 GB, a
34% gap - MORE than bzip2's real advantage - which suggests it holds
LESS data, not more. That also explains why someone re-tarred ~200 GB
four days later: the first run was probably incomplete.

Worth testing anyway. The counter-case is live: the 09-19 run could have
captured SPY and the 09-23 retry lost it.

INVENTORY ONLY - DELIBERATELY NO EXTRACTION
-------------------------------------------
tools/ingest_coldstorage_tar.py would also materialise its TARGETS to
alpaca_minute/<TICKER>.parquet, overwriting the 26 curated files and
REGRESSING the millis timestamp fix applied by
validate_alpaca_vs_ohlcv.py - those parquets were rebuilt from `millis`
(seconds) because the CSV `timestamp` column is naive Eastern. This
script reads tar headers only and writes nothing but a report.

Compares against the saved gzip inventory in
data/coldstorage_inventory.json, so only the bzip2 archive is scanned.

Writes data/bz2_twin_inventory.json.
"""
import json
import tarfile
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
INVENTORY = REPO / "data" / "coldstorage_inventory.json"
OUT = REPO / "data" / "bz2_twin_inventory.json"

CANDIDATES = [
    COLD / "market-data.tar",
    COLD / "archive" / "raw" /
    "alpaca-minute-bars_1999-01_2019-09_7859tickers_snap2019-09-19.tar.bz2",
]
WANTED = ["SPY", "QQQ", "QQQQ", "DIA", "XLE", "XLF", "YHOO", "AOL",
          "WCOM", "XLK", "AAPL", "TQQQ", "IWM"]


def main():
    src = next((p for p in CANDIDATES if p.exists()), None)
    if src is None:
        raise SystemExit(f"bzip2 archive not found in {CANDIDATES}")
    print(f"scanning {src.name} ({src.stat().st_size/1e9:.1f} GB, bzip2)")
    print("bzip2 is ~10x slower than gzip per byte - expect 70-110 min\n")

    inv = defaultdict(lambda: {"files": 0, "empty": 0, "bytes": 0,
                               "min_month": None, "max_month": None})
    t0, n = time.time(), 0
    with tarfile.open(src, "r|*") as tf:
        for m in tf:
            if not m.isfile():
                continue
            n += 1
            parts = m.name.split("/")
            if len(parts) < 3 or not parts[2].endswith(".csv"):
                continue
            ticker = parts[1]
            stem = parts[2][:-4]
            empty = stem.endswith("_EMPTY")
            if empty:
                stem = stem[:-6]
            month = stem.rsplit("_", 1)[-1][:7] if "_" in stem else None
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
            if n % 250_000 == 0:
                el = time.time() - t0
                print(f"  {n:,} members, {len(inv):,} tickers, {el:.0f}s "
                      f"({n/el:,.0f}/s)", flush=True)
    el = time.time() - t0
    print(f"  DONE {n:,} members, {len(inv):,} tickers, {el/60:.1f} min\n")

    inv = dict(inv)
    gz = {}
    if INVENTORY.exists():
        gz = json.loads(INVENTORY.read_text()).get("pigz", {}).get(
            "tickers", {})

    def real(d, t):
        e = d.get(t)
        return 0 if e is None else e["files"] - e["empty"]

    print(f"{'ticker':8}{'bz2 (09-19)':>16}{'gzip (09-23)':>16}  verdict")
    print("-" * 62)
    wins = []
    for t in WANTED:
        rb, rg = real(inv, t), real(gz, t)
        if rb > rg:
            v = "*** bz2 HAS MORE ***"
            wins.append(t)
        elif rb == rg:
            v = "same"
        else:
            v = "gzip has more"
        print(f"{t:8}{rb:>16}{rg:>16}  {v}")

    only_bz2 = sorted(set(inv) - set(gz))
    only_gz = sorted(set(gz) - set(inv))
    better = [t for t in inv if real(inv, t) > real(gz, t)]

    print(f"\ntickers only in bz2 : {len(only_bz2):,}")
    print(f"tickers only in gzip: {len(only_gz):,}")
    print(f"tickers where bz2 has MORE real months: {len(better):,}")
    if only_bz2[:20]:
        print(f"  sample only-in-bz2: {', '.join(only_bz2[:20])}")

    OUT.write_text(json.dumps({
        "archive": str(src), "members": n, "tickers": len(inv),
        "wanted_comparison": {t: {"bz2": real(inv, t), "gzip": real(gz, t)}
                              for t in WANTED},
        "only_in_bz2": only_bz2, "only_in_gzip": only_gz,
        "bz2_has_more_months": sorted(better)[:2000],
        "tickers_detail": inv}, indent=2), encoding="utf-8")

    print(f"\nVERDICT: ", end="")
    if wins or only_bz2 or better:
        print(f"the bzip2 capture ADDS data - keep it. "
              f"{len(better):,} tickers richer, {len(only_bz2):,} unique.")
    else:
        print("the bzip2 capture adds nothing. Redundant; safe to delete "
              "once the gzip copy is backed up.")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
