"""
Walk-Forward Validation for Strategy Robustness

Tests strategies on out-of-sample data to detect overfitting.

Method:
1. Split data into train/test periods
2. Run strategy on train period (if needed for optimization)
3. Test on holdout period
4. Compare in-sample vs out-of-sample performance

If performance degrades significantly out-of-sample, strategy is overfit.
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.engine import run_weighted_backtest
from backtesting.portfolio_strategies import PORTFOLIO_STRATEGIES


def load_long_history_prices(tickers):
    """Load historical prices for multiple tickers."""
    prices = {}
    for ticker in tickers:
        path = Path("data/historical_long") / f"{ticker}.json"
        if not path.exists():
            print(f"Warning: Missing {ticker}")
            continue

        with open(path) as f:
            data = json.load(f)

        df = pd.DataFrame(data["prices"])
        df["time"] = pd.to_datetime(df["date"])
        df = df.set_index("time")[["close"]]
        df.columns = [ticker]
        prices[ticker] = df

    # Merge all tickers
    all_prices = pd.concat(prices.values(), axis=1).sort_index()
    return all_prices


def walk_forward_validation(
    strategy_name,
    prices,
    train_start="1993-01-01",
    train_end="2010-12-31",
    test_start="2011-01-01",
    test_end="2026-03-16",
    transaction_cost_bps=0,
):
    """
    Walk-forward validation: train on first period, test on second period.

    Args:
        strategy_name: Name of portfolio strategy
        prices: DataFrame of prices (all tickers, full history)
        train_start/end: Training period
        test_start/end: Testing period
        transaction_cost_bps: Transaction costs

    Returns:
        dict with in_sample and out_of_sample results
    """
    if strategy_name not in PORTFOLIO_STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")

    strategy_func = PORTFOLIO_STRATEGIES[strategy_name]

    # Split data
    train_prices = prices.loc[train_start:train_end].copy()
    test_prices = prices.loc[test_start:test_end].copy()

    print(f"\n{'='*80}")
    print(f"Strategy: {strategy_name}")
    print(f"Train: {train_start} to {train_end} ({len(train_prices)} days)")
    print(f"Test:  {test_start} to {test_end} ({len(test_prices)} days)")
    print(f"{'='*80}")

    # Run on training data
    train_weights = strategy_func(train_prices)
    train_result = run_weighted_backtest(
        train_prices,
        strategy_name,
        train_weights,
        transaction_cost_bps,
        "in_sample",
        "PORTFOLIO",
    )

    # Run on test data (out-of-sample)
    test_weights = strategy_func(test_prices)
    test_result = run_weighted_backtest(
        test_prices,
        strategy_name,
        test_weights,
        transaction_cost_bps,
        "out_of_sample",
        "PORTFOLIO",
    )

    # Calculate degradation
    return_degradation = (test_result.total_return - train_result.total_return) / train_result.total_return
    sharpe_degradation = (test_result.sharpe - train_result.sharpe) / train_result.sharpe

    print(f"\n📊 Results:")
    print(f"  In-sample  (train): {train_result.total_return:7.2%} return, Sharpe {train_result.sharpe:.2f}, {train_result.trades:4} trades")
    print(f"  Out-sample (test):  {test_result.total_return:7.2%} return, Sharpe {test_result.sharpe:.2f}, {test_result.trades:4} trades")
    print(f"\n🔍 Degradation:")
    print(f"  Return: {return_degradation:+.1%}")
    print(f"  Sharpe: {sharpe_degradation:+.1%}")

    # Interpret results
    if abs(return_degradation) < 0.20 and abs(sharpe_degradation) < 0.20:
        verdict = "✅ ROBUST - Similar performance in-sample and out-of-sample"
    elif abs(return_degradation) < 0.40 and abs(sharpe_degradation) < 0.40:
        verdict = "⚠️  MODERATE - Some degradation but acceptable"
    else:
        verdict = "❌ OVERFIT - Significant degradation out-of-sample"

    print(f"\n{verdict}")
    print(f"{'='*80}\n")

    return {
        "strategy": strategy_name,
        "in_sample": train_result.to_dict(),
        "out_of_sample": test_result.to_dict(),
        "return_degradation": return_degradation,
        "sharpe_degradation": sharpe_degradation,
        "verdict": verdict,
    }


def main():
    """Run walk-forward validation on key strategies."""

    # Load data
    print("Loading historical data...")
    tickers = ["SPY", "QQQ", "GLD", "TLT", "XLE", "XLU"]
    prices = load_long_history_prices(tickers)

    print(f"Loaded {len(prices)} days of data for {len(tickers)} tickers")
    print(f"Date range: {prices.index[0].date()} to {prices.index[-1].date()}")

    # Strategies to validate
    strategies_to_test = [
        # Reddit strategies (suspected overfitting)
        "reddit_200sma_spy",
        "reddit_200sma_tqqq",

        # Our regime strategies (theory-driven)
        "regime_defensive_rotation",
        "regime_defensive_rotation_with_bands",
        "regime_defensive_rotation_2x",

        # Other rotation strategies
        "dual_momentum_rotation",
        "top2_relative_strength_rotation",
    ]

    results = []

    for strategy_name in strategies_to_test:
        try:
            result = walk_forward_validation(
                strategy_name,
                prices,
                train_start="1993-01-01",
                train_end="2010-12-31",  # 18 years train
                test_start="2011-01-01",
                test_end="2026-03-16",  # 15 years test
                transaction_cost_bps=0,
            )
            results.append(result)
        except Exception as e:
            print(f"❌ Error testing {strategy_name}: {e}\n")

    # Save results
    output_dir = Path("backtesting/results/walk_forward")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "validation_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to {output_file}")

    # Summary table
    print("\n" + "="*80)
    print("SUMMARY: Walk-Forward Validation Results")
    print("="*80)
    print(f"{'Strategy':<40} {'In-Sample':<12} {'Out-Sample':<12} {'Return Deg':<12} {'Verdict':<20}")
    print("-"*80)

    for r in results:
        in_sample_ret = r["in_sample"]["annualized_return"]
        out_sample_ret = r["out_of_sample"]["annualized_return"]
        deg = r["return_degradation"]
        verdict = r["verdict"].split(" - ")[0]  # Just emoji + word

        print(f"{r['strategy']:<40} {in_sample_ret:>11.1%} {out_sample_ret:>11.1%} {deg:>+11.1%} {verdict:<20}")

    print("="*80)


if __name__ == "__main__":
    main()
