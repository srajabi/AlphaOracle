#!/usr/bin/env python3
"""
Download 5-minute historical intraday data using Alpaca API.

Alpaca provides free historical data for stocks and ETFs with 5-minute bars
going back several years. This complements our daily data by enabling accurate
intraday stop loss backtesting.

Usage:
    # Set credentials (optional if already in environment)
    export ALPACA_API_KEY='your_key'
    export ALPACA_SECRET_KEY='your_secret'

    # Test with 1 ticker
    python3 src/download_intraday_history.py --test --years 2

    # Download full dataset
    python3 src/download_intraday_history.py --years 5

    # Download specific tickers
    python3 src/download_intraday_history.py --tickers TQQQ,SPY,QQQ
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import time

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from dotenv import load_dotenv

load_dotenv()


def get_alpaca_client():
    """Initialize Alpaca historical data client."""
    api_key = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_DEV_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_DEV_SECRET_KEY')

    if not api_key or not secret_key:
        raise ValueError(
            "Alpaca credentials not found. Set environment variables:\n"
            "  ALPACA_API_KEY or ALPACA_DEV_API_KEY\n"
            "  ALPACA_SECRET_KEY or ALPACA_DEV_SECRET_KEY"
        )

    # Strip quotes if present (from .env file)
    api_key = api_key.strip('"').strip("'")
    secret_key = secret_key.strip('"').strip("'")

    return StockHistoricalDataClient(api_key, secret_key)


def download_ticker_5min(client, ticker: str, years: int = 5, retries: int = 3):
    """
    Download 5-minute bars for a ticker in monthly chunks.

    Args:
        client: Alpaca StockHistoricalDataClient
        ticker: Stock symbol
        years: Number of years to download
        retries: Number of retry attempts

    Returns:
        dict with bars data or None if failed
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)

    # Download in monthly chunks to avoid rate limits
    print(f"  Downloading in monthly chunks from {start_date.date()} to {end_date.date()}...")

    all_bars = []
    current_start = start_date
    chunk_num = 0
    total_chunks = years * 12  # Approximate number of months

    # Download in monthly chunks
    while current_start < end_date:
        chunk_num += 1
        chunk_end = min(current_start + timedelta(days=30), end_date)

        for attempt in range(retries):
            try:
                print(f"  Chunk {chunk_num}/{total_chunks}: {current_start.date()} to {chunk_end.date()}")

                request = StockBarsRequest(
                    symbol_or_symbols=ticker,
                    timeframe=TimeFrame(5, TimeFrameUnit.Minute),
                    start=current_start,
                    end=chunk_end,
                    limit=None
                )

                bars = client.get_stock_bars(request)

                if bars and ticker in bars:
                    ticker_bars = bars[ticker]
                    print(f"    ✓ Got {len(ticker_bars)} bars")

                    # Convert to dicts
                    for bar in ticker_bars:
                        all_bars.append({
                            'timestamp': bar.timestamp.isoformat(),
                            'open': round(float(bar.open), 2),
                            'high': round(float(bar.high), 2),
                            'low': round(float(bar.low), 2),
                            'close': round(float(bar.close), 2),
                            'volume': int(bar.volume),
                            'trade_count': bar.trade_count if hasattr(bar, 'trade_count') else None,
                            'vwap': round(float(bar.vwap), 2) if hasattr(bar, 'vwap') and bar.vwap else None
                        })

                    # Success - break retry loop
                    break
                else:
                    print(f"    ⚠️  No data for this chunk")
                    break  # No point retrying if no data

            except Exception as e:
                print(f"    ❌ Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    print(f"    Waiting 5 seconds...")
                    time.sleep(5)
                else:
                    print(f"    Skipping this chunk after {retries} attempts")
                    break

        # Rate limit: wait between chunks
        time.sleep(2)
        current_start = chunk_end

    if len(all_bars) == 0:
        print(f"  ❌ No bars downloaded for {ticker}")
        return None

    # Sort by timestamp
    all_bars.sort(key=lambda x: x['timestamp'])
    prices = all_bars

    data = {
        'ticker': ticker,
        'timeframe': '5Min',
        'downloaded_at': datetime.utcnow().isoformat() + 'Z',
        'start_date': prices[0]['timestamp'],
        'end_date': prices[-1]['timestamp'],
        'total_bars': len(prices),
        'bars': prices
    }

    # Calculate time span
    start_dt = datetime.fromisoformat(prices[0]['timestamp'].replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(prices[-1]['timestamp'].replace('Z', '+00:00'))
    days = (end_dt - start_dt).days
    years_actual = days / 365.25

    # Calculate approximate trading days (252 per year)
    # Each day has ~78 bars (6.5 hours * 12 bars/hour)
    expected_bars = int(years_actual * 252 * 78)
    coverage = len(prices) / expected_bars if expected_bars > 0 else 0

    print(f"  ✓ {ticker}: {len(prices):,} bars ({years_actual:.1f} years, ~{coverage:.0%} coverage)")
    print(f"    {prices[0]['timestamp'][:10]} to {prices[-1]['timestamp'][:10]}")

    return data


def estimate_file_size(num_bars: int) -> str:
    """Estimate JSON file size based on number of bars."""
    # Each bar ~150 bytes in JSON
    bytes_estimate = num_bars * 150

    if bytes_estimate < 1024:
        return f"{bytes_estimate} B"
    elif bytes_estimate < 1024 * 1024:
        return f"{bytes_estimate / 1024:.1f} KB"
    else:
        return f"{bytes_estimate / (1024 * 1024):.1f} MB"


def main():
    parser = argparse.ArgumentParser(description='Download 5-minute intraday historical data from Alpaca')
    parser.add_argument('--test', action='store_true', help='Test mode: download only TQQQ')
    parser.add_argument('--years', type=int, default=5, help='Number of years to download (default: 5)')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers (overrides default list)')
    args = parser.parse_args()

    # Create output directory
    output_dir = Path('data/intraday_5min')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine tickers to download
    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(',')]
    elif args.test:
        tickers = ['TQQQ']  # Just one for testing
        print(f"🧪 TEST MODE: Downloading only {tickers[0]}")
    else:
        # Priority tickers for stop loss backtesting
        tickers = [
            # Leveraged ETFs (critical for strategies)
            'TQQQ', 'UPRO', 'SSO', 'TMF',
            # Major indices
            'SPY', 'QQQ', 'IWM', 'DIA',
            # Bonds and defensive
            'TLT', 'GLD', 'IAU',
            # All sectors
            'XLE', 'XLF', 'XLU', 'XLV', 'XLI', 'XLK', 'XLY', 'XLP', 'XLB', 'XLRE', 'XLC',
            # Mega caps (for factor strategies)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
            # Other liquid stocks
            'AMD', 'INTC', 'NFLX', 'AVGO', 'MU'
        ]

    print(f"\n{'='*70}")
    print(f"ALPACA 5-MINUTE INTRADAY DATA DOWNLOAD")
    print(f"{'='*70}")
    print(f"Tickers: {len(tickers)}")
    print(f"Years per ticker: {args.years}")
    print(f"Estimated bars per ticker: ~{args.years * 252 * 78:,} (5-min bars)")
    print(f"Estimated size per ticker: ~{estimate_file_size(args.years * 252 * 78 * 150)}")
    print(f"Total estimated size: ~{estimate_file_size(len(tickers) * args.years * 252 * 78 * 150)}")
    print(f"{'='*70}\n")

    # Initialize Alpaca client
    try:
        client = get_alpaca_client()
        print("✓ Connected to Alpaca API\n")
    except ValueError as e:
        print(f"❌ {e}")
        return

    # Download each ticker
    results = {
        'downloaded_at': datetime.utcnow().isoformat() + 'Z',
        'total_tickers': len(tickers),
        'years_requested': args.years,
        'successful': 0,
        'failed': 0,
        'tickers': {}
    }

    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker}")

        data = download_ticker_5min(client, ticker, years=args.years)

        if data:
            # Save individual ticker file
            ticker_file = output_dir / f"{ticker}.json"
            with open(ticker_file, 'w') as f:
                json.dump(data, f, indent=2)

            results['tickers'][ticker] = {
                'success': True,
                'bars': data['total_bars'],
                'start_timestamp': data['start_date'],
                'end_timestamp': data['end_date'],
                'file_size': estimate_file_size(len(json.dumps(data)))
            }
            results['successful'] += 1
        else:
            results['tickers'][ticker] = {
                'success': False,
                'error': 'Failed to download'
            }
            results['failed'] += 1

        # Rate limit: wait between requests (be nice to Alpaca)
        if i < len(tickers):
            time.sleep(2)  # 2 seconds between tickers

        print()

    # Save summary
    summary_file = output_dir / 'download_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "="*70)
    print("📊 DOWNLOAD SUMMARY")
    print("="*70)
    print(f"Total tickers:  {results['total_tickers']}")
    print(f"✓ Successful:   {results['successful']}")
    print(f"❌ Failed:       {results['failed']}")

    if results['successful'] > 0:
        print(f"\n✓ Successfully downloaded data:")
        total_bars = 0
        for ticker, info in results['tickers'].items():
            if info['success']:
                total_bars += info['bars']
                print(f"  {ticker}: {info['bars']:,} bars ({info['start_timestamp'][:10]} to {info['end_timestamp'][:10]})")

        print(f"\nTotal bars: {total_bars:,}")
        print(f"Estimated total size: {estimate_file_size(total_bars * 150)}")

    if results['failed'] > 0:
        print(f"\n❌ Failed tickers:")
        for ticker, info in results['tickers'].items():
            if not info['success']:
                print(f"  - {ticker}")

    print(f"\n📁 Data saved to: {output_dir}/")
    print(f"📄 Summary saved to: {summary_file}")
    print("="*70)

    if args.test:
        print("\n💡 Test successful! Run without --test flag to download all tickers:")
        print(f"   python3 src/download_intraday_history.py --years {args.years}")
        print("\nOr download specific tickers:")
        print("   python3 src/download_intraday_history.py --tickers TQQQ,SPY,QQQ --years 5")


if __name__ == '__main__':
    main()
