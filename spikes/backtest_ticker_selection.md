# Spike: Backtesting Ticker Selection Strategy

**Objective:** Determine which tickers to use for backtesting different strategy types to maximize validation quality while avoiding overfitting.

## Current State

### Available Tickers
- **Total with long history**: 42 tickers
- **20+ years history**: 26 tickers (covers dot-com, GFC, all major regimes)
- **10+ years history**: 35 tickers (covers GFC forward)

### Current Default
```python
DEFAULT_TICKERS = ["QQQ", "VOO", "GLD", "TLT", "XLE", "XLU"]
```

**Coverage:**
- US Equity: QQQ (tech), VOO (broad market)
- Cyclical: XLE (energy)
- Defensive: GLD (gold), TLT (bonds), XLU (utilities)

## Key Principle: Match Universe to Strategy Type

Different strategies require different ticker universes. One size does NOT fit all.

### Strategy Type 1: Portfolio Rotation (e.g., dual_momentum_rotation)

**Requirements:**
- Liquid, tradeable ETFs (not individual stocks)
- Uncorrelated assets across different regimes
- Must include both offensive and defensive options
- Need 20+ years for regime testing

**Ideal characteristics:**
- Low expense ratios
- High daily volume (easy to trade)
- Clean, reliable price history
- Represent distinct asset classes

### Strategy Type 2: Single-Asset Trend Following

**Requirements:**
- Can test on individual stocks OR ETFs
- Need trending assets (avoid mean-reverting choppy stocks)
- Long history preferred but not critical

**Good candidates:**
- Strong secular trends: NVDA, TSLA, AAPL, MSFT
- Index ETFs: QQQ, VOO, VTI
- Sector ETFs that trend: XLE, XLF

### Strategy Type 3: Mean Reversion

**Requirements:**
- Need range-bound or cyclical assets
- Works better on individual stocks than indexes
- Higher volatility preferred (more reversion opportunities)

**Good candidates:**
- Cyclical semiconductors: AMD, MU, INTC
- Cyclical industrials: WDC, STX
- High-beta tech: TSLA, PLTR

### Strategy Type 4: Breakout Systems

**Requirements:**
- Need assets that can make sustained moves
- Works on both stocks and ETFs
- Prefer higher volatility

**Good candidates:**
- Growth stocks: NVDA, AMD, TSLA
- Momentum ETFs: QQQ
- Sector leaders during their cycles

## Proposed Ticker Universes

### Universe 1: Portfolio Rotation (Core Strategies)

**Purpose:** Validate `dual_momentum_rotation`, `top2_relative_strength_rotation`, `regime_defensive_rotation`

**Tickers:**
```python
ROTATION_CORE = [
    # Offensive (Risk-On)
    "VOO",   # S&P 500 - broad US equity (15.5 years)
    "QQQ",   # Nasdaq 100 - tech-heavy (27 years)
    "XLE",   # Energy sector (27.2 years)

    # Defensive (Risk-Off)
    "GLD",   # Gold (21.3 years)
    "TLT",   # Long-term Treasuries (23.6 years)
    "XLU",   # Utilities (27.2 years)
]
```

**Why these 6?**
- ✅ All have 15+ years (covers GFC, COVID, 2022 inflation bear)
- ✅ QQQ has 27 years (covers dot-com crash)
- ✅ Liquid, low-cost ETFs
- ✅ Proven uncorrelated during crisis periods
- ✅ Simple, robust, not overfit

**Regime coverage:**
- Dot-com bear: QQQ available
- GFC bear: All available
- COVID crash: All available
- 2022 inflation bear: All available
- AI bull 2023-2024: All available

**Recommendation:** **Keep this as default.** It's perfect.

---

### Universe 2: Portfolio Rotation (Extended)

**Purpose:** Test if additional defensive assets or international exposure improves Sharpe

**Tickers:**
```python
ROTATION_EXTENDED = [
    # Offensive
    "VOO",   # S&P 500
    "QQQ",   # Nasdaq 100
    "VTI",   # Total US market (24.7 years)
    "XLE",   # Energy
    "XLF",   # Financials (27.2 years)

    # Defensive
    "GLD",   # Gold
    "IAU",   # Gold alternate (21.1 years) - test if diversifying gold helps
    "TLT",   # Long bonds
    "XLU",   # Utilities

    # International (diversification)
    "VGK",   # Europe (21 years)
    "EWA",   # Australia (29.9 years)
]
```

**Why add these?**
- Test if multiple gold ETFs reduce tracking error
- Test if international adds diversification
- Test if more sector options improve rotation

**Hypothesis to test:**
- Does adding VTI improve over VOO?
- Does IAU + GLD beat GLD alone?
- Do international markets improve risk-adjusted returns?

**Recommendation:** Test this AFTER validating core universe. Don't optimize on it.

---

### Universe 3: Single-Asset Mega Caps

**Purpose:** Test trend following, momentum, breakout strategies on liquid large caps

