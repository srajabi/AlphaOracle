# Spike: Backtesting Libraries Comparison

**Objective:** Evaluate popular Python backtesting libraries to understand tradeoffs vs our custom implementation and determine if we should migrate or stay custom.

## Our Current Custom Implementation

**What we built:**
- `backtesting/engine.py` - Simple vectorized backtest engine
- `backtesting/strategies.py` - Single-asset strategies
- `backtesting/portfolio_strategies.py` - Portfolio rotation strategies
- `backtesting/run_backtests.py` - Orchestration and results

**Strengths:**
- ✅ **Simple and lightweight** - ~200 lines of code total
- ✅ **Fully customized** - Does exactly what we need, nothing more
- ✅ **No dependencies** - Just pandas and numpy
- ✅ **Fast enough** - Handles 33 years × 6 assets in seconds
- ✅ **Easy to understand** - No magic, clear logic

**Limitations:**
- ❌ **No intraday support** - Daily resolution only
- ❌ **Basic order types** - Close-to-close execution only
- ❌ **Fixed transaction costs** - No dynamic slippage model
- ❌ **No portfolio constraints** - No position sizing limits
- ❌ **No optimization** - Manual parameter tuning
- ❌ **Basic metrics** - Sharpe, drawdown, win rate only

## Top Python Backtesting Libraries

### 1. VectorBT

**Website:** https://vectorbt.dev/

**Core Philosophy:** Extreme speed through full vectorization

**Architecture:**
```python
import vectorbt as vbt

# Define strategy using indicators
fast_ma = vbt.MA.run(close, 10)
slow_ma = vbt.MA.run(close, 50)

# Generate signals
entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

# Run portfolio simulation
pf = vbt.Portfolio.from_signals(close, entries, exits)

# Analyze results
pf.total_return()
pf.sharpe_ratio()
pf.plot()
```

**Strengths:**
- ⚡ **Blazingly fast** - 10-100x faster than event-driven approaches
- 📊 **Rich analytics** - 100+ built-in performance metrics
- 📈 **Beautiful visualizations** - Interactive Plotly charts
- 🔧 **Optimization** - Grid search and parameter optimization built-in
- 💼 **Portfolio-aware** - Proper position sizing and cash management

**Weaknesses:**
- 📚 **Steep learning curve** - Complex API, many abstractions
- 💾 **Memory hungry** - Vectorization loads full dataset in memory
- 🐛 **Debugging is hard** - Vectorized code less intuitive than loops
- 📦 **Heavy dependency** - Requires numba, plotly, many others

**Best for:**
- Large-scale quantitative research
- Parameter optimization across thousands of combinations
- Multi-asset portfolio strategies with complex rules
- When you need professional-grade analytics

**Our use case fit:** ⭐⭐⭐⭐ (Good, but overkill for 6-asset rotation)

---

### 2. Backtrader

**Website:** https://www.backtrader.com/

**Core Philosophy:** Comprehensive, event-driven framework with live trading support

**Architecture:**
```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    def __init__(self):
        self.sma_fast = bt.indicators.SMA(self.data.close, period=10)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=50)

    def next(self):
        if self.sma_fast > self.sma_slow and not self.position:
            self.buy()
        elif self.sma_fast < self.sma_slow and self.position:
            self.sell()

cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)
cerebro.adddata(data)
cerebro.run()
```

**Strengths:**
- 🔧 **Feature complete** - Everything you could ever need
- 🤝 **Broker integration** - Live trading with IB, Oanda, Alpaca
- 📚 **Extensive docs** - Well documented with many examples
- 👥 **Large community** - Active forums and support
- 📊 **Built-in indicators** - 100+ technical indicators included

**Weaknesses:**
- 🐌 **Slow** - Event-driven architecture is 10-100x slower than vectorized
- 📚 **Complex API** - Steep learning curve, many concepts
- 🗂️ **Verbose code** - Requires lots of boilerplate
- 🏗️ **Over-engineered** - Too many features for simple use cases

**Best for:**
- Transitioning from backtest to live trading
- Complex strategies with multiple data feeds and timeframes
- When you need extensive built-in indicators
- Institutional-grade strategies with order management

