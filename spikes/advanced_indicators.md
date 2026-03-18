# Advanced Indicators & Signal Generation

## Philosophy

Markets are driven by:
1. **Quantitative signals** - Price, volume, technical patterns
2. **Narrative/qualitative signals** - Geopolitics, policy, sentiment
3. **Cross-asset relationships** - Intermarket dynamics
4. **Behavioral patterns** - Fear, greed, positioning

The best systems combine all four. LLMs excel at processing narrative data that traditional quant systems miss.

---

## 1. Geopolitical Risk Indicators

### Why This Matters
Events like Strait of Hormuz tensions, China-Taiwan escalation, or Russia-Ukraine conflicts have predictable market impacts. An LLM can monitor news, assess severity, and suggest positioning.

### Specific Indicators

**Strait of Hormuz / Middle East Tensions**
- Monitor: Oil shipping disruption risk, Iran-Israel tensions, Saudi production
- Signals:
  - ↑ Tensions → Long XLE (energy), Long GLD (safe haven), Short XLF (risk-off)
  - ↓ Tensions → Short energy, Long growth tech

**China-Taiwan / Semiconductor Supply Chain**
- Monitor: Military exercises, export controls, diplomatic tensions
- Signals:
  - ↑ Risk → Short TSM, Long domestic semis (INTC), Long defense
  - Trade war escalation → Short AAPL/NVDA (China exposure)

**Russia-Ukraine / Commodities**
- Monitor: Grain exports, natural gas flows, sanctions
- Signals: Disruption → Long grains, energy, fertilizer stocks

**General Geopolitical Stress**
- Monitor: NATO activity, nuclear threats, cyber attacks
- Signals: Flight to safety → Long TLT, GLD, defensive sectors (XLU, XLP)

### Implementation
- LLM reads daily geopolitical news
- Assigns severity score (1-10)
- Maps events to affected sectors/tickers
- Suggests hedges or positioning changes
- Tracks "geopolitical regime" (calm, elevated, crisis)

---

## 2. Sentiment Indicators

### News Sentiment Analysis
**What to track:**
- Earnings call tone (confident vs defensive)
- Analyst language (enthusiastic vs cautious)
- Fed speaker tone (hawkish vs dovish)
- Media narrative shift (bullish → bearish or vice versa)

**How LLMs help:**
- Parse earnings transcripts for management confidence
- Detect shift in analyst consensus (cautious → bullish is actionable)
- Identify "narrative regime change" (e.g., "AI is dead" → "AI is back")

**Example Signals:**
- If 5+ major analysts upgrade a stock in 1 week → momentum signal
- If CEO language shifts from "growth" to "cost control" → bearish
- If Fed minutes show unexpected dovish pivot → long duration, tech

### Social Sentiment (Reddit/Twitter)
**What to track:**
- r/wallstreetbets mentions and sentiment
- Crypto Twitter sentiment as risk appetite gauge
- Sudden surge in ticker mentions (possible pump/momentum)

**Contrarian Use:**
- Extreme bullishness on WSB → possible top signal
- Extreme fear in crypto Twitter → possible bottom

### Insider Activity
**What to track:**
- Cluster of insider buying (bullish)
- Insider selling spike (bearish, unless routine)
- Unusual insider activity (CEOs buying in droves)

---

## 3. Cross-Asset Indicators

### Bitcoin as Risk Appetite Gauge
**Why:** Bitcoin trades like a leveraged tech stock with 24/7 liquidity
- BTC +10% → Risk-on, favor QQQ over SPY
- BTC -20% → Risk-off, raise cash or go defensive
- BTC correlation breakdown → regime change

### Credit Spreads
**Why:** High-yield spreads widen before equity crashes
- HYG (high yield) vs LQD (investment grade) spread widening → risk-off
- Junk bond selloff → expect equity weakness soon

### Emerging Market Flows
**Why:** EM outflows signal global risk aversion
- EEM (emerging markets) weak vs SPY → flight to safety
- EM currencies weak vs dollar → dollar strength, risk-off

### Commodities Divergence
**What to watch:**
- Copper (economic bellwether) vs gold (safe haven)
- Copper ↓ + Gold ↑ → stagflation fear
- Oil spike without copper → supply shock, not demand

---

## 4. Technical Pattern Recognition (LLM-Enhanced)

### Chart Patterns
Instead of rigid algorithmic pattern detection, use LLM to identify:
- "Tight consolidation after uptrend" (bullish continuation)
- "Failed breakout with volume decline" (bull trap)
- "Higher lows + declining volume" (coiling spring)

