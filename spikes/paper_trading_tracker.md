# Spike: Paper Trading Performance Tracker

**Objective:** Design and implement a forward paper trading system that tracks real-time performance of strategies and LLM recommendations without risking capital.

## Purpose

This is **Mode 3** of the three-mode AlphaOracle system:
1. LLM Analysis (general recommendations) - ✓ implemented
2. Strategy Ratings (rule-based signals) - designed in `strategy_rating_system.md`
3. **Paper Trading Tracker (forward validation)** - this spike

## Core Goals

### Accountability
- Track what the system recommends vs. what actually happens
- Measure real forward performance, not just backtest results
- Identify which strategies work in live markets
- Detect when strategies stop working (regime change, degradation)

### Transparency
- All trades logged with timestamp, price, rationale
- Daily P&L visible on frontend
- Performance metrics updated in real-time
- Compare multiple strategies side-by-side

### Learning Loop
- Feed performance results back to LLM prompts
- Enable self-correction: "This strategy predicted X but Y happened"
- Build a lessons-learned ledger
- Improve recommendations over time

## What Gets Paper Traded

### Track 1: Individual Rule-Based Strategies
Each validated strategy runs independently:
- `dual_momentum_rotation`
- `sma_200_trend`
- `sma_trend_20_50`
- `rsi_mean_reversion`
- `breakout_20d`
- `leveraged_etf_timing`
- Others as validated by backtesting

Each strategy has its own:
- Virtual cash balance (e.g., $100,000 starting capital)
- Position tracking
- Performance metrics
- Trade history

### Track 2: LLM Recommendations
Track the PM's trade recommendations from `data/trades.json`:
- Separate virtual portfolio
- Same starting capital as rule-based strategies
- Follows LLM's buy/sell recommendations
- Measures whether the AI adds value over mechanical strategies

### Track 3: Ensemble / Consensus
A meta-strategy that combines signals:
- Takes positions only when multiple strategies agree
- Weighted by strategy Sharpe ratio or recent performance
- Tests whether consensus beats individual strategies

## Architecture

### Data Flow

```
Strategy Ratings → Paper Trade Executor → Position Tracker → Performance Calculator → Frontend Display
      ↓                                          ↓
LLM Trades.json                           Daily Price Updates
```

### Daily Workflow

