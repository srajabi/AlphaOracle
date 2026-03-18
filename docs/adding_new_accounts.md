# Adding New Alpaca Accounts

## Overview

The system supports **unlimited Alpaca accounts** with clear separation between development/testing and production environments:

- **Dev Environment**: 1 account for local testing and manual workflow runs
- **Prod Environment**: 5+ accounts for scheduled automated trading

## Account Separation

### Development Account
- **Purpose**: Testing, development, manual workflow runs
- **Expected behavior**: Random/test trades are normal
- **When used**:
  - Running locally: `python src/execute_multi_account.py`
  - Manual workflow trigger: Click "Run workflow" in GitHub Actions
  - Testing new strategies before prod

### Production Accounts
- **Purpose**: Live forward-testing of validated strategies
- **Expected behavior**: Clean, strategy-specific trades only
- **When used**:
  - Scheduled runs: 10am & 3:30pm ET, Monday-Friday
  - Automatic execution only (no manual intervention)

## Adding a New Production Account

### Step 1: Create Alpaca Account

1. Go to https://alpaca.markets
2. Create a new paper trading account
3. Note the API Key and Secret Key
4. Give it a descriptive name (e.g., "Momentum Strategy 6")

### Step 2: Add to .env (Local)

Edit your `.env` file:

```bash
# Add after existing ALPACA_PROD_5 entries
ALPACA_PROD_6_NAME="Your Strategy Name"
ALPACA_PROD_6_API_KEY="your_api_key_here"
ALPACA_PROD_6_SECRET_KEY="your_secret_key_here"
```

### Step 3: Add to GitHub Secrets

1. Go to your repository on GitHub
2. Settings → Secrets and variables → Actions
3. Add new secrets:
   - `ALPACA_PROD_6_API_KEY`
   - `ALPACA_PROD_6_SECRET_KEY`

### Step 4: Update config/accounts.json

Add a new account entry:

```json
{
  "id": "prod_6_your_strategy",
  "name": "Your Strategy Name",
  "description": "Brief description of what this strategy does",
  "strategy": "your_strategy_name",
  "env_prefix": "ALPACA_PROD_6",
  "environment": "prod",
  "paper_trading": true,
  "enabled": true,
  "config": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Step 5: Update GitHub Workflow

Edit `.github/workflows/daily_analysis.yml`:

```yaml
- name: Execute Multi-Account Trades
  env:
    # ... existing vars ...
    ALPACA_PROD_6_API_KEY: ${{ secrets.ALPACA_PROD_6_API_KEY }}
    ALPACA_PROD_6_SECRET_KEY: ${{ secrets.ALPACA_PROD_6_SECRET_KEY }}
```

### Step 6: Implement Strategy (if new)

If using a new strategy not in `src/strategies/momentum.py`:

1. Add strategy class to `src/strategies/momentum.py`:

```python
class YourNewStrategy(MomentumStrategyGenerator):
    def generate_signals(self, current_positions: List[Dict]) -> List[Dict]:
        # Your strategy logic here
        signals = []
        # ... generate buy/sell signals ...
        return signals
```

2. Register in `generate_strategy_signals()`:

```python
def generate_strategy_signals(strategy_name: str, config: Dict, current_positions: List[Dict]) -> List[Dict]:
    if strategy_name == 'your_strategy_name':
        generator = YourNewStrategy(config)
    # ... existing strategies ...
    return generator.generate_signals(current_positions)
```

### Step 7: Test Locally

Test with dev environment first:

```bash
# Dry run
python src/execute_multi_account.py --env dev --dry-run

# Real execution (dev account)
python src/execute_multi_account.py --env dev

# Test specific prod account (dry run)
python src/execute_multi_account.py --account prod_6_your_strategy --dry-run
```

### Step 8: Enable in Production

Once tested:

1. Ensure `"enabled": true` in `config/accounts.json`
2. Commit and push changes
3. Wait for next scheduled run (10am or 3:30pm ET)
4. Check logs: `data/multi_account_logs/latest.json`

## Configuration Reference

### Account Configuration Fields

```json
{
  "id": "unique_identifier",           // Required: Unique ID for this account
  "name": "Display Name",              // Required: Human-readable name
  "description": "What it does",       // Required: Brief description
  "strategy": "strategy_name",         // Required: Strategy identifier (or null)
  "env_prefix": "ALPACA_PROD_X",       // Required: Environment variable prefix
  "environment": "prod",               // Required: "dev" or "prod"
  "paper_trading": true,               // Required: Always true for paper accounts
  "enabled": true,                     // Required: Enable/disable this account
  "config": {                          // Optional: Strategy-specific config
    // Strategy parameters go here
  }
}
```

### Strategy Configuration Examples

**LLM Recommendations:**
```json
"config": {
  "auto_scale_to_buying_power": true,
  "max_buying_power_usage": 0.98,
  "trades_source": "data/trades.json"
}
```

**Reddit 200 SMA:**
```json
"config": {
  "ticker": "TQQQ",
  "sma_period": 200,
  "rebalance_frequency": "daily",
  "max_position_size": 1.0
}
```

**Dual Momentum:**
```json
"config": {
  "tickers": ["SPY", "QQQ", "GLD"],
  "lookback_period": 126,
  "rebalance_frequency": "monthly",
  "max_position_size": 1.0
}
```

## Testing Workflow

### Local Testing

Always test locally first:

```bash
# 1. Test with dry-run
python src/execute_multi_account.py --env dev --dry-run

