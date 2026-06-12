# Paid Options Data + the Volatility Risk Premium ("Renaissance play?")

User question (2026-06): if we pay for options data and approximate
Black-Scholes with options prices + stock data, realistically how good could
that get? Could we do a Renaissance-type play?

## The honest Renaissance answer first

No - and it's worth being precise about why, because the why points at what
IS achievable.

- Medallion's edge is ~50.75% per-trade hit rate x ~hundreds of thousands of
  trades/day x decades of proprietary data x execution infrastructure x
  ~300 researchers, capped at ~$10-15B because the edges have tiny capacity.
  The structure of the edge is scale-of-trades, not quality-of-insight.
- We trade ~monthly on liquid ETFs. Our entire trade count per YEAR is less
  than Medallion's per MINUTE. No data purchase changes that geometry.
- Even Renaissance can't sell Medallion: their public funds (RIEF etc.) are
  ordinary. The replicable part of RenTech is the discipline (hypothesis,
  validation, costs) - which we already practice - not the returns.

## What "Black-Scholes + options prices" actually gets you

Backing prices out of BS = implied volatility. That's not an edge - IV IS
the market's quote. The real, documented, retail-accessible edge in options
is one level up:

**The volatility risk premium (VRP): implied vol systematically exceeds
subsequently-realized vol.** 1990-2018: VIX averaged 19.3% vs realized
15.1% - a 4.2pt premium ([CBOE white paper](https://www.cboe.com/insights/posts/white-paper-shows-volatility-risk-premium-facilitated-higher-risk-adjusted-returns-for-put-index/)).
Sellers of index options get paid it; buyers pay it (crash insurance has
negative expected value, like all insurance).

Benchmark evidence (CBOE PUT index - systematic cash-secured SPX
put-writing, live since 1986):
- vol 9.95% vs S&P's 14.93%, beta 0.56, monthly alpha ~0.2%
- maxDD -32.7% vs -50.9% for the S&P (2006-2015 window incl. GFC)
- BUT: strongly negative skew - it earns steadily and loses violently;
  post-2012 returns weakened (the trade is crowded)
- Counterpart evidence: continuously BUYING puts (PPUT) has well-documented
  negative alpha (Israelov & Klein) - protection is systematically overpriced,
  which is exactly why selling it pays.

Realistic expectation for a disciplined VRP sleeve: **Sharpe ~0.5-0.9
standalone, equity-like returns at ~2/3 the vol, with crash months that
hurt** - a genuine diversifier-with-teeth, NOT a money printer. The most
practical retail forms:
1. Covered calls on holdings we already own (income overlay, ~1-3%/yr)
2. Cash-secured puts on indexes we'd buy anyway (PUT-style)
3. Both gated by our regime signals (sell premium only in non-stress
   regimes - our VIX term-structure data is exactly the right filter)

## What paid data unlocks (and costs)

The blocker today: yfinance has NO historical options chains - we can see
today's chain (options_ingestion.py) but cannot backtest. Vendors:

| Vendor | ~Cost | What |
|---|---|---|
| **ORATS** | ~$99-249/mo | clean historical chains + greeks + backtest API; the research-grade choice |
| **Polygon.io options** | $29-199/mo | raw historical NBBO/chains, more DIY |
| **CBOE DataShop** | one-off purchases | official, per-dataset pricing |
| **Theta Data** | ~$40-80/mo | budget historical chains, retail-aimed |

Recommended path if we spend: **ORATS or Theta Data, SPY/QQQ/XLE chains,
2012+ (post-crowding sample, deliberately)**, then:
1. Replicate PUT/BXM mechanics with real chains; validate vs CBOE's
   published index values (calibration check)
2. Test regime-gated variants (sell premium only when VIX term structure
   is in contango / canary risk-on)
3. Run everything through the standard gauntlet (DSR, bootstrap, costs at
   realistic option spreads - which are 10-50x ETF spreads; this kills most
   naive options backtests and must be modeled honestly)
4. Paper trade via Alpaca options before any real sizing

## Decision

Worth doing as a RESEARCH thread (VRP is among the best-documented premia
in finance), with expectations set at "diversifying income sleeve", not
"Renaissance". Entry cost ~$50-100/mo of data + meaningful spread-modeling
work. Not started; awaiting user go/no-go on the data spend.
