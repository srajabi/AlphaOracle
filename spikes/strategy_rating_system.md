# Spike: Strategy Rating System Design

**Objective:** Design and implement a rule-based strategy rating system that provides buy/sell/hold signals for each ticker based on validated technical strategies.

## Purpose

This is **Mode 2** of the three-mode AlphaOracle system:
1. LLM Analysis (general recommendations) - ✓ implemented
2. **Strategy Ratings (rule-based signals)** - this spike
3. Paper Trading (forward validation) - next

## Key Principles

### Rule-Based, Not LLM-Based
- Each strategy applies mechanical rules to technical indicators
- No interpretation, no judgment calls
- Reproducible and backtestable
- Transparent to users

### Multiple Strategy Perspectives
Each ticker gets rated by multiple strategies simultaneously:
- Trend following strategies (SMA 200, dual momentum)
- Mean reversion strategies (RSI oversold/overbought)
- Breakout strategies (20-day highs, volatility squeeze)
- Momentum strategies (relative strength rotation)
- Special strategies (3x leveraged ETF timing, sector rotation)

### Three-State Output
Each strategy outputs one of three states per ticker:
- **BUY**: Strategy is long this ticker right now
- **SELL** (or SHORT): Strategy is not holding / would be short
- **HOLD**: Neutral / no position / waiting for setup

Note: For long-only strategies, SELL means "not holding" rather than actual shorting.

## Data Flow

```
Market Data → Strategy Engine → Ratings JSON → Frontend Display
                    ↓
              Backtesting Validation
                    ↓
              Paper Trading Tracker
```

### Daily Workflow Integration
Add after `src/data_ingestion.py` and before `src/llm_agents.py`:

```bash
# New step: Generate strategy ratings
python3 src/generate_strategy_ratings.py
```

This reads `data/market_context.json` and outputs `data/strategy_ratings.json`.

## Output Schema

### File: `data/strategy_ratings.json`

```json
{
  "generated_at": "2026-03-16T16:30:00Z",
  "strategies": {
    "sma_200_trend": {
      "name": "200 SMA Trend Following",
      "description": "Long when price > 200 SMA, otherwise out",
      "type": "trend_following",
      "universe": "all"
    },
    "dual_momentum": {
      "name": "Dual Momentum Rotation",
      "description": "Rotates to best offensive asset if positive, else best defensive",
      "type": "momentum_rotation",
      "universe": "portfolio"
    },
    "rsi_mean_reversion": {
      "name": "RSI Mean Reversion",
      "description": "Buy when RSI < 35, sell when RSI > 65",
      "type": "mean_reversion",
      "universe": "all"
    },
    "breakout_20d": {
      "name": "20-Day Breakout",
      "description": "Buy on 20-day high, sell on 10-day low",
      "type": "breakout",
      "universe": "all"
    },
    "sma_trend_20_50": {
      "name": "SMA 20/50 Crossover",
      "description": "Long when SMA20 > SMA50",
      "type": "trend_following",
      "universe": "all"
    },
    "leveraged_etf_timing": {
      "name": "3x Leveraged ETF Timing",
      "description": "Use 3x ETFs only in strong confirmed trends",
      "type": "aggressive_trend",
      "universe": ["TQQQ", "SOXL", "UPRO"]
    }
  },
  "ratings": {
    "NVDA": {
      "sma_200_trend": "buy",
      "dual_momentum": "hold",
      "rsi_mean_reversion": "hold",
      "breakout_20d": "buy",
      "sma_trend_20_50": "buy",
      "leveraged_etf_timing": "n/a"
    },
    "SPY": {
      "sma_200_trend": "buy",
      "dual_momentum": "sell",
      "rsi_mean_reversion": "sell",
      "breakout_20d": "hold",
      "sma_trend_20_50": "buy",
      "leveraged_etf_timing": "n/a"
    },
    "GLD": {
      "sma_200_trend": "buy",
      "dual_momentum": "buy",
      "rsi_mean_reversion": "hold",
      "breakout_20d": "hold",
      "sma_trend_20_50": "buy",
      "leveraged_etf_timing": "n/a"
    },
    "TQQQ": {
      "sma_200_trend": "buy",
      "dual_momentum": "n/a",
      "rsi_mean_reversion": "hold",
      "breakout_20d": "buy",
      "sma_trend_20_50": "buy",
      "leveraged_etf_timing": "buy"
    }
  },
  "summary": {
    "total_tickers": 40,
    "total_strategies": 6,
    "most_bullish": ["NVDA", "TQQQ", "AAPL"],
    "most_bearish": ["XLU", "TLT"],
    "consensus_buy": 12,
    "consensus_sell": 8,
    "consensus_hold": 20
  }
}
```

### Consensus Logic
For ticker detail pages, show a consensus score:
- BUY from applicable strategy = +1
- SELL = -1
- HOLD = 0

Example: NVDA gets 4 BUYs, 0 SELLs, 2 HOLDs → Consensus: +4 (Strong Buy)

