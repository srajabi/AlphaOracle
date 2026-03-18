import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.config_loader import load_config, list_available_configs
from backtesting.engine import run_backtest, run_weighted_backtest
from backtesting.periods import MARKET_PERIODS
from backtesting.portfolio_strategies import PORTFOLIO_STRATEGIES
from backtesting.strategies import STRATEGIES


DEFAULT_TICKERS = ["SPY", "QQQ", "GLD", "TLT", "XLE", "XLU"]  # SPY has 33 years (1993), longest history
DEFAULT_PERIODS = "10,20,30,40,full"
DEFAULT_SINGLE_ASSET_STRATEGIES = "buy_and_hold,sma_trend_following,rsi_mean_reversion,breakout_20d"
DEFAULT_PORTFOLIO_STRATEGIES = "top2_relative_strength_rotation,dual_momentum_rotation,regime_defensive_rotation"


def load_history(ticker: str, use_long_history: bool = True, _cache={}) -> pd.DataFrame:
    """
    Load price history for a ticker.

    Args:
        ticker: Stock ticker symbol
        use_long_history: If True, load from data/historical_long/ (20+ years).
                         If False, load from data/history/ (recent data only).

    Returns:
        DataFrame with OHLCV data indexed by time
    """
    # Simple cache to avoid reloading same ticker
    cache_key = (ticker, use_long_history)
    if cache_key in _cache:
        return _cache[cache_key].copy()

    if use_long_history:
        path = Path("data/historical_long") / f"{ticker}.json"
    else:
        path = Path("data/history") / f"{ticker}.json"

    if not path.exists():
        raise FileNotFoundError(f"Missing history file for {ticker}: {path}")

    with open(path) as f:
        data = json.load(f)

    # Handle both formats:
    # - historical_long: {"ticker": "X", "prices": [...]}
    # - history: [{...}, {...}, ...]
    if isinstance(data, dict) and "prices" in data:
        # historical_long format
        df = pd.DataFrame(data["prices"])
        if "date" in df.columns:
            df["time"] = pd.to_datetime(df["date"])
            df = df.drop(columns=["date"])
    else:
        # history format (array of objects)
        df = pd.DataFrame(data)
        if "time" not in df.columns:
            raise ValueError(f"No time field found in {path}")
        df["time"] = pd.to_datetime(df["time"])

    # Ensure we have OHLCV columns
    required_cols = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for {ticker}: {missing}")

    # Sort and index by time
    df = df.sort_values("time").set_index("time")
    df.attrs["ticker"] = ticker

    # Keep only OHLCV (drop any extra columns like SMAs from daily data)
    df = df[required_cols]

    # Cache and return
    _cache[cache_key] = df.copy()
    return df


def summarize_results(results_df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "max_drawdown",
        "win_rate",
        "trades",
    ]
    summary = (
        results_df.groupby("strategy", as_index=False)[numeric_columns]
        .mean(numeric_only=True)
        .sort_values(by=["sharpe", "annualized_return"], ascending=[False, False])
    )
    return summary


def summarize_by_period(results_df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe",
        "max_drawdown",
        "win_rate",
        "trades",
    ]
    summary = (
        results_df.groupby(["period", "strategy"], as_index=False)[numeric_columns]
        .mean(numeric_only=True)
        .sort_values(by=["period", "sharpe", "annualized_return"], ascending=[True, False, False])
    )
    return summary


def build_named_periods(df: pd.DataFrame, period_spec: str):
    periods = []
    tokens = [token.strip().lower() for token in period_spec.split(",") if token.strip()]
    for token in tokens:
        if token == "full":
            periods.append(("full_sample", df.copy()))
            continue
        window = int(token)
        if len(df) >= window:
            periods.append((f"last_{window}d", df.tail(window).copy()))
    return periods


def build_market_regime_periods(df: pd.DataFrame, regime_names: str):
    periods = []
    names = [name.strip() for name in regime_names.split(",") if name.strip()]
    for name in names:
        if name not in MARKET_PERIODS:
            raise ValueError(f"Unknown market period '{name}'. Available: {sorted(MARKET_PERIODS)}")
        start, end = MARKET_PERIODS[name]
        period_df = df.loc[start:end].copy()
        if not period_df.empty:
            periods.append((name, period_df))
    return periods


