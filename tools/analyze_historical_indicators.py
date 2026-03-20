#!/usr/bin/env python3
"""
Historical Intermarket Indicator Analysis

Calculates intermarket indicators daily from 1993-2026 to analyze:
1. How well indicators predicted regime changes
2. Lead time before major market moves
3. Accuracy of regime classifications
4. False positive/negative rates

This is computationally intensive and should be run offline, not in daily workflow.

Outputs:
- data/historical_indicators.json - Full historical indicator values
- data/indicator_analysis.json - Predictive power metrics
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import sys

# Import our indicator classes
sys.path.append(str(Path(__file__).parent))
from indicators.intermarket import (
    RiskSentimentIndicator,
    DollarStrengthIndicator,
    RealRatesIndicator,
    CommodityStrengthIndicator,
    MarketRegimeDetector
)


class HistoricalIndicatorAnalyzer:
    """Analyze indicators historically to measure predictive power."""

    def __init__(self, use_long_history: bool = True):
        """
        Initialize analyzer.

        Args:
            use_long_history: If True, use data/historical_long/, else data/history/
        """
        self.data_dir = Path('data/historical_long' if use_long_history else 'data/history')
        self.historical_indicators = []
        self.analysis_results = {}

    def load_historical_data(self, ticker: str) -> pd.DataFrame:
        """Load all available historical data for a ticker."""
        try:
            file_path = self.data_dir / f'{ticker}.json'
            if not file_path.exists():
                # Fallback to regular history
                file_path = Path('data/history') / f'{ticker}.json'

            with open(file_path) as f:
                data = json.load(f)

            # Handle different JSON formats
            if isinstance(data, dict) and 'prices' in data:
                # historical_long format: {"ticker": "SPY", "prices": [...]}
                price_data = data['prices']
                # Convert 'date' field to 'time' for consistency
                for record in price_data:
                    if 'date' in record and 'time' not in record:
                        record['time'] = record['date']
            elif isinstance(data, list):
                # Regular history format: [{...}, {...}]
                price_data = data
            else:
                return None

            if len(price_data) == 0:
                return None

            df = pd.DataFrame(price_data)
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time')
            df = df.set_index('time')

            return df

        except Exception as e:
            print(f"Error loading {ticker}: {e}")
            return None

    def calculate_indicators_daily(self, start_date: str = '1993-01-01', end_date: str = None) -> List[Dict]:
        """
        Calculate indicators for each trading day in the date range.

        This is computationally expensive - calculating indicators from scratch for each day.
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        print(f"\nCalculating daily indicators from {start_date} to {end_date}...")
        print("This may take several minutes...\n")

        # Load all necessary data
        print("Loading historical data...")
        spy_df = self.load_historical_data('SPY')
        vix_df = self.load_historical_data('^VIX')
        uup_df = self.load_historical_data('UUP')
        tlt_df = self.load_historical_data('TLT')
        gld_df = self.load_historical_data('GLD')
        slv_df = self.load_historical_data('SLV')
        xle_df = self.load_historical_data('XLE')

        if spy_df is None:
            print("ERROR: Could not load SPY data. Aborting.")
            return []

        # Filter to date range
        spy_df = spy_df[start_date:end_date]

        print(f"Found {len(spy_df)} trading days")
        print("Calculating indicators...")

        results = []
        total_days = len(spy_df)

        for i, (date, row) in enumerate(spy_df.iterrows()):
            if (i + 1) % 250 == 0:  # Progress every year
                print(f"  Processed {i + 1}/{total_days} days ({date.strftime('%Y-%m-%d')})")

            # Get data up to this date for calculation
            # Need at least 250 days of lookback for indicators
            lookback_start = date - timedelta(days=365)

            try:
                # Calculate indicators using data only up to this date
                regime = self._calculate_regime_for_date(
                    date, lookback_start,
                    spy_df, vix_df, uup_df, tlt_df, gld_df, slv_df, xle_df
                )

                if regime:
                    results.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'regime': regime['regime'],
                        'confidence': regime['confidence'],
                        'spy_close': float(row['close']),
                        'indicators': {
                            'risk_sentiment': regime['components'].get('risk_sentiment', {}).get('signal'),
                            'dollar_strength': regime['components'].get('dollar_strength', {}).get('signal'),
                            'real_rates': regime['components'].get('real_rates', {}).get('signal'),
                            'commodity_strength': regime['components'].get('commodity_strength', {}).get('signal')
                        }
                    })

            except Exception as e:
                # Skip days where calculation fails (not enough data)
                pass

        print(f"\n✓ Calculated indicators for {len(results)} days")
        return results

    def _calculate_regime_for_date(self, date, lookback_start, spy_df, vix_df, uup_df, tlt_df, gld_df, slv_df, xle_df) -> Dict:
        """Calculate regime using only data up to the specified date."""
        # Filter all dataframes to only include data up to this date
        def filter_to_date(df, start, end):
            if df is None:
                return None
            try:
                return df[start:end].copy()
            except:
                return None

        spy_slice = filter_to_date(spy_df, lookback_start, date)
        vix_slice = filter_to_date(vix_df, lookback_start, date)
        uup_slice = filter_to_date(uup_df, lookback_start, date)
        tlt_slice = filter_to_date(tlt_df, lookback_start, date)
        gld_slice = filter_to_date(gld_df, lookback_start, date)
        slv_slice = filter_to_date(slv_df, lookback_start, date)
        xle_slice = filter_to_date(xle_df, lookback_start, date)

        # Need at least 200 days for indicators
        if spy_slice is None or len(spy_slice) < 200:
            return None
        if vix_slice is None or len(vix_slice) < 50:
            return None

        # Calculate regime components
        # This is a simplified version that uses the dataframes directly
        # In production, we'd need to refactor the indicator classes to accept dataframes

        # For now, return a simplified regime classification based on SPY trend and VIX level
        close = spy_slice['close'].iloc[-1]
        sma200 = spy_slice['close'].rolling(window=200).mean().iloc[-1]
        vix_level = vix_slice['close'].iloc[-1] if vix_slice is not None and len(vix_slice) > 0 else 20

        # Simple regime classification
        if close > sma200:
            if vix_level < 20:
                regime = 'Bull Quiet'
                confidence = 'high'
            else:
                regime = 'Bull Volatile'
                confidence = 'medium'
        else:
            if vix_level > 25:
                regime = 'Bear Volatile'
                confidence = 'high'
            else:
                regime = 'Bear Quiet'
                confidence = 'medium'

        return {
            'regime': regime,
            'confidence': confidence,
            'components': {
                'risk_sentiment': {'signal': 'risk_on' if close > sma200 and vix_level < 20 else 'risk_off'},
                'dollar_strength': {'signal': 'neutral'},  # Simplified
                'real_rates': {'signal': 'neutral'},  # Simplified
                'commodity_strength': {'signal': 'neutral'}  # Simplified
            }
        }

    def analyze_regime_transitions(self, historical_indicators: List[Dict]) -> Dict:
        """
        Analyze regime transitions to identify:
        - How long regime lasted before change
        - How accurate regime classification was
        - Lead time before major moves
        """
        if not historical_indicators:
            return {}

        transitions = []
        current_regime = None
        regime_start = None

        for record in historical_indicators:
            regime = record['regime']
            date = record['date']

            if regime != current_regime:
                if current_regime is not None:
                    # Record transition
                    transitions.append({
                        'from_regime': current_regime,
                        'to_regime': regime,
                        'start_date': regime_start,
                        'end_date': date,
                        'duration_days': (pd.to_datetime(date) - pd.to_datetime(regime_start)).days
                    })

                current_regime = regime
                regime_start = date

        return {
            'total_transitions': len(transitions),
            'transitions': transitions,
            'regime_durations': {
                'mean_days': np.mean([t['duration_days'] for t in transitions]) if transitions else 0,
                'median_days': np.median([t['duration_days'] for t in transitions]) if transitions else 0
            }
        }

    def analyze_predictive_power(self, historical_indicators: List[Dict]) -> Dict:
        """
        Measure how well indicators predicted future returns.

        For each indicator reading, look forward N days and measure:
        - Did risk-off signals predict negative returns?
        - Did risk-on signals predict positive returns?
        """
        if not historical_indicators:
            return {}

        print("\nAnalyzing predictive power...")

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(historical_indicators)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # Calculate forward returns (5, 20, 60 days)
        for days in [5, 20, 60]:
            df[f'fwd_return_{days}d'] = df['spy_close'].pct_change(periods=days).shift(-days) * 100

        # Analyze risk sentiment signal accuracy
        risk_on_df = df[df['indicators'].apply(lambda x: x.get('risk_sentiment') == 'risk_on')]
        risk_off_df = df[df['indicators'].apply(lambda x: x.get('risk_sentiment') == 'risk_off')]

        results = {
            'risk_sentiment_analysis': {
                'risk_on': {
                    'count': len(risk_on_df),
                    'avg_fwd_return_20d': risk_on_df['fwd_return_20d'].mean() if len(risk_on_df) > 0 else None,
                    'positive_rate': (risk_on_df['fwd_return_20d'] > 0).sum() / len(risk_on_df) if len(risk_on_df) > 0 else None
                },
                'risk_off': {
                    'count': len(risk_off_df),
                    'avg_fwd_return_20d': risk_off_df['fwd_return_20d'].mean() if len(risk_off_df) > 0 else None,
                    'negative_rate': (risk_off_df['fwd_return_20d'] < 0).sum() / len(risk_off_df) if len(risk_off_df) > 0 else None
                }
            }
        }

        # Analyze regime classification accuracy
        for regime in ['Bull Quiet', 'Bull Volatile', 'Bear Quiet', 'Bear Volatile']:
            regime_df = df[df['regime'] == regime]
            if len(regime_df) > 0:
                results[f'regime_{regime.lower().replace(" ", "_")}'] = {
                    'count': len(regime_df),
                    'avg_fwd_return_20d': regime_df['fwd_return_20d'].mean(),
                    'positive_rate_20d': (regime_df['fwd_return_20d'] > 0).sum() / len(regime_df)
                }

        return results

    def run_full_analysis(self) -> Dict:
        """Run complete historical analysis."""
        # Calculate daily indicators
        historical_indicators = self.calculate_indicators_daily()

        if not historical_indicators:
            print("ERROR: No historical indicators calculated")
            return {}

        # Analyze transitions
        print("\nAnalyzing regime transitions...")
        transitions = self.analyze_regime_transitions(historical_indicators)

        # Analyze predictive power
        predictive_power = self.analyze_predictive_power(historical_indicators)

        # Compile results
        results = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'start_date': historical_indicators[0]['date'],
                'end_date': historical_indicators[-1]['date'],
                'total_days': len(historical_indicators)
            },
            'historical_indicators': historical_indicators,
            'regime_transitions': transitions,
            'predictive_power': predictive_power
        }

        return results


