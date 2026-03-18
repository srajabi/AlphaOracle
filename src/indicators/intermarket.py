#!/usr/bin/env python3
"""
Intermarket Indicators for Regime Change Detection

Individual reusable indicators based on relationships between:
- Equities (SPY)
- Bonds (TLT)
- Dollar (UUP)
- Commodities (GLD, SLV, XLE)
- Volatility (VIX)

Each indicator returns structured data for display on ticker dashboards.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class IndicatorBase:
    """Base class for all indicators."""

    def __init__(self):
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

    def calculate_trend(self, df: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> Dict:
        """
        Calculate trend status based on multiple SMAs.
        Returns dict with SMA values and trend classification.
        """
        close = df['close'].iloc[-1]
        result = {'current_price': close, 'smas': {}, 'above_count': 0}

        for period in periods:
            if len(df) >= period:
                sma = df['close'].rolling(window=period).mean().iloc[-1]
                result['smas'][f'sma{period}'] = sma
                if close > sma:
                    result['above_count'] += 1

        total_smas = len(result['smas'])
        if result['above_count'] == total_smas:
            result['trend'] = 'strong_uptrend'
        elif result['above_count'] >= total_smas / 2:
            result['trend'] = 'uptrend'
        elif result['above_count'] > 0:
            result['trend'] = 'neutral'
        else:
            result['trend'] = 'downtrend'

        return result

    def calculate_momentum(self, df: pd.DataFrame, period: int = 20) -> Dict:
        """
        Calculate rate of change momentum.
        Returns dict with momentum value and interpretation.
        """
        if len(df) < period + 1:
            return {'momentum': None, 'signal': 'insufficient_data'}

        current = df['close'].iloc[-1]
        past = df['close'].iloc[-(period + 1)]
        momentum = ((current / past) - 1) * 100  # Percentage change

        if momentum > 5:
            signal = 'strong_positive'
        elif momentum > 0:
            signal = 'positive'
        elif momentum > -5:
            signal = 'negative'
        else:
            signal = 'strong_negative'

        return {
            'momentum': momentum,
            'signal': signal,
            'period': period
        }


class RiskSentimentIndicator(IndicatorBase):
    """
    Risk Sentiment: Combines SPY trend with VIX level.

    High VIX + SPY downtrend = Risk-off environment
    Low VIX + SPY uptrend = Risk-on environment
    """

    def calculate(self) -> Dict:
        """Calculate risk sentiment indicator."""
        spy_df = self.load_price_data('SPY', days=250)
        vix_df = self.load_price_data('^VIX', days=250)

        if spy_df is None or vix_df is None:
            return {
                'name': 'Risk Sentiment',
                'value': None,
                'signal': 'no_data',
                'interpretation': 'Insufficient data'
            }

        # SPY trend
        spy_trend = self.calculate_trend(spy_df, periods=[20, 50, 200])

        # VIX level analysis
        vix_current = vix_df['close'].iloc[-1]
        vix_sma20 = vix_df['close'].rolling(window=20).mean().iloc[-1]
        vix_sma50 = vix_df['close'].rolling(window=50).mean().iloc[-1]

        # Classify VIX level
        if vix_current < 15:
            vix_level = 'low'
        elif vix_current < 20:
            vix_level = 'normal'
        elif vix_current < 30:
            vix_level = 'elevated'
        else:
            vix_level = 'high'

        # VIX trend
        if vix_current > vix_sma20 and vix_current > vix_sma50:
            vix_trend = 'rising'
        elif vix_current < vix_sma20 and vix_current < vix_sma50:
            vix_trend = 'falling'
        else:
            vix_trend = 'neutral'

        # Combine to determine risk sentiment
        if spy_trend['trend'] in ['strong_uptrend', 'uptrend'] and vix_level in ['low', 'normal'] and vix_trend == 'falling':
            signal = 'risk_on'
            interpretation = 'Strong risk-on: Equities rising, volatility low and falling'
        elif spy_trend['trend'] == 'downtrend' and vix_level in ['elevated', 'high'] and vix_trend == 'rising':
            signal = 'risk_off'
            interpretation = 'Risk-off: Equities falling, volatility elevated and rising'
        elif vix_level == 'high' or vix_trend == 'rising':
            signal = 'cautious'
            interpretation = 'Cautious environment: Elevated volatility signals uncertainty'
        else:
            signal = 'neutral'
            interpretation = 'Neutral risk environment'

        return {
            'name': 'Risk Sentiment',
            'value': signal,
            'signal': signal,
            'interpretation': interpretation,
            'components': {
                'spy_trend': spy_trend['trend'],
                'spy_price': spy_trend['current_price'],
                'vix_level': vix_level,
                'vix_value': vix_current,
                'vix_trend': vix_trend
            },
            'timestamp': datetime.now().isoformat()
        }


class DollarStrengthIndicator(IndicatorBase):
    """
    Dollar Strength: Tracks UUP (US Dollar Index ETF).

    Strong dollar typically negative for:
    - Commodities (priced in USD)
    - International stocks
    - Emerging markets
    """

    def calculate(self) -> Dict:
        """Calculate dollar strength indicator."""
        uup_df = self.load_price_data('UUP', days=250)

        if uup_df is None:
            return {
                'name': 'Dollar Strength',
                'value': None,
                'signal': 'no_data',
                'interpretation': 'Insufficient data'
            }

        # Trend analysis
        trend = self.calculate_trend(uup_df, periods=[20, 50, 200])

        # Momentum analysis
        momentum = self.calculate_momentum(uup_df, period=20)

        # Classify dollar strength
        if trend['trend'] == 'strong_uptrend' and momentum['signal'] in ['strong_positive', 'positive']:
            signal = 'strong_dollar'
            interpretation = 'Dollar strengthening: Headwind for commodities and international assets'
        elif trend['trend'] in ['uptrend', 'neutral'] and momentum['signal'] == 'positive':
            signal = 'dollar_rising'
            interpretation = 'Dollar rising: Moderate pressure on commodity prices'
        elif trend['trend'] == 'downtrend' and momentum['signal'] in ['strong_negative', 'negative']:
            signal = 'weak_dollar'
            interpretation = 'Dollar weakening: Tailwind for commodities and international assets'
        else:
            signal = 'neutral'
            interpretation = 'Dollar stable: Neutral for commodities'

        return {
            'name': 'Dollar Strength',
            'value': signal,
            'signal': signal,
            'interpretation': interpretation,
            'components': {
                'uup_price': trend['current_price'],
                'trend': trend['trend'],
                'momentum': momentum['momentum'],
                'smas': trend['smas']
            },
            'timestamp': datetime.now().isoformat()
        }


class RealRatesIndicator(IndicatorBase):
    """
    Real Rates Proxy: Tracks TLT (20+ Year Treasury Bond ETF).

    TLT rising = Yields falling = Rates down = Good for growth stocks
    TLT falling = Yields rising = Rates up = Good for value/financials
    """

    def calculate(self) -> Dict:
        """Calculate real rates indicator."""
        tlt_df = self.load_price_data('TLT', days=250)

        if tlt_df is None:
            return {
                'name': 'Real Rates',
                'value': None,
                'signal': 'no_data',
                'interpretation': 'Insufficient data'
            }

        # Trend analysis
        trend = self.calculate_trend(tlt_df, periods=[20, 50, 200])

        # Momentum analysis
        momentum = self.calculate_momentum(tlt_df, period=20)

        # Classify rate environment
        # Note: TLT price inversely related to yields
        if trend['trend'] == 'strong_uptrend' and momentum['signal'] in ['strong_positive', 'positive']:
            signal = 'falling_rates'
            interpretation = 'Rates falling sharply: Favorable for growth stocks and long duration assets'
        elif trend['trend'] in ['uptrend', 'neutral'] and momentum['signal'] == 'positive':
            signal = 'rates_declining'
            interpretation = 'Rates declining: Moderately favorable for equities'
        elif trend['trend'] == 'downtrend' and momentum['signal'] in ['strong_negative', 'negative']:
            signal = 'rising_rates'
            interpretation = 'Rates rising: Headwind for growth stocks, favor value/financials'
        else:
            signal = 'stable_rates'
            interpretation = 'Rates stable: Neutral environment'

        return {
            'name': 'Real Rates',
            'value': signal,
            'signal': signal,
            'interpretation': interpretation,
            'components': {
                'tlt_price': trend['current_price'],
                'trend': trend['trend'],
                'momentum': momentum['momentum'],
                'smas': trend['smas']
            },
            'timestamp': datetime.now().isoformat()
        }


class CommodityStrengthIndicator(IndicatorBase):
    """
    Commodity Strength: Tracks GLD (gold), SLV (silver), XLE (energy).

    Strong commodities can signal:
    - Inflation concerns
    - Weak dollar environment
    - Risk-off (gold) or risk-on (energy/industrial metals)
    """

    def calculate(self) -> Dict:
        """Calculate commodity strength indicator."""
        gld_df = self.load_price_data('GLD', days=250)
        slv_df = self.load_price_data('SLV', days=250)
        xle_df = self.load_price_data('XLE', days=250)

        results = {}

        # Analyze each commodity
        for ticker, df, name in [('GLD', gld_df, 'Gold'), ('SLV', slv_df, 'Silver'), ('XLE', xle_df, 'Energy')]:
            if df is None:
                results[ticker.lower()] = {'signal': 'no_data'}
                continue

            trend = self.calculate_trend(df, periods=[20, 50, 200])
            momentum = self.calculate_momentum(df, period=20)

            results[ticker.lower()] = {
                'name': name,
                'price': trend['current_price'],
                'trend': trend['trend'],
                'momentum': momentum['momentum'],
                'signal': momentum['signal']
            }

        # Count how many commodities are in uptrend
        uptrend_count = sum(1 for v in results.values()
                           if v.get('trend') in ['strong_uptrend', 'uptrend'])

        # Determine overall commodity strength
        if uptrend_count >= 2:
            if results['gld'].get('trend') in ['strong_uptrend', 'uptrend']:
                signal = 'commodities_strong_defensive'
                interpretation = 'Commodities rallying with gold leading: Possible inflation/risk-off signal'
            else:
                signal = 'commodities_strong_cyclical'
                interpretation = 'Cyclical commodities strong: Risk-on, economic growth signal'
        elif uptrend_count == 1:
            signal = 'commodities_mixed'
            interpretation = 'Mixed commodity signals: Sector-specific factors at play'
        else:
            signal = 'commodities_weak'
            interpretation = 'Commodities weak across the board: Disinflationary/strong dollar environment'

        return {
            'name': 'Commodity Strength',
            'value': signal,
            'signal': signal,
            'interpretation': interpretation,
            'components': results,
            'timestamp': datetime.now().isoformat()
        }


class MarketRegimeDetector(IndicatorBase):
    """
    Market Regime: Combines all intermarket indicators to classify current regime.

    Regimes:
    - Bull Quiet: Risk-on, low vol, rising equities
    - Bull Volatile: Rising equities but elevated vol
    - Bear Quiet: Declining equities, rising bonds
    - Bear Volatile: Risk-off, high vol, flight to safety
    - Transitional: Mixed signals, regime unclear
    """

    def __init__(self):
        super().__init__()
        self.risk_sentiment = RiskSentimentIndicator()
        self.dollar_strength = DollarStrengthIndicator()
        self.real_rates = RealRatesIndicator()
        self.commodity_strength = CommodityStrengthIndicator()

    def calculate(self) -> Dict:
        """Calculate market regime based on all indicators."""
        # Get all indicator readings
        risk = self.risk_sentiment.calculate()
        dollar = self.dollar_strength.calculate()
        rates = self.real_rates.calculate()
        commodities = self.commodity_strength.calculate()

        # Determine regime
        risk_signal = risk.get('signal', 'neutral')

        if risk_signal == 'risk_on':
            if risk['components']['vix_level'] in ['low', 'normal']:
                regime = 'Bull Quiet'
                confidence = 'high'
            else:
                regime = 'Bull Volatile'
                confidence = 'medium'
        elif risk_signal == 'risk_off':
            if risk['components']['vix_level'] in ['high', 'elevated']:
                regime = 'Bear Volatile'
                confidence = 'high'
            else:
                regime = 'Bear Quiet'
                confidence = 'medium'
        elif risk_signal == 'cautious':
            # Check other indicators for clarity
            if dollar['signal'] == 'strong_dollar' and rates['signal'] == 'rising_rates':
                regime = 'Bear Quiet'
                confidence = 'medium'
            else:
                regime = 'Transitional'
                confidence = 'low'
        else:
            regime = 'Transitional'
            confidence = 'low'

        # Build regime interpretation
        factors = []
        if risk_signal != 'neutral':
            factors.append(f"Risk: {risk_signal.replace('_', ' ').title()}")
        if dollar['signal'] != 'neutral':
            factors.append(f"Dollar: {dollar['signal'].replace('_', ' ').title()}")
        if rates['signal'] != 'stable_rates':
            factors.append(f"Rates: {rates['signal'].replace('_', ' ').title()}")
        if commodities['signal'] != 'commodities_mixed':
            factors.append(f"Commodities: {commodities['signal'].replace('commodities_', '').replace('_', ' ').title()}")

        interpretation = f"{regime} regime. " + " | ".join(factors)

        return {
            'name': 'Market Regime',
            'value': regime,
            'regime': regime,
            'confidence': confidence,
            'interpretation': interpretation,
            'components': {
                'risk_sentiment': risk,
                'dollar_strength': dollar,
                'real_rates': rates,
                'commodity_strength': commodities
            },
            'timestamp': datetime.now().isoformat()
        }


def calculate_all_indicators() -> Dict:
    """
    Calculate all intermarket indicators.
    Returns structured data ready for JSON export.
    """
    regime_detector = MarketRegimeDetector()

    # Get regime (includes all sub-indicators)
    regime = regime_detector.calculate()

    return {
        'market_regime': regime,
        'indicators': {
            'risk_sentiment': regime['components']['risk_sentiment'],
            'dollar_strength': regime['components']['dollar_strength'],
            'real_rates': regime['components']['real_rates'],
            'commodity_strength': regime['components']['commodity_strength']
        },
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'data_source': 'EOD historical data',
            'lookback_days': 250
        }
    }


if __name__ == '__main__':
    """Test the indicators."""
    print("Calculating Intermarket Indicators...\n")

    indicators = calculate_all_indicators()

    print("=" * 80)
    print(f"MARKET REGIME: {indicators['market_regime']['regime']}")
    print(f"Confidence: {indicators['market_regime']['confidence'].upper()}")
    print(f"Interpretation: {indicators['market_regime']['interpretation']}")
    print("=" * 80)
    print()

    print("Individual Indicators:")
    print("-" * 80)

    for name, indicator in indicators['indicators'].items():
        print(f"\n{indicator['name'].upper()}")
        print(f"  Signal: {indicator['signal']}")
        print(f"  {indicator['interpretation']}")

    print("\n" + "=" * 80)
    print("\nFull JSON output:")
    print(json.dumps(indicators, indent=2, default=str))
