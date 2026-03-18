# Spike: Config-Based Backtesting System

**Date:** 2026-03-16
**Decision:** Implemented Option B (YAML configuration files) for making backtesting more generic

## Problem Statement

The original `run_backtests.py` script required remembering complex CLI arguments:
```bash
python3 backtesting/run_backtests.py \
  --tickers SPY,QQQ,GLD,TLT,XLE,XLU \
  --strategies buy_and_hold,sma_trend_following,rsi_mean_reversion,breakout_20d \
  --portfolio-strategies top2_relative_strength_rotation,dual_momentum_rotation,regime_defensive_rotation \
  --periods 10,20,30,40,full \
  --market-periods dotcom_bear,gfc_bear,covid_crash,inflation_bear_2022,ai_bull_2023_2024 \
  --rolling-window 20 \
  --rolling-step 10 \
  --transaction-cost-bps 5.0 \
  --output-dir backtesting/results
```

This became unwieldy and made it hard to:
- Reproduce backtest configurations
- Share setups with collaborators
- Version control test scenarios
- Run standard tests repeatedly

## Options Considered

We considered four approaches for making backtesting more generic:

### Option A: Unified Interface (Abstract Base Class)
Create `BaseStrategy` class with standard interface for all strategies.

**Pros:**
- Type safety
- IDE autocomplete
- Clear contract

**Cons:**
- Requires refactoring all existing strategies
- More complex to add new strategies
- Over-engineering for current needs

### Option B: Config-Based (YAML/JSON) ✅ SELECTED
Define backtest scenarios in YAML configuration files.

**Pros:**
- Easy to create and modify configs
- Version controllable
- No code changes needed for new scenarios
- Clear, human-readable format
- Supports commenting

**Cons:**
- Adds dependency (PyYAML)
- Need validation layer
- Less type safety than code

### Option C: Pluggable Components (Modular Architecture)
Create plugin system for strategies, data loaders, analyzers.

**Pros:**
- Maximum flexibility
- Can add components without modifying core
- Good for extensibility

**Cons:**
- Most complex to implement
- Overkill for current needs
- Requires plugin discovery mechanism

### Option D: Flexible Runner (Enhanced CLI)
Improve CLI with subcommands and better argument parsing.

**Pros:**
- No external config files needed
- Still use CLI only
- Good for one-off tests

**Cons:**
- CLI gets even more complex
- Hard to version control
- Difficult to share setups

## Why Option B Was Chosen

**Primary reasons:**

1. **Version Control**: YAML configs can be committed to git, making it easy to track changes to backtest setups over time.

2. **Reproducibility**: Named configs like `default.yaml`, `regime_deep_dive.yaml` ensure consistent testing across sessions.

3. **Sharability**: Team members can easily share backtest configurations by sending a config file.

4. **Clarity**: YAML is human-readable and self-documenting:
   ```yaml
   name: "33-Year Regime Analysis"
   tickers: [SPY, QQQ, GLD, TLT, XLE, XLU]
   strategies: [buy_and_hold, dual_momentum_rotation]
   ```

5. **Low Implementation Cost**: PyYAML is a standard library, and the implementation was straightforward.

6. **Backward Compatible**: CLI args still work exactly as before. Config is optional.

7. **CLI Overrides**: You can use a config as a base and override specific settings:
   ```bash
   python3 backtesting/run_backtests.py \
     --config backtesting/configs/default.yaml \
     --output-dir custom/results
   ```

## Implementation

### Components Created

1. **`backtesting/config_loader.py`**
   - `BacktestConfig` class - container for parsed config
   - `load_config()` - loads and validates YAML
   - `list_available_configs()` - discovers config files

2. **Updated `backtesting/run_backtests.py`**
   - Added `--config` argument
   - Added `--list-configs` flag
   - Config settings merged with CLI args (CLI takes precedence)
   - Added caching to `load_history()` to avoid reloading same ticker

3. **Example Configs** (`backtesting/configs/`)
   - `default.yaml` - Standard 33-year test
   - `quick_test.yaml` - Fast development testing
   - `regime_deep_dive.yaml` - All market regimes
   - `rolling_validation.yaml` - Rolling window analysis

4. **Documentation**
   - `backtesting/CONFIG_README.md` - Comprehensive guide
   - Examples of each config
   - Migration guide from CLI to configs
   - Troubleshooting section

### Config File Format