**Tickers:**
```python
MEGA_CAPS = [
    # FAANG / Tech Leaders (20+ years)
    "AAPL",   # 45.3 years - consistent growth
    "MSFT",   # 40.0 years - consistent growth
    "AMZN",   # 28.8 years - high growth, volatile
    "GOOGL",  # 21.5 years - steady growth
    "NFLX",   # 23.8 years - cyclical growth, volatile

    # Semiconductors (20+ years)
    "NVDA",   # 27.1 years - explosive growth, volatile
    "AMD",    # 46.0 years - cyclical, mean-reverting
    "INTC",   # 46.0 years - mature, declining
    "TSM",    # 28.4 years - steady growth

    # Reference
    "QQQ",    # Benchmark
]
```

**Good for:**
- Testing SMA trend following (which mega-caps trend best?)
- Testing breakout strategies (NVDA, AMD have big moves)
- Testing mean reversion (AMD, INTC are cyclical)

**Not good for:**
- Portfolio rotation (individual stocks too volatile)

**Recommendation:** Use this universe for testing **single-asset strategies** only.

---

### Universe 4: Semiconductor Deep Dive

**Purpose:** Test sector-specific strategies on a homogeneous group

**Tickers:**
```python
SEMICONDUCTORS = [
    # Leaders with 20+ years
    "NVDA",   # 27.1 years - GPU leader, AI
    "AMD",    # 46.0 years - GPU competitor
    "INTC",   # 46.0 years - Foundry turnaround
    "MU",     # 41.8 years - Memory (HBM)
    "KLAC",   # 45.4 years - Equipment
    "TSM",    # 28.4 years - Foundry leader

    # Storage (related)
    "WDC",    # 47.4 years - Storage cycle
    "STX",    # 23.2 years - HDD/Data
]
```

**Why test this universe?**
- Semiconductors are **highly cyclical** (good for mean reversion testing)
- Strong **sector correlation** (test relative strength within sector)
- **Different sub-sectors**: GPU, CPU, memory, equipment, storage
- Can test: "Buy the laggard in semi cycle" strategies

**Good for:**
- Relative strength rotation within semiconductors
- Mean reversion on cyclical downturns
- Testing "buy the dip in semi" strategies

**Recommendation:** Use this for **sector-specific strategy research**, not core validation.

---

### Universe 5: High-Volatility Swing Trades

**Purpose:** Test aggressive momentum and breakout strategies on volatile assets

**Tickers:**
```python
HIGH_VOL = [
    # Individual stocks
    "TSLA",   # 15.7 years - extreme volatility
    "PLTR",   # 5.5 years - recent IPO, high vol
    "CRWD",   # 6.8 years - cybersecurity growth

    # 3x Leveraged ETFs (if we add them to watchlist)
    # "TQQQ",   # 3x QQQ
    # "SOXL",   # 3x semiconductors

    # Crypto proxy
    "IBIT",   # 2.2 years - Bitcoin ETF (too recent)

    # Benchmark
    "QQQ",
]
```

**Why test this universe?**
- High volatility = more trading opportunities
- Tests if strategies can handle extreme moves
- These are popular swing trading targets