## Strategy Definitions

### 1. SMA 200 Trend Following
```python
def sma_200_trend(ticker_data):
    price = ticker_data['close']
    sma_200 = ticker_data['sma_200']

    if price > sma_200:
        return "buy"
    else:
        return "sell"
```

**Rationale:** Classic long-term trend filter. Above 200 SMA = bull market for that ticker.

### 2. SMA 20/50 Crossover
```python
def sma_trend_20_50(ticker_data):
    sma_20 = ticker_data['sma_20']
    sma_50 = ticker_data['sma_50']

    if sma_20 > sma_50:
        return "buy"
    elif sma_20 < sma_50:
        return "sell"
    else:
        return "hold"
```

**Rationale:** Shorter-term trend following. More responsive than 200 SMA.

### 3. RSI Mean Reversion
```python
def rsi_mean_reversion(ticker_data):
    rsi = ticker_data['rsi_14']

    if rsi < 35:
        return "buy"
    elif rsi > 65:
        return "sell"
    else:
        return "hold"
```

**Rationale:** Buy oversold, sell overbought. Works best in range-bound markets.

### 4. 20-Day Breakout
```python
def breakout_20d(ticker_data, history):
    current_price = ticker_data['close']
    high_20d = history['close'].tail(20).max()
    low_10d = history['close'].tail(10).min()

    if current_price > high_20d:
        return "buy"
    elif current_price < low_10d:
        return "sell"
    else:
        return "hold"
```

**Rationale:** Momentum breakout system. Catches new trends early.

### 5. Dual Momentum Rotation
```python
def dual_momentum(market_data):
    # Portfolio-level strategy
    # Only returns ratings for SPY, QQQ, XLE, GLD, TLT, XLU

    offensive = ['SPY', 'QQQ', 'XLE']
    defensive = ['GLD', 'TLT', 'XLU']

    # Calculate 20-day returns for each
    returns = {ticker: calculate_return_20d(market_data[ticker]) for ticker in offensive + defensive}

    # Find best offensive asset
    best_offensive = max([(ticker, returns[ticker]) for ticker in offensive], key=lambda x: x[1])

    # If best offensive is positive, use it
    if best_offensive[1] > 0:
        winner = best_offensive[0]
        return {ticker: "buy" if ticker == winner else "sell" for ticker in offensive + defensive}

    # Otherwise, use best defensive
    best_defensive = max([(ticker, returns[ticker]) for ticker in defensive], key=lambda x: x[1])
    winner = best_defensive[0]
    return {ticker: "buy" if ticker == winner else "sell" for ticker in offensive + defensive}
```

**Rationale:** This is the top-performing strategy from backtests. Rotates between offensive and defensive based on momentum.

### 6. 3x Leveraged ETF Timing
```python
def leveraged_etf_timing(ticker_data, underlying_data):
    # Only applies to TQQQ, SOXL, UPRO, etc.
    # Requires strong trend confirmation on underlying

    if ticker not in ['TQQQ', 'SOXL', 'UPRO', 'SOXS', 'TECS', 'SPXU']:
        return "n/a"

    # Get underlying (QQQ for TQQQ, SOX for SOXL, SPY for UPRO)
    underlying = get_underlying(ticker)

    # Require multiple confirmations for leveraged long:
    # 1. Price > 50 SMA
    # 2. 50 SMA > 200 SMA
    # 3. RSI > 40 (not oversold)
    # 4. Recent 20-day return > 0

    price = underlying_data['close']
    sma_50 = underlying_data['sma_50']
    sma_200 = underlying_data['sma_200']
    rsi = underlying_data['rsi_14']
    mom_20d = calculate_return_20d(underlying_data)

    # Inverse ETFs (SOXS, TECS, SPXU) - flip logic
    is_inverse = ticker in ['SOXS', 'TECS', 'SPXU']

    if not is_inverse:
        # Long 3x ETFs: need strong uptrend
        if price > sma_50 and sma_50 > sma_200 and rsi > 40 and mom_20d > 0:
            return "buy"
        else:
            return "sell"
    else:
        # Inverse 3x ETFs: need strong downtrend
        if price < sma_50 and sma_50 < sma_200 and rsi < 60 and mom_20d < 0:
            return "buy"
        else:
            return "sell"
```

**Rationale:** 3x leveraged ETFs are dangerous in choppy or downtrending markets. Only use them in confirmed strong trends.

## Implementation Plan

### Phase 1: Core Infrastructure
Create `src/generate_strategy_ratings.py`:

