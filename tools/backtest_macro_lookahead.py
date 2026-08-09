#!/usr/bin/env python3
"""How much does macro lookahead inflate a backtest?

Runs one identical strategy two ways and compares:

  NAIVE    joins the macro series on its period label - the value for
           "July" is assumed knowable on 31 July. This is what almost
           every macro backtest does by default.
  VINTAGE  gates on the ALFRED publication date, so July payrolls only
           become usable around 7 August, and the value used is the one
           FIRST PUBLISHED rather than today's revised figure.

Strategy (deliberately plain, so the comparison is about the data and
not about strategy cleverness):

    at each month end, if payrolls have grown over the last 3 months
    -> hold SPY for the following month, else hold cash at the 13-week
    T-bill yield.

Writes data/macro_lookahead_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.vintage_data import load_vintage, value_as_of  # noqa: E402

DATA = Path("data/historical_long")
OUT = Path("data/macro_lookahead_study.json")
START, END = "1994-01-31", "2026-03-31"


def load_prices(ticker):
    payload = json.loads((DATA / f"{ticker}.json").read_text())
    s = pd.Series({p["date"]: p["close"] for p in payload["prices"]},
                  dtype=float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def payroll_growth(decision_date, mode):
    """3-month payroll change as visible on decision_date.

    mode="vintage": only values published on or before the date, using
    the figure as first released.
    mode="naive":   the period-label join - assumes a month's number is
    available on that month's last day, and (in the general case) uses
    today's revised value.
    """
    df = load_vintage("PAYEMS").sort_values("date")
    cutoff = pd.Timestamp(decision_date)

    if mode == "vintage":
        visible = df[df["first_available"] <= cutoff].sort_values("date")
    else:
        visible = df[df["date"] <= cutoff]

    if len(visible) < 4:
        return None
    latest = visible.iloc[-1]["value"]
    three_ago = visible.iloc[-4]["value"]
    return latest - three_ago


def run(mode, month_ends, spy, cash_yield):
    """Returns a monthly return series and the position taken."""
    rows = []
    for i in range(len(month_ends) - 1):
        decision, nxt = month_ends[i], month_ends[i + 1]
        growth = payroll_growth(decision, mode)
        in_market = growth is not None and growth > 0

        px_now = spy.asof(decision)
        px_next = spy.asof(nxt)
        if pd.isna(px_now) or pd.isna(px_next):
            continue

        if in_market:
            ret = px_next / px_now - 1.0
        else:
            annual = cash_yield.asof(decision)
            annual = 0.0 if pd.isna(annual) else float(annual) / 100.0
            ret = (1 + annual) ** (1 / 12) - 1

        rows.append({"date": nxt, "ret": ret, "in_market": bool(in_market)})
    return pd.DataFrame(rows).set_index("date")


def stats(returns):
    r = returns.dropna()
    if r.empty:
        return {}
    growth = float((1 + r).prod())
    years = len(r) / 12.0
    curve = (1 + r).cumprod()
    drawdown = curve / curve.cummax() - 1.0
    vol = float(r.std(ddof=1) * np.sqrt(12))
    cagr = growth ** (1 / years) - 1
    return {
        "cagr_pct": float(cagr * 100),
        "vol_pct": float(vol * 100),
        "max_drawdown_pct": float(drawdown.min() * 100),
        "sharpe_naive": float(cagr / vol) if vol else float("nan"),
        "total_growth_x": growth,
        "months": int(len(r)),
    }


def main():
    spy = load_prices("SPY")
    try:
        cash = load_prices("^IRX")
    except FileNotFoundError:
        cash = pd.Series(dtype=float)

    month_ends = list(pd.date_range(START, END, freq="ME"))

    naive = run("naive", month_ends, spy, cash)
    vintage = run("vintage", month_ends, spy, cash)

    joined = naive.join(vintage, lsuffix="_naive", rsuffix="_vintage").dropna()
    disagreements = int((joined["in_market_naive"]
                         != joined["in_market_vintage"]).sum())

    buy_hold = spy.resample("ME").last().pct_change().dropna()
    buy_hold = buy_hold[(buy_hold.index >= joined.index.min())
                        & (buy_hold.index <= joined.index.max())]

    result = {
        "window": {"start": str(joined.index.min().date()),
                   "end": str(joined.index.max().date())},
        "naive": stats(joined["ret_naive"]),
        "vintage": stats(joined["ret_vintage"]),
        "buy_and_hold": stats(buy_hold),
        "signal_disagreements": disagreements,
        "signal_disagreement_pct": float(disagreements / len(joined) * 100),
        "months_in_market_naive": int(joined["in_market_naive"].sum()),
        "months_in_market_vintage": int(joined["in_market_vintage"].sum()),
    }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"window {result['window']['start']} -> {result['window']['end']}"
          f"   ({result['naive']['months']} months)\n")
    header = f"{'':16}{'CAGR':>8}{'vol':>8}{'maxDD':>9}{'growth':>9}"
    print(header)
    for label, key in [("naive (lookahead)", "naive"),
                       ("vintage (correct)", "vintage"),
                       ("buy & hold SPY", "buy_and_hold")]:
        s = result[key]
        print(f"{label:16}{s['cagr_pct']:>7.2f}%{s['vol_pct']:>7.2f}%"
              f"{s['max_drawdown_pct']:>8.2f}%{s['total_growth_x']:>8.2f}x")

    gap = result["naive"]["cagr_pct"] - result["vintage"]["cagr_pct"]
    print(f"\nlookahead premium: {gap:+.2f}pp CAGR")
    print(f"signal disagreements: {disagreements} of {len(joined)} months "
          f"({result['signal_disagreement_pct']:.1f}%)")
    print(f"months in market: naive {result['months_in_market_naive']}, "
          f"vintage {result['months_in_market_vintage']}")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
