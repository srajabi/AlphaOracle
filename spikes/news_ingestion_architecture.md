# News Ingestion Architecture

## Goal
Build a system to ingest, categorize, and analyze news from multiple sources to drive trading decisions. Focus on geopolitical events, macro developments, and sector-specific catalysts.

---

## News Categories

### 1. Geopolitical Events
**Why:** Events like Strait of Hormuz tensions drive predictable sector moves (energy up, risk assets down)

**Sources:**
- Reuters (geopolitical coverage)
- BBC News (international events)
- Al Jazeera (Middle East focus)
- Bloomberg (market implications of geopolitics)

**Keywords to track:**
- Strait of Hormuz, Taiwan Strait, South China Sea
- Russia-Ukraine, Israel-Iran, North Korea
- Oil embargo, sanctions, military exercises
- Trade war, tariffs, export controls

**Output:**
```json
{
  "event_type": "geopolitical_tension",
  "region": "middle_east",
  "severity": 7,
  "summary": "Iran threatens Strait of Hormuz closure after Israeli strike",
  "market_implications": {
    "bullish": ["XLE", "GLD", "XLU"],
    "bearish": ["XLF", "tech_growth"],
    "hedge": "Buy protective puts on QQQ"
  }
}
```

### 2. Fed Policy & Macro
**Why:** Rate policy drives everything

**Sources:**
- Fed press releases
- FOMC minutes
- Fed speaker calendar
- Bloomberg/Reuters Fed coverage

**Events:**
- Rate decisions
- QE/QT changes
- Forward guidance shifts
- Fed speaker hawkish/dovish tone

**Output:**
```json
{
  "event_type": "fed_policy",
  "action": "rate_hold",
  "tone": "dovish_pivot",
  "summary": "Powell signals rates may have peaked, watching data",
  "market_implications": {
    "bullish": ["TLT", "growth_tech", "small_caps"],
    "bearish": ["USD", "financials"],
    "catalyst": "First dovish signal after 18 months"
  }
}
```

### 3. Economic Data
**Why:** Surprises move markets

**Sources:**
- Bureau of Labor Statistics (jobs, CPI)
- Census Bureau (retail sales, housing)
- ISM (manufacturing, services PMI)
- Regional Fed surveys

**Data releases:**
- CPI, PCE (inflation)
- NFP, unemployment rate (jobs)
- Retail sales (consumer health)
- PMIs (manufacturing/services)

**Output:**
```json
{
  "release": "CPI",
  "actual": 3.2,
  "expected": 3.5,
  "surprise": -0.3,
  "interpretation": "Cooling inflation, dovish for Fed",
  "market_implications": {
    "bullish": ["TLT", "growth_tech"],
    "bearish": ["commodities"],
    "narrative": "Soft landing looking more likely"
  }
}
```

### 4. Earnings & Corporate Events
**Why:** Company-specific catalysts

**Sources:**
- SEC EDGAR (8-Ks, earnings filings)
- Earnings call transcripts (AlphaStreet, Seeking Alpha)
- Company press releases

**Events:**
- Earnings beats/misses
- Guidance changes
- M&A announcements
- Product launches
- Management changes

**Output:**
```json
{
  "ticker": "NVDA",
  "event_type": "earnings_report",
  "result": "beat_and_raise",
  "revenue_surprise": "+8%",
  "guidance": "raised",
  "management_tone": "confident",
  "market_reaction": "+12% after hours",
  "implications": "AI demand accelerating, read through to AMD, AVGO"
}
```

### 5. Sector-Specific Events
**Why:** Sector rotations drive returns

**Semiconductors:**
- Chip export controls
- Fab construction announcements
- Design wins
- Manufacturing bottlenecks

**Energy:**
- OPEC meetings
- Oil inventory reports
- Refinery utilization
- Natural gas storage

**Financials:**
- Banking stress (deposits, capital ratios)
- Regulatory changes
- Loan growth trends

**Healthcare:**
- FDA approvals
- Clinical trial results
- Medicare reimbursement changes

---

## Architecture

