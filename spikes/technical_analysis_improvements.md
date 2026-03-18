# Spike: Technical Analysis Improvements

**Objective:** Improve the quality of the technical-analysis input used by the pipeline so the system stops treating raw indicators as if they were sufficient signals. The goal is to move from "indicator dump" to "ranked, contextualized setup engine".

## Current Problem
Right now the system gives the LLM a limited snapshot:

* 20/50/200 SMAs
* RSI
* MACD
* Bollinger Bands
* A simple market regime label

That is enough for basic commentary, but not enough for robust trade selection. The current setup has several weaknesses:

* It does not distinguish between **trend-following**, **mean-reversion**, and **breakout** regimes at the ticker level.
* It does not score setup quality, so the LLM is forced to improvise ranking logic.
* It lacks **relative strength** vs. benchmark and sector.
* It largely ignores **volume structure**, which is critical for breakout confirmation.
* It uses mostly a single-timeframe interpretation of signals.
* It provides indicator values, but not enough derived features that explain **why a setup matters now**.

## Improvement Themes

### 1. Add Derived Signals, Not Just Raw Indicators
Raw indicator values are low-level features. The LLM will do better if Python derives higher-level states first.

Examples:

* `price_above_sma_20`, `price_above_sma_50`, `price_above_sma_200`
* `sma_20_above_sma_50`, `sma_50_above_sma_200`
* `distance_from_sma_20_pct`, `distance_from_sma_50_pct`, `distance_from_sma_200_pct`
* `rsi_state`: oversold, weak, neutral, strong, overbought
* `macd_state`: bullish_cross, bearish_cross, positive_rising, negative_falling
* `band_position`: below_lower, near_lower, mid_band, near_upper, above_upper

This gives the model explicit market structure instead of just numbers.

### 2. Add Multi-Timeframe Context
Many bad signals come from looking only at one daily snapshot. A stock can be oversold on the daily chart but still in a strong weekly uptrend, or vice versa.

Ideas:

* Daily trend state
* Weekly trend state
* Daily momentum vs. weekly momentum
* Whether the daily move is aligned with the weekly trend

Useful examples:

* `weekly_trend = up`, `daily_pullback = true`
* `weekly_trend = down`, `daily_bounce = low_quality`
* `daily_breakout_attempt = true`, `weekly_resistance_nearby = true`

This would materially improve distinction between:

* healthy pullbacks in strong trends
* dead-cat bounces in downtrends
* breakouts that are running into higher-timeframe resistance

### 3. Add Relative Strength Measures
Absolute price action is not enough. A stock that is flat while the index is down hard can be strong. A stock rising slower than its sector can still be weak.

Add:

* Relative strength vs. `SPY`
* Relative strength vs. sector ETF where applicable
* 1-month, 3-month, and 6-month performance ranking
* Distance from 52-week high
* Percentile rank inside the current watchlist

Derived outputs:

* `rs_vs_spy_20d`
* `rs_vs_sector_20d`
* `near_52w_high`
* `watchlist_momentum_rank`

This helps the system prioritize leadership instead of simply buying anything oversold.

### 4. Add Volume and Participation Signals
Breakouts and reversals without volume confirmation are usually lower quality. The current pipeline mostly ignores this.

Add:

* Volume vs. 20-day average volume
* Up-volume vs. down-volume balance over recent sessions
* Breakout day volume expansion
* Distribution day count over the last 20 sessions
* Accumulation vs. distribution heuristics

Examples of useful states:

* `breakout_confirmed_by_volume`
* `bounce_on_light_volume`
* `recent_distribution_pressure`
* `accumulation_improving`

This is especially important for ranking swing-trade candidates.

### 5. Split Technical Setups Into Named Buckets
The system should classify each ticker into one or more setup families before the LLM sees it.

Suggested setup buckets:

* Trend continuation
* Pullback in uptrend
* Oversold mean reversion
* Volatility contraction / squeeze
* Base breakout
* Failed breakout
* Late-stage overbought extension
* Breakdown / avoid

For each ticker, Python can emit:

* primary setup type
* setup confidence
* invalidation level
* entry quality

That is much more actionable than asking the LLM to infer everything from RSI and MACD.

### 6. Add Volatility-Normalized Features
A 3% pullback means something different for a slow ETF vs. a volatile growth stock. Normalize moves by ATR or realized volatility.

