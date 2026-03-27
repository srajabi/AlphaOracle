# Profitability Improvement Ideas

**Goal:** Increase returns across the 6 paper trading accounts through better strategies, new alpha sources, and optimized execution.

**Created:** 2026-03-20
**Status:** Research & Planning

---

## Current Performance Analysis

### Backtest Results (33 years, SPY)
- **Buy & Hold:** 26.6x total return, 10.5% annual, Sharpe 0.57
- **Our Strategies:** 3.6x total return, 4.7% annual, Sharpe 0.43
- **Problem:** Active strategies underperforming passive by ~6% annually
- **Root Cause:**
  - Too defensive (lower volatility but worse returns)
  - High trading frequency (~24 trades/year)
  - Transaction costs eating returns (5 bps per trade)

### Current Account Performance
Need to track forward performance for 3-6 months to validate:
- Dev: Advanced LLM (2x daily)
- PROD_1: Standard LLM (EOD)
- PROD_2: TQQQ Momentum (EOD)
- PROD_3: Dual Momentum (EOD)
- PROD_4: Sector Rotation (EOD)
- PROD_5: Mean Reversion (EOD)

---

## Improvement Ideas

### 1. Quick Wins (Implement This Week)

#### A. Add Stop Losses
**Rationale:** Reduce max drawdown, protect capital
**Implementation:** Use existing `backtesting/backtest_stop_losses.py`
**Test:** 5%, 8%, 10%, 15% trailing stops
**Expected Impact:** -20% to -30% max drawdown

```python
# Add to execute_advanced_llm.py and execute_trades.py
# Check if position down >X% from entry, exit immediately
if position_return < -0.08:  # 8% stop loss
    close_position(symbol)
```

#### B. Reduce Trading Frequency
**Current:** ~24 trades/year (792 trades / 33 years)
**Proposed:** Monthly rebalancing max
**Expected Impact:** -50% transaction costs, +1-2% annual return

#### C. Position Sizing by Confidence
**Current:** Equal weight or fixed allocations
**Proposed:** Scale by:
- Options flow confirmation (2x size)
- Multiple LLM consensus (1.5x size)
- Technical + fundamental alignment (1.5x size)
- Max multiplier: 3x normal size

---

### 2. Polymarket <> Stock Market Arbitrage ⭐

**Concept:** Exploit divergences between prediction market probabilities and stock market implied probabilities.

#### Examples

**A. Direct Price Predictions**
```
Polymarket: "Will NVDA close above $200 by Friday?" → 65%
Stock Market: NVDA at $195 (needs +2.6%)
Historical: NVDA moves >2.6% in a week 40% of the time

→ If momentum + options flow suggest >65% probability, BUY NVDA
→ If <65%, potentially SELL or stay out
```

**B. Macro Events → Sector Rotation**
```
Election Probabilities:
- Trump up → Long: XLE (Energy), XLF (Financials), Aerospace
- Specific candidate up → Long: Clean Energy, TSLA, Tech

Fed Rate Decisions:
- Polymarket: 80% chance of rate cut
- TLT not reflecting → Arb opportunity in bonds/rate-sensitive
```

**C. Earnings Predictions**
```
Polymarket: "Will TSLA beat earnings?" → 45%
Options Market: IV suggests 55% chance of big move
Historical: TSLA beats 60% of time

→ Divergence signals opportunity
```

#### Implementation Plan

**Phase 1: Data Collection (Week 1)**
```python
# Create: src/polymarket_ingestion.py

import requests

def fetch_polymarket_markets():
    """Fetch active markets from Polymarket API"""
    url = "https://gamma-api.polymarket.com/markets"
    response = requests.get(url)

    # Filter for stock/market-related predictions
    relevant_markets = filter_markets(response.json())

    # Store in data/polymarket_context.json
    save_markets(relevant_markets)

def filter_markets(markets):
    """Focus on: stock prices, Fed decisions, elections, earnings"""
    keywords = ['stock', 'nvda', 'tsla', 'spy', 'fed', 'rate',
                'election', 'earnings', 'close above', 'close below']
    return [m for m in markets if any(k in m['question'].lower() for k in keywords)]
```

**Phase 2: Divergence Detection (Week 2)**
```python
# Create: src/polymarket_arbitrage_signals.py

def calculate_divergence(polymarket_prob, ticker, target_price, timeframe):
    """
    Compare Polymarket probability to historical/implied probability
    """
    # Get historical probability of move
    hist_prob = calculate_historical_probability(ticker, target_price, timeframe)

    # Get implied probability from options
    options_prob = calculate_options_implied_prob(ticker, target_price, timeframe)

    # Calculate divergence
    divergence = polymarket_prob - avg(hist_prob, options_prob)

    if abs(divergence) > 0.15:  # >15% divergence
        return {
            'signal': 'BUY' if divergence < 0 else 'SELL',
            'edge': abs(divergence),
            'confidence': calculate_confidence(hist_prob, options_prob)
        }
```

