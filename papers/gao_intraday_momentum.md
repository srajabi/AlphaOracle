# Market Intraday Momentum

**Citation:** Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). *Market
Intraday Momentum.* Journal of Financial Economics 129(2).

**Links:** [SSRN 2440866](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866)
| PDF: [pdfs/gao_market_intraday_momentum.pdf](pdfs/gao_market_intraday_momentum.pdf)

## Claims

- On SPY (1993-2013, half-hourly data): **the first half-hour return
  (measured from the prior close) predicts the last half-hour return** -
  R-squared ~1.6%, rising to 2.6% adding the 12th half-hour.
- Stronger on volatile days, high-volume days, recessions, and macro-news
  days. Holds across 10 other major ETFs.
- Mechanism: late-informed traders and intraday position management create
  predictable end-of-day flow in the morning's direction.
- A trade-the-last-half-hour strategy on the signal beats always-long with
  far less market exposure (in the money ~half the day).

## Criticisms

- The effect is per-day tiny; transaction costs and the 2x-daily execution
  matter enormously (same cost problem as the overnight effect).
- Published 2018 from a 2014 working paper - closing-auction dynamics have
  changed (auction volume exploded); decay likely.
- Needs INTRADAY data - daily OHLC cannot compute half-hourly legs.

## AlphaOracle verdict

**Not yet testable with our daily data** - this is the first strategy in the
library blocked purely by data granularity. The repo already has
`tools/download_intraday_history.py` and `spikes/alpaca_intraday_data_limits.md`
(Alpaca free tier provides recent intraday bars). Flagged for a future round:
pull 2y of SPY/QQQ 30-min bars from Alpaca, replicate the first-half-hour ->
last-half-hour regression, and check whether the effect survives 2024-2026
data and 1bp costs before any implementation thinking.

Related finding we COULD already test: the overnight decomposition
([tug_of_war_overnight.md](tug_of_war_overnight.md)) - same family
(intraday clienteles), and it replicated dramatically.
