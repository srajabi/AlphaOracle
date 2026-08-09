#!/usr/bin/env python3
"""How often should a trend rule check? Daily, weekly, or monthly?

The tension this resolves, both sides of which are in our own registry:

  finding 5  - "Monthly evaluation beats daily for trend."
  finding 13 - the DAILY VIX channel beat monthly SMA200 in COVID
               (-7.6% vs -12.1%).

And the intuition against monthly: a month is a long time to be wrong,
and you can be four weeks late to a real regime change.

The mechanism cuts both ways. Checking more often reacts sooner to a
real trend change AND reacts to more noise. Which dominates is an
empirical question, and it may differ between 1x and leveraged, because
leverage amplifies whipsaw cost more than it amplifies trend capture.

Uses SPY in USD from 1993 so the sample contains dot-com, GFC, COVID and
2022. Frequency effects are currency-independent, and the longer window
matters more here than matching the CAD reporting currency.

Leverage is simulated with daily reset from the underlying's daily
returns, which is how the real funds work - so whipsaw decay appears
rather than being assumed away. Borrowing cost and fund fees are applied
as an explicit annual drag.

Writes data/check_frequency_study.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path("data/historical_long")
OUT = Path("data/check_frequency_study.json")

START, END = "1994-01-01", "2026-03-31"
WARMUP_DAYS = 400          # signal live from the first test day
LETF_ANNUAL_DRAG = 0.0125  # ~0.95% ER + financing, conservative
CASH_ANNUAL = 0.02
BAND = 0.05


def load(ticker):
    payload = json.loads((DATA / f"{ticker}.json").read_text())
    s = pd.Series({p["date"]: p["close"] for p in payload["prices"]},
                  dtype=float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def levered_daily_returns(underlying_ret, leverage):
    """Daily-reset leverage, the way the funds actually behave."""
    if leverage == 1:
        return underlying_ret
    drag = (1 + LETF_ANNUAL_DRAG) ** (1 / 252) - 1
    return underlying_ret * leverage - drag


def build_signal(prices, freq, band=0.0):
    """In/out signal evaluated at `freq`, held until the next check.

    Returns a DAILY series so every variant trades on the same calendar
    and only the DECISION frequency differs.
    """
    sma = prices.rolling(200).mean()
    if freq == "daily":
        check_dates = prices.index
    elif freq == "weekly":
        check_dates = prices.resample("W-FRI").last().index
    elif freq == "monthly":
        check_dates = prices.resample("ME").last().index
    else:
        raise ValueError(freq)

    decisions, state = {}, True
    for date in check_dates:
        px, ma = prices.asof(date), sma.asof(date)
        if pd.isna(px) or pd.isna(ma):
            continue
        if band:
            if state and px < ma * (1 - band):
                state = False
            elif (not state) and px > ma * (1 + band):
                state = True
        else:
            state = px > ma
        decisions[date] = state

    signal = pd.Series(decisions).reindex(prices.index).ffill()
    # CAUSALITY: a decision made at the close of day D governs day D+1.
    return signal.shift(1).fillna(True)


def simulate(daily_ret, signal):
    cash = (1 + CASH_ANNUAL) ** (1 / 252) - 1
    active = signal.reindex(daily_ret.index).ffill().fillna(True)
    ret = np.where(active, daily_ret, cash)
    curve = pd.Series((1 + ret).cumprod(), index=daily_ret.index)
    trades = int((active != active.shift(1)).sum())
    years = len(curve) / 252
    dd = (curve / curve.cummax() - 1).min()
    return {
        "terminal_x": float(curve.iloc[-1]),
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_drawdown_pct": float(dd * 100),
        "trades": trades,
        "trades_per_year": float(trades / years),
        "pct_time_invested": float(active.mean() * 100),
    }


def main():
    prices = load("SPY")
    warm = pd.Timestamp(START) - pd.Timedelta(days=WARMUP_DAYS)
    prices = prices.loc[warm:END]
    underlying = prices.pct_change().dropna()

    results = {}
    for leverage in (1, 3):
        lev_ret = levered_daily_returns(underlying, leverage)
        lev_ret = lev_ret.loc[START:END]
        rows = {}

        buy_hold = simulate(lev_ret, pd.Series(True, index=lev_ret.index))
        rows["buy_hold"] = buy_hold

        for freq in ("daily", "weekly", "monthly"):
            for band in (0.0, BAND):
                sig = build_signal(prices, freq, band)
                label = f"{freq}{'_band5' if band else ''}"
                rows[label] = simulate(lev_ret, sig)
        results[f"{leverage}x"] = rows

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    for lev, rows in results.items():
        print(f"\n=== {lev} SPY, {START[:4]}-{END[:4]}, signal live from "
              f"day one ===")
        print(f"{'variant':16}{'terminal':>11}{'CAGR':>8}{'maxDD':>9}"
              f"{'trades/yr':>11}{'%in':>7}")
        for label, r in rows.items():
            print(f"{label:16}{r['terminal_x']:>10.1f}x{r['cagr_pct']:>7.2f}%"
                  f"{r['max_drawdown_pct']:>8.1f}%"
                  f"{r['trades_per_year']:>10.1f}{r['pct_time_invested']:>6.0f}%")

    print("\nfrequency effect (terminal vs monthly, same band):")
    for lev, rows in results.items():
        for band in ("", "_band5"):
            base = rows.get(f"monthly{band}")
            if not base:
                continue
            for freq in ("daily", "weekly"):
                r = rows.get(f"{freq}{band}")
                gap = (r["terminal_x"] / base["terminal_x"] - 1) * 100
                print(f"  {lev} {freq + band:16} {gap:+8.1f}% vs monthly")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
