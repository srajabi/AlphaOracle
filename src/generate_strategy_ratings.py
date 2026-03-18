#!/usr/bin/env python3
"""
Generate strategy ratings for each ticker.

This script implements Mode 2 of the AlphaOracle system:
- Loads market data from data/market_context.json
- Applies rule-based technical strategies to each ticker
- Outputs buy/sell/hold ratings for each strategy
- Writes results to data/strategy_ratings.json and frontend/public/data/strategy_ratings.json

Each strategy is mechanical and reproducible - no LLM involved.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd


# Strategy metadata
STRATEGY_METADATA = {
    "sma_200_trend": {
        "name": "200 SMA Trend Following",
        "description": "Long when price > 200 SMA, otherwise out",
        "type": "trend_following",
        "universe": "all"
    },
    "sma_trend_20_50": {
        "name": "SMA 20/50 Crossover",
        "description": "Long when SMA20 > SMA50",
        "type": "trend_following",
        "universe": "all"
    },
    "rsi_mean_reversion": {
        "name": "RSI Mean Reversion",
        "description": "Buy when RSI < 35, sell when RSI > 65",
        "type": "mean_reversion",
        "universe": "all"
    },
    "breakout_20d": {
        "name": "20-Day Breakout",
        "description": "Buy on 20-day high, sell on 10-day low",
        "type": "breakout",
        "universe": "all"
    },
    "dual_momentum": {
        "name": "Dual Momentum Rotation",
        "description": "Rotates to best offensive asset if positive, else best defensive",
        "type": "momentum_rotation",
        "universe": ["SPY", "QQQ", "XLE", "GLD", "TLT", "XLU"]
    },
    "leveraged_etf_timing": {
        "name": "3x Leveraged ETF Timing",
        "description": "Use 3x ETFs only in strong confirmed trends",
        "type": "aggressive_trend",
        "universe": ["TQQQ", "SOXL", "UPRO", "SOXS", "TECS", "SPXU"]
    }
}


def load_market_context() -> Dict[str, Any]:
    """Load market context data."""
    path = Path("data/market_context.json")
    if not path.exists():
        raise FileNotFoundError(f"Market context not found: {path}")

    with open(path) as f:
        return json.load(f)


def load_ticker_history(ticker: str) -> pd.DataFrame:
    """
    Load historical data for a ticker.

    Args:
        ticker: Stock ticker symbol

    Returns:
        DataFrame with OHLCV data indexed by time
    """
    # Try data/history first (most recent)
    path = Path("data/history") / f"{ticker}.json"
    if not path.exists():
        # Try historical_long as fallback
        path = Path("data/historical_long") / f"{ticker}.json"

    if not path.exists():
        raise FileNotFoundError(f"No history found for {ticker}")

    with open(path) as f:
        data = json.load(f)

    # Handle both formats
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
            raise ValueError(f"No time field found for {ticker}")
        df["time"] = pd.to_datetime(df["time"])

    # Ensure required columns
    required_cols = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for {ticker}: {missing}")

    df = df.sort_values("time").set_index("time")
    return df[required_cols]


def sma_200_trend(ticker: str, ticker_data: Dict, history: pd.DataFrame) -> str:
    """
    200 SMA trend following strategy.

    Args:
        ticker: Ticker symbol
        ticker_data: Current ticker data from market_context
        history: Historical OHLCV DataFrame

    Returns:
        "buy", "sell", or "hold"
    """
    if len(history) < 200:
        return "hold"  # Insufficient data

    current_price = ticker_data.get("close")
    sma_200 = history["close"].rolling(200).mean().iloc[-1]

    if current_price and sma_200:
        if current_price > sma_200:
            return "buy"
        else:
            return "sell"

    return "hold"


def sma_trend_20_50(ticker: str, ticker_data: Dict, history: pd.DataFrame) -> str:
    """
    SMA 20/50 crossover strategy.

    Args:
        ticker: Ticker symbol
        ticker_data: Current ticker data from market_context
        history: Historical OHLCV DataFrame

    Returns:
        "buy", "sell", or "hold"
    """
    if len(history) < 50:
        return "hold"

    sma_20 = history["close"].rolling(20).mean().iloc[-1]
    sma_50 = history["close"].rolling(50).mean().iloc[-1]

    if pd.notna(sma_20) and pd.notna(sma_50):
        if sma_20 > sma_50:
            return "buy"
        elif sma_20 < sma_50:
            return "sell"

    return "hold"


def rsi_mean_reversion(ticker: str, ticker_data: Dict, history: pd.DataFrame) -> str:
    """
    RSI mean reversion strategy.

    Args:
        ticker: Ticker symbol
        ticker_data: Current ticker data from market_context
        history: Historical OHLCV DataFrame

    Returns:
        "buy", "sell", or "hold"
    """
    if len(history) < 15:
        return "hold"

    # Calculate RSI
    delta = history["close"].diff()
    gains = delta.clip(lower=0).rolling(14).mean()
    losses = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gains / losses.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))

    current_rsi = rsi.iloc[-1]

    if pd.notna(current_rsi):
        if current_rsi < 35:
            return "buy"
        elif current_rsi > 65:
            return "sell"

    return "hold"


def breakout_20d(ticker: str, ticker_data: Dict, history: pd.DataFrame) -> str:
    """
    20-day breakout strategy.

    Args:
        ticker: Ticker symbol
        ticker_data: Current ticker data from market_context
        history: Historical OHLCV DataFrame

    Returns:
        "buy", "sell", or "hold"
    """
    if len(history) < 21:
        return "hold"

    current_price = ticker_data.get("close")
    high_20d = history["close"].iloc[-21:-1].max()  # Exclude current day
    low_10d = history["close"].iloc[-11:-1].min()   # Exclude current day

    if current_price and pd.notna(high_20d) and pd.notna(low_10d):
        if current_price > high_20d:
            return "buy"
        elif current_price < low_10d:
            return "sell"

    return "hold"


def dual_momentum(market_context: Dict) -> Dict[str, str]:
    """
    Dual momentum rotation strategy (portfolio-level).

    This strategy rotates between offensive assets (SPY, QQQ, XLE) and
    defensive assets (GLD, TLT, XLU) based on 20-day momentum.

    Args:
        market_context: Full market context

    Returns:
        Dictionary mapping tickers to ratings
    """
    offensive = ["SPY", "QQQ", "XLE"]
    defensive = ["GLD", "TLT", "XLU"]
    all_tickers = offensive + defensive

    ratings = {}

    # Calculate 20-day returns for each ticker
    returns = {}
    for ticker in all_tickers:
        if ticker not in market_context.get("data", {}):
            continue

        try:
            history = load_ticker_history(ticker)
            if len(history) >= 21:
                ret_20d = (history["close"].iloc[-1] / history["close"].iloc[-21]) - 1
                returns[ticker] = ret_20d
        except Exception:
            pass

    if not returns:
        # No data available
        return {ticker: "hold" for ticker in all_tickers}

    # Find best offensive asset
    offensive_returns = {t: returns.get(t, -999) for t in offensive if t in returns}
    if offensive_returns:
        best_offensive = max(offensive_returns, key=offensive_returns.get)
        best_offensive_return = offensive_returns[best_offensive]
    else:
        best_offensive = None
        best_offensive_return = -999

    # If best offensive is positive, hold it
    if best_offensive and best_offensive_return > 0:
        for ticker in all_tickers:
            ratings[ticker] = "buy" if ticker == best_offensive else "sell"
    else:
        # Rotate to best defensive
        defensive_returns = {t: returns.get(t, -999) for t in defensive if t in returns}
        if defensive_returns:
            best_defensive = max(defensive_returns, key=defensive_returns.get)
            for ticker in all_tickers:
                ratings[ticker] = "buy" if ticker == best_defensive else "sell"
        else:
            ratings = {ticker: "hold" for ticker in all_tickers}

    return ratings


def leveraged_etf_timing(ticker: str, ticker_data: Dict, history: pd.DataFrame, market_context: Dict) -> str:
    """
    3x leveraged ETF timing strategy.

    Only use leveraged ETFs in strong confirmed trends. Requires multiple confirmations.

    Args:
        ticker: Ticker symbol
        ticker_data: Current ticker data from market_context
        history: Historical OHLCV DataFrame
        market_context: Full market context for underlying index

    Returns:
        "buy", "sell", "hold", or "n/a"
    """
    # Map 3x ETF to underlying
    underlying_map = {
        "TQQQ": "QQQ",
        "SOXL": "QQQ",  # Using QQQ as proxy for semiconductor index
        "UPRO": "SPY",
        "SOXS": "QQQ",  # Inverse
        "TECS": "QQQ",  # Inverse
        "SPXU": "SPY",  # Inverse
    }

    if ticker not in underlying_map:
        return "n/a"

    underlying = underlying_map[ticker]
    is_inverse = ticker in ["SOXS", "TECS", "SPXU"]

    # Load underlying data
    try:
        underlying_history = load_ticker_history(underlying)
    except Exception:
        return "hold"

    if len(underlying_history) < 200:
        return "hold"

    # Calculate indicators on underlying
    price = underlying_history["close"].iloc[-1]
    sma_50 = underlying_history["close"].rolling(50).mean().iloc[-1]
    sma_200 = underlying_history["close"].rolling(200).mean().iloc[-1]

    # Calculate RSI on underlying
    delta = underlying_history["close"].diff()
    gains = delta.clip(lower=0).rolling(14).mean()
    losses = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gains / losses.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    # Calculate 20-day momentum
    if len(underlying_history) >= 21:
        mom_20d = (underlying_history["close"].iloc[-1] / underlying_history["close"].iloc[-21]) - 1
    else:
        mom_20d = 0

    # Check all indicators
    if pd.isna(sma_50) or pd.isna(sma_200) or pd.isna(current_rsi):
        return "hold"

    # For long 3x ETFs: need strong uptrend
    if not is_inverse:
        if price > sma_50 and sma_50 > sma_200 and current_rsi > 40 and mom_20d > 0:
            return "buy"
        else:
            return "sell"
    else:
        # For inverse 3x ETFs: need strong downtrend
        if price < sma_50 and sma_50 < sma_200 and current_rsi < 60 and mom_20d < 0:
            return "buy"
        else:
            return "sell"


def generate_ratings(market_context: Dict) -> Dict[str, Dict[str, str]]:
    """
    Generate ratings for all tickers and all strategies.

    Args:
        market_context: Market context data

    Returns:
        Dictionary mapping tickers to strategy ratings
    """
    ratings = {}

    # Get dual momentum ratings first (portfolio-level)
    dm_ratings = dual_momentum(market_context)

    # Process each ticker
    for ticker, ticker_data in market_context.get("data", {}).items():
        try:
            history = load_ticker_history(ticker)
        except Exception as e:
            print(f"Warning: Could not load history for {ticker}: {e}", file=sys.stderr)
            continue

        ticker_ratings = {}

        # Single-asset strategies
        ticker_ratings["sma_200_trend"] = sma_200_trend(ticker, ticker_data, history)
        ticker_ratings["sma_trend_20_50"] = sma_trend_20_50(ticker, ticker_data, history)
        ticker_ratings["rsi_mean_reversion"] = rsi_mean_reversion(ticker, ticker_data, history)
        ticker_ratings["breakout_20d"] = breakout_20d(ticker, ticker_data, history)

        # Dual momentum (from portfolio-level calculation)
        ticker_ratings["dual_momentum"] = dm_ratings.get(ticker, "n/a")

        # Leveraged ETF timing
        ticker_ratings["leveraged_etf_timing"] = leveraged_etf_timing(ticker, ticker_data, history, market_context)

        ratings[ticker] = ticker_ratings

    return ratings


def compute_summary(ratings: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """
    Compute summary statistics from ratings.

    Args:
        ratings: Ticker to strategy ratings mapping

    Returns:
        Summary dictionary
    """
    # Count consensus ratings
    consensus_counts = {"buy": 0, "sell": 0, "hold": 0}

    # Track most bullish/bearish tickers
    ticker_scores = {}

    for ticker, ticker_ratings in ratings.items():
        score = 0
        applicable_count = 0

        for strategy, rating in ticker_ratings.items():
            if rating == "buy":
                score += 1
                applicable_count += 1
            elif rating == "sell":
                score -= 1
                applicable_count += 1
            elif rating == "hold":
                applicable_count += 1
            # "n/a" doesn't count

        # Only consider tickers with at least 3 applicable strategies
        if applicable_count >= 3:
            ticker_scores[ticker] = score

            # Determine consensus
            if score >= 2:
                consensus_counts["buy"] += 1
            elif score <= -2:
                consensus_counts["sell"] += 1
            else:
                consensus_counts["hold"] += 1

    # Get top 3 most bullish/bearish
    sorted_tickers = sorted(ticker_scores.items(), key=lambda x: x[1], reverse=True)
    most_bullish = [ticker for ticker, score in sorted_tickers[:3] if score > 0]
    most_bearish = [ticker for ticker, score in sorted_tickers[-3:] if score < 0]
    most_bearish.reverse()  # Most bearish first

    return {
        "total_tickers": len(ratings),
        "total_strategies": len(STRATEGY_METADATA),
        "most_bullish": most_bullish,
        "most_bearish": most_bearish,
        "consensus_buy": consensus_counts["buy"],
        "consensus_sell": consensus_counts["sell"],
        "consensus_hold": consensus_counts["hold"],
    }


def main():
    """Generate strategy ratings and save to JSON."""
    print("Loading market context...")
    market_context = load_market_context()

    print("Generating strategy ratings...")
    ratings = generate_ratings(market_context)

    print("Computing summary...")
    summary = compute_summary(ratings)

    # Build output
    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "strategies": STRATEGY_METADATA,
        "ratings": ratings,
        "summary": summary,
    }

    # Write to data/
    data_path = Path("data/strategy_ratings.json")
    with open(data_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote ratings to {data_path}")

    # Write to frontend/
    frontend_path = Path("frontend/public/data/strategy_ratings.json")
    frontend_path.parent.mkdir(parents=True, exist_ok=True)
    with open(frontend_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote ratings to {frontend_path}")

    # Print summary
    print()
    print("=== Strategy Ratings Summary ===")
    print(f"Total tickers: {summary['total_tickers']}")
    print(f"Total strategies: {summary['total_strategies']}")
    print()
    print(f"Consensus BUY: {summary['consensus_buy']} tickers")
    print(f"Consensus HOLD: {summary['consensus_hold']} tickers")
    print(f"Consensus SELL: {summary['consensus_sell']} tickers")
    print()
    if summary['most_bullish']:
        print(f"Most bullish: {', '.join(summary['most_bullish'])}")
    if summary['most_bearish']:
        print(f"Most bearish: {', '.join(summary['most_bearish'])}")
    print()
    print("Done!")


if __name__ == "__main__":
    main()