### Data Flow
```
News Sources → Fetch & Parse → Categorize → LLM Analysis → Market Implications → Store → Display
```

### Components

#### 1. News Fetchers
**RSS Feed Reader:**
```python
# src/news/rss_fetcher.py
- Subscribe to RSS feeds
- Poll every hour
- Deduplicate articles
- Store raw articles
```

**API Fetchers:**
```python
# src/news/api_fetcher.py
- NewsAPI, Polygon.io, etc.
- Keyword-based queries
- Date range filtering
```

**Web Scrapers (as fallback):**
```python
# src/news/scrapers.py
- Specific high-value sources
- Rate-limited, respectful
- Only if no API/RSS
```

#### 2. Categorizer
```python
# src/news/categorizer.py
def categorize_article(article):
    """Use fast LLM (Gemini Flash) to categorize."""
    categories = [
        "geopolitical",
        "fed_policy",
        "economic_data",
        "earnings",
        "sector_specific",
        "not_relevant"
    ]
    # Return category + initial severity/relevance score
```

#### 3. Analyzer (Main LLM)
```python
# src/news/analyzer.py
def analyze_event(article, category):
    """Deep analysis with Gemini/Claude."""
    prompt = f"""
    Article: {article}
    Category: {category}

    Analyze:
    1. What happened?
    2. Why does it matter for markets?
    3. Which sectors/tickers are affected?
    4. Bullish or bearish? For what?
    5. Time horizon (immediate, days, weeks)?
    6. Confidence level?

    Output JSON.
    """
    return llm.generate(prompt)
```

#### 4. Storage
```python
# data/news_events.json
{
  "events": [
    {
      "id": "uuid",
      "timestamp": "2026-03-18T10:00:00Z",
      "category": "geopolitical",
      "source": "Reuters",
      "headline": "...",
      "summary": "...",
      "analysis": {...},
      "market_implications": {...}
    }
  ]
}
```

#### 5. Frontend Display
```astro
<!-- frontend/src/pages/news-events.astro -->
- Filterable by category
- Sortable by severity/time
- Shows market implications
- Links to affected tickers
```

---

## RSS Feed Sources

### Geopolitical
- Reuters World: `https://www.reuters.com/rss/world`
- BBC World: `http://feeds.bbci.co.uk/news/world/rss.xml`
- Al Jazeera: `https://www.aljazeera.com/xml/rss/all.xml`

### Financial/Macro
- Bloomberg Markets: `https://www.bloomberg.com/feed/...`
- Wall Street Journal Economy: `https://feeds.wsj.com/...`
- Financial Times: `https://www.ft.com/rss/...`

### Fed Watching
- Federal Reserve Press Releases: `https://www.federalreserve.gov/feeds/press_all.xml`
- CNBC Fed: `https://www.cnbc.com/id/100003114/device/rss/rss.html`

### Sector-Specific
- Semiconductor Industry Association
- Energy Information Administration
- FDA approvals feed

### Market Data
- MarketWatch: `http://feeds.marketwatch.com/...`
- Seeking Alpha: `https://seekingalpha.com/feed.xml`

---

## Implementation Phases

### Phase 1: Basic RSS Ingestion
- [x] Already have basic news via Yahoo Finance
- [ ] Add RSS feed fetcher
- [ ] Store raw articles
- [ ] Display on dashboard

### Phase 2: Categorization
- [ ] LLM-based categorizer
- [ ] Filter out noise (ads, fluff)
- [ ] Deduplication (same story, different source)

### Phase 3: Deep Analysis
- [ ] Per-category analyzer
- [ ] Extract market implications
- [ ] Generate actionable signals

### Phase 4: Integration
- [ ] Feed into LLM agents (macro, risk, tech)
- [ ] Alert system (severity > 7 → notification)
- [ ] Historical tracking (were implications correct?)

### Phase 5: Advanced
- [ ] Sentiment trends over time
- [ ] Event correlation (event A → market reaction B)
- [ ] Predictive modeling (this type of event → expected move)

---

## Example: Strait of Hormuz Event

