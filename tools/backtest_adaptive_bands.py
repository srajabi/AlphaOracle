#!/usr/bin/env python3
"""Adaptive bands from trend efficiency, and 4% vs 5% out-of-sample.

TWO QUESTIONS

1. Is 4% really better than 5%? Finding 24's sweep put 4% at 2043x and
   5% at 1474x on one US sample path, but finding 34 showed adjacent
   parameters swing ~38% with almost fully overlapping bootstrap
   intervals. If that gap is noise, the ordering should NOT survive on
   markets that had no part in producing it. Tested on the clean
   out-of-sample regions from finding 35.

2. Can we detect WHIPSAW and widen bands only then?

   A previous attempt scaled bands by realised volatility and came
   second-to-last (finding 34: 9.96% vs 12.30%). It failed for a
   diagnosable reason: volatility rises in crashes as well as chop, so
   the band widened exactly when exiting mattered.

   Kaufman's Efficiency Ratio separates the two. ER = |net change over N|
   / sum(|daily changes| over N). A market that moves 10% in a straight
   line scores near 1.0; one that oscillates to the same endpoint scores
   near 0. High ER = trending (narrow band, react fast). Low ER = chop
   (wide band, ignore noise).

   That is the mechanism the volatility version lacked: it distinguishes
   DIRECTIONLESS movement from large movement.

Writes data/adaptive_band_study.json.
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

OUT = REPO / "data" / "adaptive_band_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"
BASE = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "%s_3_Factors_Daily_CSV.zip")
OOS_REGIONS = {"developed_ex_us": "Developed_ex_US", "japan": "Japan",
               "europe": "Europe", "asia_pac_ex_japan": "Asia_Pacific_ex_Japan"}

ER_WINDOW = 20
FIXED_BANDS = (0.02, 0.03, 0.04, 0.05, 0.06)
# Adaptive: band = lo + (hi - lo) * (1 - ER), so chop -> hi, trend -> lo.
ADAPTIVE = ((0.02, 0.08), (0.03, 0.10), (0.02, 0.12))


def load_us():
    payload = json.loads(DEEP.read_text())
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


def fetch_region(slug):
    raw = subprocess.run(
        ["curl", "-sS", "-L", "-m", "120", "--retry", "3",
         "-A", "Mozilla/5.0", BASE % slug], capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")
    rows = []
    for line in text.splitlines():
        p = [x.strip() for x in line.split(",")]
        if len(p) >= 5 and len(p[0]) == 8 and p[0].isdigit():
            try:
                rows.append((p[0], float(p[1]), float(p[4])))
            except ValueError:
                continue
    df = pd.DataFrame(rows, columns=["date", "mkt_rf", "rf"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.sort_values("date").set_index("date")
    df["market_return"] = (df["mkt_rf"] + df["rf"]) / 100.0
    df["rf"] = df["rf"] / 100.0
    df["index_level"] = (1 + df["market_return"]).cumprod()
    return df[["market_return", "rf", "index_level"]]


def efficiency_ratio(level, window=ER_WINDOW):
    net = (level - level.shift(window)).abs()
    path = level.diff().abs().rolling(window).sum()
    return (net / path.replace(0, np.nan)).clip(0, 1).fillna(0.5)


def gate(level, band):
    """band may be a scalar or a per-date Series."""
    sma = level.rolling(200).mean()
    b = band if isinstance(band, pd.Series) else pd.Series(band,
                                                           index=level.index)
    state, out = True, {}
    for dt in level.index:
        p, m, bb = level.loc[dt], sma.loc[dt], b.loc[dt]
        if pd.notna(m):
            if state and p < m * (1 - bb):
                state = False
            elif (not state) and p > m * (1 + bb):
                state = True
        out[dt] = 1.0 if state else 0.0
    return pd.Series(out).shift(1).fillna(1.0)


def perf(ret, rf, exposure):
    a = exposure.reindex(ret.index).ffill().fillna(1.0)
    r = pd.Series(np.where(a > 0, ret, rf), index=ret.index)
    curve = (1 + r).cumprod()
    years = len(r) / 252
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float((curve / curve.cummax() - 1).min() * 100),
        "switches_per_year": float((a != a.shift(1)).sum() / years),
    }


def evaluate(df, label):
    level, ret, rf = df["index_level"], df["market_return"], df["rf"]
    er = efficiency_ratio(level)
    start = df.index[250]
    seg = slice(start, None)
    rows = {}
    rows["buy_hold"] = perf(ret.loc[seg], rf.loc[seg],
                            pd.Series(1.0, index=level.index))
    for b in FIXED_BANDS:
        rows[f"fixed_{b:.0%}"] = perf(ret.loc[seg], rf.loc[seg],
                                      gate(level, b))
    for lo, hi in ADAPTIVE:
        band = lo + (hi - lo) * (1 - er)
        rows[f"adaptive_{lo:.0%}-{hi:.0%}"] = perf(
            ret.loc[seg], rf.loc[seg], gate(level, band))
    print(f"\n=== {label} ===")
    print(f"{'variant':22}{'CAGR':>8}{'maxDD':>9}{'switch/yr':>11}")
    for name, r in rows.items():
        print(f"{name:22}{r['cagr_pct']:>7.2f}%{r['max_dd_pct']:>8.1f}%"
              f"{r['switches_per_year']:>10.2f}")
    return rows


def main():
    results = {}
    results["US_1926"] = evaluate(load_us(), "US 1926-2026 (in-sample)")

    for name, slug in OOS_REGIONS.items():
        try:
            results[name] = evaluate(fetch_region(slug),
                                     f"{name} (OUT-OF-SAMPLE)")
        except Exception as exc:
            print(f"{name}: FAILED {type(exc).__name__}: {exc}")

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    oos = [k for k in results if k != "US_1926"]
    if oos:
        print("\n\n4% vs 5% OUT-OF-SAMPLE - does the US ordering survive?")
        print(f"{'region':22}{'4%':>9}{'5%':>9}{'winner':>10}")
        wins4 = 0
        for k in oos:
            a = results[k]["fixed_4%"]["cagr_pct"]
            b = results[k]["fixed_5%"]["cagr_pct"]
            wins4 += a > b
            print(f"{k:22}{a:>8.2f}%{b:>8.2f}%{'4%' if a > b else '5%':>10}")
        print(f"  4% wins {wins4}/{len(oos)} out-of-sample regions")

        print("\nBest ADAPTIVE vs best FIXED, per region:")
        for k in oos:
            fixed = {n: v["cagr_pct"] for n, v in results[k].items()
                     if n.startswith("fixed")}
            adapt = {n: v["cagr_pct"] for n, v in results[k].items()
                     if n.startswith("adaptive")}
            bf, ba = max(fixed, key=fixed.get), max(adapt, key=adapt.get)
            print(f"  {k:22} fixed {bf:12} {fixed[bf]:6.2f}%   "
                  f"adaptive {ba:16} {adapt[ba]:6.2f}%")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