```python
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

def load_market_context():
    with open('data/market_context.json') as f:
        return json.load(f)

def sma_200_trend(ticker, data):
    # Implementation
    pass

def sma_trend_20_50(ticker, data):
    # Implementation
    pass

def rsi_mean_reversion(ticker, data):
    # Implementation
    pass

def breakout_20d(ticker, history):
    # Implementation
    pass

def dual_momentum(market_data):
    # Implementation
    pass

def leveraged_etf_timing(ticker, data, underlying_data):
    # Implementation
    pass

def generate_ratings():
    market_context = load_market_context()

    ratings = {}
    for ticker in market_context['tickers']:
        ticker_data = market_context['tickers'][ticker]
        history = load_history(ticker)

        ratings[ticker] = {
            'sma_200_trend': sma_200_trend(ticker, ticker_data),
            'sma_trend_20_50': sma_trend_20_50(ticker, ticker_data),
            'rsi_mean_reversion': rsi_mean_reversion(ticker, ticker_data),
            'breakout_20d': breakout_20d(ticker, history),
            'dual_momentum': 'n/a',  # Computed separately
            'leveraged_etf_timing': leveraged_etf_timing(ticker, ticker_data, market_context)
        }

    # Compute dual momentum for portfolio
    dm_ratings = dual_momentum(market_context)
    for ticker, rating in dm_ratings.items():
        if ticker in ratings:
            ratings[ticker]['dual_momentum'] = rating

    output = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'strategies': {...},  # Strategy metadata
        'ratings': ratings,
        'summary': compute_summary(ratings)
    }

    # Write outputs
    with open('data/strategy_ratings.json', 'w') as f:
        json.dump(output, f, indent=2)

    with open('frontend/public/data/strategy_ratings.json', 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == '__main__':
    generate_ratings()
```

### Phase 2: Frontend Integration
Update ticker detail pages to display strategy ratings:

```tsx
// In frontend ticker component
const strategyRatings = tickerData.strategy_ratings;

<StrategyRatingsTable>
  <h3>Strategy Ratings</h3>
  {Object.entries(strategyRatings).map(([strategy, rating]) => (
    <Row key={strategy}>
      <StrategyName>{strategyNames[strategy]}</StrategyName>
      <Rating sentiment={rating}>{rating.toUpperCase()}</Rating>
    </Row>
  ))}
  <ConsensuScore score={calculateConsensus(strategyRatings)} />
</StrategyRatingsTable>
```

### Phase 3: Integration with Workflow
Update `.github/workflows/daily_analysis.yml`:

```yaml
- name: Generate strategy ratings
  run: python3 src/generate_strategy_ratings.py

- name: Run LLM analysis
  run: python3 src/llm_agents.py
```

### Phase 4: Validation
Before deploying:
1. Backtest each strategy across multiple periods
2. Verify ratings match backtest signal logic
3. Spot-check several tickers manually
4. Ensure JSON schema is correct

## Strategy Addition Process

When adding a new strategy:

1. **Research:** Create spike document explaining the strategy
2. **Backtest:** Implement in `backtesting/strategies.py` and validate across regimes
3. **If validated:** Add to `src/generate_strategy_ratings.py`
4. **Update metadata:** Add strategy info to the strategies section of output JSON
5. **Document:** Update this spike with the new strategy definition

## Display Guidelines

### Ticker Detail Page
Show:
- Table of all applicable strategies and their ratings
- Color coding: green = buy, red = sell, gray = hold
- Consensus score with visual indicator
- Link to strategy explanation page

### Strategies Overview Page
Show:
- List of all strategies with descriptions
- Backtest performance metrics for each
- When each strategy tends to work (regime compatibility)
- Current portfolio alignment with each strategy

### Home Dashboard
Show:
- Number of tickers with consensus buy/sell/hold
- Which strategies are most bullish/bearish right now
- Ticker heatmap colored by consensus score

## Relationship to LLM Analysis

Strategy ratings are **complementary** to LLM analysis, not competitive:

**LLM Analysis:**
- Nuanced, context-aware
- Considers news, macro, risk, portfolio construction
- Can override technicals for fundamental reasons
- Explains *why*

**Strategy Ratings:**
- Mechanical, reproducible
- Pure technical rules
- Backtested and validated
- Shows *what the system does*

The LLM can reference strategy ratings in its analysis:
> "NVDA is getting buy signals from 4 out of 6 applicable strategies (200 SMA, breakout, short-term trend, and consensus momentum). However, given elevated semiconductor inventory concerns in recent news, I recommend waiting for a better entry on weakness."

## Risk Management Integration

Strategy ratings should eventually influence:

1. **Position sizing:** Stronger consensus = larger position (within limits)
2. **Entry timing:** Wait for multiple confirmations
3. **Stop placement:** Use strategy invalidation levels
4. **Portfolio construction:** Diversify across uncorrelated strategies

## Next Steps

1. Implement `src/generate_strategy_ratings.py`
2. Add to daily workflow after data ingestion
3. Create frontend components for display
4. Build strategies overview page
5. Connect to paper trading tracker (next spike)

## Success Metrics

Strategy rating system is successful if:
- Ratings match backtested signals exactly
- Users can understand why each rating was assigned
- Consensus scores correlate with forward returns
- System helps identify high-conviction setups
- Ratings provide accountability for what the system is doing

This creates transparency and trust in the system's mechanical strategies.
