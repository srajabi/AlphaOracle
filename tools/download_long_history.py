#!/usr/bin/env python3
"""
Download long historical data for backtesting.

This script downloads the maximum available history for all watchlist tickers
and saves it to data/historical_long/. This is a one-time download since
historical data is static and doesn't need updating.

Usage:
    python3 src/download_long_history.py
    python3 src/download_long_history.py --test  # Test with 3 tickers only
"""

import yfinance as yf
import json
import csv
from pathlib import Path
from datetime import datetime
import time
import argparse


def load_watchlist():
    """Load tickers from watchlist.csv"""
    tickers = []
    watchlist_file = Path('watchlist.csv')

    if not watchlist_file.exists():
        print(f"ERROR: watchlist.csv not found")
        return []

    with open(watchlist_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row['Ticker'].strip()
            if ticker:
                tickers.append(ticker)

    return tickers


def download_ticker_history(ticker, retries=3):
    """
    Download full history for a ticker with retry logic.

    Args:
        ticker: Stock ticker symbol
        retries: Number of retry attempts

    Returns:
        dict with ticker data or None if failed
    """
    for attempt in range(retries):
        try:
            print(f"  Downloading {ticker}... (attempt {attempt + 1}/{retries})")

            yf_ticker = yf.Ticker(ticker)
            df = yf_ticker.history(period="max", auto_adjust=True)

            if df.empty:
                print(f"  ⚠️  WARNING: No data returned for {ticker}")
                return None

            # Convert to our JSON format
            prices = []
            for date, row in df.iterrows():
                prices.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'volume': int(row['Volume'])
                })

            data = {
                'ticker': ticker,
                'downloaded_at': datetime.utcnow().isoformat() + 'Z',
                'start_date': prices[0]['date'],
                'end_date': prices[-1]['date'],
                'total_days': len(prices),
                'prices': prices
            }

            # Calculate time span
            start = datetime.strptime(prices[0]['date'], '%Y-%m-%d')
            end = datetime.strptime(prices[-1]['date'], '%Y-%m-%d')
            years = (end - start).days / 365.25

            print(f"  ✓ {ticker}: {len(prices)} days ({years:.1f} years) from {prices[0]['date']} to {prices[-1]['date']}")
            return data

        except Exception as e:
            print(f"  ❌ ERROR on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print(f"  Waiting 5 seconds before retry...")
                time.sleep(5)
            else:
                print(f"  ❌ FAILED: Could not download {ticker} after {retries} attempts")
                return None


def main():
    parser = argparse.ArgumentParser(description='Download long historical data for backtesting')
    parser.add_argument('--test', action='store_true', help='Test mode: download only 3 tickers')
    args = parser.parse_args()

    # Create output directory
    output_dir = Path('data/historical_long')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load watchlist
    all_tickers = load_watchlist()

    if not all_tickers:
        print("ERROR: No tickers found in watchlist.csv")
        return

    # Use subset for testing
    if args.test:
        tickers = all_tickers[:3]
        print(f"🧪 TEST MODE: Downloading only {len(tickers)} tickers: {', '.join(tickers)}\n")
    else:
        tickers = all_tickers
        print(f"📥 FULL MODE: Found {len(tickers)} tickers to download\n")

    # Download each ticker
    results = {
        'downloaded_at': datetime.utcnow().isoformat() + 'Z',
        'total_tickers': len(tickers),
        'successful': 0,
        'failed': 0,
        'tickers': {}
    }

    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker}")

        data = download_ticker_history(ticker)

        if data:
            # Save individual ticker file
            ticker_file = output_dir / f"{ticker}.json"
            with open(ticker_file, 'w') as f:
                json.dump(data, f, indent=2)

            results['tickers'][ticker] = {
                'success': True,
                'days': data['total_days'],
                'start_date': data['start_date'],
                'end_date': data['end_date']
            }
            results['successful'] += 1
        else:
            results['tickers'][ticker] = {
                'success': False,
                'error': 'Failed to download'
            }
            results['failed'] += 1

        # Rate limit: wait between requests (be nice to Yahoo)
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
        for ticker, info in results['tickers'].items():
            if info['success']:
                print(f"  {ticker}: {info['days']} days ({info['start_date']} to {info['end_date']})")

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
        print("   python3 src/download_long_history.py")


if __name__ == '__main__':
    main()
