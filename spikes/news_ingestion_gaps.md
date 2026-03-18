# Spike: News Ingestion Gaps And Macro Shock Coverage

**Objective:** Fix the news pipeline so the LLMs actually receive timely market-moving context, including geopolitical and macro events like Strait of Hormuz disruptions.

## Current State
The current implementation in `src/data_ingestion.py` does this:

* loop through each ticker
* call `yf.Ticker(ticker).news`
* keep only the top 3 titles

This has several problems:

* it is **ticker-scoped**, not market-scoped
* it captures only titles, not summaries or source metadata
* it does not explicitly query for macro themes like oil, shipping, war, sanctions, Fed, CPI, tariffs, or geopolitics
* it depends on Yahoo Finance surfacing relevant articles under that symbol
* it gives the LLM no sense of article freshness, source quality, or cross-market implications

So yes, the current system can absolutely miss events like Strait of Hormuz effects.

## Why Strait Of Hormuz Matters
A disruption there is not "just news". It can materially affect:

* oil prices
* inflation expectations
* energy equities
* airlines and transports
* defense names
* bond yields
* broad risk sentiment
* gold and USD safe-haven flows

If the pipeline only sees a few ticker headlines, that macro linkage will often never reach the model.

## Design Problem
The current system treats news as an attribute of a ticker. That is too narrow.

The system needs at least three separate news layers:

### 1. Global macro news
Examples:

* Fed
* CPI / PPI
* jobs
* Treasury yields
* OPEC
* Strait of Hormuz
* sanctions
* tariffs
* war / shipping disruptions
* major elections

### 2. Sector and theme news
Examples:

* semiconductors
* AI capex
* utilities / power demand
* energy supply shocks
* banks / credit stress
* gold / central-bank buying

### 3. Ticker-specific news
Examples:

* earnings
* guidance
* analyst actions
* product announcements
* litigation
* M&A

All three need to exist side by side.

## What To Add

### 1. Dedicated macro-news feed
Build a separate ingestion block for top-down topics.

Suggested keyword buckets:

* `Federal Reserve`, `FOMC`, `interest rates`, `CPI`, `inflation`
* `oil`, `Brent`, `WTI`, `OPEC`, `Strait of Hormuz`, `shipping`
* `tariffs`, `sanctions`, `trade war`
* `Treasury yields`, `bond market`
* `recession`, `soft landing`, `consumer spending`

Output should include:

* headline
* source
* published timestamp
* topic bucket
* short summary if available

### 2. Sector-theme feed
For each major thesis bucket, gather recent theme headlines.

Examples:

* energy
* gold / metals
* semiconductors
* utilities / power
* software
* international markets

That is much better than hoping the headline appears under a single ticker.

### 3. Event extraction
Do not just pass article titles through. Extract structured events.

Examples:

* `event_type = geopolitical_supply_shock`
* `assets_impacted = [XLE, GLD, airlines, SPY]`
* `direction = risk_off / inflationary`
* `confidence = medium`

This can be rule-based at first.

### 4. Article freshness and deduplication
News without timestamps is weak context.

Need:

* publication time
* recency windows
* source dedupe
* duplicate headline collapse

The LLM should know what is new today versus stale.

## Candidate Source Strategy

### MVP source mix
* Yahoo Finance ticker news for company-specific coverage
* RSS feeds for macro and market headlines
* optional paid upgrade later for better market news APIs

The architecture should not assume one source is enough.

### Good RSS candidates
* Reuters business/world feeds
* CNBC markets feed
* Financial Times markets/world if accessible
* major energy-market feeds if available

Even simple RSS ingestion would be better than the current setup.

## Suggested Output Shape
Instead of only embedding news under each ticker, write a broader context object:

```json
{
  "date": "2026-03-14",
  "macro_news": [
    {
      "headline": "Oil jumps as shipping risk rises near Strait of Hormuz",
      "source": "Reuters",
      "published_utc": "2026-03-14T10:15:00Z",
      "topic": "energy_geopolitics",
      "summary": "Shipping disruption fears are pushing crude and inflation expectations higher."
    }
  ],
  "theme_news": {
    "energy": [],
    "rates": [],
    "semiconductors": []
  },
  "ticker_news": {
    "XLE": [],
    "GLD": [],
    "NVDA": []
  }
}
```

This gives the LLM much better context structure.

## Prompting Implications
Once macro news exists, prompts should explicitly ask:

* which positions benefit from the shock
* which positions are hurt by the shock
* whether the event changes the regime
* whether it creates a hedge need or a tactical opportunity

For example:

* oil shock -> bullish energy, inflationary, possibly bearish airlines and bonds
* shipping disruption -> risk-off, supportive for gold and defensives

Right now the prompts are capable of reasoning about this, but the data path is too weak.

## Recommended Implementation Plan

### Phase 1
Keep current ticker news, but add:

* macro RSS ingestion
* sector-theme RSS ingestion
* timestamps and source metadata
* deduplication

### Phase 2
Add rule-based event tagging:

* inflationary
* growth-positive
* risk-off
* supply shock
* policy shock

### Phase 3
Add market-impact summaries generated by code or a smaller model:

* likely winners
* likely losers
* affected sectors
* confidence

## Recommendation
The issue is real: the system is not ingesting macro news in a robust way today.

If only one fix gets built next, it should be:

* add a dedicated **macro and sector news layer** separate from ticker headlines

That will improve decision quality faster than trying to make the existing Yahoo ticker-news path do something it was not designed for.
