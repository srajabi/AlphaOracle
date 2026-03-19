# Historical Data Repository

## Overview

This directory contains **33+ years of daily OHLCV data** (Open, High, Low, Close, Volume) for 60+ tickers covering stocks, ETFs, leveraged products, sectors, bonds, commodities, and market indicators.

**Last Updated:** 2026-03-18
**Total Tickers:** 60 successful, 1 failed
**Date Range:** 1973-2026 (up to 53 years depending on ticker)

---

## Key Features

✅ **High/Low data included** - Enables accurate intraday stop loss backtesting
✅ **33 years of index data** - SPY back to 1993, perfect for long-term strategy validation
✅ **Leveraged ETFs** - TQQQ (16yr), UPRO (16yr), TMF (16yr) for risk-adjusted testing
✅ **Complete sector coverage** - All 11 S&P sectors (XLE, XLF, XLU, XLV, XLI, XLK, XLY, XLP, XLB, XLRE, XLC)
✅ **Market indicators** - VIX (36yr), UUP, SLV for regime detection
✅ **JSON format** - Easy to parse, includes metadata

---

## Data Structure

Each ticker file (`{TICKER}.json`) contains:

```json
{
  "ticker": "SPY",
  "downloaded_at": "2026-03-18T...",
  "start_date": "1993-01-29",
  "end_date": "2026-03-18",
  "total_days": 8340,
  "prices": [
    {
      "date": "1993-01-29",
      "open": 24.26,
      "high": 24.26,      // ← Intraday high for stop loss testing
      "low": 24.14,       // ← Intraday low for stop loss testing
      "close": 24.24,
      "volume": 1003200
    },
    ...
  ]
}
```

**Critical:** `high` and `low` fields enable accurate stop loss backtesting by checking if intraday price hit stop level.

---

## Available Tickers by Category

### 📊 Index ETFs (For Strategies)
| Ticker | Years | Start Date | Purpose |
|--------|-------|------------|---------|
| **SPY** | **33.1** | **1993-01-29** | **S&P 500 - Longest history** |
| **QQQ** | **27.0** | 1999-03-10 | Nasdaq 100 - Tech proxy |
| VOO | 15.5 | 2010-09-09 | S&P 500 alternative |
| VTI | 24.8 | 2001-06-15 | Total US market |
| IWM | 25.8 | 2000-05-26 | Russell 2000 small caps |
| DIA | 28.2 | 1998-01-20 | Dow Jones 30 |

### 🚀 Leveraged ETFs (For Aggressive Strategies)
| Ticker | Leverage | Years | Start Date | Notes |
|--------|----------|-------|------------|-------|
| **TQQQ** | **3x QQQ** | **16.1** | **2010-02-11** | **Critical for TQQQ Momentum strategy** |
| **UPRO** | **3x SPY** | **16.7** | **2009-06-25** | **Critical for Reddit 200 SMA strategy** |
| SSO | 2x SPY | 19.7 | 2006-06-21 | For leverage comparison backtests |
| TMF | 3x TLT | 16.7 | 2009-04-16 | Leveraged bonds for hedging |

### 🏭 Sector ETFs (For Rotation Strategies)
All sectors have **27+ years** of data (1998-2026):

| Ticker | Sector | Years | Start Date |
|--------|--------|-------|------------|
| XLE | Energy | 27.2 | 1998-12-22 |
| XLF | Financials | 27.2 | 1998-12-22 |
| XLU | Utilities (Defensive) | 27.2 | 1998-12-22 |
| XLV | Healthcare | 27.2 | 1998-12-22 |
| XLI | Industrials | 27.2 | 1998-12-22 |
| XLK | Technology | 27.2 | 1998-12-22 |
| XLY | Consumer Discretionary | 27.2 | 1998-12-22 |
| XLP | Consumer Staples | 27.2 | 1998-12-22 |
| XLB | Materials | 27.2 | 1998-12-22 |
| XLRE | Real Estate | 10.4 | 2015-10-08 |
| XLC | Communication Services | 5.3 | 2018-06-19 |

