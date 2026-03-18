# Intermarket Indicators for Regime Change Detection

**Date:** 2026-03-17
**Status:** Implemented and deployed

## Overview

Built a comprehensive intermarket analysis system that uses 7 uncorrelated markets to detect market regime changes. Each indicator is standalone, reusable, and displayable on ticker dashboards.

## Philosophy

**Build individual indicators first, combine into strategies later.**

Instead of jumping straight to a complex scoring system, we:
1. Create standalone indicator calculations
2. Make them display-ready for dashboards
3. Test them individually on current data
4. Eventually combine into trading strategies

This iterative approach provides immediate value (regime detection on dashboards) while building reusable components for future strategies.

## The 7 Markets

Based on intermarket analysis principles, we track:

1. **SPY** - US Equities (S&P 500)
2. **^VIX** - Volatility Index
3. **TLT** - Long-term Treasury Bonds (20+ year)
4. **UUP** - US Dollar Index
5. **GLD** - Gold
6. **SLV** - Silver
7. **XLE** - Energy Sector

These markets are largely uncorrelated, providing orthogonal signals that confirm regime changes.

## Individual Indicators

### 1. Risk Sentiment (SPY + VIX)

**Concept:** Combines equity trend with volatility level to gauge market risk appetite.

**Calculation:**
- SPY trend: Analyze 20/50/200 SMA positioning
- VIX level: Classify as low (<15), normal (15-20), elevated (20-30), high (>30)
- VIX trend: Rising vs falling vs neutral

**Signals:**
- **risk_on**: SPY uptrend + low/falling VIX
- **risk_off**: SPY downtrend + elevated/rising VIX
- **cautious**: Elevated VIX regardless of SPY
- **neutral**: Mixed signals

**Current Reading (2026-03-17):**
- Signal: **risk_off**
- SPY: downtrend (below all SMAs)
- VIX: 23.5 (elevated and rising)
- Interpretation: "Risk-off: Equities falling, volatility elevated and rising"

### 2. Dollar Strength (UUP)

**Concept:** Strong dollar typically negative for commodities (priced in USD) and international stocks.

**Calculation:**
- UUP trend: 20/50/200 SMA analysis
- UUP momentum: 20-day rate of change

**Signals:**
- **strong_dollar**: Strong uptrend + positive momentum
- **dollar_rising**: Uptrend or moderate momentum
- **weak_dollar**: Downtrend + negative momentum
- **neutral**: Stable

**Current Reading (2026-03-17):**
- Signal: **strong_dollar**
- UUP: $27.73 (strong uptrend)
- Momentum: +3.4% over 20 days
- Interpretation: "Dollar strengthening: Headwind for commodities and international assets"

### 3. Real Rates (TLT as Proxy)

**Concept:** TLT price inversely related to yields. Rising TLT = falling rates = good for growth stocks.

**Calculation:**
- TLT trend: 20/50/200 SMA analysis
- TLT momentum: 20-day rate of change

**Signals:**
- **falling_rates**: TLT strong uptrend + positive momentum
- **rates_declining**: TLT uptrend or moderate momentum
- **rising_rates**: TLT downtrend + negative momentum
- **stable_rates**: Neutral

**Current Reading (2026-03-17):**
- Signal: **rising_rates**
- TLT: $87.21 (downtrend)
- Momentum: -2.5% over 20 days
- Interpretation: "Rates rising: Headwind for growth stocks, favor value/financials"

### 4. Commodity Strength (GLD, SLV, XLE)

**Concept:** Different commodities signal different regimes. Gold = defensive, Energy/Silver = cyclical.

**Calculation:**
- Analyze trend and momentum for each commodity
- Count how many are in uptrend
- Determine if defensive (gold) or cyclical (energy/silver) leading

**Signals:**
- **commodities_strong_defensive**: Gold leading rally (inflation/risk-off)
- **commodities_strong_cyclical**: Energy/silver leading (risk-on/growth)
- **commodities_mixed**: Some up, some down
- **commodities_weak**: All in downtrend

**Current Reading (2026-03-17):**
- Signal: **commodities_strong_defensive**
- GLD: Uptrend (defensive bid)
- SLV: Strong positive momentum (+5%)
- XLE: Strong uptrend (+6.5% momentum)
- Interpretation: "Commodities rallying with gold leading: Possible inflation/risk-off signal"

### 5. Market Regime Detector

**Concept:** Combines all indicators to classify the current market regime.

**Regimes:**
- **Bull Quiet**: Risk-on + low VIX + rising equities
- **Bull Volatile**: Rising equities but elevated VIX
- **Bear Quiet**: Declining equities + rising bonds
- **Bear Volatile**: Risk-off + high VIX + flight to safety
- **Transitional**: Mixed signals, regime unclear

**Current Reading (2026-03-17):**
- Regime: **Bear Volatile**
- Confidence: **High**
- Components:
  - Risk: Risk-off
  - Dollar: Strong dollar
  - Rates: Rising rates
  - Commodities: Strong defensive
- Interpretation: "Bear Volatile regime. Risk: Risk Off | Dollar: Strong Dollar | Rates: Rising Rates | Commodities: Strong Defensive"

## Why This Approach Works

### 1. Uncorrelated Signals
Using 7 different asset classes provides confirmation. If only one signal triggers, it might be noise. If multiple uncorrelated signals align, it's likely a real regime change.

### 2. Less Crowded Trades
Single-asset technical indicators (RSI, MACD, Bollinger Bands) are widely used and saturated. Intermarket analysis using relationships between asset classes is less common among retail traders.

### 3. Reusable Components
Each indicator is a standalone function that returns structured data. This makes them:
- Easy to test individually
- Easy to display on dashboards
- Easy to combine into strategies later
- Easy to debug when something breaks