**Phase 3: Paper Trading (Month 1)**
- Generate signals daily
- Track performance without real execution
- Validate edge exists before going live

**Phase 4: Live Trading (Month 2+)**
- If paper trading shows >55% win rate + positive expectancy
- Allocate 10-20% of one account to Polymarket arb
- Max 10% per trade, 24-48 hour holds

#### Risk Management
- Max 20% of single account allocated
- Max 10% per individual trade
- 24-48 hour max hold (these are short-term bets)
- Stop loss if market moves against thesis by >X%
- Track win rate, require >55% to continue

#### Data Sources
- Polymarket API: `https://gamma-api.polymarket.com/`
- Historical probabilities: Our existing data
- Options implied vol: Already collecting via yfinance

---

### 3. Options-Informed Equity Trading

**We already collect options data!** Use it more intelligently.

#### A. Unusual Activity Detection
```python
# Add to src/options_ingestion.py

def detect_unusual_options_activity(ticker):
    """
    Flag unusual options activity as signal
    """
    # Put/Call ratio spike (>2 stdev from normal)
    # Large volume on specific strike
    # Unusual OI buildup
    # Deep OTM calls by institutions (smart money)

    if unusual_activity_detected:
        return {
            'signal': 'BUY' or 'SELL',
            'rationale': 'Institutions loading up on Jan $250 calls',
            'confidence': 'HIGH'
        }
```

#### B. Implied Vol vs Realized Vol Arbitrage
```python
# If IV >> RV: Sell premium (or avoid long positions)
# If IV << RV: Buy straddles (or increase equity position size)

def compare_iv_rv(ticker):
    iv = get_implied_volatility(ticker)
    rv = calculate_realized_volatility(ticker, window=30)

    if iv > rv * 1.5:
        return 'OVERPRICED_VOLATILITY'  # Be cautious
    elif iv < rv * 0.7:
        return 'UNDERPRICED_VOLATILITY'  # Opportunity
```

#### C. Dark Pool Prints
```python
# Large institutional trades often precede moves
# Can detect via unusual volume + price stability

def detect_dark_pool_activity(ticker):
    # Volume spike without price movement = dark pool
    # Usually precedes directional move within 1-5 days
    pass
```

---

### 4. Intraday Mean Reversion (0DTE Options)

**We have intraday 5-min data!** Exploit it.

#### Strategy: Trade SPY/QQQ 0DTE options on:

**A. Morning Gap Reversals**
```
9:30 AM: Market gaps up >1%
9:45 AM: Check if holding gap or fading
If fading + volume declining → BUY puts (gap will fill)
If holding + volume increasing → BUY calls (trend continues)

Win rate: 60-70% historically
Hold time: 30 min to 2 hours max
```

**B. VWAP Bounces**
```
Price touches VWAP from above/below
Combined with:
- RSI oversold/overbought
- Volume spike
- Support/resistance level

→ Mean reversion play (0DTE options for max leverage)
```

**C. 2+ Sigma Moves**
```
When intraday move >2 standard deviations:
- Usually reverts within same day
- Can use 0DTE options for asymmetric payoff
- Stop loss if move accelerates (trend, not noise)
```

#### Risk Management for 0DTE
- Max 5% of account per trade
- Stop loss at -50% (options can go to zero fast)
- Max 3 trades per day
- Only trade first/last 2 hours (most liquidity)

---

### 5. Intermarket Divergence Trading

**We track 7 markets!** Exploit correlation breaks.

#### Signals

**A. Gold + Dollar Both Up**
```
Normal: Inverse correlation (DXY up → GLD down)
When both up: Major fear/uncertainty
→ SELL equities, BUY defensive (XLU, TLT)
```

**B. VIX Down + Market Down**
```
Normal: VIX spikes when market drops
When VIX low + market dropping: Capitulation phase
→ BUY signal (fear has been wrung out)
```

**C. All 7 Markets Same Direction**
```
Extremely rare (happens during regime changes)
All up → Bubble/euphoria → Reduce exposure
All down → Panic → Max buying opportunity
```

**D. Oil vs Energy Stocks Divergence**
```
XLE tracks crude oil closely
When divergence >10%:
→ Oil up, XLE flat → BUY XLE (will catch up)
→ Oil flat, XLE up → SELL XLE (will correct)
```

---

### 6. Leverage Optimization

#### A. Dynamic Leverage Based on Regime
```python
# Current: Fixed allocations
# Proposed: Adjust based on market regime

if regime == 'BULL_STABLE':
    leverage = 2.0  # Use UPRO, SSO
elif regime == 'BULL_VOLATILE':
    leverage = 1.5  # Mix 2x + 1x
elif regime == 'SIDEWAYS':
    leverage = 1.0  # No leverage
elif regime == 'BEAR':
    leverage = 0.5  # Defensive (50% cash, 50% TLT/GLD)
```

