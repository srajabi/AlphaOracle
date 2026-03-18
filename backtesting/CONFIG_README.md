# Config-Based Backtesting

## Overview

The backtesting system now supports YAML configuration files for defining backtest scenarios. This makes it easy to:
- Define reusable backtest configurations
- Share backtest setups with others
- Run standard scenarios without remembering complex CLI arguments
- Version control your backtest configurations

## Quick Start

### Using a Config File

```bash
# Run with a config file
python3 backtesting/run_backtests.py --config backtesting/configs/default.yaml

# List available configs
python3 backtesting/run_backtests.py --list-configs

# Override config settings with CLI args
python3 backtesting/run_backtests.py --config backtesting/configs/default.yaml --output-dir custom/output
```

### Traditional CLI Usage (Still Supported)

```bash
# CLI args work as before
python3 backtesting/run_backtests.py \
  --tickers SPY,QQQ,GLD \
  --strategies buy_and_hold,sma_trend_following \
  --periods 20,40,full \
  --output-dir backtesting/results
```

## Config File Format

Configuration files use YAML format and support the following structure:

### Basic Structure

```yaml
name: "My Backtest Configuration"
description: "Brief description of what this config tests"

# Required: List of tickers to test
tickers:
  - SPY
  - QQQ
  - GLD

# Single-asset strategies (optional)
strategies:
  - buy_and_hold
  - sma_trend_following
  - rsi_mean_reversion
  - breakout_20d

# Portfolio strategies (optional)
portfolio_strategies:
  - top2_relative_strength_rotation
  - dual_momentum_rotation
  - regime_defensive_rotation

# Time periods to test
periods:
  # Lookback windows in trading days
  lookback_days:
    - 10
    - 20
    - 30
    - 40

  # Include full sample period
  full_sample: true

  # Named market regimes (see backtesting/periods.py)
  market_regimes:
    - dotcom_bear
    - gfc_bear
    - covid_crash
    - inflation_bear_2022
    - ai_bull_2023_2024

# Rolling window analysis (optional)
rolling_windows:
  enabled: false
  window: 20   # Window size in trading days
  step: 10     # Step size in trading days

# Transaction costs in basis points (1 bp = 0.01%)
transaction_cost_bps: 5.0

# Data source configuration
data_source:
  use_long_history: true  # Use 33-year data from data/historical_long/
  # use_long_history: false  # Use recent data from data/history/

# Output settings
output:
  directory: "backtesting/results"
  save_trades: false  # Set to true for detailed trade logs
```

## Available Config Files

### `default.yaml`
**Purpose:** Comprehensive testing across 33 years with all market regimes
**Use case:** Standard analysis for rotation strategies
**Tickers:** SPY, QQQ, GLD, TLT, XLE, XLU
**Time:** 33 years + all named regimes

```bash
python3 backtesting/run_backtests.py --config backtesting/configs/default.yaml
```

### `quick_test.yaml`
**Purpose:** Fast testing during development
**Use case:** Rapid iteration when modifying strategies
**Tickers:** SPY, GLD (minimal set)
**Time:** Recent data only, short periods

```bash
python3 backtesting/run_backtests.py --config backtesting/configs/quick_test.yaml
```

### `regime_deep_dive.yaml`
**Purpose:** Deep analysis across all market regimes
**Use case:** Understanding how strategies perform in different market conditions
**Tickers:** Full rotation universe
**Time:** Each named market regime separately

```bash
python3 backtesting/run_backtests.py --config backtesting/configs/regime_deep_dive.yaml
```

### `rolling_validation.yaml`
**Purpose:** Rolling window analysis to avoid overfitting
**Use case:** Validating strategy robustness
**Tickers:** Full rotation universe
**Time:** 20-day rolling windows across entire history

```bash
python3 backtesting/run_backtests.py --config backtesting/configs/rolling_validation.yaml
```

## Available Strategies

### Single-Asset Strategies
These run on individual tickers:
- `buy_and_hold` - Simple buy and hold baseline
- `sma_trend_following` - 20/50 SMA crossover system
- `rsi_mean_reversion` - Buy RSI < 35, sell RSI > 65
- `breakout_20d` - 20-day high breakout / 10-day low exit

### Portfolio Strategies
These run across the entire ticker universe:
- `top2_relative_strength_rotation` - Hold top 2 performers by 20-day momentum
- `dual_momentum_rotation` - Offensive/defensive rotation based on momentum
- `regime_defensive_rotation` - SPY/QQQ/XLE when risk-on, GLD/TLT/XLU when risk-off

## Available Market Regimes

From `backtesting/periods.py`:

- `dotcom_bear` (2000-2002) - Tech bubble crash
- `post_dotcom_bull` (2002-2007) - Recovery to GFC
- `gfc_bear` (2007-2009) - Global Financial Crisis
- `post_gfc_bull` (2009-2019) - Long bull market
- `covid_crash` (Feb-Mar 2020) - Pandemic crash
- `covid_rebound` (Mar-Dec 2020) - V-shaped recovery
- `inflation_bear_2022` (2022) - Inflation bear market
- `ai_bull_2023_2024` (2023-2024) - AI-driven rally
- `chop_2015_2016` (2015-2016) - Sideways/choppy period
- `chop_2018` (2018) - Late 2018 volatility

## Creating Custom Configs