### Price Action Context
LLMs can describe nuance:
- "Price testing 200 SMA for 3rd time in 2 weeks - support strengthening"
- "Breakdown below support, but VIX not spiking - likely false breakdown"
- "New 52-week high on declining volume - bearish divergence"

### Multi-Timeframe Analysis
- Daily: Trend direction
- Weekly: Major support/resistance
- Monthly: Long-term context
- Intraday: Entry timing

LLM can synthesize: "Daily uptrend intact, but weekly resistance overhead at $150. Wait for weekly breakout before adding."

---

## 5. Market Structure & Breadth

### Advance/Decline Line
- SPY making new highs but A/D line declining → divergence, weakness
- Broad participation (many stocks rising) → healthy rally
- Narrow leadership (only 5-10 stocks up) → fragile

### New Highs / New Lows
- New highs expanding → momentum
- New lows expanding → deteriorating breadth

### Sector Rotation Signals
**What LLM can detect:**
- "Tech weak, energy strong, dollar strong → stagflation positioning"
- "Defensive sectors leading (XLU, XLP) while SPY flat → hidden weakness"
- "Small caps outperforming large caps → risk-on, rotation to value"

### Options Flow (Future)
- Unusual call buying → bullish positioning
- Large put buying → hedging or bearish bet
- Skew changes → tail risk perception

---

## 6. Macro Event Tracking

### Fed Policy Regime
**Track:**
- Hiking cycle vs cutting cycle vs pause
- QT (quantitative tightening) vs QE
- Forward guidance changes

**Signals:**
- First rate cut after hiking cycle → duration rally (TLT up, growth stocks up)
- Hawkish surprise → short duration, favor value over growth

### Economic Data Surprises
**Track:**
- CPI surprise (higher = bearish, lower = bullish)
- Unemployment surprise (higher = recession fear, lower = resilient economy)
- Retail sales, housing starts, PMIs

**LLM advantage:**
- Can read full report context, not just headline number
- "CPI rose 0.3% but due to shelter lag, core goods deflation continuing" → nuanced read

### Earnings Season Patterns
- % of companies beating estimates
- Guidance revisions (are companies raising or lowering?)
- Sector-specific trends (tech guidance improving while retail weakening)

---

## 7. Behavioral Finance & Positioning

### Fear/Greed Indicators
- VIX levels (fear gauge)
- Put/call ratio (extreme puts = fear, extreme calls = complacency)
- AAII sentiment survey (extreme bullishness = contrarian bearish)

### Contrarian Signals
**When to fade the crowd:**
- Magazine covers ("Is this the end of stocks?") → buy signal
- Everyone bearish → time to get bullish
- Everyone bullish → time to get cautious