```yaml
name: "My Backtest"
description: "What this config tests"

tickers:
  - SPY
  - QQQ

strategies:
  - buy_and_hold

portfolio_strategies:
  - dual_momentum_rotation

periods:
  lookback_days: [10, 20, 40]
  full_sample: true
  market_regimes: [covid_crash, inflation_bear_2022]

rolling_windows:
  enabled: false
  window: 20
  step: 10

transaction_cost_bps: 5.0

data_source:
  use_long_history: true

output:
  directory: "backtesting/results"
  save_trades: false
```

## Usage Examples

### List Available Configs
```bash
python3 backtesting/run_backtests.py --list-configs
```

### Run a Config
```bash
python3 backtesting/run_backtests.py --config backtesting/configs/default.yaml
```

### Override Config Settings
```bash
# Use default.yaml but change output directory
python3 backtesting/run_backtests.py \
  --config backtesting/configs/default.yaml \
  --output-dir backtesting/results/custom
```

### Traditional CLI (Still Works)
```bash
python3 backtesting/run_backtests.py \
  --tickers SPY,GLD \
  --strategies buy_and_hold \
  --periods 20,full
```

## Benefits Realized

### Before (CLI Only)
- Had to remember 10+ CLI arguments
- Couldn't version control backtest setups
- Hard to share configurations
- Difficult to reproduce exact tests
- No way to name/describe test scenarios

### After (Config-Based)
- `python3 backtesting/run_backtests.py --config backtesting/configs/regime_deep_dive.yaml`
- Configs committed to git
- Easy to share: "Use `regime_deep_dive.yaml`"
- Reproducible: same config = same test
- Self-documenting: config has `name` and `description`

## Standard Configs Created

### 1. `default.yaml`
**Purpose:** Comprehensive 33-year test across all regimes
**When to use:** Standard validation for rotation strategies
**Runs:** ~3-5 minutes

### 2. `quick_test.yaml`
**Purpose:** Fast iteration during development
**When to use:** Testing code changes, debugging
**Runs:** ~10 seconds

### 3. `regime_deep_dive.yaml`
**Purpose:** Deep analysis of each market regime separately
**When to use:** Understanding regime-specific performance
**Runs:** ~2-3 minutes

### 4. `rolling_validation.yaml`
**Purpose:** Rolling window analysis to avoid overfitting
**When to use:** Validating strategy robustness
**Runs:** ~5-10 minutes (many windows)

## Future Enhancements

### Potential Additions

1. **Config Inheritance**
   - `extends: base.yaml`
   - Override only specific settings
   - Reduce duplication

2. **Parameterized Configs**
   - Variables in configs: `${TICKER_UNIVERSE}`
   - Template system for generating multiple configs

3. **Config Validation Schema**
   - JSON Schema or Pydantic models
   - Better error messages
   - IDE autocomplete for configs

4. **Web UI for Config Creation**
   - Visual config builder
   - Form-based interface
   - Generates YAML automatically

5. **Config Comparison Tool**
   - `python3 backtesting/compare_configs.py config1.yaml config2.yaml`
   - Show differences
   - Merge conflicts

## Best Practices

### 1. Name Configs Descriptively
Good: `spy_33_years_all_regimes.yaml`
Bad: `test1.yaml`

### 2. Include Documentation
Always fill in `name` and `description` fields.

### 3. Version Control
Commit configs to git alongside code changes.

### 4. Start Small
Use `quick_test.yaml` for development, graduate to `default.yaml` for validation.

### 5. Create Templates
Copy existing configs as starting points:
```bash
cp backtesting/configs/default.yaml backtesting/configs/my_test.yaml
```

## Validation Results

Tested with:
- ✅ All 4 example configs run successfully
- ✅ `--list-configs` lists all configs
- ✅ CLI overrides work correctly
- ✅ Traditional CLI usage still functional
- ✅ PyYAML dependency added to requirements.txt

## Conclusion

Option B (config-based) was the right choice for making backtesting more generic because it:
- Balances simplicity with power
- Enables version control and sharing
- Maintains backward compatibility
- Provides clear, human-readable format
- Low implementation and maintenance cost

This approach aligns with the project's goals of:
- Systematic, reproducible testing
- Documentation-driven development
- Easy onboarding for new collaborators
- Long-term maintainability

The config system is now ready for use in daily backtesting workflows and future paper trading validation.