**Limitations:**
- **Short history** for most (can't test across regimes)
- **Survivorship bias** (TSLA survived, many didn't)
- **High risk** - not suitable for core portfolio

**Recommendation:** Use for **swing trading strategy research** only. Not for core validation.

---

### Universe 6: Defensive & Income

**Purpose:** Test strategies focused on downside protection and yield

**Tickers:**
```python
DEFENSIVE = [
    # Bonds
    "TLT",    # 23.6 years - Long-term Treasuries

    # Dividend/Quality
    "SCHD",   # 14.4 years - Dividend growth
    "QUAL",   # 12.7 years - Quality factor

    # Defensive sectors
    "XLU",    # 27.2 years - Utilities

    # Gold
    "GLD",    # 21.3 years
    "IAU",    # 21.1 years

    # Benchmark
    "VOO",
]
```

**Why test this universe?**
- Test strategies that prioritize **capital preservation**
- Test **bear market performance**
- Validate **risk-off rotation** logic

**Good for:**
- Testing "flight to safety" strategies
- Validating defensive rotation timing
- Testing dividend/quality factor strategies

**Recommendation:** Use for **defensive strategy validation** after core strategies proven.

---

## Decision Framework

### For Each Strategy Type, Use This Universe:

| Strategy Type | Universe | Why |
|--------------|----------|-----|
| **Portfolio rotation** (dual_momentum, top2_RS) | **Universe 1: Core Rotation** ✅ | Liquid ETFs, 20+ years, uncorrelated |
| **Extended rotation research** | Universe 2: Extended | Test after core validated |
| **Single-asset trend following** | Universe 3: Mega Caps | Test on individual stocks |
| **Mean reversion** | Universe 3 or 4 | Cyclical assets needed |
| **Breakout systems** | Universe 3 or 5 | Need big moves |
| **Sector rotation** | Universe 4: Semiconductors | Homogeneous sector |
| **Swing trading research** | Universe 5: High Vol | Popular swing targets |
| **Defensive strategies** | Universe 6: Defensive | Capital preservation focus |

## Overfitting Risk Management

### Red Flags to Avoid:

1. **Testing too many tickers** - Don't test 42 tickers and pick the best performer
2. **Cherry-picking periods** - Don't only test during bull markets
3. **Multiple strategy tweaks** - Don't optimize parameters on the same dataset
4. **Universe mining** - Don't keep expanding universe until you find something that works

### Best Practices:

1. **Define universe BEFORE backtesting** - Based on strategy logic, not results
2. **Use out-of-sample validation** - Test on different time periods
3. **Test across all regimes** - Including periods where strategy should struggle
4. **Keep it simple** - Fewer tickers = more robust
5. **Document decisions** - Write down WHY you chose each ticker

## Recommended Testing Sequence

### Phase 1: Core Validation (CURRENT) ✅
```bash
python3 backtesting/run_backtests.py \
  --tickers QQQ,VOO,GLD,TLT,XLE,XLU \
  --market-periods dotcom_bear,gfc_bear,covid_crash,inflation_bear_2022,ai_bull_2023_2024
```

**Status:** ✅ DONE - `dual_momentum_rotation` validated

---

### Phase 2: Extended Rotation (Optional)
Test if adding more assets improves performance:

```bash
python3 backtesting/run_backtests.py \
  --tickers VOO,QQQ,VTI,XLE,XLF,GLD,IAU,TLT,XLU,VGK,EWA \
  --portfolio-strategies dual_momentum_rotation,top2_relative_strength_rotation \
  --market-periods gfc_bear,covid_crash,inflation_bear_2022,ai_bull_2023_2024
```

**Hypothesis:**
- Does VTI outperform VOO?
- Does IAU + GLD improve over GLD alone?
- Do international markets help during US bear markets?

**Expected result:** Probably marginal improvement at best. Core 6 likely optimal.

---

### Phase 3: Single-Asset Strategy Validation
Test which individual stocks work best with trend/momentum strategies:

```bash
python3 backtesting/run_backtests.py \
  --tickers AAPL,MSFT,AMZN,GOOGL,NVDA,AMD,QQQ \
  --strategies buy_and_hold,sma_trend_following,breakout_20d \
  --market-periods full_sample,gfc_bear,ai_bull_2023_2024
```

**Goal:** Identify which mega-caps are best for single-asset systematic trading

**Expected finding:** NVDA and AAPL likely best for trend following due to consistent uptrends

---

### Phase 4: Mean Reversion on Cyclicals
Test if mean reversion works better on cyclical semiconductors:

```bash
python3 backtesting/run_backtests.py \
  --tickers AMD,MU,INTC,WDC,STX \
  --strategies rsi_mean_reversion,buy_and_hold \
  --market-periods full_sample
```

**Goal:** Test if cyclical nature improves mean reversion strategy

**Expected finding:** Mean reversion probably still weak unless tuned for specific cycles

---

### Phase 5: Research-Only Experiments
Test exotic ideas that may not work but are worth exploring:

**Test A: Semiconductor sector rotation**
```bash
python3 backtesting/run_backtests.py \
  --tickers NVDA,AMD,INTC,MU,KLAC,TSM \
  --portfolio-strategies top2_relative_strength_rotation
```

**Test B: Defensive rotation during high VIX**
(Would need to add ^VIX conditional logic to strategies)

**Test C: International vs US rotation**
```bash
python3 backtesting/run_backtests.py \
  --tickers VOO,VTI,VT,VXUS,VGK,EWA,EWC \
  --portfolio-strategies dual_momentum_rotation
```

## Recommendation Summary

### For Production Deployment (Paper Trading):

**Use Universe 1: Core Rotation** ✅
```python
PRODUCTION_UNIVERSE = ["QQQ", "VOO", "GLD", "TLT", "XLE", "XLU"]
```

**Rationale:**
1. ✅ **Proven across 20+ years and all major regimes**
2. ✅ **Liquid, low-cost ETFs** (easy to trade)
3. ✅ **Simple, robust, not overfit**
4. ✅ **Covers offensive + defensive + cyclical**
5. ✅ **Uncorrelated during crises**

### For Research & Strategy Development:

**Start with Universe 1, then explore:**
- Universe 2 (extended rotation) - IF core strategies work
- Universe 3 (mega caps) - For single-asset strategies
- Universe 4 (semiconductors) - For sector-specific strategies
- Universe 5 (high vol) - For swing trading research
- Universe 6 (defensive) - For risk-off strategies

**But always validate new ideas on Universe 1 first.**

## Key Takeaway

**More tickers ≠ better validation**

The current default of 6 tickers is **optimal** for portfolio rotation strategies because:
- It's the minimum viable universe (offensive, defensive, cyclical)
- It has 20+ years of history for regime testing
- It avoids overfitting from too many choices
- It's actually tradeable in real money

**Keep Universe 1 as the default.** Only expand when testing specific hypotheses.

## Next Actions

1. ✅ **Keep current 6-ticker universe for production**
2. Document which universe to use for each strategy type
3. Run Phase 2-5 tests ONLY if/when we need to validate new strategy ideas
4. Never optimize strategy parameters on expanded universes

The goal is **robust validation**, not **optimized results**.
