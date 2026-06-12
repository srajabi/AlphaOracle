#!/usr/bin/env python3
"""
Market-entry strategy backtest: how to deploy a cash lump sum.

Question this answers: a large cash position needs to enter the market,
possibly near an all-time high. Which entry rule gives the best trade-off
between forward returns and downside protection?

Strategies compared (deploying capital starting at date T):
  - lump_sum:        everything on day 1
  - dca_6m/12m/24m:  equal monthly tranches over 6/12/24 months
  - sma_gated_12m:   12 monthly tranches, but a tranche only deploys when
                     price > 200-day SMA; paused tranches accumulate and
                     deploy at the first monthly check back above the SMA
  - dip_buy_10:      hold cash until a 10% dip from the start price, then
                     deploy everything; force-deploys at month 24 if no dip
  - ls_sma_managed:  lump sum on day 1, then SMA200 in/out overlay forever
                     (the "enter now but use the signal to exit" approach)

Every strategy is evaluated over every monthly start date with enough
forward history, measured over a fixed horizon. Cash earns a flat yield.
Results are reported for ALL starts and for "at-the-top" starts (price
within 2% of its prior all-time high) - the scenario that matters when
the market looks toppy.

Usage:
    python backtesting/entry_strategies.py
    python backtesting/entry_strategies.py --ticker VT --horizon-years 5
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.run_backtests import load_history

TRADING_DAYS_PER_MONTH = 21
TRADING_DAYS_PER_YEAR = 252


def build_deployment_schedule(prices, sma200, start_idx, horizon_days, strategy,
                              n_days_total):
    """Return a Series of capital fractions deployed per day (index-aligned).

    Fractions sum to <= 1.0. Undeployed capital stays in cash.
    """
    deploy = np.zeros(n_days_total)

    if strategy == "lump_sum" or strategy == "ls_sma_managed":
        deploy[start_idx] = 1.0
        return deploy

    if strategy.startswith("dca_"):
        months = int(strategy.split("_")[1].rstrip("m"))
        tranche = 1.0 / months
        for m in range(months):
            idx = start_idx + m * TRADING_DAYS_PER_MONTH
            if idx >= n_days_total:
                break
            deploy[idx] = tranche
        return deploy

    if strategy == "sma_gated_12m":
        months = 12
        tranche = 1.0 / months
        pending = 0.0
        tranches_released = 0
        m = 0
        while tranches_released < months:
            idx = start_idx + m * TRADING_DAYS_PER_MONTH
            if idx >= n_days_total:
                break
            pending += tranche
            tranches_released += 1
            above = (
                not math.isnan(sma200[idx])
                and prices[idx] > sma200[idx]
            )
            if above:
                deploy[idx] += pending
                pending = 0.0
            m += 1
        # Any still-pending capital deploys at the first day back above SMA
        if pending > 0:
            idx = start_idx + (m - 1) * TRADING_DAYS_PER_MONTH
            for j in range(idx + 1, n_days_total):
                if not math.isnan(sma200[j]) and prices[j] > sma200[j]:
                    deploy[j] += pending
                    pending = 0.0
                    break
        return deploy

    if strategy == "dip_buy_10":
        start_price = prices[start_idx]
        force_idx = min(start_idx + 24 * TRADING_DAYS_PER_MONTH, n_days_total - 1)
        for j in range(start_idx, force_idx + 1):
            if prices[j] <= start_price * 0.90:
                deploy[j] = 1.0
                return deploy
        deploy[force_idx] = 1.0
        return deploy

    raise ValueError(f"Unknown strategy {strategy}")


def simulate(prices, sma200, daily_returns, start_idx, horizon_days, strategy,
             cash_daily_yield):
    """Simulate account value; returns (wealth_multiple, max_drawdown)."""
    n = len(prices)
    end_idx = start_idx + horizon_days
    if end_idx >= n:
        return None

    deploy = build_deployment_schedule(
        prices, sma200, start_idx, horizon_days, strategy, n
    )

    cash = 1.0
    invested = 0.0
    values = np.empty(horizon_days + 1)
    sma_managed = strategy == "ls_sma_managed"

    for step, i in enumerate(range(start_idx, end_idx + 1)):
        if step > 0:
            cash *= 1.0 + cash_daily_yield
            invested *= 1.0 + daily_returns[i]
        # SMA overlay: move fully to cash below SMA, back in above
        if sma_managed and not math.isnan(sma200[i]):
            if prices[i] <= sma200[i] and invested > 0:
                cash += invested
                invested = 0.0
            elif prices[i] > sma200[i] and cash > 0 and step > 0:
                invested += cash
                cash = 0.0
        if deploy[i] > 0:
            amount = min(deploy[i], cash)
            cash -= amount
            invested += amount
        values[step] = cash + invested

    running_max = np.maximum.accumulate(values)
    max_dd = float(np.min(values / running_max - 1.0))
    return float(values[-1]), max_dd


def simulate_decumulation(prices, sma200, daily_returns, start_idx, horizon_days,
                          managed, withdrawal_rate, inflation, cash_daily_yield):
    """Retirement mode: withdraw an inflation-adjusted X%/yr of the initial
    balance, monthly. Returns (ending_balance_real, ruined, max_drawdown).

    managed=False: 100% invested throughout.
    managed=True: SMA200 overlay - fully invested above the SMA, cash below.
    Balances are tracked nominally; the ending balance is deflated back to
    start-date dollars.
    """
    n = len(prices)
    end_idx = start_idx + horizon_days
    if end_idx >= n:
        return None

    monthly_withdrawal = withdrawal_rate / 12.0  # of initial balance
    daily_inflation = (1.0 + inflation) ** (1.0 / TRADING_DAYS_PER_YEAR) - 1.0

    cash = 0.0
    invested = 1.0
    price_level = 1.0
    values = []
    days_since_withdrawal = 0

    for step, i in enumerate(range(start_idx, end_idx + 1)):
        if step > 0:
            invested *= 1.0 + daily_returns[i]
            cash *= 1.0 + cash_daily_yield
            price_level *= 1.0 + daily_inflation
            days_since_withdrawal += 1

        if managed and not math.isnan(sma200[i]):
            if prices[i] <= sma200[i] and invested > 0:
                cash += invested
                invested = 0.0
            elif prices[i] > sma200[i] and cash > 0:
                invested += cash
                cash = 0.0

        if days_since_withdrawal >= TRADING_DAYS_PER_MONTH:
            days_since_withdrawal = 0
            need = monthly_withdrawal * price_level
            take_cash = min(cash, need)
            cash -= take_cash
            invested -= (need - take_cash)
            if invested < 0:  # portfolio exhausted
                return 0.0, True, -1.0

        values.append(cash + invested)

    series = np.array(values)
    running_max = np.maximum.accumulate(series)
    max_dd = float(np.min(series / running_max - 1.0))
    return float((series[-1]) / price_level), False, max_dd


def run_decumulation(args, prices, sma200, daily_returns, dates, running_ath,
                     cash_daily_yield):
    horizon_days = int(args.horizon_years * TRADING_DAYS_PER_YEAR)
    n = len(prices)
    start_indices = list(range(200, n - horizon_days - 1, TRADING_DAYS_PER_MONTH))
    if not start_indices:
        print("Not enough history for this horizon.")
        return

    print(f"DECUMULATION: {args.withdrawal_rate:.1%}/yr withdrawal "
          f"(inflation-adjusted at {args.inflation:.1%}), "
          f"{args.horizon_years:.0f}y horizon, {len(start_indices)} start dates "
          f"({dates[start_indices[0]].date()} to {dates[start_indices[-1]].date()})")
    print("NOTE: start windows overlap heavily; treat rates as illustrative, "
          "not independent samples.")

    rows = []
    for start_idx in start_indices:
        at_top = prices[start_idx] >= running_ath[start_idx] * (1 - args.ath_threshold)
        for managed, name in [(False, "all_equity"), (True, "equity_sma_managed")]:
            result = simulate_decumulation(
                prices, sma200, daily_returns, start_idx, horizon_days,
                managed, args.withdrawal_rate, args.inflation, cash_daily_yield)
            if result is None:
                continue
            ending, ruined, max_dd = result
            rows.append({"start": str(dates[start_idx].date()), "strategy": name,
                         "at_top": bool(at_top), "ending_real": ending,
                         "ruined": ruined, "max_drawdown": max_dd})

    results = pd.DataFrame(rows)
    summary = []
    for cohort, subset in [("all_starts", results),
                           ("at_top_starts", results[results.at_top])]:
        for name in ["all_equity", "equity_sma_managed"]:
            s = subset[subset.strategy == name]
            survivors = s[~s.ruined]
            summary.append({
                "cohort": cohort,
                "strategy": name,
                "starts": len(s),
                "ruin_rate_pct": round(float(s["ruined"].mean()) * 100, 1),
                "median_ending_real": round(float(s["ending_real"].median()), 3),
                "p5_ending_real": round(float(s["ending_real"].quantile(0.05)), 3),
                "median_max_dd": round(float(survivors["max_drawdown"].median()), 4)
                if len(survivors) else None,
            })
    summary_df = pd.DataFrame(summary)
    for cohort in ["all_starts", "at_top_starts"]:
        block = summary_df[summary_df.cohort == cohort]
        print(f"\n=== {cohort} ({block['starts'].iloc[0]} start dates) ===")
        print(block.drop(columns=["cohort"]).to_string(index=False))

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump({
                "ticker": args.ticker,
                "horizon_years": args.horizon_years,
                "withdrawal_rate": args.withdrawal_rate,
                "inflation": args.inflation,
                "start_range": [str(dates[start_indices[0]].date()),
                                str(dates[start_indices[-1]].date())],
                "summary": summary,
            }, f, indent=2)
        print(f"\nSaved JSON to {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", default="SPY")
    parser.add_argument("--mix", default=None,
                        help="Synthetic daily-rebalanced blend instead of a single "
                             "ticker, e.g. 'SPY:0.6,TLT:0.4'. Overrides --ticker.")
    parser.add_argument("--horizon-years", type=float, default=5.0)
    parser.add_argument("--cash-yield", type=float, default=0.03,
                        help="Annual cash yield while undeployed (default 3%%)")
    parser.add_argument("--ath-threshold", type=float, default=0.02,
                        help="Within this fraction of ATH counts as 'at the top'")
    parser.add_argument("--output", default=None,
                        help="Optional JSON output path")
    parser.add_argument("--withdrawal-rate", type=float, default=None,
                        help="Switch to decumulation mode: annual withdrawal "
                             "as a fraction of the initial balance (e.g. 0.04)")
    parser.add_argument("--inflation", type=float, default=0.03,
                        help="Annual inflation for withdrawal adjustment")
    args = parser.parse_args()

    if args.mix:
        # Build a synthetic daily-rebalanced blend index from close prices.
        parts = [p.split(":") for p in args.mix.split(",")]
        weights = {ticker.strip(): float(w) for ticker, w in parts}
        closes = pd.concat(
            [load_history(t)["close"].rename(t) for t in weights], axis=1
        ).dropna()
        blend_returns = sum(
            closes[t].pct_change().fillna(0.0) * w for t, w in weights.items()
        )
        blend = (1.0 + blend_returns).cumprod()
        df = pd.DataFrame({"close": blend})
        args.ticker = args.mix
    else:
        df = load_history(args.ticker)
    prices = df["close"].astype(float).to_numpy()
    dates = df.index
    sma200 = df["close"].rolling(200).mean().to_numpy()
    daily_returns = df["close"].pct_change().fillna(0.0).to_numpy()
    n = len(prices)

    horizon_days = int(args.horizon_years * TRADING_DAYS_PER_YEAR)
    cash_daily_yield = (1.0 + args.cash_yield) ** (1.0 / TRADING_DAYS_PER_YEAR) - 1.0

    running_ath = np.maximum.accumulate(prices)

    if args.withdrawal_rate is not None:
        run_decumulation(args, prices, sma200, daily_returns, dates,
                         running_ath, cash_daily_yield)
        return

    strategies = [
        "lump_sum", "dca_6m", "dca_12m", "dca_24m",
        "sma_gated_12m", "dip_buy_10", "ls_sma_managed",
    ]

    # Monthly start dates with full forward horizon. Skip the SMA warmup so
    # signal strategies are never accidentally "in cash by ignorance".
    start_indices = list(range(200, n - horizon_days - 1, TRADING_DAYS_PER_MONTH))
    print(f"Ticker: {args.ticker}  |  {dates[0].date()} to {dates[-1].date()}")
    print(f"Horizon: {args.horizon_years}y  |  cash yield {args.cash_yield:.1%}  |  "
          f"{len(start_indices)} monthly start dates "
          f"({dates[start_indices[0]].date()} to {dates[start_indices[-1]].date()})")

    rows = []
    for start_idx in start_indices:
        at_top = prices[start_idx] >= running_ath[start_idx] * (1 - args.ath_threshold)
        for strategy in strategies:
            result = simulate(prices, sma200, daily_returns, start_idx,
                              horizon_days, strategy, cash_daily_yield)
            if result is None:
                continue
            wealth, max_dd = result
            rows.append({
                "start": str(dates[start_idx].date()),
                "strategy": strategy,
                "at_top": bool(at_top),
                "wealth": wealth,
                "max_drawdown": max_dd,
            })

    results = pd.DataFrame(rows)

    def summarize(subset, label):
        lump = subset[subset.strategy == "lump_sum"].set_index("start")["wealth"]
        out = []
        for strategy in strategies:
            s = subset[subset.strategy == strategy].set_index("start")
            vs_lump = (s["wealth"] / lump.reindex(s.index)).dropna()
            out.append({
                "cohort": label,
                "strategy": strategy,
                "starts": len(s),
                "median_wealth": round(float(s["wealth"].median()), 4),
                "p5_wealth": round(float(s["wealth"].quantile(0.05)), 4),
                "worst_wealth": round(float(s["wealth"].min()), 4),
                "median_max_dd": round(float(s["max_drawdown"].median()), 4),
                "worst_max_dd": round(float(s["max_drawdown"].min()), 4),
                "beats_lump_pct": round(float((vs_lump > 1.0).mean()) * 100, 1),
            })
        return out

    summary = (
        summarize(results, "all_starts")
        + summarize(results[results.at_top], "at_top_starts")
        + summarize(results[~results.at_top], "below_top_starts")
    )
    summary_df = pd.DataFrame(summary)

    for cohort in ["all_starts", "at_top_starts", "below_top_starts"]:
        block = summary_df[summary_df.cohort == cohort]
        print(f"\n=== {cohort} ({block['starts'].iloc[0]} start dates) ===")
        print(block.drop(columns=["cohort"]).to_string(index=False))

    if args.output:
        payload = {
            "ticker": args.ticker,
            "start_range": [str(dates[start_indices[0]].date()),
                            str(dates[start_indices[-1]].date())],
            "horizon_years": args.horizon_years,
            "cash_yield": args.cash_yield,
            "ath_threshold": args.ath_threshold,
            "summary": summary,
        }
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"\nSaved JSON to {out_path}")


if __name__ == "__main__":
    main()
