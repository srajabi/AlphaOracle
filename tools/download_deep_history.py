#!/usr/bin/env python3
"""Ingest deep market history: French (1926 daily) and Shiller (1871 monthly).

WHY THIS MATTERS MORE THAN ANY OTHER DATA WORK HERE
---------------------------------------------------
Finding 29 established the binding constraint: ~32 independent annual
observations from 32 years of one index, and no amount of compute fixes
it. The only real fix is more independent REGIME EPISODES, and the only
honest source of those is history that actually happened.

SPY starts 1993. That sample contains exactly ONE lost decade
(2000-2010) - so every claim about how a strategy behaves when beta pays
nothing rests on n=1.

  Kenneth French, daily, 1926-07 -> now: adds 1929-1932, the 1930s,
    1937, and the 1966-1982 stagflation grind.
  Shiller, monthly, 1871 -> now: adds the pre-war era and, importantly,
    CAPE, which is the valuation measure finding 28 could not test.

Lost-decade observations go from n=1 to roughly n=4.

Both are free and academically maintained. French returns are TOTAL
RETURN including dividends (Mkt-RF + RF), which is what a backtest
should use; note this differs from the price-only SPY series elsewhere
in this repo, and mixing them silently would understate the older
history.

Writes data/deep_history/{french_daily,shiller_monthly}.json
"""
import io
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

OUT = Path("data/deep_history")
FRENCH_URL = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/"
              "ftp/F-F_Research_Data_Factors_daily_CSV.zip")
SHILLER_URL = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"


def fetch(url, timeout=120):
    """curl rather than requests - some academic hosts tarpit Python TLS
    (see tools/download_fred_history.py for the FRED case)."""
    result = subprocess.run(
        ["curl", "-sS", "-L", "-m", str(timeout), "--retry", "3",
         "-A", "Mozilla/5.0", url],
        capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr.decode()[:200]}")
    return result.stdout


def load_french():
    raw = fetch(FRENCH_URL)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        name = zf.namelist()[0]
        text = zf.read(name).decode("latin-1")

    # The file has a prose header, then the daily block, then an annual
    # block after a blank line. Take only rows with an 8-digit date.
    rows = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5 and len(parts[0]) == 8 and parts[0].isdigit():
            try:
                rows.append((parts[0], float(parts[1]), float(parts[4])))
            except ValueError:
                continue
    if not rows:
        raise RuntimeError("no daily rows parsed from French file")

    df = pd.DataFrame(rows, columns=["date", "mkt_rf", "rf"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    # Percent -> decimal. Total market return = excess + riskfree.
    df["market_return"] = (df["mkt_rf"] + df["rf"]) / 100.0
    df["rf"] = df["rf"] / 100.0
    df = df.sort_values("date").reset_index(drop=True)
    df["index_level"] = (1 + df["market_return"]).cumprod() * 100
    return df[["date", "market_return", "rf", "index_level"]]


def load_shiller():
    raw = fetch(SHILLER_URL)
    xl = pd.ExcelFile(io.BytesIO(raw))
    sheet = next((s for s in xl.sheet_names if "data" in s.lower()),
                 xl.sheet_names[0])
    df = xl.parse(sheet, skiprows=7)
    df.columns = [str(c).strip() for c in df.columns]

    def col(*names):
        for n in names:
            for c in df.columns:
                if c.lower().startswith(n):
                    return c
        return None

    date_c = col("date")
    keep = {"price": col("p", "price"), "dividend": col("d", "dividend"),
            "earnings": col("e", "earnings"), "cpi": col("cpi"),
            "cape": col("cape", "cyclically")}

    out = pd.DataFrame()
    # Shiller encodes the period as a fractional year: 1871.01 is
    # January 1871 and 1871.10 is OCTOBER, not January. So the fraction
    # is hundredths-of-a-year-as-month-number, not a true fraction.
    frac = pd.to_numeric(df[date_c], errors="coerce").dropna()
    year = frac.astype(int)
    month = ((frac - year) * 100).round().astype(int).clip(1, 12)
    out["year"] = year
    out["month"] = month
    df = df.loc[frac.index]
    for name, c in keep.items():
        out[name] = pd.to_numeric(df[c], errors="coerce") if c else pd.NA

    out = out.dropna(subset=["year", "month", "price"])
    out["date"] = pd.to_datetime(
        out["year"].astype(str) + "-" + out["month"].astype(str).str.zfill(2)
        + "-01", errors="coerce")
    out = out.dropna(subset=["date"]).sort_values("date")
    return out[["date", "price", "dividend", "earnings", "cpi", "cape"]]


def save(name, df, note):
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads(df.to_json(orient="records", date_format="iso"))
    payload = {
        "source": name,
        "note": note,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "start_date": str(df["date"].min().date()),
        "end_date": str(df["date"].max().date()),
        "n": len(df),
        "observations": records,
    }
    (OUT / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")
    print(f"  {name:18} {len(df):>7} rows  {payload['start_date']} -> "
          f"{payload['end_date']}")


def main():
    print(f"downloading deep history -> {OUT}\n")
    ok = 0

    try:
        french = load_french()
        save("french_daily", french,
             "Kenneth French daily US market TOTAL return (Mkt-RF + RF) "
             "and risk-free rate. Total return, not price-only.")
        ok += 1
    except Exception as exc:
        print(f"  french_daily      FAILED: {type(exc).__name__}: {exc}")

    try:
        shiller = load_shiller()
        save("shiller_monthly", shiller,
             "Shiller monthly S&P price, dividend, earnings, CPI, CAPE.")
        ok += 1
    except Exception as exc:
        print(f"  shiller_monthly   FAILED: {type(exc).__name__}: {exc}")

    print(f"\n{ok}/2 succeeded")
    return 0 if ok == 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