def build_rolling_periods(df: pd.DataFrame, window: int, step: int):
    periods = []
    if window <= 1 or len(df) < window:
        return periods
    for start in range(0, len(df) - window + 1, step):
        end = start + window
        period_df = df.iloc[start:end].copy()
        start_label = period_df.index[0].strftime("%Y-%m-%d")
        end_label = period_df.index[-1].strftime("%Y-%m-%d")
        periods.append((f"roll_{start_label}_to_{end_label}", period_df))
    return periods


def dedupe_periods(periods):
    seen = set()
    deduped = []
    for period_name, period_df in periods:
        if period_df.empty:
            continue
        key = (period_name, period_df.index[0], period_df.index[-1], len(period_df))
        if key in seen:
            continue
        seen.add(key)
        deduped.append((period_name, period_df))
    return deduped


def load_price_matrix(tickers, use_long_history=True):
    price_frames = []
    for ticker in tickers:
        df = load_history(ticker, use_long_history=use_long_history)
        price_frames.append(df["close"].rename(ticker))
    prices = pd.concat(price_frames, axis=1).dropna(how="any")
    return prices


def main():
    parser = argparse.ArgumentParser(
        description="Run local backtests against cached history JSON files.",
        epilog="Use --config to load settings from YAML, or use individual CLI args to override.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file. If provided, overrides other CLI args unless they are explicitly set.",
    )
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="List available config files and exit.",
    )
    parser.add_argument("--tickers", default=None, help="Comma-separated list of tickers.")
    parser.add_argument(
        "--strategies",
        default=None,
        help="Comma-separated single-asset strategy names.",
    )
    parser.add_argument(
        "--portfolio-strategies",
        default=None,
        help="Comma-separated portfolio rotation strategy names.",
    )
    parser.add_argument(
        "--periods",
        default=None,
        help="Comma-separated lookback windows in trading days plus optional 'full'. Example: 10,20,30,full",
    )
    parser.add_argument(
        "--rolling-window",
        type=int,
        default=None,
        help="Optional rolling evaluation window in trading days.",
    )
    parser.add_argument(
        "--rolling-step",
        type=int,
        default=None,
        help="Step size for rolling windows.",
    )
    parser.add_argument(
        "--market-periods",
        default=None,
        help="Comma-separated named market regimes from backtesting/periods.py.",
    )
    parser.add_argument("--transaction-cost-bps", type=float, default=None, help="One-way transaction cost in bps.")
    parser.add_argument("--output-dir", default=None, help="Where to save JSON and CSV outputs.")
    parser.add_argument(
        "--use-long-history",
        action="store_true",
        default=None,
        help="Use long history data (data/historical_long/) instead of recent data.",
    )
    args = parser.parse_args()

    # Handle --list-configs
    if args.list_configs:
        configs = list_available_configs()
        if not configs:
            print("No config files found in backtesting/configs/")
        else:
            print("Available config files:")
            for config_path in configs:
                print(f"  - {config_path}")
        return

    # Load config file if specified
    if args.config:
        print(f"Loading config from: {args.config}")
        config = load_config(args.config)
        print(f"Config: {config.name}")
        print(f"Description: {config.description}")
        print()

        # Convert config to args dict
        config_args = config.to_cli_args()

        # CLI args override config (if explicitly provided)
        # Use a helper to check if arg was explicitly set
        if args.tickers is None:
            args.tickers = config_args["tickers"]
        if args.strategies is None:
            args.strategies = config_args["strategies"]
        if args.portfolio_strategies is None:
            args.portfolio_strategies = config_args["portfolio_strategies"]
        if args.periods is None:
            args.periods = config_args["periods"]
        if args.market_periods is None:
            args.market_periods = config_args["market_periods"]
        if args.rolling_window is None:
            args.rolling_window = config_args["rolling_window"]
        if args.rolling_step is None:
            args.rolling_step = config_args["rolling_step"]
        if args.transaction_cost_bps is None:
            args.transaction_cost_bps = config_args["transaction_cost_bps"]
        if args.output_dir is None:
            args.output_dir = config_args["output_dir"]
        if args.use_long_history is None:
            args.use_long_history = config_args["use_long_history"]
    else:
        # No config file - use defaults
        if args.tickers is None:
            args.tickers = ",".join(DEFAULT_TICKERS)
        if args.strategies is None:
            args.strategies = DEFAULT_SINGLE_ASSET_STRATEGIES
        if args.portfolio_strategies is None:
            args.portfolio_strategies = DEFAULT_PORTFOLIO_STRATEGIES
        if args.periods is None:
            args.periods = DEFAULT_PERIODS
        if args.market_periods is None:
            args.market_periods = ""
        if args.rolling_window is None:
            args.rolling_window = 0
        if args.rolling_step is None:
            args.rolling_step = 5
        if args.transaction_cost_bps is None:
            args.transaction_cost_bps = 5.0
        if args.output_dir is None:
            args.output_dir = "backtesting/results"
        if args.use_long_history is None:
            args.use_long_history = True

    tickers = [ticker.strip() for ticker in args.tickers.split(",") if ticker.strip()]
    strategy_names = [name.strip() for name in args.strategies.split(",") if name.strip()]
    portfolio_strategy_names = [name.strip() for name in args.portfolio_strategies.split(",") if name.strip()]

    unknown = [name for name in strategy_names if name not in STRATEGIES]
    if unknown:
        raise ValueError(f"Unknown strategies requested: {unknown}. Available: {sorted(STRATEGIES)}")
    unknown_portfolio = [name for name in portfolio_strategy_names if name not in PORTFOLIO_STRATEGIES]
    if unknown_portfolio:
        raise ValueError(
            f"Unknown portfolio strategies requested: {unknown_portfolio}. "
            f"Available: {sorted(PORTFOLIO_STRATEGIES)}"
        )

    results = []
    price_matrix = load_price_matrix(tickers, use_long_history=args.use_long_history)
    portfolio_periods = build_named_periods(price_matrix, args.periods)
    portfolio_periods.extend(build_rolling_periods(price_matrix, args.rolling_window, args.rolling_step))
    if args.market_periods:
        portfolio_periods.extend(build_market_regime_periods(price_matrix, args.market_periods))
    portfolio_periods = dedupe_periods(portfolio_periods)

    for ticker in tickers:
        df = load_history(ticker, use_long_history=args.use_long_history)
        full_signals = {strategy_name: STRATEGIES[strategy_name](df) for strategy_name in strategy_names}
        periods = build_named_periods(df, args.periods)
        periods.extend(build_rolling_periods(df, args.rolling_window, args.rolling_step))
        if args.market_periods:
            periods.extend(build_market_regime_periods(df, args.market_periods))
        periods = dedupe_periods(periods)
        if not periods:
            raise ValueError(f"No valid periods produced for {ticker}.")

        for period_name, period_df in periods:
            period_df.attrs["ticker"] = ticker
            for strategy_name in strategy_names:
                signal = full_signals[strategy_name].reindex(period_df.index)
                result = run_backtest(
                    period_df,
                    strategy_name,
                    signal,
                    args.transaction_cost_bps,
                    period_name,
                )
                results.append(result.to_dict())

    full_portfolio_weights = {
        strategy_name: PORTFOLIO_STRATEGIES[strategy_name](price_matrix)
        for strategy_name in portfolio_strategy_names
    }
    for period_name, period_prices in portfolio_periods:
        for strategy_name in portfolio_strategy_names:
            weights = full_portfolio_weights[strategy_name].reindex(period_prices.index)
            result = run_weighted_backtest(
                period_prices,
                strategy_name,
                weights,
                args.transaction_cost_bps,
                period_name,
                ticker_name="PORTFOLIO",
            )
            results.append(result.to_dict())

    results_df = pd.DataFrame(results)
    summary_df = summarize_results(results_df)
    period_summary_df = summarize_by_period(results_df)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(output_dir / "results_by_ticker.csv", index=False)
    summary_df.to_csv(output_dir / "summary.csv", index=False)
    period_summary_df.to_csv(output_dir / "summary_by_period.csv", index=False)

    payload = {
        "tickers": tickers,
        "strategies": strategy_names,
        "portfolio_strategies": portfolio_strategy_names,
        "periods": args.periods,
        "market_periods": args.market_periods,
        "rolling_window": args.rolling_window,
        "rolling_step": args.rolling_step,
        "transaction_cost_bps": args.transaction_cost_bps,
        "summary": summary_df.to_dict(orient="records"),
        "summary_by_period": period_summary_df.to_dict(orient="records"),
        "results_by_ticker": results,
    }
    with open(output_dir / "summary.json", "w") as f:
        json.dump(payload, f, indent=2)

    print("Backtest complete.")
    print(summary_df.to_string(index=False))
    print()
    print("By period:")
    print(period_summary_df.to_string(index=False))
    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":
    main()
