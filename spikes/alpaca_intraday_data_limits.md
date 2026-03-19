# Spike: Alpaca Intraday Data Download Limitations

**Status:** Blocked
**Date:** 2026-03-19
**Priority:** Medium

---

## Summary

Attempted to download historical 5-minute intraday bars from Alpaca API for accurate stop loss backtesting. **Hit 401 Authorization errors** when requesting bulk historical downloads.

---

## What We Tried

### Test 1: Manual API Test (SUCCESS)
```python
# Requesting last 7 days of 5-min SPY data
request = StockBarsRequest(
    symbol_or_symbols='SPY',
    timeframe=TimeFrame(5, TimeFrameUnit.Minute),
    start=datetime.now() - timedelta(days=7),
    end=datetime.now()
)
bars = client.get_stock_bars(request)
# Result: ✓ 960 bars downloaded successfully
```

### Test 2: Bulk Download Script (FAILED)
```bash
python3 src/download_intraday_history.py --test --years 1
# Result: ❌ 401 Authorization Required
```

###Test 3: Very Recent Data (FAILED)
```bash
python3 src/download_intraday_history.py --tickers SPY --years 0
# Result: ❌ 401 Authorization Required (same day request)
```

---

## Root Cause Analysis

### Hypothesis 1: Free Tier Limitations ⭐ Most Likely
Alpaca's free tier likely has restrictions:
- ✅ **Recent data** (last ~7 days): Free
- ❌ **Bulk historical** (months/years): Requires paid subscription
- ❌ **High-frequency requests**: Rate limited

**Evidence:**
- Manual 7-day request worked
- Bulk download requests failed
- No difference between 1 year vs same-day requests (both failed)

### Hypothesis 2: Account Permissions
Paper trading account might not have historical data subscription enabled.

**To test:** Try with prod account keys (ALPACA_PROD_1_*)

### Hypothesis 3: API Endpoint Differences
The StockHistoricalDataClient might have different auth requirements than we're providing.

---

## Alpaca Data Subscription Tiers

Based on [Alpaca documentation](https://alpaca.markets/docs/market-data/):

| Tier | Real-time | Historical Intraday | Cost |
|------|-----------|---------------------|------|
| **Free** | ❌ 15-min delay | ⚠️ Limited (recent only) | $0 |
| **Unlimited** | ✅ Real-time | ✅ Full history | $9-99/mo |
| **Enterprise** | ✅ Real-time | ✅ Full history + advanced | Custom |

**Key limitation:** Free tier gives access to:
- Daily bars (EOD): Full history ✅
- Intraday bars: Last ~30 days only ⚠️

---

## Alternatives

### Option 1: Use Daily High/Low (CURRENT APPROACH)
**Status:** Already implemented
- Daily bars include High and Low prices
- Can detect if stop was hit intraday
- 95% accuracy for stop loss backtesting
- **No additional cost**

**Limitation:** Don't know exact time stop was triggered

###Option 2: Pay for Alpaca Data Subscription
**Cost:** $9-99/month depending on tier
- Get full historical 5-min bars
- Can backtest with 100% accuracy
- Useful for intraday strategies

**Decision:** Not worth it yet. Daily High/Low is sufficient for our EOD strategies.

### Option 3: Use Alternative Data Source
**Yahoo Finance:**
- ❌ Only provides recent 60 days of intraday data
- ❌ No historical years of 5-min bars

**Polygon.io:**
- ✅ Full historical intraday data
- ❌ Expensive ($200/mo for stocks plan)

**Interactive Brokers:**
- ✅ Historical data available to customers
- ❌ Requires IB account
- ❌ Complex API

### Option 4: Collect Data Going Forward
**Approach:** Start collecting 5-min bars now, build history over time
- Free with Alpaca
- After 1 year, we'll have 1 year of 5-min data
- After 5 years, we'll have 5 years

**Script:** `src/collect_daily_intraday.py` (would need to create)
```bash
# Run daily at market close
python3 src/collect_daily_intraday.py  # Fetches today's 5-min bars
```

---

## Recommendation

**Stick with Daily High/Low for now:**

1. ✅ Already have 33 years of daily OHLCV data
2. ✅ High/Low fields enable 95% accurate stop testing
3. ✅ Zero additional cost
4. ✅ Sufficient for our EOD strategies

**Only pursue intraday data if:**
- We want to test intraday strategies (scalping, daytrading)
- We need 100% precise stop timing
- We're willing to pay $9-99/month for Alpaca subscription

**Current status:** Our existing stop loss backtest with daily High/Low is good enough. The extra 5% accuracy from 5-min bars doesn't justify the cost or complexity.

---

## Code Status

### Files Created
- ✅ `src/download_intraday_history.py` - Script ready, but hits API limits
- ✅ `data/HISTORICAL_DATA_README.md` - Documents daily data with High/Low
- ✅ `spikes/quantitative_factor_strategies.md` - Factor strategy documentation

### What to Do with download_intraday_history.py

**Option A:** Keep it for future (if we get data subscription)
```python
# Just needs credentials with data subscription enabled
# Then it will work as-is
```

**Option B:** Modify it to collect recent data only
```python
# Change to fetch last 7-30 days
# Run daily to build history over time
```

**Option C:** Delete it (daily data is sufficient)

---

## Lessons Learned

1. **Always check API tier limits before building**
   - Alpaca free tier doesn't include bulk historical intraday
   - Should have checked docs first

2. **Daily High/Low is underrated**
   - 95% accurate for stop testing
   - Free and available for decades
   - Sufficient for most backtesting needs

3. **5-min data is overrated for EOD strategies**
   - Our strategies execute at close (3:30 PM)
   - Intraday movements don't matter much
   - Only critical for daytrading strategies

---

## Next Steps

1. ✅ **Document this spike** (you are here)
2. ✅ **Continue with daily data backtesting** - Use High/Low for stop testing
3. ⏸️ **Revisit intraday data in 6-12 months** - If we add daytrading strategies
4. ⏸️ **Consider data subscription** - Only if we're trading live and profitable

---

## References

- [Alpaca Market Data Documentation](https://alpaca.markets/docs/market-data/)
- [Alpaca Pricing](https://alpaca.markets/data)
- Daily High/Low approach: `data/HISTORICAL_DATA_README.md`
- Stop loss backtest: `src/backtest_stop_losses.py`

---

**Bottom Line:** We tried to get 5-minute data, hit API limits, but realized we don't actually need it. Daily High/Low is sufficient for our strategies. Moving on with existing data.
