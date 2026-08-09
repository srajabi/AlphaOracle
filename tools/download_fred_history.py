#!/usr/bin/env python3
"""Download FRED macro series into data/historical_long/.

WHY curl AND NOT requests
-------------------------
`fred.stlouisfed.org` sits behind Akamai, which tarpits Python's TLS
fingerprint: the TCP connect and TLS handshake both succeed, then the
server never sends a byte and the client sits until timeout. urllib and
requests both hang; curl returns 200 in 0.13s from the same machine,
same second. It is not a network block, an IPv6 problem, or a firewall -
it is client fingerprinting, so it will follow us onto a CI runner.

`api.stlouisfed.org` (the real API) is NOT behind that protection and
works from Python directly - but it needs a free API key. That path is
also the one that serves ALFRED vintages, which is what
lookahead-free backtesting actually requires. See VINTAGES below.

So: curl subprocess for the keyless path today, API key for vintages.

REVISION WARNING
----------------
These are *current* values, not point-in-time. Payrolls are published
~3 weeks late and revised twice; GDP is revised for years. Backtesting a
2008 decision against today's series feeds the model numbers that did
not exist until 2010 - lookahead bias living inside the data, where the
repo's causality tests cannot see it. Use these for CONTEXT and regime
labelling, not for timing entries, until the vintage path lands.

Usage:
    python tools/download_fred_history.py
    python tools/download_fred_history.py --test
"""
import argparse
import io
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

OUT = Path("data/historical_long")
BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

# series -> (why it earns its place, revision behaviour)
SERIES = {
    "T10Y2Y": ("10y-2y term spread - classic recession signal",
               "market-derived, not revised"),
    "T10Y3M": ("10y-3m term spread - the stronger recession predictor",
               "market-derived, not revised"),
    "BAMLH0A0HYM2": ("ICE BofA HY option-adjusted spread - the real "
                     "credit stress read, cleaner than HYG/LQD",
                     "market-derived, not revised"),
    "NFCI": ("Chicago Fed National Financial Conditions Index",
             "weekly, lightly revised"),
    "VIXCLS": ("VIX close - cross-check against our own ^VIX",
               "market-derived, not revised"),
    "DTWEXBGS": ("Broad trade-weighted dollar",
                 "market-derived, not revised"),
    "UNRATE": ("Unemployment rate", "REVISED - context only"),
    "CPIAUCSL": ("CPI all urban", "REVISED - context only"),
    "INDPRO": ("Industrial production", "REVISED - context only"),
    "PAYEMS": ("Nonfarm payrolls", "HEAVILY REVISED - context only"),
}

TEST_SUBSET = ["T10Y3M", "BAMLH0A0HYM2"]


def fetch_csv(series_id, timeout=90):
    """Fetch one series via curl. See module docstring for why."""
    result = subprocess.run(
        ["curl", "-sS", "-m", str(timeout), "--compressed",
         "--retry", "3", "--retry-delay", "2", BASE + series_id],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed ({result.returncode}): "
                           f"{result.stderr.strip()[:200]}")
    if not result.stdout.strip():
        raise RuntimeError("empty response")
    return pd.read_csv(io.StringIO(result.stdout))


def to_payload(series_id, df, note, revision):
    date_col = df.columns[0]
    value_col = df.columns[1]
    df = df[[date_col, value_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna()

    prices = [{"date": str(d)[:10], "close": float(v)}
              for d, v in zip(df[date_col], df[value_col])]
    if not prices:
        raise RuntimeError("no numeric observations")
    return {
        "ticker": f"FRED:{series_id}",
        "note": note,
        "revision": revision,
        "source": "FRED (current vintage, not point-in-time)",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "start_date": prices[0]["date"],
        "end_date": prices[-1]["date"],
        "total_days": len(prices),
        "prices": prices,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    ids = TEST_SUBSET if args.test else list(SERIES)
    print(f"downloading {len(ids)} FRED series via curl -> {OUT}")

    ok, failed = 0, []
    for series_id in ids:
        note, revision = SERIES[series_id]
        try:
            payload = to_payload(series_id, fetch_csv(series_id), note,
                                 revision)
            (OUT / f"FRED_{series_id}.json").write_text(
                json.dumps(payload), encoding="utf-8")
            flag = "  [REVISED]" if "REVISED" in revision else ""
            print(f"  {series_id:14} {payload['total_days']:>6} obs  "
                  f"{payload['start_date']} -> {payload['end_date']}{flag}")
            ok += 1
        except Exception as exc:
            print(f"  {series_id:14} FAILED: {type(exc).__name__}: {exc}")
            failed.append(series_id)
        time.sleep(1)

    print(f"\n{ok}/{len(ids)} succeeded")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