**Our use case fit:** ⭐⭐⭐ (Overkill, but live trading integration is nice)

---

### 3. Backtesting.py

**Website:** https://kernc.github.io/backtesting.py/

**Core Philosophy:** Simple, lightweight, and beginner-friendly

**Architecture:**
```python
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class SmaCross(Strategy):
    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, 10)
        self.sma2 = self.I(SMA, self.data.Close, 50)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()

bt = Backtest(data, SmaCross, cash=10000, commission=.002)
stats = bt.run()
bt.plot()
```

**Strengths:**
- 🎯 **Simple API** - Clean, intuitive, minimal boilerplate
- 📊 **Interactive plots** - Beautiful Bokeh visualizations out of the box
- 🔧 **Built-in optimizer** - Easy parameter optimization
- 📦 **Lightweight** - Minimal dependencies
- 📚 **Great docs** - Clear examples and tutorials

**Weaknesses:**
- ⏱️ **Daily data only** - No sub-daily resolution support
- 🐌 **Moderate speed** - Faster than Backtrader, slower than VectorBT
- 🎛️ **Limited features** - No multi-timeframe, no portfolio management
- 📈 **Basic indicators** - Must bring your own (TA-Lib integration)

**Best for:**
- Beginners learning algorithmic trading
- Rapid prototyping of simple strategies
- When you want clean visualizations with minimal code
- Single-asset strategies on daily data

**Our use case fit:** ⭐⭐⭐⭐⭐ (Perfect for our 6-asset rotation strategies!)

---

### 4. Zipline Reloaded

**Website:** https://github.com/stefan-jansen/zipline-reloaded

**Core Philosophy:** Quantopian's legacy - institutional-grade equity research

**Architecture:**
```python
from zipline.api import order_target, record, symbol

def initialize(context):
    context.asset = symbol('AAPL')

def handle_data(context, data):
    ma_short = data.history(context.asset, 'price', 10, '1d').mean()
    ma_long = data.history(context.asset, 'price', 50, '1d').mean()

    if ma_short > ma_long:
        order_target(context.asset, 100)
    elif ma_short < ma_long:
        order_target(context.asset, 0)
```

**Strengths:**
- 🏛️ **Institutional quality** - Used by professional quants
- 📊 **Factor research** - Built for equity factor strategies
- 📦 **Data bundles** - Integrated data management system
- 🎓 **Academic friendly** - Clean, reproducible research

**Weaknesses:**
- 🔧 **Complex setup** - Difficult dependency management
- 🐌 **Slow** - Event-driven architecture
- 📉 **Maintenance** - Original Quantopian closed, fork maintenance uncertain
- 🎯 **Equity-focused** - Not ideal for futures, FX, crypto

**Best for:**
- Academic research and papers
- Equity long-short strategies
- Factor-based portfolio construction
- When you need reproducible research infrastructure

**Our use case fit:** ⭐⭐ (Too complex for our needs)

---

### 5. bt (pronounced "bee-tee")

**Website:** https://pmorissette.github.io/bt/

**Core Philosophy:** Portfolio-first backtesting

**Architecture:**
```python
import bt

# Define strategy
strategy = bt.Strategy('s1', [
    bt.algos.RunMonthly(),
    bt.algos.SelectAll(),
    bt.algos.WeighEqually(),
    bt.algos.Rebalance()
])

# Run backtest
backtest = bt.Backtest(strategy, data)
result = bt.run(backtest)
result.plot()
```

**Strengths:**
- 🎯 **Portfolio-centric** - Built for asset allocation strategies
- 🔧 **Composable** - Mix and match algorithm building blocks
- 📊 **Clean API** - Intuitive for portfolio managers
- 📈 **Good for rebalancing** - Natural fit for rotation strategies

**Weaknesses:**
- 📚 **Limited docs** - Smaller community than alternatives
- 🎛️ **Less flexible** - Opinionated design for portfolio strategies
- 📦 **Fewer features** - No live trading, limited optimization
- 🐌 **Moderate speed** - Not as fast as VectorBT