1. **Morning:** Update positions with latest EOD prices (previous day's close)
2. **After Market Close:**
   - Run `src/data_ingestion.py` (get new prices, news, technicals)
   - Run `src/generate_strategy_ratings.py` (get new signals)
   - Run `src/llm_agents.py` (get new LLM recommendations)
3. **Execute Paper Trades:**
   - Run `src/execute_paper_trades.py`
   - Compare new signals to current positions
   - Generate trades to align positions with signals
   - Log all trades with timestamp and rationale
4. **Update Performance Metrics:**
   - Calculate daily P&L for each strategy
   - Update cumulative returns
   - Recalculate Sharpe, drawdown, win rate
   - Identify best and worst performing strategies
5. **Generate Frontend Data:**
   - Write `data/paper_performance.json`
   - Write `data/paper_trades_history.json`
   - Copy to `frontend/public/data/`

### File Structure

```
data/
├── paper_trading/
│   ├── positions.json           # Current positions per strategy
│   ├── trades_history.json      # Complete trade log
│   ├── daily_snapshots/         # Daily portfolio snapshots
│   │   ├── 2026-03-16.json
│   │   ├── 2026-03-15.json
│   │   └── ...
│   └── performance.json         # Current performance metrics
```

## Data Schemas

### File: `data/paper_trading/positions.json`

Tracks current holdings for each strategy.

```json
{
  "updated_at": "2026-03-16T21:00:00Z",
  "strategies": {
    "dual_momentum_rotation": {
      "starting_capital": 100000,
      "current_cash": 5234.56,
      "current_positions": {
        "GLD": {
          "shares": 432.18,
          "avg_entry_price": 218.45,
          "current_price": 219.30,
          "market_value": 94785.44,
          "unrealized_pnl": 367.53,
          "unrealized_pnl_pct": 0.39,
          "entry_date": "2026-03-10"
        }
      },
      "total_portfolio_value": 100020.00,
      "total_return": 0.0002,
      "total_return_pct": 0.02
    },
    "sma_200_trend": {
      "starting_capital": 100000,
      "current_cash": 12456.78,
      "current_positions": {
        "NVDA": {
          "shares": 75.0,
          "avg_entry_price": 845.20,
          "current_price": 852.40,
          "market_value": 63930.00,
          "unrealized_pnl": 540.00,
          "unrealized_pnl_pct": 0.85,
          "entry_date": "2026-02-28"
        },
        "AAPL": {
          "shares": 120.0,
          "avg_entry_price": 195.30,
          "current_price": 197.15,
          "market_value": 23658.00,
          "unrealized_pnl": 222.00,
          "unrealized_pnl_pct": 0.95,
          "entry_date": "2026-03-01"
        }
      },
      "total_portfolio_value": 100044.78,
      "total_return": 0.00045,
      "total_return_pct": 0.045
    },
    "llm_recommendations": {
      "starting_capital": 100000,
      "current_cash": 34500.00,
      "current_positions": {
        "XLU": {
          "shares": 950.0,
          "avg_entry_price": 68.50,
          "current_price": 69.00,
          "market_value": 65550.00,
          "unrealized_pnl": 475.00,
          "unrealized_pnl_pct": 0.73,
          "entry_date": "2026-03-12"
        }
      },
      "total_portfolio_value": 100050.00,
      "total_return": 0.0005,
      "total_return_pct": 0.05
    }
  }
}
```

### File: `data/paper_trading/trades_history.json`

Complete trade log for accountability.

```json
{
  "trades": [
    {
      "id": "trade_20260316_001",
      "timestamp": "2026-03-16T21:05:00Z",
      "strategy": "dual_momentum_rotation",
      "ticker": "SPY",
      "action": "sell",
      "shares": 185.0,
      "price": 560.25,
      "notional": 103646.25,
      "commission": 0.0,
      "rationale": "Dual momentum rotation: SPY 20-day return -2.3% < GLD 20-day return +1.8%. Rotating to GLD.",
      "signal_data": {
        "spy_return_20d": -0.023,
        "gld_return_20d": 0.018,
        "winner": "GLD"
      }
    },
    {
      "id": "trade_20260316_002",
      "timestamp": "2026-03-16T21:06:00Z",
      "strategy": "dual_momentum_rotation",
      "ticker": "GLD",
      "action": "buy",
      "shares": 473.45,
      "price": 219.10,
      "notional": 103718.50,
      "commission": 0.0,
      "rationale": "Dual momentum rotation: GLD is best defensive with +1.8% 20-day return.",
      "signal_data": {
        "gld_return_20d": 0.018
      }
    },
    {
      "id": "trade_20260316_003",
      "timestamp": "2026-03-16T21:10:00Z",
      "strategy": "llm_recommendations",
      "ticker": "XLU",
      "action": "buy",
      "shares": 950.0,
      "price": 68.50,
      "notional": 65075.00,
      "commission": 0.0,
      "rationale": "LLM PM recommendation: Buy XLU for defensive positioning given elevated macro risk and utility sector relative strength.",
      "signal_data": {
        "pm_conviction": "medium",
        "pm_rationale": "Utilities showing resilience with power demand theme intact."
      }
    }
  ]
}
```

### File: `data/paper_trading/performance.json`

Performance metrics for each strategy.

```json
{
  "updated_at": "2026-03-16T21:30:00Z",
  "period_start": "2026-01-15",
  "period_end": "2026-03-16",
  "trading_days": 42,
  "strategies": {
    "dual_momentum_rotation": {
      "starting_capital": 100000,
      "current_value": 100367.89,
      "total_return": 367.89,
      "total_return_pct": 0.368,
      "annualized_return_pct": 2.89,
      "daily_returns": [...],
      "sharpe_ratio": 1.42,
      "sortino_ratio": 2.18,
      "max_drawdown": -0.0145,
      "max_drawdown_pct": -1.45,
      "current_drawdown": 0.0,
      "volatility_annualized": 0.089,
      "trades_total": 8,
      "trades_winning": 5,
      "trades_losing": 3,
      "win_rate": 0.625,
      "avg_win": 124.50,
      "avg_loss": -58.30,
      "profit_factor": 2.14,
      "current_positions": 1,
      "cash_pct": 5.2,
      "equity_pct": 94.8
    },
    "sma_200_trend": {
      "starting_capital": 100000,
      "current_value": 99845.22,
      "total_return": -154.78,
      "total_return_pct": -0.155,
      "annualized_return_pct": -1.21,
      "sharpe_ratio": -0.34,
      "max_drawdown_pct": -3.12,
      "trades_total": 12,
      "win_rate": 0.42,
      "profit_factor": 0.87
    },
    "llm_recommendations": {
      "starting_capital": 100000,
      "current_value": 100523.45,
      "total_return": 523.45,
      "total_return_pct": 0.523,
      "annualized_return_pct": 4.11,
      "sharpe_ratio": 1.89,
      "max_drawdown_pct": -2.05,
      "trades_total": 6,
      "win_rate": 0.67,
      "profit_factor": 2.45
    }
  },
  "benchmarks": {
    "SPY": {
      "period_return_pct": 1.23,
      "annualized_return_pct": 9.65,
      "volatility_annualized": 0.152,
      "max_drawdown_pct": -4.23
    }
  },
  "rankings": {
    "by_total_return": [
      {"strategy": "llm_recommendations", "return_pct": 0.523},
      {"strategy": "dual_momentum_rotation", "return_pct": 0.368},
      {"strategy": "sma_200_trend", "return_pct": -0.155}
    ],
    "by_sharpe": [
      {"strategy": "llm_recommendations", "sharpe": 1.89},
      {"strategy": "dual_momentum_rotation", "sharpe": 1.42},
      {"strategy": "sma_200_trend", "sharpe": -0.34}
    ]
  }
}
```

## Implementation

### Script: `src/execute_paper_trades.py`

```python
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

class PaperTradingEngine:
    def __init__(self):
        self.positions_file = Path('data/paper_trading/positions.json')
        self.trades_file = Path('data/paper_trading/trades_history.json')
        self.performance_file = Path('data/paper_trading/performance.json')

        self.load_state()

    def load_state(self):
        """Load current positions and trade history"""
        if self.positions_file.exists():
            with open(self.positions_file) as f:
                self.positions = json.load(f)
        else:
            self.positions = self.initialize_positions()

        if self.trades_file.exists():
            with open(self.trades_file) as f:
                self.trades_history = json.load(f)
        else:
            self.trades_history = {"trades": []}

    def initialize_positions(self):
        """Initialize starting positions for all strategies"""
        strategies = [
            'dual_momentum_rotation',
            'sma_200_trend',
            'sma_trend_20_50',
            'rsi_mean_reversion',
            'breakout_20d',
            'llm_recommendations'
        ]

        return {
            "updated_at": datetime.utcnow().isoformat() + 'Z',
            "strategies": {
                strategy: {
                    "starting_capital": 100000,
                    "current_cash": 100000,
                    "current_positions": {},
                    "total_portfolio_value": 100000,
                    "total_return": 0.0,
                    "total_return_pct": 0.0
                }
                for strategy in strategies
            }
        }

    def execute_strategy_signals(self, strategy_name, target_positions):
        """
        Execute trades to align current positions with target positions.

        Args:
            strategy_name: Name of strategy
            target_positions: Dict of {ticker: target_weight}
                             target_weight is 0.0 to 1.0 or specific share count
        """
        current = self.positions['strategies'][strategy_name]
        current_holdings = set(current['current_positions'].keys())
        target_holdings = set(target_positions.keys())

        # Sell positions no longer in target
        to_sell = current_holdings - target_holdings
        for ticker in to_sell:
            self.execute_trade(strategy_name, ticker, 'sell', current['current_positions'][ticker]['shares'])

        # Buy or adjust positions in target
        for ticker, target_weight in target_positions.items():
            self.execute_trade(strategy_name, ticker, 'buy', shares=None, target_weight=target_weight)

    def execute_trade(self, strategy_name, ticker, action, shares=None, target_weight=None, rationale=""):
        """Execute a single paper trade"""
        current_price = self.get_current_price(ticker)

        if target_weight is not None:
            # Calculate shares from target weight
            portfolio_value = self.positions['strategies'][strategy_name]['total_portfolio_value']
            target_value = portfolio_value * target_weight
            shares = target_value / current_price

        if action == 'sell':
            # Remove position
            position = self.positions['strategies'][strategy_name]['current_positions'].pop(ticker)
            proceeds = shares * current_price
            self.positions['strategies'][strategy_name]['current_cash'] += proceeds

        elif action == 'buy':
            # Add or update position
            cost = shares * current_price
            self.positions['strategies'][strategy_name]['current_cash'] -= cost

            self.positions['strategies'][strategy_name]['current_positions'][ticker] = {
                'shares': shares,
                'avg_entry_price': current_price,
                'current_price': current_price,
                'market_value': shares * current_price,
                'unrealized_pnl': 0.0,
                'unrealized_pnl_pct': 0.0,
                'entry_date': datetime.utcnow().date().isoformat()
            }

        # Log trade
        trade_id = f"trade_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        trade = {
            'id': trade_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'strategy': strategy_name,
            'ticker': ticker,
            'action': action,
            'shares': shares,
            'price': current_price,
            'notional': shares * current_price,
            'commission': 0.0,
            'rationale': rationale
        }

        self.trades_history['trades'].append(trade)

        # Update portfolio value
        self.update_portfolio_value(strategy_name)

    def update_portfolio_value(self, strategy_name):
        """Recalculate total portfolio value"""
        strategy = self.positions['strategies'][strategy_name]

        total_value = strategy['current_cash']
        for ticker, position in strategy['current_positions'].items():
            current_price = self.get_current_price(ticker)
            position['current_price'] = current_price
            position['market_value'] = position['shares'] * current_price
            position['unrealized_pnl'] = (current_price - position['avg_entry_price']) * position['shares']
            position['unrealized_pnl_pct'] = (current_price / position['avg_entry_price']) - 1.0
            total_value += position['market_value']

        strategy['total_portfolio_value'] = total_value
        strategy['total_return'] = total_value - strategy['starting_capital']
        strategy['total_return_pct'] = strategy['total_return'] / strategy['starting_capital']

    def get_current_price(self, ticker):
        """Get current EOD price for ticker"""
        # Load from data/history/{ticker}.json
        history_file = Path(f'data/history/{ticker}.json')
        with open(history_file) as f:
            data = json.load(f)
        return data['prices'][-1]['close']

    def save_state(self):
        """Save positions and trades"""
        self.positions['updated_at'] = datetime.utcnow().isoformat() + 'Z'

        with open(self.positions_file, 'w') as f:
            json.dump(self.positions, f, indent=2)

        with open(self.trades_file, 'w') as f:
            json.dump(self.trades_history, f, indent=2)

    def calculate_performance_metrics(self):
        """Calculate performance metrics for all strategies"""
        # Implementation of Sharpe, drawdown, win rate, etc.
        pass

    def run_daily_update(self):
        """Main daily execution"""
        # 1. Update all portfolio values with latest prices
        for strategy_name in self.positions['strategies'].keys():
            self.update_portfolio_value(strategy_name)

        # 2. Load latest strategy ratings
        with open('data/strategy_ratings.json') as f:
            ratings = json.load(f)

        # 3. Execute rule-based strategy signals
        for strategy_name in ['dual_momentum_rotation', 'sma_200_trend', ...]:
            target_positions = self.get_target_positions_for_strategy(strategy_name, ratings)
            self.execute_strategy_signals(strategy_name, target_positions)

        # 4. Execute LLM recommendations
        with open('data/trades.json') as f:
            llm_trades = json.load(f)
        self.execute_llm_trades(llm_trades)

        # 5. Save state
        self.save_state()

        # 6. Calculate and save performance metrics
        performance = self.calculate_performance_metrics()
        with open(self.performance_file, 'w') as f:
            json.dump(performance, f, indent=2)

        # 7. Copy to frontend
        self.copy_to_frontend()

if __name__ == '__main__':
    engine = PaperTradingEngine()
    engine.run_daily_update()
```

## Frontend Display

### Performance Dashboard

Create new page: `frontend/src/pages/paper-trading.astro`

Display:
- **Equity curves:** Line chart showing portfolio value over time for each strategy + SPY benchmark
- **Performance table:** All strategies ranked by return, Sharpe, max drawdown
- **Recent trades:** Last 20 trades across all strategies
- **Current positions:** What each strategy is holding right now
- **Best/worst trades:** Highlight biggest wins and losses

### Strategy Detail Pages

For each strategy, show:
- Equity curve
- Trade history
- Win/loss analysis
- Metrics vs. benchmark
- Current positions
- Strategy description and rules

## Accountability and Learning

### Weekly Review Process

Every Sunday, generate a review report:

1. **What happened last week:**
   - Market performance (SPY, QQQ, GLD, etc.)
   - Major news events
   - Regime changes

2. **How strategies performed:**
   - Which strategies made money
   - Which lost money
   - Which trades worked, which didn't

3. **Lessons learned:**
   - Did dual momentum correctly rotate during volatility?
   - Did LLM overreact to news?
   - Did mean reversion get whipsawed?

4. **Feed to LLM:**
   - Add performance context to next week's prompts
   - "Last week, the system recommended X but Y happened. Consider..."
   - Build a lessons ledger that persists

### Degradation Detection

Alert if:
- Strategy Sharpe drops below 0.0 for more than 20 days
- Drawdown exceeds backtest max drawdown by 50%
- Win rate drops below 40%
- Consecutive losing trades > 5

Action: Pause that strategy's paper trading and review

## Success Metrics

Paper trading system is successful if:

1. **Transparency:** Every trade is logged and explainable
2. **Validation:** At least one strategy beats SPY over 90 days
3. **Learning:** LLM performance improves quarter-over-quarter
4. **Reliability:** System runs daily without manual intervention
5. **Accountability:** Bad calls are acknowledged and learned from

## Phased Rollout

### Phase 1 (Week 1-2): Basic Infrastructure
- Implement positions tracking
- Implement trade execution logic
- Test with 2-3 strategies manually

### Phase 2 (Week 3-4): Automation
- Integrate with daily workflow
- Auto-execute all strategy signals
- Build performance calculator

### Phase 3 (Week 5-8): Frontend
- Build equity curve charts
- Create performance dashboard
- Add trade history table

### Phase 4 (Week 9+): Learning Loop
- Weekly review generation
- Feed results to LLM
- Degradation alerts
- Strategy refinement based on live results

## Risk Controls

Even though this is paper trading:

1. **Max position size:** No single position > 25% of strategy portfolio
2. **Max leverage:** None (cash only, no margin)
3. **Diversification:** Force at least 2 positions per portfolio strategy
4. **Sanity checks:** Alert if any trade exceeds $50k notional (half the portfolio)

This prevents paper trading results from being unrealistic.

## Next Steps

1. Create `data/paper_trading/` directory structure
2. Implement `src/execute_paper_trades.py`
3. Initialize starting positions for all strategies
4. Add to daily workflow after `src/generate_strategy_ratings.py`
5. Build basic performance calculator
6. Create frontend dashboard (Phase 3)

After 30-60 days of paper trading, evaluate:
- Which strategy should graduate to real-money execution?
- Should any strategies be retired?
- What did we learn about the LLM's strengths and weaknesses?

This creates a systematic, accountable path from backtest → paper trade → real money.