### Raw Article (Reuters RSS)
```
"Iran threatens to close Strait of Hormuz after Israeli strike on nuclear facility.
Oil tankers rerouting. U.S. Navy deploying additional ships."
```

### Categorization
```json
{
  "category": "geopolitical",
  "subcategory": "middle_east_tension",
  "severity": 8,
  "relevance": ["energy", "commodities", "risk_sentiment"]
}
```

### LLM Analysis
```json
{
  "event": "Iran threatens Strait of Hormuz closure",
  "significance": "20% of global oil flows through strait. Closure would spike oil prices.",
  "historical_context": "Similar threats in 2018 led to 10% oil rally in 2 weeks.",
  "market_implications": {
    "immediate": {
      "bullish": ["XLE", "OXY", "SLB", "GLD", "TLT"],
      "bearish": ["Airlines", "Transports", "Cyclicals"],
      "hedges": ["Long VIX calls", "Short QQQ"]
    },
    "if_escalates": {
      "scenario": "Actual blockade or military action",
      "impact": "Oil to $120+, global recession risk",
      "positioning": "Max defense, energy, short everything else"
    },
    "if_deescalates": {
      "scenario": "Diplomatic resolution in days",
      "impact": "Oil back to $75, risk-on resumes",
      "positioning": "Fade the move, buy the dip in tech"
    }
  },
  "confidence": 0.75,
  "time_horizon": "1-2 weeks"
}
```

### Dashboard Display
```
🚨 HIGH SEVERITY GEOPOLITICAL EVENT

Iran threatens Strait of Hormuz closure (Severity: 8/10)

Implications:
✅ Bullish: XLE (+5%), GLD, TLT
❌ Bearish: Airlines, Consumer discretionary
⚠️ Hedge: Consider protective puts on QQQ

Watch: Oil prices, U.S. response, diplomatic efforts
Update: 2 hours ago
```

---

## LLM Prompt Template: Geopolitical Event

```python
GEOPOLITICAL_ANALYSIS_PROMPT = """
You are an expert market analyst specializing in geopolitical risk.

EVENT:
{headline}

DETAILS:
{article_text}

CURRENT MARKET CONTEXT:
- SPY: {spy_price} ({spy_regime})
- VIX: {vix}
- Oil: ${oil_price}
- Gold: ${gold_price}

ANALYZE:

1. WHAT HAPPENED?
   - Summarize the event in 2 sentences

2. MARKET RELEVANCE (0-10):
   - How significant is this for markets?
   - Has this happened before? What was the market reaction?

3. AFFECTED SECTORS/TICKERS:
   - Bullish (list specific tickers and why)
   - Bearish (list specific tickers and why)
   - Safe havens (gold, treasuries, dollar?)

4. TIME HORIZON:
   - Immediate (today/tomorrow)
   - Short-term (days to weeks)
   - Long-term (months)

5. SCENARIOS:
   - Best case (event resolves) → market impact?
   - Base case (current trajectory) → market impact?
   - Worst case (escalation) → market impact?

6. RECOMMENDED POSITIONING:
   - What to buy
   - What to sell/avoid
   - What hedges to consider

7. CONFIDENCE LEVEL (0-1):
   - How confident are you in this analysis?

Output as JSON.
"""
```

---

## Success Metrics

**Good news system:**
- Catches events before market fully reacts (early signal)
- Low false positive rate (don't cry wolf)
- Actionable (tells you what to do)
- Trackable (can backtest "if we followed this signal, would we profit?")

**Track:**
- Event severity vs market reaction (calibration)
- Time from event to market reaction (lead time)
- Accuracy of bullish/bearish calls
- P&L of trades based on news signals

---

## Next Steps

1. Build RSS feed ingester (Python feedparser library)
2. Set up news database (SQLite or JSON files)
3. Create LLM categorizer (Gemini Flash for speed)
4. Build analysis prompt templates per category
5. Create news events dashboard page
6. Integrate news context into existing LLM agents
7. Backtest: historical events → market reactions

This will give the LLMs qualitative data to complement quantitative indicators, making decisions more robust.
