#!/usr/bin/env python3
"""Consolidate every macro / reference series into one tidy parquet.

SCOPE
-----
Everything that is not a price bar: FRED levels, ALFRED point-in-time
vintages, Ken French factor and portfolio returns, Shiller's 1871
monthly series, Jorda-Schularick-Taylor macrohistory, the EPU index and
the Moody's Aaa/Baa corporate yields.

TIDY LONG FORMAT
----------------
    series_id | date | value | source | vintage_date | unit

One row per observation. Long format because these series have wildly
different frequencies (daily factors, monthly CPI, annual JST) and
column sets; a wide table would be mostly nulls and would need
rebuilding every time a series is added.

VINTAGE IS A FIRST-CLASS COLUMN, NOT A SEPARATE TABLE
-----------------------------------------------------
`vintage_date` is the date a value BECAME KNOWN, which is not the date
it describes. FRED serves the current (revised) vintage; ALFRED serves
what was actually published at the time. Finding 11 established that
using revised macro data is lookahead - GDP for Q1 is not knowable in
Q1. Keeping vintage in the same table means a query cannot accidentally
forget it: filter `vintage_date <= decision_date` and the lookahead is
structurally impossible.

NULL vintage_date means the series is not revised (market prices,
factor returns) or no point-in-time source exists - in which case it is
NOT safe for decision-time backtests and the manifest says so.

Writes E:/ColdStorage/archive/derived/reference_master/reference.parquet
"""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
OUT = COLD / "archive" / "derived" / "reference_master"
DATA = REPO / "data"

rows = []
notes = []


def add(series_id, dates, values, source, vintage=None, unit=None):
    df = pd.DataFrame({"date": pd.to_datetime(dates, errors="coerce"),
                       "value": pd.to_numeric(values, errors="coerce")})
    df = df.dropna(subset=["date"])
    if df.empty:
        return 0
    df["series_id"] = series_id
    df["source"] = source
    df["vintage_date"] = pd.to_datetime(vintage) if vintage else pd.NaT
    df["unit"] = unit
    rows.append(df)
    return len(df)


def load_fred():
    n = 0
    for f in sorted((DATA / "historical_long").glob("FRED_*.json")):
        try:
            p = json.loads(f.read_text())
        except Exception as e:
            notes.append(f"{f.name}: {e}")
            continue
        obs = p.get("observations") or p.get("prices") or p.get("data")
        if not obs:
            notes.append(f"{f.name}: no observations key ({list(p)[:6]})")
            continue
        d = pd.DataFrame(obs)
        dc = next((c for c in ("date", "Date") if c in d), None)
        vc = next((c for c in ("value", "close", "Close") if c in d), None)
        if dc is None or vc is None:
            notes.append(f"{f.name}: cols {list(d.columns)[:6]}")
            continue
        n += add(f.stem.replace("FRED_", ""), d[dc], d[vc], "fred")
    return n


def load_vintage():
    """ALFRED point-in-time. vintage_date is the whole point."""
    n = 0
    vdir = DATA / "vintage"
    if not vdir.exists():
        return 0
    for f in sorted(vdir.glob("*.json")):
        try:
            p = json.loads(f.read_text())
        except Exception as e:
            notes.append(f"vintage/{f.name}: {e}")
            continue
        obs = p.get("observations") or p.get("data")
        if not obs:
            notes.append(f"vintage/{f.name}: keys {list(p)[:6]}")
            continue
        d = pd.DataFrame(obs)
        dc = next((c for c in ("date", "observation_date") if c in d), None)
        vc = next((c for c in ("value",) if c in d), None)
        rc = next((c for c in ("realtime_start", "first_available",
                               "vintage_date") if c in d), None)
        if dc is None or vc is None:
            notes.append(f"vintage/{f.name}: cols {list(d.columns)[:6]}")
            continue
        sub = pd.DataFrame({
            "date": pd.to_datetime(d[dc], errors="coerce"),
            "value": pd.to_numeric(d[vc], errors="coerce"),
            "vintage_date": (pd.to_datetime(d[rc], errors="coerce")
                             if rc else pd.NaT)})
        sub = sub.dropna(subset=["date"])
        sub["series_id"] = f.stem
        sub["source"] = "alfred"
        sub["unit"] = None
        rows.append(sub)
        n += len(sub)
    return n


