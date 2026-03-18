#!/usr/bin/env python3
"""
Momentum Strategy Signal Generators

Generates buy/sell signals for momentum-based strategies to be executed on Alpaca accounts.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, date


class MomentumStrategyGenerator:
    """Base class for momentum strategy signal generation."""

    def __init__(self, config: Dict):
        self.config = config
        self.data_dir = Path('data/history')

    def load_price_data(self, ticker: str, days: int = 250) -> Optional[pd.DataFrame]:
        """Load historical price data for a ticker."""
        try:
            with open(self.data_dir / f'{ticker}.json') as f:
                data = json.load(f)

            if not isinstance(data, list) or len(data) == 0:
                return None

            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time')

            # Get last N days
            df = df.tail(days)

            return df

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading price data for {ticker}: {e}")
            return None

    def generate_signals(self, current_positions: List[Dict]) -> List[Dict]:
        """Generate trade signals. Override in subclasses."""
        raise NotImplementedError


class Reddit200SMAStrategy(MomentumStrategyGenerator):
    """
    Reddit 200-day SMA strategy on leveraged ETFs (e.g., TQQQ, UPRO).

    Rules:
    - Buy when price > 200-day SMA
    - Sell when price < 200-day SMA
    - Uses all buying power when in position
    """

    def generate_signals(self, current_positions: List[Dict]) -> List[Dict]:
        ticker = self.config.get('ticker', 'TQQQ')
        sma_period = self.config.get('sma_period', 200)
        max_position = self.config.get('max_position_size', 1.0)

        # Load price data
        df = self.load_price_data(ticker, days=max(250, sma_period + 50))
        if df is None:
            print(f"No data for {ticker}")
            return []

        # Calculate SMA if not already in data
        if 'sma200' not in df.columns:
            df['sma200'] = df['close'].rolling(window=sma_period).mean()

        # Get latest values
        latest = df.iloc[-1]
        current_price = latest['close']
        sma_200 = latest.get('sma200', latest.get(f'sma{sma_period}', np.nan))

        if pd.isna(sma_200):
            print(f"SMA not available for {ticker}")
            return []

        # Check current position
        has_position = any(p.get('symbol') == ticker for p in current_positions)

        signals = []

        # Signal logic
        if current_price > sma_200 and not has_position:
            # Buy signal
            signals.append({
                "ticker": ticker,
                "action": "buy",
                "notional_value": None,  # Will use all buying power
                "rationale": f"Reddit 200 SMA: Price ${current_price:.2f} > SMA ${sma_200:.2f}",
                "signal_data": {
                    "strategy": "reddit_200sma",
                    "price": current_price,
                    "sma_200": sma_200,
                    "date": latest['time'].isoformat()
                }
            })

        elif current_price < sma_200 and has_position:
            # Sell signal
            signals.append({
                "ticker": ticker,
                "action": "sell",
                "qty": "all",
                "rationale": f"Reddit 200 SMA: Price ${current_price:.2f} < SMA ${sma_200:.2f}",
                "signal_data": {
                    "strategy": "reddit_200sma",
                    "price": current_price,
                    "sma_200": sma_200,
                    "date": latest['time'].isoformat()
                }
            })

        return signals


class DualMomentumStrategy(MomentumStrategyGenerator):
    """
    Dual Momentum (Absolute + Relative) across multiple assets.

    Rules:
    - Calculate momentum for each asset (lookback period, default 126 days / 6 months)
    - Select asset with highest positive momentum
    - If all momentum is negative, go to cash
    - Rebalance monthly or on signal change
    """

    def generate_signals(self, current_positions: List[Dict]) -> List[Dict]:
        tickers = self.config.get('tickers', ['SPY', 'QQQ', 'GLD'])
        lookback = self.config.get('lookback_period', 126)
        max_position = self.config.get('max_position_size', 1.0)

        # Calculate momentum for each ticker
        momentum_scores = {}
        for ticker in tickers:
            df = self.load_price_data(ticker, days=lookback + 10)
            if df is None or len(df) < lookback:
                continue

            # Simple momentum: (current_price / price_N_days_ago) - 1
            current_price = df.iloc[-1]['close']
            past_price = df.iloc[-lookback]['close']
            momentum = (current_price / past_price) - 1.0
            momentum_scores[ticker] = momentum

        if not momentum_scores:
            print("No momentum scores calculated")
            return []

        # Find best performer
        best_ticker = max(momentum_scores, key=momentum_scores.get)
        best_momentum = momentum_scores[best_ticker]

        # Get current position
        current_ticker = None
        for p in current_positions:
            if p.get('symbol') in tickers:
                current_ticker = p.get('symbol')
                break

        signals = []

        # Signal logic
        if best_momentum > 0:
            # Positive momentum - hold best asset
            if current_ticker != best_ticker:
                # Need to switch
                if current_ticker:
                    # Sell current position
                    signals.append({
                        "ticker": current_ticker,
                        "action": "sell",
                        "qty": "all",
                        "rationale": f"Dual Momentum: Switching from {current_ticker} to {best_ticker}",
                        "signal_data": {
                            "strategy": "dual_momentum",
                            "from_ticker": current_ticker,
                            "to_ticker": best_ticker,
                            "momentum_scores": momentum_scores
                        }
                    })

                # Buy new position
                signals.append({
                    "ticker": best_ticker,
                    "action": "buy",
                    "notional_value": None,  # Use all buying power
                    "rationale": f"Dual Momentum: Best performer with {best_momentum:.2%} momentum",
                    "signal_data": {
                        "strategy": "dual_momentum",
                        "ticker": best_ticker,
                        "momentum": best_momentum,
                        "momentum_scores": momentum_scores
                    }
                })
        else:
            # All momentum negative - go to cash
            if current_ticker:
                signals.append({
                    "ticker": current_ticker,
                    "action": "sell",
                    "qty": "all",
                    "rationale": f"Dual Momentum: All momentum negative, go to cash",
                    "signal_data": {
                        "strategy": "dual_momentum",
                        "momentum_scores": momentum_scores
                    }
                })

        return signals


def generate_strategy_signals(strategy_name: str, config: Dict, current_positions: List[Dict]) -> List[Dict]:
    """
    Generate signals for a specific strategy.

    Args:
        strategy_name: Name of the strategy
        config: Strategy configuration
        current_positions: Current positions in the account

    Returns:
        List of trade signals
    """
    if strategy_name == 'reddit_200sma_tqqq':
        generator = Reddit200SMAStrategy(config)
    elif strategy_name == 'reddit_200sma_spy':
        generator = Reddit200SMAStrategy(config)  # Same strategy, different ticker
    elif strategy_name == 'dual_momentum':
        generator = DualMomentumStrategy(config)
    else:
        print(f"Unknown strategy: {strategy_name}")
        return []

    return generator.generate_signals(current_positions)


if __name__ == '__main__':
    # Test the strategies
    print("Testing Reddit 200 SMA on TQQQ:")
    config = {"ticker": "TQQQ", "sma_period": 200, "max_position_size": 1.0}
    signals = generate_strategy_signals('reddit_200sma_tqqq', config, [])
    print(json.dumps(signals, indent=2))

    print("\nTesting Dual Momentum:")
    config = {"tickers": ["SPY", "QQQ", "GLD"], "lookback_period": 126}
    signals = generate_strategy_signals('dual_momentum', config, [])
    print(json.dumps(signals, indent=2))
