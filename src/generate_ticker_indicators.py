#!/usr/bin/env python3
"""
Generate Per-Ticker Indicators

Calculates technical indicators for all tickers in the watchlist
and saves them to JSON files for backend analysis and frontend display.

Outputs:
- data/ticker_indicators.json - Backend reference
- frontend/public/data/ticker_indicators.json - Frontend display
"""

import json
import csv
from pathlib import Path
from indicators.ticker_indicators import calculate_all_ticker_indicators


def load_watchlist() -> list:
    """Load tickers from watchlist.csv."""
    watchlist_path = Path('watchlist.csv')
    tickers = []

    if not watchlist_path.exists():
        print(f"Warning: {watchlist_path} not found")
        return tickers

    with open(watchlist_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row.get('Ticker', '').strip()
            if ticker:
                tickers.append(ticker)

    return tickers


def main():
    """Generate and save ticker indicator data."""
    print("Loading watchlist...")
    tickers = load_watchlist()

    if not tickers:
        print("No tickers found in watchlist")
        return

    print(f"Found {len(tickers)} tickers in watchlist")
    print("\nCalculating ticker indicators...")

    # Calculate all indicators
    indicators = calculate_all_ticker_indicators(tickers)

    # Save to backend data directory
    backend_path = Path('data/ticker_indicators.json')
    backend_path.parent.mkdir(parents=True, exist_ok=True)
    with open(backend_path, 'w') as f:
        json.dump(indicators, indent=2, fp=f, default=str)
    print(f"\n✓ Saved to {backend_path}")

    # Save to frontend data directory
    frontend_path = Path('frontend/public/data/ticker_indicators.json')
    frontend_path.parent.mkdir(parents=True, exist_ok=True)
    with open(frontend_path, 'w') as f:
        json.dump(indicators, indent=2, fp=f, default=str)
    print(f"✓ Saved to {frontend_path}")

    # Print summary
    print("\n" + "=" * 80)
    print(f"TICKER INDICATOR GENERATION COMPLETE")
    print("=" * 80)
    print(f"Total tickers: {indicators['metadata']['ticker_count']}")
    print(f"Successful: {indicators['metadata']['successful']}")
    print(f"Errors: {indicators['metadata']['ticker_count'] - indicators['metadata']['successful']}")

    # Show sample of indicators for a few tickers
    sample_tickers = ['SPY', 'AAPL', 'NVDA']
    for ticker in sample_tickers:
        if ticker in indicators['tickers']:
            ticker_data = indicators['tickers'][ticker]
            if 'error' not in ticker_data:
                print(f"\n{ticker}:")
                print(f"  Trend: {ticker_data.get('trend_strength', {}).get('signal', 'N/A')}")
                print(f"  Momentum: {ticker_data.get('price_momentum', {}).get('signal', 'N/A')}")
                print(f"  Relative Strength: {ticker_data.get('relative_strength', {}).get('signal', 'N/A')}")

    print("\n✓ Ticker indicator generation complete!")


if __name__ == '__main__':
    main()