### 4. Display-Ready Format
All indicators return structured dictionaries with:
- `name`: Display name
- `signal`: Machine-readable signal
- `value`: Current value
- `interpretation`: Human-readable explanation
- `components`: Detailed breakdown
- `timestamp`: When calculated

This format is ready to be rendered on frontend dashboards without transformation.

## Implementation Details

### File Structure

```
src/indicators/
  intermarket.py       # All indicator classes

src/generate_indicators.py  # Daily generation script

data/indicators.json         # Backend reference
frontend/public/data/indicators.json  # Frontend display
```

### Class Hierarchy

```python
IndicatorBase
  ├─ load_price_data()      # Load ticker history
  ├─ calculate_trend()       # SMA analysis
  └─ calculate_momentum()    # Rate of change

RiskSentimentIndicator(IndicatorBase)
  └─ calculate() → Dict

DollarStrengthIndicator(IndicatorBase)
  └─ calculate() → Dict

RealRatesIndicator(IndicatorBase)
  └─ calculate() → Dict

CommodityStrengthIndicator(IndicatorBase)
  └─ calculate() → Dict

MarketRegimeDetector(IndicatorBase)
  └─ calculate() → Dict (includes all sub-indicators)
```

### Daily Workflow Integration

The indicator generation now runs daily as part of the analysis pipeline:

```yaml
# .github/workflows/daily_analysis.yml

- name: Run Data Ingestion
  run: python src/data_ingestion.py

- name: Generate Intermarket Indicators  # ← NEW
  run: python src/generate_indicators.py

- name: Run LLM Agents
  run: python src/llm_agents.py
```

This ensures:
1. Latest price data is downloaded first
2. Indicators are calculated from fresh data
3. LLMs can see current regime in their analysis
4. Frontend displays are up-to-date

## Example Output

```json
{
  "market_regime": {
    "name": "Market Regime",
    "regime": "Bear Volatile",
    "confidence": "high",
    "interpretation": "Bear Volatile regime. Risk: Risk Off | Dollar: Strong Dollar | Rates: Rising Rates | Commodities: Strong Defensive",
    "components": {
      "risk_sentiment": {...},
      "dollar_strength": {...},
      "real_rates": {...},
      "commodity_strength": {...}
    }
  },
  "indicators": {
    "risk_sentiment": {
      "name": "Risk Sentiment",
      "signal": "risk_off",
      "interpretation": "Risk-off: Equities falling, volatility elevated and rising",
      "components": {
        "spy_trend": "downtrend",
        "spy_price": 669.03,
        "vix_level": "elevated",
        "vix_value": 23.51,
        "vix_trend": "rising"
      }
    },
    "dollar_strength": {...},
    "real_rates": {...},
    "commodity_strength": {...}
  }
}
```

## Testing Results

Ran indicators on current market data (2026-03-17):

**Output:**
```
================================================================================
MARKET REGIME: Bear Volatile
Confidence: HIGH
Interpretation: Bear Volatile regime. Risk: Risk Off | Dollar: Strong Dollar | Rates: Rising Rates | Commodities: Strong Defensive
================================================================================

Individual Indicators:
  • Risk Sentiment: Risk Off
  • Dollar Strength: Strong Dollar
  • Real Rates: Rising Rates
  • Commodity Strength: Commodities Strong Defensive
```

**Validation:**
- All indicators calculated successfully
- Regime detection correctly identified current market stress
- Output format ready for frontend display
- Interpretations are clear and actionable

## Next Steps

### 1. Frontend Display (Immediate)
- Add indicators section to homepage
- Display regime badge on all pages
- Create indicator detail page showing historical trends
- Add tooltips explaining each indicator

### 2. Per-Ticker Indicators (Near-term)
Build similar indicators for individual tickers:
- Relative strength vs sector
- Trend strength (ADX-like)
- Volume confirmation
- Support/resistance levels
- Breakout/breakdown signals

### 3. Strategy Integration (Future)
Once we've validated indicator predictive power:
- Combine indicators into trading signals
- Backtest strategies using these indicators
- Paper trade indicator-based strategies
- Compare to existing rule-based strategies

### 4. Historical Analysis (Research)
- Calculate indicators historically (1993-2026)
- Identify regime transitions
- Measure indicator lead time before major moves
- Quantify false positive rates

## Advantages Over Original Reddit Strategy

The original Reddit gold trading strategy used 7 markets with a complex scoring system. Our approach improves on this:

**Better:**
- ✅ Individual indicators are testable and debuggable
- ✅ No premature optimization with ML or complex scoring
- ✅ Display-ready for immediate dashboard value
- ✅ Iterative development (build → test → display → combine)
- ✅ Regime detection helps all strategies, not just gold

**Similar:**
- Uses 7 uncorrelated markets
- Focuses on intermarket relationships
- Less saturated than single-asset technicals

**Trade-offs:**
- 🔄 No trading signals yet (indicators only)
- 🔄 Not optimized for any specific asset
- 🔄 Requires manual interpretation currently

## Key Insight

**"It's nice if we get indicators out of it."**

This approach prioritizes building reusable components over jumping straight to a complete strategy. By creating display-ready indicators first, we:
1. Get immediate value (regime detection on dashboards)
2. Build systematically (test each component individually)
3. Avoid premature optimization (no scoring systems yet)
4. Create a toolkit for future strategies

This is the right foundation for long-term development.

## References

- Reddit post: 7-market intermarket system for gold (user's inspiration)
- Classic intermarket analysis: John Murphy's "Intermarket Analysis"
- Implementation: `src/indicators/intermarket.py`
- Daily generation: `src/generate_indicators.py`
- Current state: Bear Volatile regime detected 2026-03-17
