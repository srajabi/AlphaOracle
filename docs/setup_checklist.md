# Initial 3-Strategy Setup - Ready to Deploy

## ✅ Code is Ready!

All systems configured for your initial 3 strategies:

1. **Prod 1 - LLM Recommendations** (auto-scaled AI trades)
2. **Prod 2 - TQQQ Momentum** (Reddit 200 SMA, +26,860% backtest)
3. **Prod 3 - UPRO Momentum** (Reddit 200 SMA, +8,809% backtest)

Plus 2 reserved accounts for strategies you'll backtest later.

## 📋 What You Need to Do

### 1. API Keys (Already Done! ✅)
You've added all 6 account keys to `.env.example`:
- ✅ ALPACA_DEV (dev/testing)
- ✅ ALPACA_PROD_1 (LLM)
- ✅ ALPACA_PROD_2 (TQQQ)
- ✅ ALPACA_PROD_3 (UPRO)
- ✅ ALPACA_PROD_4 (reserved)
- ✅ ALPACA_PROD_5 (reserved)

### 2. Copy to GitHub Secrets
Go to Settings → Secrets → Actions, add:
```
ALPACA_DEV_API_KEY
ALPACA_DEV_SECRET_KEY
ALPACA_PROD_1_API_KEY
ALPACA_PROD_1_SECRET_KEY
ALPACA_PROD_2_API_KEY
ALPACA_PROD_2_SECRET_KEY
ALPACA_PROD_3_API_KEY
ALPACA_PROD_3_SECRET_KEY
ALPACA_PROD_4_API_KEY
ALPACA_PROD_4_SECRET_KEY
ALPACA_PROD_5_API_KEY
ALPACA_PROD_5_SECRET_KEY
```

### 3. Copy .env.example to .env (Local)
```bash
cp .env.example .env
# All keys are already in .env.example!
```

### 4. Download TQQQ and UPRO Data
```bash
python src/data_ingestion.py
```

This will fetch historical data for TQQQ and UPRO (just added to watchlist).

### 5. Test Locally
```bash
# Test dev environment
python src/execute_multi_account.py --env dev --dry-run

# Test prod environment (all 3 strategies)
python src/execute_multi_account.py --env prod --dry-run
```

### 6. Commit and Push
```bash
git add .
git commit -m "feat: multi-account system with 3 initial strategies"
git push
```

### 7. Wait for Scheduled Run
Next scheduled run: **10am or 3:30pm ET, Monday-Friday**

Or manually trigger:
- Go to Actions → "AlphaOracle Daily Run" → "Run workflow"
- This uses **dev environment only** for testing

## 📊 Initial Strategy Allocation

Each account starts with **$100k** (recommended):

| Account | Strategy | Ticker | Backtest CAGR | Max DD |
|---------|----------|--------|---------------|--------|
| Prod 1 | LLM Recs | Various | TBD | TBD |
| Prod 2 | Reddit 200 SMA | TQQQ | +40.1% | -58% |
| Prod 3 | Reddit 200 SMA | UPRO | +27.6% | -58% |
| Prod 4 | Reserved | - | - | - |
| Prod 5 | Reserved | - | - | - |

**Total Forward Test Capital: $300k** across 3 strategies

## 🎯 Next Steps (After Running)

1. **Monitor First Week**
   - Check `data/multi_account_logs/latest.json`
   - Verify trades make sense
   - Watch buying power usage

2. **Backtest 2 More Strategies**
   - Ideas: Mean reversion, sector rotation, volatility timing
   - Run backtests with `backtesting/` system
   - Validate over 33-year period

3. **Add Strategies 4 & 5**
   - Implement in `src/strategies/momentum.py`
   - Update `config/accounts.json` prod_4 and prod_5
   - Set `"enabled": true`

## 📖 Documentation

- **Quick Reference**: `docs/dev_vs_prod_accounts.md`
- **Adding Strategies**: `docs/adding_new_accounts.md`
- **Full System**: `docs/multi_account_system.md`

## 🚨 Important Notes

1. **Dev account will have random trades** - that's expected!
2. **Prod accounts run on schedule** - 10am & 3:30pm ET only
3. **Manual triggers use dev** - safe to test anytime
4. **All paper trading** - no real money at risk
5. **Each account independent** - failures don't cascade

## ✨ What Happens on Next Run

```
10:00 AM ET:
  ↓
Pull latest code
  ↓
Fetch market data
  ↓
Run LLM analysis → generates trades.json
  ↓
Execute Multi-Account (PROD environment)
  ↓
  ├─ Prod 1: Read trades.json, scale to $100k, execute
  ├─ Prod 2: Check QQQ vs 200 SMA, buy/sell TQQQ
  └─ Prod 3: Check SPY vs 200 SMA, buy/sell UPRO
  ↓
Log results to data/multi_account_logs/
  ↓
Update frontend
  ↓
Commit & push
```

You're all set! 🚀