def load_deep():
    n = 0
    ddir = DATA / "deep_history"
    for f in sorted(ddir.glob("*.json")):
        try:
            p = json.loads(f.read_text())
        except Exception as e:
            notes.append(f"deep/{f.name}: {e}")
            continue
        obs = p.get("observations") or p.get("data")
        if not obs or not isinstance(obs, list):
            notes.append(f"deep/{f.name}: keys {list(p)[:6]}")
            continue
        d = pd.DataFrame(obs)
        dc = next((c for c in ("date", "Date") if c in d), None)
        if dc is None:
            # EPU publishes Year + Month rather than a date column.
            if {"Year", "Month"} <= set(d.columns):
                d = d.assign(date=pd.to_datetime(
                    dict(year=pd.to_numeric(d["Year"], errors="coerce"),
                         month=pd.to_numeric(d["Month"], errors="coerce"),
                         day=1), errors="coerce"))
                d = d.drop(columns=["Year", "Month"])
                dc = "date"
            # JST is a COUNTRY PANEL - one row per (year, country), so it
            # must fan out to series_id "jst:<iso>:<column>" or every
            # country would collapse into one series.
            elif "year" in d.columns and "iso" in d.columns:
                d = d.assign(date=pd.to_datetime(
                    pd.to_numeric(d["year"], errors="coerce").astype("Int64")
                    .astype("string") + "-01-01", errors="coerce"))
                for iso, g in d.groupby("iso"):
                    for c in g.columns:
                        if c in ("date", "year", "country", "iso", "ifs"):
                            continue
                        v = pd.to_numeric(g[c], errors="coerce")
                        if v.notna().sum() == 0:
                            continue
                        n += add(f"jst:{iso}:{c}", g["date"], v,
                                 "deep_history")
                continue
            else:
                notes.append(f"deep/{f.name}: cols {list(d.columns)[:8]}")
                continue
        # every numeric column becomes its own series
        for c in d.columns:
            if c == dc:
                continue
            v = pd.to_numeric(d[c], errors="coerce")
            if v.notna().sum() == 0:
                continue
            n += add(f"{f.stem}:{c}", d[dc], v, "deep_history")
    return n


def load_csv_series():
    n = 0
    for f, sid in ((DATA / "_AAA.csv", "MOODY_AAA"),
                   (DATA / "_BAA.csv", "MOODY_BAA")):
        if not f.exists():
            continue
        d = pd.read_csv(f)
        d.columns = ["date", "value"][:len(d.columns)]
        n += add(sid, d["date"], d["value"], "fred", unit="percent")
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    counts = {
        "fred": load_fred(),
        "alfred_vintage": load_vintage(),
        "deep_history": load_deep(),
        "moodys_csv": load_csv_series(),
    }
    if not rows:
        raise SystemExit("no reference data found")
    out = pd.concat(rows, ignore_index=True)
    out = out[["series_id", "date", "value", "source", "vintage_date", "unit"]]
    out = out.sort_values(["series_id", "date"]).reset_index(drop=True)
    dest = OUT / "reference.parquet"
    out.to_parquet(dest, index=False, compression="zstd")

    summary = (out.groupby(["source", "series_id"])
                 .agg(rows=("value", "size"), first=("date", "min"),
                      last=("date", "max"),
                      has_vintage=("vintage_date",
                                   lambda s: bool(s.notna().any())))
                 .reset_index())
    summary.to_parquet(OUT / "reference_index.parquet", index=False)

    print(f"{len(out):,} observations, {out.series_id.nunique()} series")
    for k, v in counts.items():
        print(f"  {k:16} {v:>10,}")
    pit = summary[summary.has_vintage]
    print(f"\npoint-in-time safe (has vintage_date): {len(pit)} series")
    print(f"NOT vintage-safe: {len(summary)-len(pit)} series "
          f"- do not use these for decision-time backtests")
    print(f"\nby source:")
    for s, g in summary.groupby("source"):
        print(f"  {s:14} {len(g):4} series  "
              f"{g['first'].min().date()} .. {g['last'].max().date()}")
    if notes:
        print(f"\nunparsed ({len(notes)}):")
        for x in notes[:12]:
            print(f"  {x}")
    print(f"\nwrote {dest} ({dest.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
