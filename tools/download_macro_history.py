#!/usr/bin/env python3
"""Download macro/cross-asset series into data/historical_long/.

Deliberately price-based rather than macro-statistical. Released
economic data (payrolls, CPI, GDP) is published with lag AND revised for
years afterwards, so backtesting against the current series feeds a 2008
model numbers that did not exist until 2010. That is lookahead bias
living inside the data, where the repo's no-lookahead causality tests
cannot see it. Point-in-time (ALFRED vintage) data is the fix, and is
tracked separately - see spikes/macro_regime_data.md.

Everything here is a market price: published continuously, never
revised, no release lag. Same reason the existing signals (200dma, VIX
term structure, HYG/LQD) hold up out of sample.

Usage:
    python tools/download_macro_history.py
    python tools/download_macro_history.py --test
"""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf

OUT = Path("data/historical_long")

# symbol -> why it is here
SERIES = {
    # --- rates / curve -------------------------------------------------
    "^FVX": "5-year Treasury yield - curve belly",
    "^TYX": "30-year Treasury yield - curve long end",
    # ^TNX (10y) and ^IRX (13w) already present; together these give the
    # 10y-3m slope, the strongest single recession predictor in the
    # literature, plus curve shape rather than a single point.

    # --- commodities ---------------------------------------------------
    "CL=F": "WTI crude - growth/inflation impulse",
    "HG=F": "Copper - the growth half of the copper/gold ratio",
    "GC=F": "Gold futures - the risk half of copper/gold",
    "SI=F": "Silver - industrial/precious hybrid",

    # --- FX ------------------------------------------------------------
    "CAD=X": "USD/CAD - needed for XEQT live-vs-paper parity (finding 17)",
    "EURUSD=X": "EUR/USD - dollar direction cross-check",
    "DX-Y.NYB": "Dollar index - risk-on/off and commodity headwind",

    # --- credit / breadth ----------------------------------------------
    "JNK": "HY credit, second read alongside HYG",
    "AGG": "Aggregate bonds - the canary universe's defensive leg",
}

TEST_SUBSET = ["CAD=X", "HG=F", "^FVX"]


def download(symbol, note, retries=3):
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(symbol, period="max", progress=False,
                             auto_adjust=True)
            if df is None or df.empty:
                print(f"  {symbol:10} EMPTY (attempt {attempt})")
                time.sleep(2 * attempt)
                continue
            if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
                df.columns = df.columns.get_level_values(0)
            prices = []
            for idx, row in df.iterrows():
                prices.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": _f(row.get("Open")),
                    "high": _f(row.get("High")),
                    "low": _f(row.get("Low")),
                    "close": _f(row.get("Close")),
                    "volume": _f(row.get("Volume"), 0),
                })
            payload = {
                "ticker": symbol,
                "note": note,
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "start_date": prices[0]["date"],
                "end_date": prices[-1]["date"],
                "total_days": len(prices),
                "prices": prices,
            }
            safe = symbol.replace("/", "_")
            (OUT / f"{safe}.json").write_text(json.dumps(payload),
                                              encoding="utf-8")
            print(f"  {symbol:10} {len(prices):>6} rows  "
                  f"{prices[0]['date']} -> {prices[-1]['date']}")
            return True
        except Exception as exc:
            print(f"  {symbol:10} attempt {attempt} failed: "
                  f"{type(exc).__name__}: {exc}")
            time.sleep(2 * attempt)
    return False


def _f(value, default=None):
    try:
        out = float(value)
        return out if out == out else default  # NaN check
    except (TypeError, ValueError):
        return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true",
                    help="download a three-symbol subset")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    symbols = TEST_SUBSET if args.test else list(SERIES)
    print(f"downloading {len(symbols)} macro series -> {OUT}")

    ok, failed = 0, []
    for symbol in symbols:
        if download(symbol, SERIES[symbol]):
            ok += 1
        else:
            failed.append(symbol)
        time.sleep(1)

    print(f"\n{ok}/{len(symbols)} succeeded")
    if failed:
        print(f"FAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
