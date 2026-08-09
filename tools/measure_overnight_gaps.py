#!/usr/bin/env python3
"""Measure the real overnight gap distribution from minute bars.

Finding 14 sizes the satellite sleeve on an ASSUMED 15% overnight gap in
the underlying (so -22.5% for a 2x rule, -45% for a 3x). That assumption
governs how much of a real portfolio sits in a leveraged ETF, and until
now there was no intraday data to test it against.

An overnight gap here is the 09:30 open against the prior 16:00 close,
using the regular session on both ends. That is deliberately what a
market order at the open actually receives - a thin 04:00 pre-market
print would flatter the result.

Writes data/overnight_gaps.json. Usage:
    python tools/measure_overnight_gaps.py [TICKER ...]
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.minute_data import (  # noqa: E402
    daily_from_minute, load_minute_multi, robust_session_edges,
)


def gaps_from_frame(df):
    """Robust and naive gap series from one already-loaded frame."""
    import pandas as pd
    if not len(df):
        return pd.Series(dtype=float), pd.Series(dtype=float)

    edges = robust_session_edges(df)
    robust = (edges["open_robust"] / edges["close_robust"].shift(1) - 1.0
              ).dropna()

    daily = daily_from_minute(df)
    naive = (daily["open"] / daily["close"].shift(1) - 1.0).dropna()
    return robust, naive

DEFAULT = ["SPY", "QQQ", "TQQQ", "UPRO", "SOXL", "TLT", "GLD"]
OUT = Path("data/overnight_gaps.json")

# Thresholds implied by finding 14's sizing rule.
THRESHOLDS = {"underlying_15pct": -0.15,
              "two_x_22_5pct": -0.225,
              "three_x_45pct": -0.45}


def describe(gaps):
    g = gaps.dropna()
    if len(g) < 30:
        return {"n": int(len(g)), "insufficient": True}
    v = g.values
    out = {
        "n": int(len(v)),
        "start": str(g.index.min().date()),
        "end": str(g.index.max().date()),
        "mean_pct": float(np.mean(v) * 100),
        "std_pct": float(np.std(v, ddof=1) * 100),
        "worst_pct": float(np.min(v) * 100),
        "worst_date": str(g.idxmin().date()),
        "best_pct": float(np.max(v) * 100),
        "p50_pct": float(np.percentile(v, 50) * 100),
        "p1_pct": float(np.percentile(v, 1) * 100),
        "p0_5_pct": float(np.percentile(v, 0.5) * 100),
        "p0_1_pct": float(np.percentile(v, 0.1) * 100),
    }
    for name, level in THRESHOLDS.items():
        breaches = int((v <= level).sum())
        out[f"breaches_{name}"] = breaches
        out[f"breach_rate_{name}"] = float(breaches / len(v))
    return out


def main(tickers):
    print(f"loading {len(tickers)} tickers in one archive pass "
          "(per-ticker passes re-read the same hundreds of GB)...",
          flush=True)
    frames = load_minute_multi(tickers, "1993-01-01", "2026-06-30",
                               session="regular")
    print("loaded; computing gaps\n", flush=True)

    results = {}
    for ticker in tickers:
        try:
            gaps, naive = gaps_from_frame(frames[ticker])
        except Exception as exc:
            print(f"[{ticker}] FAILED: {type(exc).__name__}: {exc}")
            continue
        stats = describe(gaps)
        # Record what the single-print method would have claimed. The
        # difference is bad-tick contamination, and it lands squarely in
        # the tail this analysis exists to measure.
        if len(naive.dropna()) >= 30:
            stats["naive_worst_pct"] = float(naive.min() * 100)
            stats["naive_worst_date"] = str(naive.idxmin().date())
            stats["contamination_pp"] = (stats["naive_worst_pct"]
                                         - stats["worst_pct"])
        results[ticker] = stats
        if stats.get("insufficient"):
            print(f"[{ticker}] only {stats['n']} gaps; skipping")
            continue
        print(f"[{ticker}] n={stats['n']} {stats['start']}..{stats['end']}  "
              f"worst={stats['worst_pct']:.2f}% ({stats['worst_date']})  "
              f"p0.1={stats['p0_1_pct']:.2f}%  "
              f"breaches<=-15%={stats['breaches_underlying_15pct']}",
              flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or DEFAULT))