### 📈 Bonds & Defensive Assets
| Ticker | Type | Years | Start Date |
|--------|------|-------|------------|
| TLT | 20+ Year Treasury | 23.6 | 2002-07-30 |
| TMF | 3x Leveraged TLT | 16.7 | 2009-04-16 |
| GLD | Gold | 21.2 | 2004-11-18 |
| IAU | Gold (alternative) | 21.0 | 2005-01-28 |

### 🌍 International ETFs
| Ticker | Region | Years | Start Date |
|--------|--------|-------|------------|
| VXUS | Total International | 15.1 | 2011-01-28 |
| VGK | Europe | 21.0 | 2005-03-10 |
| EWC | Canada | 30.0 | 1996-03-18 |
| EWA | Australia | 30.0 | 1996-03-18 |

### 📊 Market Indicators
| Ticker | Type | Years | Start Date | Purpose |
|--------|------|-------|------------|---------|
| **^VIX** | **Volatility** | **36.2** | **1990-01-02** | **Risk sentiment / regime detection** |
| UUP | US Dollar | 19.0 | 2007-03-01 | Currency strength |
| SLV | Silver | 19.9 | 2006-04-28 | Commodity proxy |

### 💻 Individual Stocks (Mean Reversion / Picking)
Notable longest histories:
- **MTZ** (53 years): 1973-2026
- **WDC** (47 years): 1978-2026
- **AMD, INTC, KLAC** (46 years): 1980-2026
- **AAPL** (45 years): 1980-2026
- **MU, ORCL, MSFT** (40+ years): 1984-1986

See full list in `download_summary.json`

---

## Usage Examples

### 1. Load Data in Python

```python
import json
from pathlib import Path

def load_ticker_history(ticker: str):
    """Load historical data for a ticker."""
    path = Path(f"data/historical_long/{ticker}.json")
    with open(path) as f:
        return json.load(f)

# Example: Load SPY
spy_data = load_ticker_history("SPY")
print(f"{spy_data['ticker']}: {spy_data['total_days']} days")
print(f"Range: {spy_data['start_date']} to {spy_data['end_date']}")
```

### 2. Test Trailing Stop Loss (Using High/Low)

```python
def check_stop_hit(daily_bar, stop_price):
    """
    Check if intraday price hit trailing stop.

    Returns True if stop was triggered during the day.
    """
    return daily_bar['low'] <= stop_price

# Example backtest loop
for bar in spy_data['prices']:
    if position_open:
        stop_price = entry_price * (1 - stop_loss_pct)

        # Check if stop was hit intraday (not just at close)
        if check_stop_hit(bar, stop_price):
            # Stop triggered - exit at stop price
            exit_price = stop_price
            position_open = False
```

### 3. Access via Existing Backtest Framework

The `backtesting/` directory already uses this data:

```python
from backtesting.run_backtests import load_history

# Load with long history (uses data/historical_long/)
df = load_history("SPY", use_long_history=True)

# Load recent data only (uses data/history/)
df_recent = load_history("SPY", use_long_history=False)
```

---

## Backtest Recommendations

### Minimum Years Needed by Test Type

| Test Type | Min Years | Rationale |
|-----------|-----------|-----------|
| Quick validation | 5 years | Covers recent regime |
| Standard backtest | 15 years | Includes 2008 crisis, 2020 COVID |
| Robust validation | 25+ years | Includes dot-com crash, multiple cycles |
| Ultimate stress test | 33 years (SPY) | Maximum statistical significance |

### Strategy-Specific Recommendations

**TQQQ Momentum (200 SMA):**
- Available: 16 years (2010-2026)
- Recommendation: Use full 16 years
- Note: TQQQ didn't exist before 2010

