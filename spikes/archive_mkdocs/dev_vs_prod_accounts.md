# Dev vs Prod Account Architecture

## Quick Reference

| Environment | # Accounts | When Used | Purpose |
|------------|-----------|-----------|---------|
| **Dev** | 1 | Local runs, Manual workflow | Testing, development, verification |
| **Prod** | 5 | Scheduled workflow only | Live forward-testing strategies |

## Environment Selection

### Automatic (in GitHub Actions)

```yaml
ALPACA_ENVIRONMENT: ${{ github.event_name == 'workflow_dispatch' && 'dev' || 'prod' }}
```

- **Scheduled** (10am & 3:30pm ET) → Uses **prod** accounts
- **Manual trigger** (click "Run workflow") → Uses **dev** account

### Manual (Local Execution)

```bash
# Dev environment (default for local)
python src/execute_multi_account.py --env dev

# Prod environment (test locally before deploying)
python src/execute_multi_account.py --env prod --dry-run

# All accounts
python src/execute_multi_account.py --env all
```

## Setup Checklist

### Local Development

1. ✅ Copy `.env.example` to `.env`
2. ✅ Fill in `ALPACA_DEV_API_KEY` and `ALPACA_DEV_SECRET_KEY`
3. ✅ Test: `python src/execute_multi_account.py --env dev --dry-run`

### Production Deployment

1. ✅ Create 5 Alpaca paper trading accounts
2. ✅ Add API keys to `.env` locally (`ALPACA_PROD_1_*` through `ALPACA_PROD_5_*`)
3. ✅ Add same keys to GitHub Secrets
4. ✅ Update `config/accounts.json` - set `"enabled": true` for active accounts
5. ✅ Test locally: `python src/execute_multi_account.py --env prod --dry-run`
6. ✅ Commit and push
7. ✅ Wait for scheduled run or manually trigger to verify

## Account Configuration

### Dev Account (config/accounts.json)

```json
{
  "id": "dev_account",
  "name": "Development/Testing Account",
  "env_prefix": "ALPACA_DEV",
  "environment": "dev",
  "enabled": true
}
```

### Prod Accounts (config/accounts.json)

```json
{
  "id": "prod_1_llm",
  "name": "LLM Recommendations",
  "env_prefix": "ALPACA_PROD_1",
  "environment": "prod",
  "enabled": true
}
```

## Environment Variables

### .env (Local)

```bash
# Dev
ALPACA_DEV_API_KEY="..."
ALPACA_DEV_SECRET_KEY="..."

# Prod (1-5)
ALPACA_PROD_1_API_KEY="..."
ALPACA_PROD_1_SECRET_KEY="..."
# ... etc
```

### GitHub Secrets

Same names as `.env`:
- `ALPACA_DEV_API_KEY`
- `ALPACA_DEV_SECRET_KEY`
- `ALPACA_PROD_1_API_KEY`
- `ALPACA_PROD_1_SECRET_KEY`
- ... (through PROD_5)

## Testing Workflow

### Step 1: Local Dev Testing

```bash
# 1. Dry run
python src/execute_multi_account.py --env dev --dry-run

# 2. Real execution (dev account only)
python src/execute_multi_account.py --env dev

# 3. Check logs
cat data/multi_account_logs/latest.json
```

### Step 2: Manual GitHub Test

1. Go to Actions → "AlphaOracle Daily Run"
2. Click "Run workflow" → "Run workflow"
3. This uses **dev environment only**
4. Check logs in Actions tab

### Step 3: Test Prod Locally

```bash
# Test prod accounts without executing
python src/execute_multi_account.py --env prod --dry-run

# Test specific prod account
python src/execute_multi_account.py --account prod_1_llm --dry-run
```

### Step 4: Deploy to Prod

1. Ensure all prod accounts enabled in `config/accounts.json`
2. Commit and push changes
3. Wait for scheduled run (10am or 3:30pm ET)
4. Monitor execution logs

## Execution Flow

```
┌─────────────────┐
│  Trigger Type   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
Scheduled  Manual
    │         │
    v         v
  PROD       DEV
    │         │
    v         v
5 accounts  1 account
```

## State Management

### Dev Account State

- **Location**: That Alpaca account
- **Expected**: Random/test trades
- **Cleanup**: Not needed - it's meant to be messy
- **Use for**: Testing new strategies, verifying workflow

### Prod Account State

- **Location**: 5 separate Alpaca accounts
- **Expected**: Clean, strategy-specific trades
- **Monitoring**: Check `data/multi_account_logs/`
- **Use for**: Live forward-testing validated strategies

## Common Commands

```bash
# Local dev testing
python src/execute_multi_account.py --env dev --dry-run
python src/execute_multi_account.py --env dev

# Local prod testing (dry run only!)
python src/execute_multi_account.py --env prod --dry-run

# Test specific account
python src/execute_multi_account.py --account prod_2_tqqq --dry-run

# Run all accounts (not recommended locally)
python src/execute_multi_account.py --env all --dry-run
```

## Monitoring

### Check Execution Logs

```bash
# Latest
cat data/multi_account_logs/latest.json

# Specific execution
cat data/multi_account_logs/20260317_182819.json
```

### Check GitHub Actions

1. Go to Actions tab
2. Select "AlphaOracle Daily Run"
3. View recent runs
4. Check environment used in logs

### Check Account Balance

```bash
# Set env vars for specific account
export ALPACA_API_KEY="your_key"
export ALPACA_SECRET_KEY="your_secret"

# Fetch portfolio
python src/fetch_alpaca_portfolio.py
cat data/portfolio_status.json
```

## Troubleshooting

### "Filtered to dev environment: 0 accounts"

Check `config/accounts.json` - ensure dev account has `"environment": "dev"`.

### "Missing API keys"

For local: Check `.env` has correct keys
For GitHub: Check Secrets are set correctly

### Manual trigger uses prod accounts

Check workflow file - should have:
```yaml
ALPACA_ENVIRONMENT: ${{ github.event_name == 'workflow_dispatch' && 'dev' || 'prod' }}
```

### Scheduled run uses dev account

Same check as above - verify the environment logic.

## Security Notes

1. ✅ Never commit `.env` to git
2. ✅ Keep GitHub Secrets updated
3. ✅ Use paper trading accounts only
4. ✅ Separate dev/prod keys clearly
5. ✅ Rotate keys periodically

## Benefits of This Architecture

1. **Safe Testing**: Dev account for all testing - prod stays clean
2. **Clear Separation**: Easy to see which environment is running
3. **Flexible**: Can test prod accounts locally with dry-run
4. **Scalable**: Add more prod accounts easily
5. **Stateful**: Each account maintains independent state
6. **Auditable**: Logs clearly show environment used
