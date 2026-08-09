#!/usr/bin/env python3
"""Does a macro filter help more in slow drawdowns than fast ones?

Finding 19 showed macro cannot time 2020. The obvious hypothesis is that
publication lag matters in PROPORTION to how fast the drawdown unfolds:
a 35-day lag is the whole event in a one-month crash and a rounding error
in an 18-month one.

Testable rather than arguable. For each major SPY drawdown:
  - how long peak-to-trough (the speed)
  - did the vintage-correct payroll filter exit, and when relative to the
    trough (early = useful, late = it sold the bottom)
  - how much of the decline it avoided

Writes data/drawdown_speed_study.json.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.backtest_macro_lookahead import load_prices, payroll_growth  # noqa

OUT = Path("data/drawdown_speed_study.json")
MIN_DRAWDOWN = 0.15


def find_drawdowns(monthly, threshold=MIN_DRAWDOWN):
    """Peak-to-trough episodes worse than `threshold`."""
    peak, peak_date = monthly.iloc[0], monthly.index[0]
    trough, trough_date = peak, peak_date
    in_dd, episodes = False, []

    for date, price in monthly.items():
        if price > peak:
            if in_dd and (peak - trough) / peak >= threshold:
                episodes.append({"peak_date": peak_date,
                                 "trough_date": trough_date,
                                 "peak": peak, "trough": trough,
                                 "recovery_date": date})
            peak, peak_date = price, date
            trough, trough_date = price, date
            in_dd = False
        elif price < trough:
            trough, trough_date = price, date
            in_dd = (peak - trough) / peak >= threshold

    if in_dd and (peak - trough) / peak >= threshold:
        episodes.append({"peak_date": peak_date, "trough_date": trough_date,
                         "peak": peak, "trough": trough,
                         "recovery_date": None})
    return episodes


def main():
    spy = load_prices("SPY")
    monthly = spy.resample("ME").last().dropna()
    monthly = monthly[monthly.index >= "1994-01-01"]

    episodes = find_drawdowns(monthly)
    month_ends = list(monthly.index)

    results = []
    for ep in episodes:
        depth = (ep["trough"] - ep["peak"]) / ep["peak"] * 100
        months = len(pd.date_range(ep["peak_date"], ep["trough_date"],
                                   freq="ME"))

        # When did the vintage-correct filter first go risk-off?
        exit_date, exit_price = None, None
        for date in month_ends:
            if date < ep["peak_date"] or date > ep["trough_date"]:
                continue
            growth = payroll_growth(date, "vintage")
            if growth is not None and growth <= 0:
                exit_date, exit_price = date, monthly.loc[date]
                break

        if exit_date is None:
            avoided = 0.0
            timing = "never exited"
        else:
            # Decline still ahead at the exit = what the filter avoided.
            avoided = (ep["trough"] - exit_price) / exit_price * 100
            through = (exit_price - ep["peak"]) / ep["peak"] * 100
            timing = (f"exited {exit_date:%Y-%m} after {through:.0f}% "
                      f"of the fall")

        results.append({
            "peak": f"{ep['peak_date']:%Y-%m}",
            "trough": f"{ep['trough_date']:%Y-%m}",
            "depth_pct": round(depth, 1),
            "months_peak_to_trough": months,
            "speed_pct_per_month": round(depth / max(months, 1), 2),
            "exit": f"{exit_date:%Y-%m}" if exit_date is not None else None,
            "decline_avoided_pct": round(avoided, 1),
            "timing": timing,
        })

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"{'episode':22}{'depth':>8}{'months':>8}{'speed':>9}"
          f"{'avoided':>9}  timing")
    for r in sorted(results, key=lambda x: x["months_peak_to_trough"]):
        print(f"{r['peak']} -> {r['trough']:8}{r['depth_pct']:>7.1f}%"
              f"{r['months_peak_to_trough']:>8}"
              f"{r['speed_pct_per_month']:>8.1f}%"
              f"{r['decline_avoided_pct']:>8.1f}%  {r['timing']}")

    fast = [r for r in results if r["months_peak_to_trough"] <= 6]
    slow = [r for r in results if r["months_peak_to_trough"] > 6]
    for label, group in (("FAST (<=6 months)", fast), ("SLOW (>6 months)", slow)):
        if not group:
            continue
        avg = sum(r["decline_avoided_pct"] for r in group) / len(group)
        exited = sum(1 for r in group if r["exit"])
        print(f"\n{label}: n={len(group)}, exited in {exited}, "
              f"mean decline avoided {avg:.1f}%")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
