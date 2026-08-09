#!/usr/bin/env python3
"""Datasets that buy INDEPENDENT SAMPLES, which is our binding constraint.

Finding 29 established that no amount of compute fixes ~32 independent
annual observations from one index. Finding 30 showed what deep history
buys: the Depression alone reversed the leveraged-sleeve conclusion.

This pulls the remaining sources that add independent observations
rather than more of the same:

  JST Macrohistory   17 advanced economies, 1870-2020, annual real
                     returns on equity/housing/bonds/bills. The single
                     largest sample expansion available for free. A US
                     sample cannot contain Japan 1990 or the Nordic
                     banking crises; this does. Cross-country crashes
                     are far closer to independent draws than
                     overlapping US windows are.

  French 48 industry 48 daily portfolios from 1926. Not 48 independent
                     samples - they share a market factor - but 48
                     different exposures to the same century, which is
                     the right test for whether a rule works on
                     something other than the aggregate it was fitted to.

  French momentum    Daily UMD from 1926. The academic version of trend
                     following, and the honest benchmark for whether our
                     overlay is doing anything a documented factor does
                     not already do.

  Developed 3-factor Daily international factors, for out-of-sample
                     geography.

  EPU index          Baker/Bloom/Davis policy uncertainty, monthly from
                     1985. Turns "Trump/tariffs/geopolitics" from a
                     narrative into a measurable series.

Writes data/deep_history/*.json
"""
import io
import json
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

OUT = Path("data/deep_history")

SOURCES = {
    "jst_macrohistory": (
        "https://www.macrohistory.net/app/download/9834512569/JSTdatasetR6.xlsx",
        "xlsx",
        "Jorda-Schularick-Taylor: 17 economies, 1870-2020, annual returns"),
    "french_48industry_daily": (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "48_Industry_Portfolios_daily_CSV.zip", "ffzip",
        "48 US industry portfolios, daily from 1926"),
    "french_momentum_daily": (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "F-F_Momentum_Factor_daily_CSV.zip", "ffzip",
        "Daily UMD momentum factor from 1926"),
    "french_developed_daily": (
        "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "Developed_3_Factors_Daily_CSV.zip", "ffzip",
        "Developed-market daily 3 factors"),
    "epu_us": (
        "https://www.policyuncertainty.com/media/US_Policy_Uncertainty_Data.xlsx",
        "xlsx",
        "Baker/Bloom/Davis economic policy uncertainty, monthly from 1985"),
}


def fetch(url, timeout=180):
    r = subprocess.run(["curl", "-sS", "-L", "-m", str(timeout),
                        "--retry", "3", "-A", "Mozilla/5.0", url],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl {r.returncode}: {r.stderr.decode()[:200]}")
    if not r.stdout:
        raise RuntimeError("empty response")
    return r.stdout


def parse_ff_zip(raw):
    """French CSVs: prose header, a dated block, then an annual block."""
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")

    lines = text.splitlines()
    header = None
    rows = []
    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if header is None:
            # The header row is the one preceding the first dated row.
            if len(parts) > 1 and parts[0] == "" and any(parts[1:]):
                header = ["date"] + parts[1:]
            continue
        if parts and len(parts[0]) == 8 and parts[0].isdigit():
            try:
                rows.append([parts[0]] + [float(v) for v in parts[1:]])
            except ValueError:
                continue
    if not rows:
        raise RuntimeError("no dated rows parsed")
    width = len(rows[0])
    if header is None or len(header) != width:
        header = ["date"] + [f"c{i}" for i in range(1, width)]
    df = pd.DataFrame([r for r in rows if len(r) == width], columns=header)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    for c in df.columns[1:]:
        # French encodes missing as -99.99 / -999; percent -> decimal.
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df.loc[df[c] <= -99, c] = pd.NA
        df[c] = df[c] / 100.0
    return df


def parse_xlsx(raw):
    xl = pd.ExcelFile(io.BytesIO(raw))
    sheet = next((s for s in xl.sheet_names
                  if s.lower() in ("data", "main")), xl.sheet_names[0])
    return xl.parse(sheet)


def save(name, df, note):
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": name,
        "note": note,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "n_rows": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "observations": json.loads(
            df.to_json(orient="records", date_format="iso")),
    }
    (OUT / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")
    size_mb = (OUT / f"{name}.json").stat().st_size / 1e6
    print(f"  {name:26} {len(df):>7} rows  {len(df.columns):>3} cols  "
          f"{size_mb:>6.1f} MB")


def main():
    print(f"downloading long-sample datasets -> {OUT}\n")
    ok, failed = 0, []
    for name, (url, kind, note) in SOURCES.items():
        try:
            raw = fetch(url)
            df = parse_ff_zip(raw) if kind == "ffzip" else parse_xlsx(raw)
            save(name, df, note)
            ok += 1
        except Exception as exc:
            print(f"  {name:26} FAILED: {type(exc).__name__}: {exc}")
            failed.append(name)
    print(f"\n{ok}/{len(SOURCES)} succeeded")
    if failed:
        print("FAILED:", ", ".join(failed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