1. Copy an existing config as a starting point:
   ```bash
   cp backtesting/configs/default.yaml backtesting/configs/my_test.yaml
   ```

2. Edit the config to match your needs:
   - Change tickers to test different universes
   - Select specific strategies
   - Choose relevant time periods
   - Adjust transaction costs

3. Run your custom config:
   ```bash
   python3 backtesting/run_backtests.py --config backtesting/configs/my_test.yaml
   ```

## Output Files

All configs generate the same output structure:

```
backtesting/results/
├── results_by_ticker.csv    # Detailed results per ticker/strategy/period
├── summary.csv               # Aggregate performance by strategy
├── summary_by_period.csv     # Performance broken down by period
└── summary.json              # JSON format with all results
```

## CLI Overrides

You can override any config setting with CLI arguments:

```bash
# Use config but change output directory
python3 backtesting/run_backtests.py \
  --config backtesting/configs/default.yaml \
  --output-dir backtesting/results/custom

# Use config but add more tickers
python3 backtesting/run_backtests.py \
  --config backtesting/configs/quick_test.yaml \
  --tickers SPY,QQQ,GLD,TLT

# Use config but change transaction costs
python3 backtesting/run_backtests.py \
  --config backtesting/configs/default.yaml \
  --transaction-cost-bps 10.0
```

CLI arguments always take precedence over config file settings.

## Best Practices

### 1. Use Configs for Standard Scenarios
Create configs for common use cases:
- `default.yaml` - Your standard comprehensive test
- `quick_test.yaml` - Fast iteration during development
- `regime_analysis.yaml` - Regime-specific analysis
- `new_strategy_validation.yaml` - Template for testing new strategies

### 2. Version Control Your Configs
Commit your config files to git so you can:
- Track changes to backtest setups over time
- Share configurations with collaborators
- Reproduce historical backtest results

### 3. Name Configs Descriptively
Use clear names that indicate what the config tests:
- `spy_only_33_years.yaml` - SPY-only long-term test
- `semiconductor_universe.yaml` - Semiconductor stock rotation
- `defensive_strategies.yaml` - Only defensive strategies

### 4. Document Your Configs
Include `name` and `description` fields:
```yaml
name: "Semiconductor Rotation Strategy Backtest"
description: "Tests rotation strategies on NVDA, AMD, TSM, AVGO, MU using 10-year history"
```

### 5. Start with Quick Tests
When developing new strategies:
1. Use `quick_test.yaml` for rapid iteration
2. Graduate to `default.yaml` for comprehensive testing
3. Run `regime_deep_dive.yaml` for final validation

## Advanced Usage

### Multiple Configs in Sequence

Run several configs back-to-back:
```bash
for config in backtesting/configs/*.yaml; do
  echo "Running $config..."
  python3 backtesting/run_backtests.py --config "$config"
done
```

### Programmatic Config Generation

Create configs programmatically in Python:
```python
import yaml

config = {
    "name": "Custom Test",
    "tickers": ["SPY", "QQQ"],
    "strategies": ["buy_and_hold"],
    "periods": {"lookback_days": [20], "full_sample": True},
    "transaction_cost_bps": 5.0,
    "output": {"directory": "backtesting/results/custom"}
}

with open("backtesting/configs/generated.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False)
```

### Config Inheritance (Manual)

While YAML doesn't support inheritance natively, you can:
1. Create a `base.yaml` with common settings
2. Copy and modify for specific scenarios
3. Use CLI overrides for one-off changes

## Troubleshooting

### "Config file not found"
Ensure path is correct relative to where you run the command:
```bash
python3 backtesting/run_backtests.py --config backtesting/configs/default.yaml
```

### "Unknown strategies requested"
Check that strategy names match exactly:
- Available single-asset: `buy_and_hold`, `sma_trend_following`, `rsi_mean_reversion`, `breakout_20d`
- Available portfolio: `top2_relative_strength_rotation`, `dual_momentum_rotation`, `regime_defensive_rotation`

### "Missing history file"
Ensure you have downloaded historical data:
```bash
# For long history
python3 src/download_long_history.py

# For recent history
python3 src/data_ingestion.py
```

### Empty Results
If no results are generated:
1. Check that tickers have sufficient history for the period
2. Verify strategy warmup periods (e.g., 200 SMA needs 200 days)
3. Try a longer period or `full_sample: true`

## Migration from CLI Args

If you have existing CLI commands, convert them to configs:

**Before (CLI):**
```bash
python3 backtesting/run_backtests.py \
  --tickers SPY,QQQ,GLD \
  --strategies buy_and_hold,sma_trend_following \
  --periods 20,40,full \
  --market-periods covid_crash,covid_rebound \
  --transaction-cost-bps 5.0
```

**After (Config):**
```yaml
# backtesting/configs/my_test.yaml
name: "My Test"
tickers: [SPY, QQQ, GLD]
strategies: [buy_and_hold, sma_trend_following]
periods:
  lookback_days: [20, 40]
  full_sample: true
  market_regimes: [covid_crash, covid_rebound]
transaction_cost_bps: 5.0
output:
  directory: "backtesting/results"
```

```bash
python3 backtesting/run_backtests.py --config backtesting/configs/my_test.yaml
```

## Next Steps

1. Explore the example configs in `backtesting/configs/`
2. Run `--list-configs` to see available options
3. Copy a config and customize for your needs
4. Add your custom configs to version control
5. Share configs with team members for consistent testing
