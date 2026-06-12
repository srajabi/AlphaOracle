# Data Sources Expansion (2026-06)

What data we have, what we just added, and what's worth adding next - each
entry mapped to the signal it would feed.

## Already in the repo

| Source | Data | Used by |
|---|---|---|
| yfinance EOD | 60+ tickers, decades of OHLCV (`data/historical_long/`) | everything |
| yfinance daily refresh | 2y window per ticker (`data/history/`) | indicators, dashboards |
| ^VIX | 1990+ | vix_regime, composite_regime, tqqq filters |
| Alpaca | portfolio state, trades, intraday bars (limits in `spikes/alpaca_intraday_data_limits.md`) | execution + future intraday work |
| Yahoo news | macro/theme/ticker headlines | LLM analysts |

## Added this session (all in `data/historical_long/`, yfinance pipeline)

| Series | History | Signal it feeds |
|---|---|---|
| **^VIX3M** | 2006+ | **VIX term structure** (VIX/VIX3M ratio): backwardation = stress. Cleaner regime signal than VIX level - prime round-5 strategy input |
| **^VIX9D** | 2011+ | short-end of the vol curve |
| **HYG, LQD** | 2007+/2002+ | **credit stress** (HYG/LQD relative momentum ~ HY spread proxy) - the signal the Xiong cash-overlay paper used |
| **^TNX, ^IRX** | **1962+/1960+** | **yield curve** (10y minus 13w) - the classic recession lead, with 60+ years of history |

## Worth adding next (free, in rough priority order)

1. **FRED** (api key, free; fredgraph.csv timed out from this network - retry
   or use the API): real HY OAS (BAMLH0A0HYM2), T10Y2Y, unemployment claims,
   CPI. Macro regime layer.
2. **Shiller CAPE** (Yale, monthly Excel): valuation-conditioned entry rules -
   directly relevant to the "market screaming top" question.
3. **CFTC COT reports** (weekly, free CSV): positioning extremes as
   contrarian signal.
4. **AAII sentiment survey** (weekly): the classic retail sentiment contrarian
   input (ties to Baker-Wurgler in the papers library).
5. **CBOE put/call ratios** (free daily CSV): short-term sentiment.
6. **EDGAR full-text** (free API): filing-change signals for our 25 single
   stocks (ties to Lazy Prices) - feeds the LLM analysts, not a strategy.
7. **Alpaca intraday bars** (already have access): needed for the Gao
   intraday-momentum replication.

## Explicitly not pursuing

- Paid tick/L2 data, options chains beyond yfinance, alt-data vendors -
  cost/benefit wrong for a paper-trading research system.
- Twitter/X sentiment APIs - paywalled and noisy.
