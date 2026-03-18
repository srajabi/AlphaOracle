#!/usr/bin/env python3
"""
Per-Ticker Technical Indicators

Individual stock/ETF indicators for display on ticker dashboard pages:
- Relative strength vs SPY and sector
- Trend strength (ADX-like)
- Volume confirmation
- Support/resistance levels
- Price momentum
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent))
from indicators.intermarket import IndicatorBase


class TickerIndicators(IndicatorBase):
    """Calculate technical indicators for individual tickers."""

    def __init__(self, ticker: str):
        super().__init__()
        self.ticker = ticker

    def calculate_relative_strength(self, lookback: int = 60) -> Dict:
        """
        Calculate relative strength vs SPY and sector.
        Returns performance comparison over various periods.
        """
        # Load ticker data
        ticker_df = self.load_price_data(self.ticker, days=lookback + 10)
        spy_df = self.load_price_data('SPY', days=lookback + 10)

        if ticker_df is None or spy_df is None or len(ticker_df) < lookback:
            return {
                'name': 'Relative Strength',
                'signal': 'no_data',
                'vs_spy': None,
                'interpretation': 'Insufficient data',
                'periods': {},
                'timestamp': datetime.now().isoformat()
            }

        # Calculate returns over multiple periods
        periods = [5, 20, 60]
        results = {}

        for period in periods:
            if len(ticker_df) >= period + 1:
                ticker_return = ((ticker_df['close'].iloc[-1] / ticker_df['close'].iloc[-(period + 1)]) - 1) * 100
                spy_return = ((spy_df['close'].iloc[-1] / spy_df['close'].iloc[-(period + 1)]) - 1) * 100
                outperformance = ticker_return - spy_return
                results[f'{period}d'] = {
                    'ticker_return': ticker_return,
                    'spy_return': spy_return,
                    'outperformance': outperformance
                }

        # Determine overall relative strength signal
        if '60d' in results:
            outperf_60d = results['60d']['outperformance']
            if outperf_60d > 10:
                signal = 'strong_outperformance'
                interpretation = f"Strongly outperforming SPY by {outperf_60d:.1f}% over 60 days"
            elif outperf_60d > 0:
                signal = 'outperformance'
                interpretation = f"Outperforming SPY by {outperf_60d:.1f}% over 60 days"
            elif outperf_60d > -10:
                signal = 'underperformance'
                interpretation = f"Underperforming SPY by {abs(outperf_60d):.1f}% over 60 days"
            else:
                signal = 'strong_underperformance'
                interpretation = f"Strongly underperforming SPY by {abs(outperf_60d):.1f}% over 60 days"
        else:
            signal = 'neutral'
            interpretation = 'Insufficient history for relative strength calculation'

        return {
            'name': 'Relative Strength',
            'signal': signal,
            'interpretation': interpretation,
            'periods': results,
            'vs_spy': results.get('60d', {}).get('outperformance'),
            'timestamp': datetime.now().isoformat()
        }

    def calculate_trend_strength(self) -> Dict:
        """
        Calculate trend strength using multiple indicators.
        Similar to ADX but simpler for display.
        """
        df = self.load_price_data(self.ticker, days=100)

        if df is None or len(df) < 50:
            return {
                'signal': 'no_data',
                'strength': None,
                'interpretation': 'Insufficient data'
            }

        # Calculate SMAs
        df['sma20'] = df['close'].rolling(window=20).mean()
        df['sma50'] = df['close'].rolling(window=50).mean()

        close = df['close'].iloc[-1]
        sma20 = df['sma20'].iloc[-1]
        sma50 = df['sma50'].iloc[-1]

        # Check SMA alignment
        smas_aligned_up = close > sma20 > sma50
        smas_aligned_down = close < sma20 < sma50

        # Calculate 20-day price range as % of price (volatility proxy)
        price_range = (df['close'].iloc[-20:].max() - df['close'].iloc[-20:].min()) / close * 100

        # Calculate direction consistency (% of days in same direction)
        daily_changes = df['close'].pct_change().iloc[-20:]
        up_days = (daily_changes > 0).sum()
        direction_consistency = (max(up_days, 20 - up_days) / 20) * 100

        # Determine trend strength
        if smas_aligned_up and direction_consistency > 70:
            signal = 'strong_uptrend'
            interpretation = f"Strong uptrend: Aligned SMAs, {direction_consistency:.0f}% directional consistency"
            strength = 'strong'
        elif smas_aligned_up or (close > sma20 and direction_consistency > 60):
            signal = 'uptrend'
            interpretation = f"Uptrend: Price above key moving averages"
            strength = 'moderate'
        elif smas_aligned_down and direction_consistency > 70:
            signal = 'strong_downtrend'
            interpretation = f"Strong downtrend: Aligned SMAs, {direction_consistency:.0f}% directional consistency"
            strength = 'strong'
        elif smas_aligned_down or (close < sma20 and direction_consistency > 60):
            signal = 'downtrend'
            interpretation = f"Downtrend: Price below key moving averages"
            strength = 'moderate'
        else:
            signal = 'choppy'
            interpretation = f"Choppy/sideways: No clear trend, {price_range:.1f}% 20-day range"
            strength = 'weak'

        return {
            'name': 'Trend Strength',
            'signal': signal,
            'strength': strength,
            'interpretation': interpretation,
            'components': {
                'direction_consistency': direction_consistency,
                'price_range_pct': price_range,
                'close': close,
                'sma20': sma20,
                'sma50': sma50
            },
            'timestamp': datetime.now().isoformat()
        }

    def calculate_volume_profile(self) -> Dict:
        """
        Analyze volume patterns to confirm price moves.
        """
        df = self.load_price_data(self.ticker, days=60)

        if df is None or len(df) < 20 or 'volume' not in df.columns:
            return {
                'signal': 'no_data',
                'interpretation': 'Insufficient volume data'
            }

        # Calculate average volume
        avg_volume_20d = df['volume'].iloc[-20:].mean()
        avg_volume_60d = df['volume'].iloc[-60:].mean()
        latest_volume = df['volume'].iloc[-1]

        # Volume trend
        volume_increasing = avg_volume_20d > avg_volume_60d * 1.2
        volume_decreasing = avg_volume_20d < avg_volume_60d * 0.8

        # Recent volume vs average
        recent_high_volume = latest_volume > avg_volume_20d * 1.5

        # Price direction
        price_change_20d = ((df['close'].iloc[-1] / df['close'].iloc[-20]) - 1) * 100

        # Determine signal
        if recent_high_volume and price_change_20d > 0:
            signal = 'bullish_volume'
            interpretation = f"Bullish: High volume (+{(latest_volume / avg_volume_20d - 1) * 100:.0f}%) on price rise"
        elif recent_high_volume and price_change_20d < 0:
            signal = 'bearish_volume'
            interpretation = f"Bearish: High volume on price decline (distribution)"
        elif volume_increasing and price_change_20d > 0:
            signal = 'volume_confirming_uptrend'
            interpretation = "Volume increasing on uptrend (healthy)"
        elif volume_decreasing and price_change_20d > 0:
            signal = 'weak_uptrend'
            interpretation = "Volume decreasing on uptrend (weak/exhaustion)"
        elif volume_increasing and price_change_20d < 0:
            signal = 'volume_confirming_downtrend'
            interpretation = "Volume increasing on downtrend (pressure)"
        else:
            signal = 'neutral'
            interpretation = "Volume patterns neutral"

        return {
            'name': 'Volume Profile',
            'signal': signal,
            'interpretation': interpretation,
            'components': {
                'latest_volume': int(latest_volume),
                'avg_volume_20d': int(avg_volume_20d),
                'avg_volume_60d': int(avg_volume_60d),
                'volume_vs_avg': (latest_volume / avg_volume_20d - 1) * 100,
                'price_change_20d': price_change_20d
            },
            'timestamp': datetime.now().isoformat()
        }

    def calculate_support_resistance(self) -> Dict:
        """
        Identify key support and resistance levels using pivot points and swing highs/lows.
        """
        df = self.load_price_data(self.ticker, days=120)

        if df is None or len(df) < 60:
            return {
                'signal': 'no_data',
                'interpretation': 'Insufficient data'
            }

        close = df['close'].iloc[-1]
        high_60d = df['high'].iloc[-60:].max()
        low_60d = df['low'].iloc[-60:].min()

        # Find recent swing highs and lows (local peaks/troughs)
        window = 5
        resistance_levels = []
        support_levels = []

        for i in range(window, len(df) - window):
            # Swing high (resistance)
            if df['high'].iloc[i] == df['high'].iloc[i - window:i + window + 1].max():
                resistance_levels.append(df['high'].iloc[i])
            # Swing low (support)
            if df['low'].iloc[i] == df['low'].iloc[i - window:i + window + 1].min():
                support_levels.append(df['low'].iloc[i])

        # Find nearest resistance and support
        resistance_above = [r for r in resistance_levels if r > close]
        support_below = [s for s in support_levels if s < close]

        nearest_resistance = min(resistance_above) if resistance_above else high_60d
        nearest_support = max(support_below) if support_below else low_60d

        # Distance to levels
        dist_to_resistance = ((nearest_resistance / close) - 1) * 100
        dist_to_support = ((close / nearest_support) - 1) * 100

        # Determine position
        if dist_to_resistance < 2:
            signal = 'at_resistance'
            interpretation = f"At resistance: {dist_to_resistance:.1f}% to ${nearest_resistance:.2f}"
        elif dist_to_support < 2:
            signal = 'at_support'
            interpretation = f"At support: {dist_to_support:.1f}% above ${nearest_support:.2f}"
        elif dist_to_resistance < dist_to_support:
            signal = 'closer_to_resistance'
            interpretation = f"Mid-range, closer to resistance (${nearest_resistance:.2f})"
        else:
            signal = 'closer_to_support'
            interpretation = f"Mid-range, closer to support (${nearest_support:.2f})"

        return {
            'name': 'Support/Resistance',
            'signal': signal,
            'interpretation': interpretation,
            'levels': {
                'current_price': close,
                'nearest_resistance': nearest_resistance,
                'nearest_support': nearest_support,
                'dist_to_resistance_pct': dist_to_resistance,
                'dist_to_support_pct': dist_to_support,
                'high_60d': high_60d,
                'low_60d': low_60d
            },
            'timestamp': datetime.now().isoformat()
        }

    def calculate_price_momentum(self) -> Dict:
        """
        Calculate price momentum using rate of change over multiple periods.
        """
        df = self.load_price_data(self.ticker, days=90)

        if df is None or len(df) < 60:
            return {
                'signal': 'no_data',
                'interpretation': 'Insufficient data'
            }

        close = df['close'].iloc[-1]

        # Calculate momentum over different periods
        momentum = {}
        periods = [5, 10, 20, 60]

        for period in periods:
            if len(df) >= period + 1:
                past_price = df['close'].iloc[-(period + 1)]
                mom = ((close / past_price) - 1) * 100
                momentum[f'{period}d'] = mom

        # Determine signal based on 20-day momentum
        mom_20d = momentum.get('20d', 0)

        if mom_20d > 10:
            signal = 'strong_positive'
            interpretation = f"Strong positive momentum: +{mom_20d:.1f}% over 20 days"
        elif mom_20d > 5:
            signal = 'positive'
            interpretation = f"Positive momentum: +{mom_20d:.1f}% over 20 days"
        elif mom_20d > 0:
            signal = 'slightly_positive'
            interpretation = f"Slightly positive: +{mom_20d:.1f}% over 20 days"
        elif mom_20d > -5:
            signal = 'slightly_negative'
            interpretation = f"Slightly negative: {mom_20d:.1f}% over 20 days"
        elif mom_20d > -10:
            signal = 'negative'
            interpretation = f"Negative momentum: {mom_20d:.1f}% over 20 days"
        else:
            signal = 'strong_negative'
            interpretation = f"Strong negative momentum: {mom_20d:.1f}% over 20 days"

        return {
            'name': 'Price Momentum',
            'signal': signal,
            'interpretation': interpretation,
            'periods': momentum,
            'timestamp': datetime.now().isoformat()
        }

    def calculate_all(self) -> Dict:
        """Calculate all ticker indicators."""
        return {
            'ticker': self.ticker,
            'relative_strength': self.calculate_relative_strength(),
            'trend_strength': self.calculate_trend_strength(),
            'volume_profile': self.calculate_volume_profile(),
            'support_resistance': self.calculate_support_resistance(),
            'price_momentum': self.calculate_price_momentum(),
            'timestamp': datetime.now().isoformat()
        }


def calculate_all_ticker_indicators(tickers: List[str]) -> Dict:
    """
    Calculate indicators for all tickers.

    Args:
        tickers: List of ticker symbols

    Returns:
        Dict with ticker symbols as keys, indicator data as values
    """
    results = {}

    for ticker in tickers:
        print(f"Calculating indicators for {ticker}...")
        try:
            calculator = TickerIndicators(ticker)
            results[ticker] = calculator.calculate_all()
        except Exception as e:
            print(f"Error calculating indicators for {ticker}: {e}")
            results[ticker] = {
                'ticker': ticker,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    return {
        'tickers': results,
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'ticker_count': len(tickers),
            'successful': len([t for t in results.values() if 'error' not in t])
        }
    }


if __name__ == '__main__':
    """Test ticker indicators."""
    test_tickers = ['AAPL', 'NVDA', 'SPY']

    for ticker in test_tickers:
        print(f"\n{'=' * 80}")
        print(f"TICKER: {ticker}")
        print('=' * 80)

        calc = TickerIndicators(ticker)
        indicators = calc.calculate_all()

        rs = indicators['relative_strength']
        print(f"\nRelative Strength: {rs['signal']}")
        print(f"  {rs.get('interpretation', rs.get('vs_spy_interpretation', 'N/A'))}")

        ts = indicators['trend_strength']
        print(f"\nTrend Strength: {ts['signal']}")
        print(f"  {ts.get('interpretation', 'N/A')}")

        vp = indicators['volume_profile']
        print(f"\nVolume Profile: {vp['signal']}")
        print(f"  {vp.get('interpretation', 'N/A')}")

        sr = indicators['support_resistance']
        print(f"\nSupport/Resistance: {sr['signal']}")
        print(f"  {sr.get('interpretation', 'N/A')}")

        pm = indicators['price_momentum']
        print(f"\nPrice Momentum: {pm['signal']}")
        print(f"  {pm.get('interpretation', 'N/A')}")