#### B. UPRO/TMF Rotation
```python
# For Account 3 (Dual Momentum):
# Instead of QQQ/TLT, use 3x versions

def enhanced_dual_momentum():
    spy_momentum = calculate_momentum('SPY', window=6)
    tlt_momentum = calculate_momentum('TLT', window=6)

    if spy_momentum > tlt_momentum and spy_momentum > 0:
        return {'UPRO': 1.0}  # 3x SPY
    elif tlt_momentum > 0:
        return {'TMF': 1.0}   # 3x TLT
    else:
        return {'CASH': 1.0}  # Both negative
```

#### C. Kelly Criterion Position Sizing
```python
# Optimal position size based on edge
# Kelly = (W * R - L) / R
# W = win rate, R = avg_win/avg_loss, L = loss rate

def calculate_kelly_size(strategy_stats):
    W = strategy_stats['win_rate']
    avg_win = strategy_stats['avg_win_pct']
    avg_loss = abs(strategy_stats['avg_loss_pct'])
    R = avg_win / avg_loss

    kelly_fraction = (W * R - (1 - W)) / R

    # Use half-kelly for safety (full kelly too aggressive)
    return max(0, min(kelly_fraction * 0.5, 0.25))  # Cap at 25%
```

---

### 7. LLM Strategy Improvements

#### A. Multi-Timeframe Analysis
```python
# Current: Daily only
# Add: Weekly trend + Hourly timing

def multi_timeframe_signal(ticker):
    weekly_trend = analyze_trend(ticker, '1wk')
    daily_setup = analyze_setup(ticker, '1d')
    hourly_entry = find_entry(ticker, '1h')

    # Only trade when all align
    if weekly_trend == 'BULLISH' and \
       daily_setup == 'BULLISH' and \
       hourly_entry == 'BULLISH':
        return {'signal': 'BUY', 'confidence': 'HIGH'}
```

#### B. Ensemble with Weighted Voting
```python
# Track which LLM is most accurate
# Weight votes accordingly

llm_weights = {
    'deepseek': 0.25,  # Best on technical
    'gemini': 0.20,    # Good all-around
    'claude': 0.20,    # Best on risk
    'gpt-4': 0.20,     # Good on macro
    'glm-5': 0.15      # Experimental
}

def weighted_ensemble_decision(llm_signals):
    buy_score = sum(weights[llm] for llm, signal in llm_signals.items()
                    if signal == 'BUY')

    if buy_score > 0.6:  # 60% weighted consensus
        return 'BUY'
    elif buy_score < 0.3:
        return 'SELL'
    else:
        return 'HOLD'
```

#### C. Learn from Mistakes
```python
# Track accuracy per LLM per ticker
# Adjust weights dynamically

def update_llm_weights(trade_result):
    """After each trade closes, update accuracy tracking"""
    for llm in trade_result['llm_votes']:
        if trade_result['profitable']:
            llm_accuracy[llm] += 1
        llm_total_calls[llm] += 1

    # Recompute weights quarterly
    recompute_weights_if_needed()
```

---

## Implementation Priority

### Immediate (This Week)
1. ✅ Document all ideas (this file)
2. ⬜ Implement stop losses on live strategies
3. ⬜ Reduce trading frequency to monthly

### Near Term (This Month)
1. ⬜ Build Polymarket data ingestion
2. ⬜ Create divergence detection script
3. ⬜ Start 30-day paper trading of Polymarket signals

### Medium Term (3 Months)
1. ⬜ Add options flow signals to LLM strategy
2. ⬜ Implement Kelly criterion sizing
3. ⬜ Launch Polymarket arb if edge validates
4. ⬜ Test 0DTE intraday strategies (separate small account)

### Long Term (6+ Months)
1. ⬜ Full intermarket arbitrage framework
2. ⬜ Dynamic leverage based on regime
3. ⬜ Multi-timeframe LLM analysis
4. ⬜ Automated learning from mistakes

---

## Success Metrics

**Track these for each improvement:**

1. **Win Rate:** Target >55% (currently ~54%)
2. **Sharpe Ratio:** Target >1.0 (currently 0.43)
3. **Max Drawdown:** Target <30% (currently 46%)
4. **Annual Return:** Target >15% (currently 4.7%)
5. **Profit Factor:** Target >1.5 (Avg Win / Avg Loss)

**Goal:** Beat SPY buy & hold (10.5% annual) on risk-adjusted basis

---

## Resources Needed

### For Polymarket Integration
- Polymarket API access (free)
- Options data for implied probability (✅ have it)
- Historical probability calculator (can build)
- ~1 week development time

### For 0DTE Trading
- Intraday 5-min data (✅ have it)
- Options pricing/Greeks calculator
- Fast execution (Alpaca supports)
- ~2 weeks development + testing

### For All Improvements
- 3-6 months forward testing to validate
- Dedicated tracking of each strategy performance
- Quarterly review and weight adjustment

---

## Notes

- All strategies tested on paper trading first (6 Alpaca accounts available)
- No real money until validated edge
- Conservative position sizing initially
- Scale up only after proven profitability
- Focus on risk-adjusted returns, not just raw returns