Add:

* ATR as percent of price
* Distance from moving averages in ATR units
* Daily range expansion vs. trailing ATR
* Gap size vs. ATR

Useful derived outputs:

* `pullback_depth_atr`
* `breakout_size_atr`
* `stop_distance_atr`
* `volatility_bucket`

This would improve both signal quality and later position-sizing logic.

### 7. Add Support, Resistance, and Market Structure
The current setup is indicator-heavy and structure-light. That is a problem because many swing decisions are really about price structure.

Ideas:

* Recent swing highs and lows
* 20-day and 60-day breakout levels
* Base length
* Number of recent resistance tests
* Tightness of recent closes
* Whether price is reclaiming a key level or failing below it

Derived outputs:

* `at_20d_breakout_level`
* `base_length_days`
* `resistance_tests`
* `tight_closes`
* `support_reclaim`

This helps distinguish real setups from random oscillator moves.

### 8. Reduce LLM Burden With Setup Scoring
Instead of having the LLM rank all names itself, build a simple scoring model in Python.

Example score components:

* Trend score
* Momentum score
* Relative strength score
* Volume confirmation score
* Volatility quality score
* Regime fit score

Possible outputs:

* `technical_score_total`
* `technical_score_breakout`
* `technical_score_mean_reversion`
* `technical_score_trend`

The LLM can then focus on tradeoffs and thesis alignment rather than raw ranking.

## Candidate Indicators / Features To Add

### High priority
* ATR
* EMA 21
* 10-day and 20-day rate of change
* Relative strength vs. SPY
* Relative volume
* 52-week high proximity
* Donchian channel breakout levels

### Medium priority
* ADX for trend strength
* On-balance volume
* Chaikin money flow
* Keltner channels
* Stochastic RSI
* Anchored VWAP from recent swing points or year-to-date

### Lower priority
* Ichimoku
* Fibonacci retracements
* Exotic candlestick pattern detection

Those lower-priority ideas may add noise faster than they add signal.

## Recommended Output Shape
Instead of only returning a flat block of values per ticker, emit structured fields like:

```json
{
  "ticker": "NVDA",
  "trend": {
    "daily": "down",
    "weekly": "up",
    "adx": 24.1
  },
  "momentum": {
    "rsi_14": 41.2,
    "macd_state": "bearish_but_improving",
    "roc_20d": -6.3
  },
  "relative_strength": {
    "vs_spy_20d": -4.1,
    "vs_sector_20d": -2.3,
    "distance_from_52w_high_pct": -12.8
  },
  "volume": {
    "rel_volume": 1.4,
    "accumulation_state": "neutral"
  },
  "setup": {
    "primary": "pullback_in_uptrend",
    "confidence": 0.64,
    "entry_quality": "medium",
    "invalidation_level": 842.5
  },
  "scores": {
    "trend": 7,
    "momentum": 4,
    "relative_strength": 5,
    "total": 16
  }
}
```

This is a much better interface for both the LLM and the frontend.

## Practical Implementation Plan

### Phase 1: Immediate upgrade
Extend the current ingestion step with:

* ATR
* EMA 21
* Relative strength vs. SPY
* Relative volume
* Distance from 52-week high
* Derived state labels for RSI, MACD, moving averages, and Bollinger Bands

This is the highest ROI and should be done first.

### Phase 2: Setup engine
Add rule-based detection for:

* pullback in uptrend
* oversold bounce
* squeeze
* breakout
* failed breakout

Then score each setup and surface only the best candidates to the LLM.

### Phase 3: Multi-timeframe and structure
Add:

* weekly trend features
* support/resistance detection
* base quality
* sector-relative comparisons

This is where the engine starts becoming much more discriminating.

## Key Design Principle
The right direction is not "add every indicator". The right direction is:

1. derive market structure in Python
2. classify setup type explicitly
3. score quality before the LLM sees it
4. let the LLM reason about portfolio construction and macro fit

That division of labor is much more robust than treating the LLM as the primary technical-analysis engine.

## Recommendation
If only one improvement gets built next, it should be this:

* implement a **ticker-level setup classifier + scorecard**

That would likely improve trade quality more than adding three or four extra indicators with no ranking logic.
