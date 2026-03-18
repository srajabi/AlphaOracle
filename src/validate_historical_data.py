#!/usr/bin/env python3
"""
Validate quality of downloaded historical data.

This script checks for data quality issues like gaps, zero prices,
extreme outliers, and insufficient history.

Usage:
    python3 src/validate_historical_data.py
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd


def load_ticker_data(ticker, data_dir='data/historical_long'):
    """Load historical data for a ticker"""
    ticker_file = Path(data_dir) / f"{ticker}.json"

    if not ticker_file.exists():
        return None

    with open(ticker_file) as f:
        data = json.load(f)

    return data


def validate_ticker(ticker, data_dir='data/historical_long'):
    """
    Validate data quality for a single ticker.

    Returns dict with validation results.
    """
    data = load_ticker_data(ticker, data_dir)

    if data is None:
        return {
            'ticker': ticker,
            'valid': False,
            'error': 'File not found',
            'issues': []
        }

    df = pd.DataFrame(data['prices'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    issues = []

    # 1. Check minimum data length
    if len(df) < 252:  # Less than 1 year of trading days
        issues.append(f"⚠️  Only {len(df)} days of data (< 1 year)")

    # 2. Calculate time span
    start = df.iloc[0]['date']
    end = df.iloc[-1]['date']
    years = (end - start).days / 365.25

    if years < 5:
        issues.append(f"⚠️  Only {years:.1f} years of history (< 5 years)")

    # 3. Check for large gaps (more than 10 trading days)
    df['days_since_prev'] = df['date'].diff().dt.days
    large_gaps = df[df['days_since_prev'] > 10]

    if not large_gaps.empty:
        for _, row in large_gaps.iterrows():
            gap_days = int(row['days_since_prev'])
            issues.append(f"⚠️  {gap_days}-day gap ending {row['date'].date()}")

    # 4. Check for zero or negative prices
    zero_prices = df[(df['close'] <= 0) | (df['open'] <= 0) | (df['high'] <= 0) | (df['low'] <= 0)]
    if not zero_prices.empty:
        issues.append(f"❌ {len(zero_prices)} rows with zero/negative prices")

    # 5. Check for zero volume (except indices like ^VIX)
    if not ticker.startswith('^'):
        zero_volume = df[df['volume'] == 0]
        if not zero_volume.empty and len(zero_volume) > len(df) * 0.01:  # More than 1% of data
            issues.append(f"⚠️  {len(zero_volume)} rows with zero volume ({len(zero_volume)/len(df)*100:.1f}%)")

    # 6. Check for extreme price moves (possible data errors)
    df['pct_change'] = df['close'].pct_change()
    extreme_moves = df[abs(df['pct_change']) > 0.5]  # 50% moves

    # Filter out known events (like stock splits that might not be adjusted)
    suspicious_moves = extreme_moves[abs(extreme_moves['pct_change']) > 0.8]  # 80%+ moves

    if not suspicious_moves.empty:
        for _, row in suspicious_moves.head(3).iterrows():
            move_pct = row['pct_change'] * 100
            issues.append(f"⚠️  Extreme move: {move_pct:+.1f}% on {row['date'].date()}")

    # 7. Check high-low consistency
    invalid_candles = df[(df['high'] < df['low']) |
                         (df['close'] > df['high']) |
                         (df['close'] < df['low']) |
                         (df['open'] > df['high']) |
                         (df['open'] < df['low'])]

    if not invalid_candles.empty:
        issues.append(f"❌ {len(invalid_candles)} rows with invalid OHLC (high < low, etc.)")

    # Determine if data is valid
    critical_issues = [issue for issue in issues if issue.startswith('❌')]
    valid = len(critical_issues) == 0

    return {
        'ticker': ticker,
        'valid': valid,
        'days': len(df),
        'years': round(years, 1),
        'start_date': str(start.date()),
        'end_date': str(end.date()),
        'issues': issues
    }


def main():
    data_dir = Path('data/historical_long')

    if not data_dir.exists():
        print(f"❌ ERROR: {data_dir} does not exist")
        print("Run download_long_history.py first")
        return

    # Get all ticker files
    ticker_files = sorted(data_dir.glob('*.json'))
    ticker_files = [f for f in ticker_files if f.name != 'download_summary.json']

    if not ticker_files:
        print(f"❌ ERROR: No ticker data files found in {data_dir}")
        return

    print(f"🔍 Validating {len(ticker_files)} tickers...\n")

    all_results = []
    valid_count = 0
    invalid_count = 0

    for ticker_file in ticker_files:
        ticker = ticker_file.stem
        result = validate_ticker(ticker, data_dir)
        all_results.append(result)

        if result['valid']:
            valid_count += 1
            status = "✓"
        else:
            invalid_count += 1
            status = "❌"

        print(f"{status} {ticker}: {result['days']} days ({result['years']} years)")

        if result.get('issues'):
            for issue in result['issues']:
                print(f"    {issue}")

        print()

    # Summary
    print("="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    print(f"Total tickers:  {len(ticker_files)}")
    print(f"✓ Valid:        {valid_count}")
    print(f"❌ Issues:       {invalid_count}")

    # Statistics on valid data
    if valid_count > 0:
        valid_results = [r for r in all_results if r['valid']]
        avg_years = sum(r['years'] for r in valid_results) / len(valid_results)
        min_years = min(r['years'] for r in valid_results)
        max_years = max(r['years'] for r in valid_results)

        print(f"\n📈 Valid data statistics:")
        print(f"  Average: {avg_years:.1f} years")
        print(f"  Min:     {min_years:.1f} years")
        print(f"  Max:     {max_years:.1f} years")

    # List tickers with issues
    if invalid_count > 0:
        print(f"\n⚠️  Tickers with issues:")
        for result in all_results:
            if not result['valid']:
                print(f"  {result['ticker']}: {', '.join(result['issues'][:2])}")

    # Check if minimum requirements met for backtesting
    print(f"\n✅ Backtesting readiness:")
    tickers_5plus_years = sum(1 for r in all_results if r.get('years', 0) >= 5)
    tickers_10plus_years = sum(1 for r in all_results if r.get('years', 0) >= 10)
    tickers_20plus_years = sum(1 for r in all_results if r.get('years', 0) >= 20)

    print(f"  5+ years:  {tickers_5plus_years}/{len(ticker_files)}")
    print(f"  10+ years: {tickers_10plus_years}/{len(ticker_files)}")
    print(f"  20+ years: {tickers_20plus_years}/{len(ticker_files)}")

    if tickers_10plus_years >= len(ticker_files) * 0.8:
        print(f"\n✅ READY: {tickers_10plus_years} tickers have 10+ years of data")
        print(f"   You can now run backtests across market regimes!")
    else:
        print(f"\n⚠️  LIMITED: Only {tickers_10plus_years} tickers have 10+ years")
        print(f"   Some regime backtests may have limited coverage")

    print("="*70)


if __name__ == '__main__':
    main()
