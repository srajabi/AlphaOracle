#!/usr/bin/env python3
"""The clean out-of-sample test: same rule, same FREQUENCY, no US.

The first attempt (tools/backtest_international_trend.py) changed two
things at once - geography AND frequency - and its USA control exposed
the confound: annual absolute momentum lost 1.82pp in the US, where the
same rule family on DAILY US data gained 2.24pp (finding 34). Annual
decisions carry up to a 12-month reaction lag, so 1987, 2020 and most of
2008 are invisible. That test could not answer the geography question.

This holds frequency constant at daily and removes the US:

  Developed ex-US    the clean out-of-sample market
  Japan              the single most informative market for a lost
                     decade - a 30-year bear the US sample has no
                     analogue for
  Europe             independent regime timing
  Asia Pacific ex-JP
  Developed          includes the US, kept as the contaminated control

If the 200-day gate works on markets that did NOT shape the folklore,
the family is real. If it only works in the US, it is a coincidence with
excellent PR.

Writes data/oos_geography_study.json.
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

OUT = REPO / "data" / "oos_geography_study.json"
BASE = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "%s_3_Factors_Daily_CSV.zip")

REGIONS = {
    "developed_ex_us": ("Developed_ex_US", "CLEAN out-of-sample"),
    "japan": ("Japan", "CLEAN - the lost-decade market"),
    "europe": ("Europe", "CLEAN"),
    "asia_pac_ex_japan": ("Asia_Pacific_ex_Japan", "CLEAN"),
    "developed": ("Developed", "contaminated control - includes US"),
}


def fetch_region(slug):
    raw = subprocess.run(
        ["curl", "-sS", "-L", "-m", "120", "--retry", "3",
         "-A", "Mozilla/5.0", BASE % slug],
        capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")
    rows = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5 and len(parts[0]) == 8 and parts[0].isdigit():
            try:
                rows.append((parts[0], float(parts[1]), float(parts[4])))
            except ValueError:
                continue
    df = pd.DataFrame(rows, columns=["date", "mkt_rf", "rf"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.sort_values("date").set_index("date")
    df["ret"] = (df["mkt_rf"] + df["rf"]) / 100.0
    df["rf"] = df["rf"] / 100.0
    df["level"] = (1 + df["ret"]).cumprod()
    return df[["ret", "rf", "level"]]


def gate(level, window=200, band=0.05):
    sma = level.rolling(window).mean()
    state, out = True, {}
    for dt in level.index:
        p, m = level.loc[dt], sma.loc[dt]
        if pd.notna(m):
            if state and p < m * (1 - band):
                state = False
            elif (not state) and p > m * (1 + band):
                state = True
        out[dt] = 1.0 if state else 0.0
    return pd.Series(out).shift(1).fillna(1.0)


def perf(ret, rf, exposure=None):
    if exposure is None:
        r = ret
    else:
        a = exposure.reindex(ret.index).ffill().fillna(1.0)
        r = pd.Series(np.where(a > 0, ret, rf), index=ret.index)
    curve = (1 + r).cumprod()
    years = len(r) / 252
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "years": float(years),
    }


def main():
    results = {}
    for name, (slug, note) in REGIONS.items():
        try:
            df = fetch_region(slug)
        except Exception as exc:
            print(f"{name}: FAILED {type(exc).__name__}: {exc}")
            continue
        # Warmup before the scored window so the signal is live day one.
        exposure = gate(df["level"])
        start = df.index[250]
        seg = df.loc[start:]
        bh = perf(seg["ret"], seg["rf"])
        tr = perf(seg["ret"], seg["rf"], exposure)
        results[name] = {
            "note": note, "start": str(start.date()),
            "end": str(df.index[-1].date()),
            "buy_hold": bh, "trend": tr,
            "edge_pp": tr["cagr_pct"] - bh["cagr_pct"],
            "dd_improvement_pp": tr["max_dd_pct"] - bh["max_dd_pct"],
            "pct_invested": float(
                exposure.reindex(seg.index).ffill().fillna(1.0).mean() * 100),
        }

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("200-day gate, 5% bands, DAILY - frequency held constant\n")
    print(f"{'region':20}{'yrs':>5}{'B&H':>8}{'trend':>8}{'edge':>8}"
          f"{'B&H DD':>9}{'trend DD':>10}{'%in':>6}  status")
    print("-" * 88)
    for name, r in results.items():
        print(f"{name:20}{r['buy_hold']['years']:>5.0f}"
              f"{r['buy_hold']['cagr_pct']:>7.2f}%{r['trend']['cagr_pct']:>7.2f}%"
              f"{r['edge_pp']:>+7.2f}{r['buy_hold']['max_dd_pct']:>8.1f}%"
              f"{r['trend']['max_dd_pct']:>9.1f}%{r['pct_invested']:>5.0f}%"
              f"  {r['note']}")

    clean = {k: v for k, v in results.items() if "CLEAN" in v["note"]}
    if clean:
        edges = [v["edge_pp"] for v in clean.values()]
        dds = [v["dd_improvement_pp"] for v in clean.values()]
        wins = sum(1 for e in edges if e > 0)
        print(f"\nCLEAN out-of-sample markets ({len(clean)}):")
        print(f"  trend beats buy-hold on CAGR in {wins}/{len(clean)}")
        print(f"  median edge            {np.median(edges):+.2f}pp")
        print(f"  median DD improvement  {np.median(dds):+.1f}pp")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