**LLM can detect:**
- Narrative exhaustion ("10th article this week on AI bubble" → maybe it's not)
- Shift from skepticism to acceptance (bullish)
- Shift from euphoria to doubt (bearish)

### Fund Flows
- Retail inflows at tops, outflows at bottoms
- Institutional buying quietly (no headlines) = bullish
- Hedge fund positioning (via 13F filings, quarterly)

---

## 8. Supply Chain & Real Economy

### Shipping & Logistics
- Baltic Dry Index (bulk shipping demand)
- Container rates (China → US)
- Port congestion

**Signals:**
- Shipping costs rising → demand strong, possible inflation
- Shipping costs falling → demand weakening, deflationary

### Manufacturing PMIs
- Above 50 = expansion, below 50 = contraction
- Regional Fed surveys (Empire, Philly, ISM)

### Employment Trends
- Job postings (leading indicator)
- Layoff announcements (leading indicator of recession)
- Wage growth (inflation pressure)

---

## 9. Specific Event-Driven Signals

### Earnings Events
- Pre-earnings run-up (momentum)
- Post-earnings gap (surprise)
- Guidance revision impact

### M&A Activity
- Acquisition rumors → buy target, sometimes short acquirer
- Sector consolidation → industry maturation

### Product Launches
- Apple product cycles
- Pharma drug approvals
- Tech platform shifts (AI model releases)

---

## 10. LLM-Specific Advantages

### Narrative Synthesis
**What LLMs can do that quant systems can't:**
1. Read 50 articles and synthesize: "Consensus shifting from hard landing to soft landing"
2. Detect subtle tone changes: "Fed is less confident than they sound"
3. Connect disparate signals: "China stimulus + copper rally + EM strength = risk-on"
4. Contextualize data: "Jobs report missed, but this is expected in Fed pivot phase"

### Multi-Factor Integration
Instead of rigid rules, LLM can weigh factors contextually:
- "VIX is high (bearish) BUT put/call ratio extreme (contrarian bullish) → net neutral"
- "Breadth weak (bearish) BUT new sector leaders emerging (bullish) → consolidation, not crash"

### Regime Detection
LLM can identify market regime changes:
- Bull Quiet → Bull Volatile (take profits, raise stops)
- Bear Volatile → Transitional (watch for bottoming signals)
- Chop → Trending (shift from mean reversion to momentum strategies)

---

## Implementation Plan

### Phase 1: Foundational Indicators (Done)
- [x] Intermarket indicators (SPY, VIX, TLT, UUP, GLD, etc.)
- [x] Basic technical indicators per ticker
- [x] Market regime classification

### Phase 2: News & Sentiment (Next)
- [ ] Daily geopolitical event tracking
- [ ] News sentiment analysis per ticker
- [ ] Macro event calendar with LLM commentary
- [ ] Fed/policy tone analysis

### Phase 3: Cross-Asset Signals
- [ ] Bitcoin correlation tracking
- [ ] Credit spread monitoring
- [ ] Commodity divergence signals
- [ ] Currency pair signals

### Phase 4: Market Structure
- [ ] Breadth indicators (A/D line, new highs/lows)
- [ ] Sector rotation detector
- [ ] Leadership changes
- [ ] Volume profile analysis

### Phase 5: Behavioral Signals
- [ ] Extreme sentiment detection (contrarian)
- [ ] Positioning indicators
- [ ] Narrative shift detection
- [ ] Fund flow tracking

### Phase 6: Advanced Analytics
- [ ] Options flow (unusual activity)
- [ ] Insider activity clustering
- [ ] Short interest spikes
- [ ] 13F positioning (quarterly)

---

## Data Sources Needed

**Current:**
- ✅ Yahoo Finance (prices, basic news)
- ✅ Alpaca (portfolio, trades)

**To Add:**
- [ ] RSS feeds (geopolitical news, macro)
- [ ] Reddit API (sentiment)
- [ ] Twitter/X API (sentiment)
- [ ] FRED API (economic data)
- [ ] Quandl (alternative data)
- [ ] SEC EDGAR (insider trades, 13Fs)
- [ ] Options data provider (Tradier, Polygon.io)

---

## Example LLM Prompt Enhancement

### Before (Simple):
"Analyze SPY. Is it bullish or bearish?"

### After (Multi-Factor):
"Analyze SPY considering:
1. Geopolitical: Strait of Hormuz tensions elevated, Iran-Israel risk
2. Technical: At 200 SMA support, but breadth deteriorating
3. Intermarket: VIX spiking, TLT rallying (flight to safety)
4. Sentiment: Extreme fear (AAII survey 20% bulls)
5. Macro: Fed meeting tomorrow, CPI beat expectations

Given these factors, is this a buy-the-dip opportunity or start of correction?"

**LLM can weigh:**
- Geopolitical risk (bearish)
- Technical support (bullish)
- Flight to safety signals (bearish)
- Extreme fear (contrarian bullish)
- Fed uncertainty (neutral/bearish)

**Synthesis:** "Mixed signals. Extreme fear + technical support suggest short-term bounce possible, but geopolitical risk + flight to safety → keep position small, tight stops. Wait for Fed clarity."

---

## Success Metrics

**Good indicator:**
- Actionable (tells you what to do)
- Timely (signal before the move)
- Historically predictive (backtest shows edge)
- Non-redundant (adds info beyond other indicators)

**Test indicators by:**
- Backtesting predictive power
- Tracking in real-time (paper trading)
- Comparing to benchmark (SPY)
- Measuring false positive rate

---

## Next Steps

1. **Spike: News Ingestion Architecture** - Design system to ingest, parse, and analyze news from multiple sources
2. **Spike: Geopolitical Event Taxonomy** - Define specific events to track and their market implications
3. **Spike: Sentiment Scoring System** - LLM-based sentiment analysis for news, earnings calls, social media
4. **Spike: Cross-Asset Signal Dashboard** - Visualization of BTC, credit spreads, commodities, currencies

The goal: Build a system where LLMs process qualitative/narrative data and combine it with quantitative signals for better decision-making than either alone.
