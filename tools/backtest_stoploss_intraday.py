#!/usr/bin/env python3
"""TODO #16 - do stop-losses tested on CLOSES lie about stop-losses?

THE QUESTION
------------
Almost every stop-loss backtest triggers on the closing price, because
that is the data people have. A real stop is a resting order: it fires
the moment price TOUCHES the level, which is usually intraday and often
on a day that closes back above it. A close-only test therefore misses
every stop that triggered and recovered - which biases the result in a
specific direction, and nobody quantifies it.

The deliverable is NOT "are stops good". It is: **how wrong is the
close-only approximation?** That number determines whether every
stop-loss result in the literature (and in this repo) is trustworthy.

WHY DAILY HIGH/LOW IS THE RIGHT RESOLUTION
------------------------------------------
A stop cares about one thing: was the level breached. The daily master's
high/low come from aggregating real minute bars, so they answer that
exactly, over the full 1993-2026 SPY history, without reading 87.7 GB.

What high/low CANNOT resolve is intra-day SEQUENCE - whether the low
came before or after the high. That matters only for a same-day
stop-and-re-enter rule, which is not tested here (re-entry is always at
least the next day). Fill price is assumed to be the stop level itself;
in a fast gap-down the real fill is worse, so the intraday results here
are, if anything, OPTIMISTIC about stops.

RULES, deliberately parameter-light
-----------------------------------
Trailing stop at 5/10/15/20% below the running peak since entry.
Re-entry when the close reclaims its 200-day mean - the same trend
condition the gate uses (finding 41c), so stops are being compared
against a mechanism already validated rather than against a new
free parameter.

Each stop level is run BOTH ways - triggered on the low, and triggered
on the close - and the pair is what the study is about.

Writes data/stoploss_intraday_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
COLD = Path("E:/ColdStorage")
DAILY = COLD / "archive" / "derived" / "daily_master" / "ohlcv1m"
REF = COLD / "archive" / "derived" / "reference_master" / "reference.parquet"
OUT = REPO / "data" / "stoploss_intraday_study.json"

TICKERS = ["SPY", "QQQ"]
STOPS = (0.05, 0.10, 0.15, 0.20)
SMA = 200
MIN_BARS = 100
INCEPTION = {"SPY": "1993-01-29", "QQQ": "1999-03-10"}


def load(ticker):
    frames = []
    want = {ticker} | ({"QQQQ"} if ticker == "QQQ" else set())
    for f in sorted(DAILY.glob("*.parquet")):
        d = pd.read_parquet(f, columns=["date", "ticker", "open", "high",
                                        "low", "close", "bars"])
        d = d[d["ticker"].isin(want)]
        if len(d):
            frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d["date"] = pd.to_datetime(d["date"])
    d = (d.sort_values("date").drop_duplicates(subset=["date"])
           .set_index("date"))
    d = d[d["bars"] >= MIN_BARS]
    return d[d.index >= pd.Timestamp(INCEPTION[ticker])]


def load_rf():
    ref = pd.read_parquet(REF, columns=["series_id", "date", "value"])
    rf = ref[ref["series_id"] == "french_daily:rf"]
    return rf.set_index(pd.to_datetime(rf["date"]))["value"].sort_index()


def breach_census(df, stop_pct):
    """PURE MEASUREMENT - no strategy, no re-entry, no confound.

    Walks a trailing stop level and counts, day by day, how often the
    intraday LOW breaches it. Splits those into breaches a close-only
    test would ALSO see (close below the level) and breaches it would
    MISS ENTIRELY (low below, close back above).

    This is the honest answer to "how wrong is close-only", because it
    contains no re-entry rule to argue about. The first version of this
    study conflated the two and produced -100% drawdowns: after an
    intraday stop, SPY is nearly always still above its 200-day mean, so
    it re-entered the NEXT day above the sale price and realised a loss
    every cycle. That is a fact about that rule, not about intraday
    triggering.
    """
    close = df["close"].values
    low = df["low"].values
    n = len(close)
    peak = close[0]
    seen = missed = both = 0
    for i in range(1, n):
        peak = max(peak, close[i - 1])
        level = peak * (1 - stop_pct)
        if low[i] <= level:
            seen += 1
            if close[i] <= level:
                both += 1
            else:
                missed += 1
            peak = close[i]          # reset after a trigger, as a stop would
    return {"intraday_breaches": seen, "close_also_saw": both,
            "invisible_to_close": missed,
            "pct_invisible": float(missed / seen * 100) if seen else float("nan")}


def run(df, rf, stop_pct, intraday, cooldown=20):
    """Trailing stop with a COOLDOWN before re-entry.

    Re-entry requires both close > 200d mean AND `cooldown` days elapsed.
    Without the cooldown the rule sells intraday and buys back the next
    day at a higher price, compounding a realised loss on every cycle -
    a pathology of the rule, not a property of intraday stops.
    """
    close = df["close"].values
    low = df["low"].values
    op = df["open"].values
    sma = df["close"].rolling(SMA).mean().values
    n = len(close)

    in_mkt, peak, stops, days_out, wait = True, close[0], 0, 0, 0
    equity = np.ones(n)
    for i in range(1, n):
        r_cash = float(rf.get(df.index[i], 0.0))
        if in_mkt:
            peak = max(peak, close[i - 1])
            level = peak * (1 - stop_pct)
            trigger = (low[i] <= level) if intraday else (close[i] <= level)
            if trigger:
                fill = min(level, op[i]) if intraday else close[i]
                equity[i] = equity[i - 1] * (fill / close[i - 1])
                in_mkt, stops, wait = False, stops + 1, cooldown
                continue
            equity[i] = equity[i - 1] * (close[i] / close[i - 1])
        else:
            days_out += 1
            equity[i] = equity[i - 1] * (1 + r_cash)
            wait = max(wait - 1, 0)
            if wait == 0 and sma[i] == sma[i] and close[i] > sma[i]:
                in_mkt, peak = True, close[i]
    curve = pd.Series(equity, index=df.index)
    years = n / 252
    dd = curve / curve.cummax() - 1
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float(dd.min() * 100),
        "stops": int(stops),
        "stops_per_year": float(stops / years),
        "pct_days_out": float(days_out / n * 100),
        "terminal": float(curve.iloc[-1]),
    }


def main():
    rf = load_rf()
    results = {}
    for t in TICKERS:
        df = load(t)
        if len(df) < 500:
            print(f"{t}: insufficient data")
            continue
        years = len(df) / 252
        bh = (df["close"].iloc[-1] / df["close"].iloc[0])
        bh_dd = float((df["close"] / df["close"].cummax() - 1).min() * 100)
        print(f"\n=== {t} === {df.index.min():%Y-%m-%d}..{df.index.max():%Y-%m-%d}"
              f"  ({len(df):,} days)")
        print(f"buy_hold: {bh:.2f}x  CAGR {(bh**(1/years)-1)*100:.2f}%  "
              f"maxDD {bh_dd:.1f}%")
        print(f"{'stop':>6}{'intraday CAGR':>15}{'close CAGR':>13}"
              f"{'gap':>8}{'intra DD':>10}{'close DD':>10}"
              f"{'intra n':>9}{'close n':>9}")
        print("-" * 80)
        rows = {}
        print("  breach census (no strategy):")
        for s in STOPS:
            c = breach_census(df, s)
            print(f"    {s:.0%} stop: {c['intraday_breaches']:>4} intraday "
                  f"breaches, {c['invisible_to_close']:>4} INVISIBLE to a "
                  f"close-only test ({c['pct_invisible']:.0f}%)")
        print()
        for s in STOPS:
            a = run(df, rf, s, intraday=True)
            b = run(df, rf, s, intraday=False)
            rows[f"{s:.0%}"] = {"intraday": a, "close": b,
                                "census": breach_census(df, s),
                                "cagr_gap_pp": a["cagr_pct"] - b["cagr_pct"]}
            print(f"{s:>5.0%}{a['cagr_pct']:>14.2f}%{b['cagr_pct']:>12.2f}%"
                  f"{a['cagr_pct']-b['cagr_pct']:>7.2f}"
                  f"{a['max_dd_pct']:>9.1f}%{b['max_dd_pct']:>9.1f}%"
                  f"{a['stops']:>9}{b['stops']:>9}")
        results[t] = {"buy_hold_cagr_pct": float((bh**(1/years)-1)*100),
                      "buy_hold_max_dd_pct": bh_dd,
                      "days": int(len(df)), "stops": rows}

    print("\n\nHOW WRONG IS THE CLOSE-ONLY APPROXIMATION?")
    print(f"{'ticker':8}{'stop':>7}{'extra stops':>13}{'CAGR overstated by':>21}")
    print("-" * 49)
    for t, r in results.items():
        for s, x in r["stops"].items():
            extra = x["intraday"]["stops"] - x["close"]["stops"]
            print(f"{t:8}{s:>7}{extra:>13}{-x['cagr_gap_pp']:>19.2f}pp")

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
