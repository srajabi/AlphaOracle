#!/usr/bin/env python3
"""Does concentrating in the largest companies beat the market?

The intuition: SPY is 500 names, QQQ is 100, so surely the top 10 or 25
does better still. Testing the closest thing the free data supports.

WHAT THIS CAN AND CANNOT TEST
-----------------------------
Literal "top 10 by market cap" needs point-in-time index constituents,
which we do not have. French publishes size-sorted portfolios back to
1926, so we can test the LARGEST DECILE - hundreds of names, but the
same directional question: does tilting toward the biggest companies
beat the broad market?

THE THEORY THAT ARGUES AGAINST IT
---------------------------------
Bessembinder (2018): ~4% of US stocks account for ALL net wealth
creation above T-bills; the median stock underperforms cash. Returns are
extremely right-skewed. If a tiny minority drives everything, holding 10
names most likely means holding NONE of them - skewness makes
diversification more necessary, not less.

And reaching the top 10 means the returns already happened. 1980's top
names were IBM, AT&T, Exxon; 2000's were Microsoft, GE, Cisco, Walmart.
Cisco is still below its 2000 peak.

Writes data/concentration_study.json.
"""
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from backtesting.periods import MULTI_REGIME_WINDOWS  # noqa: E402

OUT = REPO / "data" / "concentration_study.json"
URL = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
       "Portfolios_Formed_on_ME_CSV.zip")
DEEP = REPO / "data" / "deep_history" / "french_daily.json"


def fetch_size_portfolios():
    raw = subprocess.run(
        ["curl", "-sS", "-L", "-m", "120", "--retry", "3",
         "-A", "Mozilla/5.0", URL], capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")

    header, rows = None, []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if header is None:
            if len(parts) > 5 and parts[0] == "" and "Lo 10" in line:
                header = ["date"] + parts[1:]
            continue
        if parts and len(parts[0]) == 6 and parts[0].isdigit():
            try:
                rows.append([parts[0]] + [float(v) for v in parts[1:]])
            except ValueError:
                continue
        elif rows and (not parts[0] or not parts[0].isdigit()):
            break          # stop at the next section

    width = len(header)
    df = pd.DataFrame([r for r in rows if len(r) == width], columns=header)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m")
    # French dates are month-START; the market series is resampled to
    # month-END. Align, or an inner join silently yields nothing.
    df["date"] = df["date"] + pd.offsets.MonthEnd(0)
    df = df.set_index("date").sort_index()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df.loc[df[c] <= -99, c] = np.nan
        df[c] = df[c] / 100.0
    return df


def market_monthly():
    payload = json.loads(DEEP.read_text())
    d = pd.DataFrame(payload["observations"])
    d["date"] = pd.to_datetime(d["date"])
    d = d.set_index("date").sort_index()
    return (1 + d["market_return"]).resample("ME").prod() - 1


def stats(r):
    r = r.dropna()
    if len(r) < 60:
        return None
    curve = (1 + r).cumprod()
    years = len(r) / 12
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "vol_pct": float(r.std() * np.sqrt(12) * 100),
        "months": int(len(r)),
    }


def main():
    size = fetch_size_portfolios()
    market = market_monthly()

    # Decile columns, if present.
    deciles = [c for c in size.columns
               if c.strip() in [f"Dec {i}" for i in range(1, 11)]
               or c.strip() in ("Lo 10", "Hi 10")]
    print(f"size portfolios: {size.index.min():%Y-%m} -> "
          f"{size.index.max():%Y-%m}")
    print(f"columns found: {list(size.columns)[:14]}\n")

    combined = pd.concat(
        [size, market.rename("MARKET")], axis=1, join="inner")

    candidates = [c for c in ("Hi 10", "Lo 10", "MARKET") if c in combined]
    extra = [c for c in combined.columns
             if c.strip().startswith("Dec") or "Big" in c or "Small" in c]
    candidates = list(dict.fromkeys(candidates + extra))

    results = {"full_sample": {}, "windows": {}}
    for c in candidates:
        s = stats(combined[c])
        if s:
            results["full_sample"][c.strip()] = s

    for window, (start, end, _why) in MULTI_REGIME_WINDOWS.items():
        rows = {}
        for c in candidates:
            s = stats(combined[c].loc[start:end])
            if s:
                rows[c.strip()] = s
        if rows:
            results["windows"][window] = rows

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"{'portfolio':14}{'CAGR':>8}{'vol':>8}{'maxDD':>9}{'months':>9}")
    print("-" * 48)
    for name, r in results["full_sample"].items():
        print(f"{name:14}{r['cagr_pct']:>7.2f}%{r['vol_pct']:>7.2f}%"
              f"{r['max_dd_pct']:>8.1f}%{r['months']:>9}")

    print("\nCAGR by window\n")
    names = list(results["full_sample"])
    hdr = f"{'window':18}" + "".join(f"{n[:10]:>11}" for n in names)
    print(hdr)
    print("-" * len(hdr))
    for window, rows in results["windows"].items():
        line = f"{window:18}"
        for n in names:
            line += (f"{rows[n]['cagr_pct']:>10.1f}%" if n in rows
                     else f"{'-':>11}")
        print(line)

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