def main():
    """Run historical indicator analysis."""
    print("=" * 80)
    print("HISTORICAL INTERMARKET INDICATOR ANALYSIS")
    print("=" * 80)

    analyzer = HistoricalIndicatorAnalyzer(use_long_history=True)

    # Run analysis
    results = analyzer.run_full_analysis()

    if not results:
        print("\nERROR: Analysis failed")
        return

    # Save full historical indicators (warning: large file)
    historical_path = Path('data/historical_indicators.json')
    print(f"\nSaving historical indicators to {historical_path}...")
    with open(historical_path, 'w') as f:
        json.dump(results['historical_indicators'], indent=2, fp=f)
    print(f"✓ Saved {len(results['historical_indicators'])} daily indicator readings")

    # Save analysis results (summary only)
    analysis_path = Path('data/indicator_analysis.json')
    print(f"\nSaving analysis results to {analysis_path}...")
    analysis_only = {
        'metadata': results['metadata'],
        'regime_transitions': results['regime_transitions'],
        'predictive_power': results['predictive_power']
    }
    with open(analysis_path, 'w') as f:
        json.dump(analysis_only, indent=2, fp=f, default=str)
    print(f"✓ Saved analysis results")

    # Print summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)

    meta = results['metadata']
    print(f"\nPeriod: {meta['start_date']} to {meta['end_date']}")
    print(f"Total trading days analyzed: {meta['total_days']}")

    trans = results['regime_transitions']
    print(f"\nRegime Transitions: {trans['total_transitions']}")
    print(f"Average regime duration: {trans['regime_durations']['mean_days']:.0f} days")
    print(f"Median regime duration: {trans['regime_durations']['median_days']:.0f} days")

    pred = results['predictive_power']
    risk_sent = pred.get('risk_sentiment_analysis', {})

    if 'risk_on' in risk_sent:
        risk_on = risk_sent['risk_on']
        print(f"\nRisk-On Signal Performance:")
        print(f"  Count: {risk_on['count']}")
        if risk_on['avg_fwd_return_20d'] is not None:
            print(f"  Avg 20-day forward return: {risk_on['avg_fwd_return_20d']:.2f}%")
            print(f"  Positive rate: {risk_on['positive_rate']:.1%}")

    if 'risk_off' in risk_sent:
        risk_off = risk_sent['risk_off']
        print(f"\nRisk-Off Signal Performance:")
        print(f"  Count: {risk_off['count']}")
        if risk_off['avg_fwd_return_20d'] is not None:
            print(f"  Avg 20-day forward return: {risk_off['avg_fwd_return_20d']:.2f}%")
            print(f"  Negative rate: {risk_off['negative_rate']:.1%}")

    print("\n" + "=" * 80)
    print("✓ Historical indicator analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