**Best for:**
- Asset allocation and rebalancing strategies
- ETF rotation systems
- Multi-asset portfolio strategies
- When you think in terms of weights, not signals

**Our use case fit:** ⭐⭐⭐⭐⭐ (Great fit for rotation strategies!)

---

### 6. PyAlgoTrade

**Website:** http://gbeced.github.io/pyalgotrade/

**Core Philosophy:** Event-driven with paper trading support

**Architecture:**
```python
from pyalgotrade import strategy
from pyalgotrade.technical import ma

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed)
        self.__instrument = instrument
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), 15)

    def onBars(self, bars):
        if self.__sma[-1] is None:
            return

        if bars[self.__instrument].getPrice() > self.__sma[-1]:
            self.getBroker().submitOrder(self.getBroker().createMarketOrder(
                broker.Order.Action.BUY, self.__instrument, 10))
```

**Strengths:**
- 🤝 **Paper trading** - Built-in paper trading mode
- 📊 **Multiple order types** - Market, limit, stop orders
- 📈 **TA-Lib integration** - Easy technical analysis
- 🎯 **Mature codebase** - Stable and tested

**Weaknesses:**
- 📚 **Limited community** - Smaller user base
- 🐌 **Slower** - Event-driven architecture
- 🗂️ **Verbose** - Requires more code than alternatives
- 📦 **Older design** - API feels dated compared to modern libraries

**Best for:**
- When you need paper trading built-in
- Multi-asset class strategies
- When you want event-driven architecture
- Transitioning to live trading

**Our use case fit:** ⭐⭐⭐ (Decent, but not the best fit)

---

## Feature Comparison Matrix

| Feature | VectorBT | Backtrader | Backtesting.py | Zipline | bt | PyAlgoTrade | **Our Custom** |
|---------|----------|------------|----------------|---------|----|--------------|--------------------|
| **Speed** | ⚡⚡⚡⚡⚡ | ⚡ | ⚡⚡⚡ | ⚡ | ⚡⚡ | ⚡ | ⚡⚡⚡⚡ |
| **Simplicity** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Portfolio support** | ✅ | ✅ | ❌ | ✅ | ✅✅✅ | ✅ | ✅✅ |
| **Live trading** | ❌ | ✅✅✅ | ❌ | ❌ | ❌ | ✅✅ | ❌ |
| **Optimization** | ✅✅✅ | ✅✅ | ✅✅ | ✅ | ❌ | ✅ | ❌ |
| **Visualization** | ✅✅✅ | ✅✅ | ✅✅✅ | ✅ | ✅✅ | ✅ | ❌ |
| **Learning curve** | Steep | Steep | Gentle | Very steep | Gentle | Moderate | Minimal |
| **Dependencies** | Heavy | Moderate | Light | Heavy | Light | Light | **Minimal** |
| **Community** | Large | Huge | Medium | Medium | Small | Small | **None (custom)** |
| **Maintenance** | Active | Active | Active | Fork | Active | Slow | **Us** |

## Detailed Comparison for Our Use Case

### What We Need:
1. ✅ Daily resolution backtesting (not intraday)
2. ✅ Portfolio rotation strategies (6-asset universe)
3. ✅ Simple, clean code (easy to understand)
4. ✅ Fast enough for 33 years × multiple strategies
5. ✅ Custom metrics (Sharpe, drawdown, win rate)
6. ⚠️ Parameter optimization (nice to have)
7. ⚠️ Visualization (nice to have)
8. ❌ Live trading (not yet, but eventually)

### Rankings for Our Use Case:

1. **Backtesting.py** ⭐⭐⭐⭐⭐
   - Perfect balance of simplicity and features
   - Interactive plots out of the box
   - Built-in optimization
   - Clean API for portfolio strategies
   - Lightweight dependencies

2. **bt** ⭐⭐⭐⭐⭐
   - Built specifically for portfolio rotation
   - Composable algos match our rotation logic
   - Clean weight-based API
   - Good for our 6-asset rotation

3. **Our Custom Implementation** ⭐⭐⭐⭐
   - Already working
   - Zero learning curve (we built it!)
   - Minimal dependencies
   - Fast enough
   - Missing: optimization, visualization

