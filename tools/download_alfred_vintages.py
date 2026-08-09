#!/usr/bin/env python3
"""Download ALFRED point-in-time (initial-release) macro series.

THE PROBLEM THIS SOLVES
-----------------------
FRED serves the CURRENT value of a series. Macro statistics are revised
for years, so a 2008 backtest reading today's PAYEMS is being fed
numbers that did not exist until 2010. That is lookahead bias living
inside the data rather than the code, which is exactly where the repo's
no-lookahead causality tests cannot see it.

ALFRED serves the value AS FIRST PUBLISHED, plus the date it became
public. Both halves matter: knowing July's payrolls were 158,858 is
useless for a 31 July decision if the number was not released until
7 August.

Measured on PAYEMS: median publication lag 35 days, p95 40, max 80.

output_type=4 returns initial releases only. It requires an explicit
realtime range - the default is today-to-today, for which no vintages
exist, and the API returns a 400 that does not obviously say so.

Writes data/vintage/{SERIES}.json with, per observation:
    date            the period the number describes
    value           the value AS FIRST PUBLISHED
    first_available the date it became public  <- gate decisions on this

Usage:
    python tools/download_alfred_vintages.py
    python tools/download_alfred_vintages.py --test
"""
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

OUT = Path("data/vintage")
API = "https://api.stlouisfed.org/fred/series/observations"

# FRED's documented realtime bounds; anything narrower risks silently
# clipping early vintages.
RT_MIN, RT_MAX = "1776-07-04", "9999-12-31"

SERIES = {
    "PAYEMS": "Nonfarm payrolls - the headline labour print",
    "UNRATE": "Unemployment rate",
    "CPIAUCSL": "CPI all urban - headline inflation",
    "INDPRO": "Industrial production",
    "RSAFS": "Retail sales - consumption pulse",
    "HOUST": "Housing starts - rate-sensitive leading indicator",
    "UMCSENT": "Michigan consumer sentiment",
    "ICSA": "Initial jobless claims - weekly, shortest lag",
}

TEST_SUBSET = ["PAYEMS", "ICSA"]


def fetch_initial_releases(series_id, api_key, timeout=60):
    response = requests.get(API, timeout=timeout, params={
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "output_type": 4,            # initial release only
        "realtime_start": RT_MIN,
        "realtime_end": RT_MAX,
    })
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: "
                           f"{response.text[:200]}")
    observations = response.json().get("observations", [])
    if not observations:
        raise RuntimeError("no observations returned")
    return observations


def to_payload(series_id, note, observations):
    rows = []
    for o in observations:
        raw = o.get("value")
        if raw in (None, "", "."):      # FRED encodes missing as "."
            continue
        try:
            value = float(raw)
        except ValueError:
            continue
        rows.append({
            "date": o["date"],
            "value": value,
            "first_available": o["realtime_start"],
        })
    if not rows:
        raise RuntimeError("no numeric observations")

    df = pd.DataFrame(rows)
    lag = (pd.to_datetime(df["first_available"])
           - pd.to_datetime(df["date"])).dt.days
    return {
        "series_id": series_id,
        "note": note,
        "source": "ALFRED initial release (point-in-time)",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "start_date": rows[0]["date"],
        "end_date": rows[-1]["date"],
        "n": len(rows),
        "publication_lag_days": {
            "median": float(lag.median()),
            "p95": float(lag.quantile(0.95)),
            "max": int(lag.max()),
        },
        "observations": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()

    load_dotenv()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("FRED_API_KEY not set (see .env.example). Nothing to do.")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    ids = TEST_SUBSET if args.test else list(SERIES)
    print(f"downloading {len(ids)} ALFRED initial-release series -> {OUT}\n")

    ok, failed = 0, []
    for series_id in ids:
        try:
            payload = to_payload(series_id, SERIES[series_id],
                                 fetch_initial_releases(series_id, api_key))
            (OUT / f"{series_id}.json").write_text(json.dumps(payload),
                                                   encoding="utf-8")
            lag = payload["publication_lag_days"]
            print(f"  {series_id:10} {payload['n']:>5} obs  "
                  f"{payload['start_date']} -> {payload['end_date']}  "
                  f"lag median {lag['median']:.0f}d max {lag['max']}d")
            ok += 1
        except Exception as exc:
            print(f"  {series_id:10} FAILED: {type(exc).__name__}: {exc}")
            failed.append(series_id)
        time.sleep(0.6)          # stay well inside the rate limit

    print(f"\n{ok}/{len(ids)} succeeded")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
