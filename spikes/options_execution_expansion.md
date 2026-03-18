# Spike: Expanding Into Options Strategies

**Objective:** Evaluate whether AlphaOracle can move beyond stock and ETF trades into practical options strategies, and define the safest implementation path.

## Current State
The current execution path is equity-only:

* `src/execute_trades.py` submits Alpaca market orders for `buy` and `sell`
* trade JSON only supports:
  * `ticker`
  * `action`
  * `qty` or `notional_value`

That means the system cannot currently express or execute:

* long calls
* long puts
* covered calls
* cash-secured puts
* vertical spreads
* collars
* protective puts

## Key Constraint
This is not mainly an LLM problem. It is a **broker + data + risk model** problem.

To support options cleanly, the system needs:

1. options chain data
2. contract selection logic
3. strategy-level risk rules
4. broker order support for option contracts
5. position/state tracking for option legs

Without those pieces, the LLM will generate low-quality or non-executable ideas.

## Which Strategies Are Realistic First

### Tier 1: Safest / most realistic MVP
* Protective puts on existing long equity positions
* Covered calls on existing long equity positions
* Cash-secured puts on tickers we already want to own
* Long calls or long puts only for index/ETF tactical views

Why these first:

* simpler payoff profile
* easier risk controls
* easier contract selection rules
* lower operational complexity than multi-leg spreads

### Tier 2: Reasonable after MVP
* Bull call spreads
* Bear put spreads
* Collars

Why later:

* requires multi-leg order handling
* requires net debit/credit reasoning
* needs stronger fill logic and state tracking

### Tier 3: Avoid for now
* naked short options
* iron condors
* ratio spreads
* calendar spreads
* gamma-heavy short-dated speculation

These are too easy to misuse and too hard to automate responsibly in the current architecture.

## What The LLM Should Not Be Allowed To Decide Freely
The model should not invent option contracts from scratch with no hard constraints.

Python should determine:

* allowed strategy types
* max DTE range
* allowed delta range
* minimum open interest
* minimum volume
* max bid-ask spread percentage
* max premium at risk
* max portfolio allocation by strategy

The LLM should decide:

* whether hedging or yield enhancement is warranted
* which underlying best matches the thesis
* which approved strategy family to use

Then Python should map that to actual contracts.

## Recommended Options Strategy Rules

### 1. Covered Calls
Use only when:

* underlying is already owned
* trend is neutral-to-up, but not in a strong breakout
* IV is elevated enough to justify premium collection
* call strike is above cost basis and above nearby resistance

Good fit for:

* quiet regimes
* defensive holdings
* low-conviction upside periods

### 2. Cash-Secured Puts
Use only when:

* underlying is on the approved buy list
* technicals show support nearby
* IV is elevated
* sufficient cash is reserved

Good fit for:

* high-conviction names the system wants to accumulate
* volatile but not broken charts

### 3. Protective Puts
Use only when:

* existing position is core
* macro or volatility risk is rising
* direct sale is undesirable for tax or thesis reasons

Good fit for:

* concentrated positions
* event-risk windows
* geopolitical shock scenarios

### 4. Long Calls / Puts
Use only when:

* the setup is high conviction
* the thesis is time-bounded
* defined premium-at-risk is acceptable

These should be constrained to liquid ETFs first:

* `SPY`
* `QQQ`
* `IWM`
* `GLD`
* `TLT`

## Required Data Additions
The current system does not gather enough options-specific data.

Need at minimum:

* expiration dates
* strike prices
* call/put side
* bid/ask
* last price
* implied volatility
* open interest
* volume
* delta if available

Useful derived features:

* spread width percentage
* premium yield for covered calls / CSPs
* moneyness
* IV percentile or IV rank
* expected move into expiry

## Execution Architecture Options

### Option A: Keep Alpaca, add options if supported by account/API
If the Alpaca account and SDK support the specific options workflows needed, this is the cleanest path.

Pros:

* same broker
* same secret management
* same paper-trading flow

Cons:

* may have account permissions or product limitations
* option support may not cover all desired workflows cleanly

### Option B: Recommendation-only for options, execution remains manual
The system generates a structured options order ticket, but does not auto-submit it.

Pros:

* much safer
* easier to build quickly
* useful immediately

Cons:

* no full automation

### Option C: Hybrid
Auto-execute only low-risk approved strategies:

* covered calls
* cash-secured puts
* protective puts

Keep anything multi-leg or aggressive as manual-review only.

This is probably the right medium-term path.

## Proposed Trade JSON Shape
The current trade schema is too simple. An expanded schema should distinguish equities from options.

```json
[
  {
    "asset_type": "option",
    "strategy": "covered_call",
    "underlying": "GLD",
    "action": "sell_to_open",
    "expiration": "2026-04-17",
    "strike": 485,
    "option_type": "call",
    "contracts": 2,
    "max_bid_ask_spread_pct": 0.08,
    "rationale": "Generate yield against an extended but still-owned hedge position."
  }
]
```

For multi-leg strategies, use explicit legs:

```json
{
  "asset_type": "option_strategy",
  "strategy": "bull_call_spread",
  "underlying": "SPY",
  "legs": [
    {"action": "buy_to_open", "option_type": "call", "strike": 560, "expiration": "2026-04-17", "contracts": 1},
    {"action": "sell_to_open", "option_type": "call", "strike": 575, "expiration": "2026-04-17", "contracts": 1}
  ]
}
```

## Recommended Rollout

### Phase 1
Do not auto-execute options yet.

Implement:

* options data ingestion
* contract ranking
* strategy recommendation JSON
* site display for proposed option trades

### Phase 2
Auto-execute only:

* covered calls
* cash-secured puts
* protective puts

with strict hard-coded limits.

### Phase 3
Consider vertical spreads only after:

* robust contract liquidity filters
* multi-leg order support
* state tracking of open option positions
* tested risk controls

## Recommendation
Yes, fancier options strategies are possible, but the right first step is not "let the bot trade options". The right first step is:

1. add options data and contract-selection logic
2. support recommendation-only output first
3. auto-execute only the safest approved strategy families later

If only one options feature gets built first, it should be:

* **cash-secured puts and covered calls with strict liquidity and risk filters**

Those match the current portfolio-management style much better than speculative multi-leg options trading.