4. **VectorBT** ⭐⭐⭐⭐
   - Overkill for 6 assets
   - Amazing features but complex
   - Would speed up multi-parameter optimization
   - Heavy dependencies

5. **Backtrader** ⭐⭐⭐
   - Feature complete but verbose
   - Good for eventual live trading
   - Slow for our needs
   - Over-engineered

6. **PyAlgoTrade** ⭐⭐⭐
   - Decent all-arounder
   - Paper trading is nice
   - Verbose API
   - Not the best fit

7. **Zipline** ⭐⭐
   - Way too complex for our needs
   - Equity-focused (we have ETFs)
   - Setup is painful
   - Overkill

## Should We Migrate or Stay Custom?

### Arguments FOR Migrating:

**To Backtesting.py:**
- ✅ Get beautiful interactive plots for free
- ✅ Built-in parameter optimization
- ✅ Clean API, minimal refactoring needed
- ✅ Active community and maintenance
- ✅ Could migrate in 1-2 days

**To bt:**
- ✅ Perfect conceptual fit for rotation strategies
- ✅ Think in weights, not signals (matches our logic)
- ✅ Composable algos = easy to extend
- ✅ Portfolio-first design

**To VectorBT:**
- ✅ Professional-grade analytics
- ✅ Fast parameter optimization
- ✅ Beautiful visualizations
- ✅ Future-proof for scaling

### Arguments AGAINST Migrating:

**Reasons to stay custom:**
- ✅ **Already works** - Don't fix what ain't broke
- ✅ **Zero dependencies** - Simple is better
- ✅ **Fast enough** - 33 years × 6 assets in seconds
- ✅ **Full control** - No library abstractions
- ✅ **Easy to understand** - No magic, clear logic
- ✅ **No learning curve** - We built it, we know it
- ✅ **Lightweight** - ~200 lines of code total

**Cost of migration:**
- ❌ 1-3 days of dev time
- ❌ Learning new API
- ❌ Adapting our strategies to new framework
- ❌ New dependencies to manage
- ❌ Potential bugs during migration

## Recommendation

### For Now: **Stay Custom** ✅

**Rationale:**
1. Our custom implementation works perfectly for our needs
2. It's simple, fast, and has zero external dependencies
3. We already validated strategies across 33 years
4. Migration would take 1-3 days with unclear benefits
5. We can add optimization and visualization ourselves if needed

**What we should add to our custom implementation:**
- Better visualization (matplotlib basic plots)
- Parameter sweep helper (grid search)
- More performance metrics (Sortino, Calmar, etc.)
- Better results export (JSON, CSV)

### Future: Consider **Backtesting.py** or **bt**

**When to migrate:**
- When we need interactive visualizations for frontend
- When we want to test 100+ parameter combinations
- When our strategies get more complex
- When we add intraday data

**Migration path:**
1. Keep custom implementation working
2. Implement same strategies in backtesting.py / bt
3. Validate results match (sanity check)
4. Switch if benefits are clear

## Making Our Custom Implementation More Generic

### Current Pain Points:

1. **Hardcoded strategy functions** - Can't easily add new strategies
2. **Separate single-asset vs portfolio** - Two different code paths
3. **Fixed transaction costs** - No dynamic slippage
4. **Basic metrics** - Missing Sortino, Calmar, etc.
5. **No optimization** - Manual parameter tuning

### Proposed Improvements:

#### 1. Unified Strategy Interface

```python
# strategies/base.py
from abc import ABC, abstractmethod

class Strategy(ABC):
    """Base class for all strategies"""

    @abstractmethod
    def generate_signals(self, data):
        """Generate trading signals from data

        Args:
            data: DataFrame with OHLCV data

        Returns:
            Series with signals (0 = no position, 1 = long)
        """
        pass

    def get_name(self):
        return self.__class__.__name__

    def get_params(self):
        return {}

# Single-asset strategies
class SMAStrategy(Strategy):
    def __init__(self, fast=20, slow=50):
        self.fast = fast
        self.slow = slow

    def generate_signals(self, data):
        fast_ma = data['close'].rolling(self.fast).mean()
        slow_ma = data['close'].rolling(self.slow).mean()
        return (fast_ma > slow_ma).astype(float)

# Portfolio strategies
class PortfolioStrategy(Strategy):
    """Base for portfolio rotation strategies"""

    @abstractmethod
    def generate_weights(self, prices):
        """Generate portfolio weights

        Args:
            prices: DataFrame with prices for multiple assets

        Returns:
            DataFrame with weights (sum to 1.0 per row)
        """
        pass
```