# 2. Execute on dev account
python src/execute_multi_account.py --env dev

# 3. Test specific prod account (dry-run)
python src/execute_multi_account.py --account prod_6_your_strategy --dry-run
```

### Manual Workflow Test

Test the GitHub workflow without affecting prod:

1. Go to Actions tab on GitHub
2. Select "AlphaOracle Daily Run"
3. Click "Run workflow"
4. This will use **dev environment only**

### Production Deployment

Production accounts only run on schedule:
- **10:00 AM ET** - Pre-market analysis & trades
- **3:30 PM ET** - End-of-day analysis & trades
- **Monday-Friday only**

## Monitoring

### Check Execution Logs

```bash
# Latest execution
cat data/multi_account_logs/latest.json

# Specific date
cat data/multi_account_logs/20260317_180946.json
```

### Check Account Status

For specific account (update env vars first):

```bash
export ALPACA_API_KEY="your_key"
export ALPACA_SECRET_KEY="your_secret"
python src/fetch_alpaca_portfolio.py
cat data/portfolio_status.json
```

### View in Frontend

Visit: http://localhost:4321/AlphaOracle/paper-trading/

Shows all accounts with:
- Current positions
- Performance metrics
- Trade history
- P&L tracking

## Troubleshooting

### "Account not found in config"

Check `config/accounts.json` - ensure the account ID matches exactly.

### "Missing API keys"

Verify environment variables:
```bash
grep ALPACA_PROD_6 .env
```

For GitHub Actions, check Secrets are set correctly.

### "Strategy not implemented"

Add strategy to `src/strategies/momentum.py` and register in `generate_strategy_signals()`.

### Account shows but doesn't execute

Check:
1. `"enabled": true` in config
2. `"environment": "prod"` for scheduled runs
3. Strategy is not `null`
4. API keys are correct in GitHub Secrets

## Best Practices

1. **Always test locally first** with `--dry-run`
2. **Use dev environment** for testing new strategies
3. **Start with one account** - don't enable multiple new accounts at once
4. **Monitor for 1-2 weeks** before adding more
5. **Keep config in sync** between local `.env` and GitHub Secrets
6. **Document strategy logic** in the description field
7. **Set appropriate position limits** in strategy config

## Example: Adding a Mean Reversion Strategy

```json
{
  "id": "prod_6_mean_reversion",
  "name": "RSI Mean Reversion",
  "description": "Buy oversold, sell overbought based on RSI",
  "strategy": "rsi_mean_reversion",
  "env_prefix": "ALPACA_PROD_6",
  "environment": "prod",
  "paper_trading": true,
  "enabled": true,
  "config": {
    "ticker": "SPY",
    "rsi_period": 14,
    "oversold_threshold": 30,
    "overbought_threshold": 70,
    "max_position_size": 1.0
  }
}
```

Then implement in `src/strategies/momentum.py`:

```python
class RSIMeanReversionStrategy(MomentumStrategyGenerator):
    def generate_signals(self, current_positions: List[Dict]) -> List[Dict]:
        ticker = self.config.get('ticker', 'SPY')
        rsi_period = self.config.get('rsi_period', 14)
        oversold = self.config.get('oversold_threshold', 30)
        overbought = self.config.get('overbought_threshold', 70)

        # Load data and calculate RSI
        df = self.load_price_data(ticker, days=rsi_period + 50)
        if df is None:
            return []

        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_rsi = rsi.iloc[-1]
        has_position = any(p.get('symbol') == ticker for p in current_positions)

        signals = []
        if current_rsi < oversold and not has_position:
            signals.append({
                "ticker": ticker,
                "action": "buy",
                "notional_value": None,
                "rationale": f"RSI Mean Reversion: Oversold at {current_rsi:.1f}"
            })
        elif current_rsi > overbought and has_position:
            signals.append({
                "ticker": ticker,
                "action": "sell",
                "qty": "all",
                "rationale": f"RSI Mean Reversion: Overbought at {current_rsi:.1f}"
            })

        return signals
```

Register it:

```python
def generate_strategy_signals(strategy_name: str, config: Dict, current_positions: List[Dict]) -> List[Dict]:
    if strategy_name == 'rsi_mean_reversion':
        generator = RSIMeanReversionStrategy(config)
    # ... existing strategies ...
    return generator.generate_signals(current_positions)
```

## Scaling Beyond 5 Accounts

The system is designed to scale indefinitely:

1. Just keep adding `ALPACA_PROD_N_*` entries
2. No code changes needed (except adding env vars to workflow)
3. All accounts process in parallel
4. Each maintains independent state

**Theoretical limit**: GitHub Actions environment variable limits (~100 secrets recommended max)

**Practical limit**: Number of Alpaca accounts you can manage (they're free for paper trading!)
