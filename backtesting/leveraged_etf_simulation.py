#!/usr/bin/env python3
"""
Simulate leveraged ETF performance with daily rebalancing and decay.

This shows the REAL performance of using 2x/3x ETFs vs clean margin leverage.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.portfolio_strategies import (
    regime_defensive_rotation,
    dual_momentum_rotation,
    top2_relative_strength_rotation,
)


def load_history(ticker: str) -> pd.DataFrame:
    """Load historical data for a ticker."""
    path = Path("data/historical_long") / f"{ticker}.json"
    if not path.exists():
        path = Path("data/history") / f"{ticker}.json"
    if not path.exists():
        raise FileNotFoundError(f"No history found for {ticker}")

    with open(path) as f:
        data = json.load(f)

    if isinstance(data, dict) and "prices" in data:
        df = pd.DataFrame(data["prices"])
        if "date" in df.columns:
            df["time"] = pd.to_datetime(df["date"])
            df = df.drop(columns=["date"])
    else:
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])

    df = df.sort_values("time").set_index("time")
    return df[["open", "high", "low", "close", "volume"]]


def simulate_leveraged_etf_returns(
    underlying_returns: pd.Series,
    leverage: float,
    expense_ratio: float = 0.0095,  # 0.95% annually
) -> pd.Series:
    """
    Simulate leveraged ETF returns with daily rebalancing.

    Args:
        underlying_returns: Daily returns of underlying asset
        leverage: Leverage multiple (2.0 or 3.0)
        expense_ratio: Annual expense ratio (default 0.95%)

    Returns:
        Series of leveraged ETF daily returns
    """
    # Daily expense ratio cost
    daily_expense = (1 + expense_ratio) ** (1/252) - 1

    # Leveraged returns with daily rebalancing
    leveraged_returns = underlying_returns * leverage - daily_expense

    return leveraged_returns


def run_leveraged_etf_backtest(
    strategy_name: str,
    strategy_func,
    tickers: list,
    leverage: float,
    expense_ratio: float = 0.0095,
):
    """
    Backtest a strategy using leveraged ETF simulation.

    Args:
        strategy_name: Name of strategy
        strategy_func: Strategy function
        tickers: List of tickers
        leverage: 1.0 (no leverage), 2.0, or 3.0
        expense_ratio: Annual expense ratio for leveraged ETFs
    """
    # Load price data
    price_frames = []
    for ticker in tickers:
        df = load_history(ticker)
        price_frames.append(df["close"].rename(ticker))

    prices = pd.concat(price_frames, axis=1).dropna(how="any")

    # Get strategy weights
    weights = strategy_func(prices)

    # Calculate daily returns for each asset
    returns = prices.pct_change()

    # If leveraged, simulate ETF behavior
    if leverage > 1.0:
        # Apply leverage with daily rebalancing to each asset
        leveraged_returns = pd.DataFrame(index=returns.index, columns=returns.columns)
        for ticker in returns.columns:
            leveraged_returns[ticker] = simulate_leveraged_etf_returns(
                returns[ticker],
                leverage,
                expense_ratio
            )
        returns = leveraged_returns

    # Calculate portfolio returns
    portfolio_returns = (returns * weights.shift(1)).sum(axis=1)

    # Calculate metrics
    total_return = (1 + portfolio_returns).cumprod().iloc[-1] - 1
    annual_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
    annual_vol = portfolio_returns.std() * np.sqrt(252)
    sharpe = (annual_return - 0.03) / annual_vol if annual_vol > 0 else 0

    # Calculate max drawdown
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    # Count trades
    weight_changes = weights.diff().abs().sum(axis=1)
    trades = (weight_changes > 0.01).sum()

    return {
        "strategy": f"{strategy_name}_{leverage}x_etf" if leverage > 1 else strategy_name,
        "leverage": leverage,
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "trades": trades,
        "expense_ratio": expense_ratio if leverage > 1 else 0.0,
    }


def main():
    """Run leveraged ETF simulations."""
    tickers = ["SPY", "QQQ", "GLD", "TLT", "XLE", "XLU"]

    strategies = [
        ("regime_defensive_rotation", regime_defensive_rotation),
        ("dual_momentum_rotation", dual_momentum_rotation),
        ("top2_relative_strength_rotation", top2_relative_strength_rotation),
    ]

    leverages = [1.0, 2.0, 3.0]
    expense_ratio = 0.0095  # 0.95% for leveraged ETFs

    results = []

    for strategy_name, strategy_func in strategies:
        print(f"\nBacktesting {strategy_name}...")
        for leverage in leverages:
            print(f"  {leverage}x leverage...")
            result = run_leveraged_etf_backtest(
                strategy_name,
                strategy_func,
                tickers,
                leverage,
                expense_ratio if leverage > 1 else 0.0,
            )
            results.append(result)

    # Create DataFrame and display
    df = pd.DataFrame(results)
    df = df.sort_values("sharpe", ascending=False)

    print("\n" + "=" * 80)
    print("LEVERAGED ETF SIMULATION RESULTS (33 years)")
    print("=" * 80)
    print(df.to_string(index=False))
    print()

    # Compare to clean leverage (no decay)
    print("\n" + "=" * 80)
    print("DECAY ANALYSIS: Leveraged ETF vs Clean Margin Leverage")
    print("=" * 80)
    print("Expense ratio: 0.95% annually for leveraged ETFs")
    print()

    # Group by strategy
    for strategy_name, _ in strategies:
        strat_results = [r for r in results if strategy_name in r["strategy"]]
        print(f"\n{strategy_name}:")
        for r in strat_results:
            if r["leverage"] == 1.0:
                baseline_return = r["total_return"]
            elif r["leverage"] == 2.0:
                expected_return = (1 + baseline_return) ** 2 - 1
                actual_return = r["total_return"]
                decay = (actual_return - expected_return) / expected_return * 100
                print(f"  2x ETF: {actual_return*100:.1f}% vs Clean 2x: {expected_return*100:.1f}% → {decay:.1f}% decay")
            elif r["leverage"] == 3.0:
                expected_return = (1 + baseline_return) ** 3 - 1
                actual_return = r["total_return"]
                decay = (actual_return - expected_return) / expected_return * 100
                print(f"  3x ETF: {actual_return*100:.1f}% vs Clean 3x: {expected_return*100:.1f}% → {decay:.1f}% decay")

    # Save results
    output_dir = Path("backtesting/results/leveraged_etf")
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_dir / "leveraged_etf_results.csv", index=False)
    print(f"\n\nResults saved to {output_dir}/leveraged_etf_results.csv")


if __name__ == "__main__":
    main()