#### 2. Configuration-Based Backtest Runner

```python
# config/backtest_config.yaml
strategies:
  - name: sma_trend
    type: single_asset
    class: SMAStrategy
    params:
      fast: 20
      slow: 50

  - name: dual_momentum
    type: portfolio
    class: DualMomentumStrategy
    params:
      lookback: 20
      offensive: [SPY, QQQ, XLE]
      defensive: [GLD, TLT, XLU]

backtest:
  tickers: [SPY, QQQ, GLD, TLT, XLE, XLU]
  periods: [10, 20, 30, 40, full]
  transaction_cost_bps: 5.0
  start_date: 1993-01-01
  end_date: 2026-03-16
```

#### 3. Pluggable Metrics

```python
# metrics/performance.py
class PerformanceMetrics:
    def __init__(self, returns):
        self.returns = returns

    def sharpe_ratio(self, rf=0.0):
        return (self.returns.mean() - rf) / self.returns.std() * np.sqrt(252)

    def sortino_ratio(self, rf=0.0):
        downside = self.returns[self.returns < 0].std()
        return (self.returns.mean() - rf) / downside * np.sqrt(252)

    def calmar_ratio(self):
        return self.returns.mean() * 252 / abs(self.max_drawdown())

    def max_drawdown(self):
        cum_returns = (1 + self.returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdown = (cum_returns - running_max) / running_max
        return drawdown.min()
```

#### 4. Simple Parameter Optimizer

```python
# optimization/grid_search.py
def optimize_strategy(strategy_class, data, param_grid):
    """Grid search optimization

    Args:
        strategy_class: Strategy class to optimize
        data: Historical data
        param_grid: Dict of {param: [values]}

    Returns:
        DataFrame with results for each parameter combination
    """
    results = []

    for params in itertools.product(*param_grid.values()):
        param_dict = dict(zip(param_grid.keys(), params))
        strategy = strategy_class(**param_dict)

        signals = strategy.generate_signals(data)
        result = run_backtest(data, strategy.get_name(), signals)

        results.append({
            **param_dict,
            **result.to_dict()
        })

    return pd.DataFrame(results).sort_values('sharpe', ascending=False)
```

## Action Plan

### Phase 1: Documentation (This Spike) ✅
- Document available libraries
- Evaluate pros/cons for our use case
- Make recommendation

### Phase 2: Enhance Custom Implementation (1-2 days)
- Add unified Strategy base class
- Add more performance metrics (Sortino, Calmar, etc.)
- Add basic matplotlib visualizations
- Add simple grid search optimizer

### Phase 3: Evaluate Migration (When Needed)
- If we need interactive plots → Consider backtesting.py
- If we scale to 50+ assets → Consider VectorBT
- If we add live trading → Consider Backtrader
- If we focus on portfolios → Consider bt

### Phase 4: Maintain Flexibility
- Keep our custom code modular
- Make it easy to migrate if needed
- Document our design decisions
- Add tests for correctness

## Conclusion

**Current verdict: Stay custom, enhance gradually.**

Our implementation is:
- ✅ Simple and works
- ✅ Fast enough
- ✅ Easy to understand
- ✅ Zero dependencies
- ✅ Validated across 33 years

Migration to a library would add:
- ⚠️ 1-3 days of work
- ⚠️ New dependencies
- ⚠️ Learning curve
- ⚠️ Less control

**Better approach:**
- Enhance our custom implementation with better interfaces
- Add optimization and visualization ourselves
- Keep the option to migrate later if needs change
- Document this decision for future reference

We have a working, validated backtesting system. **Don't overcomplicate it until we need to.**