**Dual Momentum (SPY/QQQ/GLD):**
- Available: 27 years (limited by QQQ start 1999)
- Recommendation: Use full 27 years to include dot-com crash

**Sector Rotation:**
- Available: 27 years (1998-2026)
- Recommendation: Use full 27 years

**Mean Reversion (Stocks):**
- Available: Varies (5-53 years)
- Recommendation: 15+ years for statistical significance

---

## Stop Loss Testing Capability

### Why High/Low Data Matters

**Problem with EOD-only data:**
- You only see closing prices
- Can't detect if stop was hit intraday
- Results show stops "not triggered" when they actually were

**With High/Low data:**
- Check if `daily_low <= stop_price` for long positions
- Check if `daily_high >= stop_price` for short positions
- Accurately simulate real stop-market order execution

### Example: Comparing Close-Only vs High/Low

```python
# ❌ WRONG: Using only close price
if close_price <= stop_price:
    # Might miss stops hit earlier in day

# ✅ CORRECT: Using daily low
if daily_low <= stop_price:
    # Catches intraday stop triggers
    exit_at_stop()
```

---

## Updating Data

Historical data is **static** - prices don't change after the fact. You only need to:

1. **Add new days:** Run daily data ingestion (`src/data_ingestion.py`)
2. **Add new tickers:** Add to `watchlist.csv` and run `src/download_long_history.py`

```bash
# Download missing tickers or refresh data
python3 src/download_long_history.py

# Test with 3 tickers first
python3 src/download_long_history.py --test
```

---

## Data Quality Notes

### ✅ Reliable Long-Term Data (1990s+)
- SPY, QQQ, sector ETFs, bonds
- Liquid, established markets
- No survivorship bias (ETFs don't delist often)

### ⚠️ Newer Products (< 15 years)
- Leveraged ETFs (TQQQ, UPRO, TMF): Started 2009-2010
- Some sectors (XLRE, XLC): More recent additions
- Bitcoin ETFs (IBIT): Only since 2024

### ❌ Known Limitations
- **HXSC.F** (SK Hynix): Delisted, no data available
- **Intraday gaps**: Data is daily close, not tick-by-tick
- **After-hours**: Only regular trading hours included
- **Splits/Dividends**: Auto-adjusted by Yahoo Finance (price-continuity maintained)

---

## File Size & Performance

| Metric | Value |
|--------|-------|
| Total files | 61 (60 tickers + 1 summary) |
| Total size | ~40 MB (JSON) |
| Average file | ~650 KB per ticker |
| Largest file | 1.6 MB (AAPL, MSFT - 40+ years) |
| Load time | <50ms per ticker |
| Full dataset load | <3 seconds |

**Performance tip:** Cache loaded data in memory if running multiple backtests.

---

## Next Steps for Backtesting

Now that you have comprehensive historical data:

1. ✅ **Stop loss optimization** - Rerun `src/backtest_stop_losses.py` with 33 years + High/Low checks
2. ✅ **Add to comprehensive framework** - Integrate stop testing into `backtesting/` engine
3. ✅ **Test all 4 strategies** - TQQQ Momentum, Dual Momentum, Sector Rotation, Mean Reversion
4. ✅ **Regime analysis** - Compare 1993-2010 (crashes) vs 2011-2026 (bull market)
5. ✅ **Walk-forward validation** - Train on first 20 years, test on last 13 years

---

## Quick Reference

```bash
# Data location
data/historical_long/{TICKER}.json

# Summary with all tickers and date ranges
data/historical_long/download_summary.json

# Download/update data
python3 src/download_long_history.py

# Load in backtests
from backtesting.run_backtests import load_history
df = load_history("SPY", use_long_history=True)
```

---

## Support

For questions or issues:
- Check `download_summary.json` for ticker availability
- Review `backtesting/CONFIG_README.md` for backtest framework usage
- See `src/backtest_stop_losses.py` for stop loss testing examples
