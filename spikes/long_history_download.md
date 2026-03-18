# Spike: Long Historical Data Download Strategy

**Objective:** Download 20+ years of historical price data for backtesting without ongoing rate limit issues.

## The Problem

Current data in `data/history/*.json` only covers ~4 months (late 2025 - March 2026). Need data going back to at least 2000 to validate strategies across:
- Dot-com crash (2000-2002)
- GFC (2007-2009)
- 2015-2016 chop
- 2018 correction
- COVID crash (2020)
- 2022 inflation bear
- 2023-2024 AI bull

## Key Insight: Historical Data is Static

**Once downloaded, it never changes.** We don't need an API for daily updates of 20-year-old price data.

## Recommended Approach: One-Time Download + Cache

### Strategy

1. **One-time download** of full available history for all watchlist tickers
2. **Store in separate directory**: `data/historical_long/` (dedicated to backtesting)
3. **Never update it** (historical data doesn't change)
4. **Keep current daily pipeline** separate in `data/history/` (for live analysis)

### Data Source: Yahoo Finance (yfinance)

**Why yfinance:**
- ✓ Free, no API key needed
- ✓ Reliable historical data going back 20+ years
- ✓ Already integrated in the project
- ✓ Simple API: `ticker.history(period="max")`
- ✓ Adjusted for splits and dividends
- ✓ Works for stocks and ETFs

**Why NOT AKShare:**
- ✗ US data from Sina Finance (Chinese source)
- ✗ Unclear historical depth
- ✗ No options data
- ✗ Documentation in Chinese
- ✗ Not designed for US markets

### Implementation

#### Script: `src/download_long_history.py`

```python
import yfinance as yf
import json
import csv
from pathlib import Path
from datetime import datetime
import time

def load_watchlist():
    """Load tickers from watchlist.csv"""
    tickers = []
    with open('watchlist.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickers.append(row['ticker'])
    return tickers

def download_ticker_history(ticker, retries=3):
    """Download full history for a ticker with retry logic"""
    for attempt in range(retries):
        try:
            print(f"Downloading {ticker}... (attempt {attempt + 1}/{retries})")

            yf_ticker = yf.Ticker(ticker)
            df = yf_ticker.history(period="max", auto_adjust=True)

            if df.empty:
                print(f"  WARNING: No data returned for {ticker}")
                return None

            # Convert to our JSON format
            prices = []
            for date, row in df.iterrows():
                prices.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
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

            print(f"  ✓ {ticker}: {len(prices)} days from {prices[0]['date']} to {prices[-1]['date']}")
            return data

        except Exception as e:
            print(f"  ERROR on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retry
            else:
                print(f"  FAILED: Could not download {ticker} after {retries} attempts")
                return None

def main():
    # Create output directory
    output_dir = Path('data/historical_long')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load watchlist
    tickers = load_watchlist()
    print(f"Found {len(tickers)} tickers to download\n")

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

        # Rate limit: wait between requests
        if i < len(tickers):
            time.sleep(2)  # 2 seconds between tickers

        print()

    # Save summary
    summary_file = output_dir / 'download_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Total tickers: {results['total_tickers']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")

    if results['failed'] > 0:
        print("\nFailed tickers:")
        for ticker, info in results['tickers'].items():
            if not info['success']:
                print(f"  - {ticker}")

    print(f"\nData saved to: {output_dir}")
    print("="*60)

if __name__ == '__main__':
    main()
```

### Usage

```bash
# One-time download of all historical data
python3 src/download_long_history.py

# This will take ~2-5 minutes (40 tickers × 2 seconds)
# Output: data/historical_long/*.json
```

### Expected Output Structure

```
data/
├── history/                    # Daily updated data (current pipeline)
│   ├── AAPL.json              # ~4 months of recent data
│   ├── SPY.json
│   └── ...
└── historical_long/           # Full history for backtesting (static)
    ├── AAPL.json              # 20+ years of data
    ├── SPY.json               # 20+ years of data
    ├── ...
    └── download_summary.json  # Metadata about the download
```

### Modify Backtesting to Use Long History

Update `backtesting/run_backtests.py`:

```python
def load_history(ticker, use_long_history=True):
    """Load price history for a ticker"""
    if use_long_history:
        # Use full historical data for backtesting
        history_file = Path(f'data/historical_long/{ticker}.json')
    else:
        # Use recent data only
        history_file = Path(f'data/history/{ticker}.json')

    if not history_file.exists():
        return None

    with open(history_file) as f:
        data = json.load(f)

    return pd.DataFrame(data['prices'])
```

## Data Quality Validation

After downloading, validate data quality:

```python
# Check for gaps, outliers, missing data
def validate_history(ticker):
    with open(f'data/historical_long/{ticker}.json') as f:
        data = json.load(f)

    df = pd.DataFrame(data['prices'])

    # Check for gaps
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['days_since_prev'] = df['date'].diff().dt.days

    gaps = df[df['days_since_prev'] > 5]  # More than 5 days (weekend + holiday)
    if not gaps.empty:
        print(f"{ticker}: Found {len(gaps)} gaps in data")

    # Check for zero prices (data errors)
    zeros = df[(df['close'] == 0) | (df['volume'] == 0)]
    if not zeros.empty:
        print(f"{ticker}: Found {len(zeros)} rows with zero prices/volume")

    # Check for extreme outliers (possible errors)
    df['pct_change'] = df['close'].pct_change()
    outliers = df[abs(df['pct_change']) > 0.5]  # 50% moves
    if not outliers.empty:
        print(f"{ticker}: Found {len(outliers)} extreme moves (>50%)")

    print(f"{ticker}: ✓ {len(df)} days from {df.iloc[0]['date'].date()} to {df.iloc[-1]['date'].date()}")
```

## Alternative: Alpha Vantage (If yfinance Fails)

If yfinance fails for some tickers, use Alpha Vantage as backup:

```python
import requests

def download_from_alphavantage(ticker, api_key):
    """Fallback to Alpha Vantage for long history"""
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': ticker,
        'outputsize': 'full',  # Full history (20+ years)
        'apikey': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Parse and convert to our format
    # ... (implementation)
```

## Recommended Execution Plan

1. **Run download once:**
   ```bash
   python3 src/download_long_history.py
   ```

2. **Validate data quality:**
   ```bash
   python3 src/validate_historical_data.py
   ```

3. **Update backtesting to use long history:**
   - Modify `backtesting/run_backtests.py`
   - Point to `data/historical_long/` instead of `data/history/`

4. **Run full regime backtests:**
   ```bash
   python3 backtesting/run_backtests.py --market-periods dotcom_bear,gfc_bear,inflation_bear_2022,ai_bull_2023_2024
   ```

5. **Never re-download:**
   - Historical data is static
   - Only re-download if adding new tickers to watchlist
   - Or if data quality issues found

## Cost Analysis

**yfinance approach:**
- Cost: $0 (free)
- Time: ~5 minutes one-time
- Maintenance: None (static data)

**Alpha Vantage approach:**
- Cost: $0 (free tier: 500 calls/day)
- Time: ~1 hour (rate limited to 5 calls/minute for 40 tickers)
- Maintenance: None

**AKShare approach:**
- Cost: $0
- Reliability: Unknown for US markets
- Depth: Unclear if 20+ years available
- Recommendation: NOT recommended

## Conclusion

**Best approach:** Use yfinance for one-time download of max history, cache in `data/historical_long/`, never update it.

This is:
- Free
- Simple
- Reliable
- Fast
- Maintenance-free

No need for complex APIs or rate limit management for static historical data.
