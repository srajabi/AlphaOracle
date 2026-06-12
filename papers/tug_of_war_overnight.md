# A Tug of War: Overnight versus Intraday Expected Returns

**Citation:** Lou, D., Polk, C., & Skouras, S. (2019). *A Tug of War:
Overnight versus Intraday Expected Returns.* Journal of Financial Economics
134(1).

**Links:** [Author PDF (LSE)](https://personal.lse.ac.uk/polk/research/tugofwar.pdf)
| [DOI](https://doi.org/10.1016/j.jfineco.2018.11.011)
| PDF: [pdfs/tug_of_war_2019.pdf](pdfs/tug_of_war_2019.pdf)
| Found via vince.quant.

## Claims

- Decomposing returns into overnight (close→open) and intraday (open→close):
  a large share of the equity premium - nearly all of it for the largest
  stocks - is earned overnight.
- Momentum profits are ~entirely overnight (+0.98%/mo overnight vs ~0
  intraday; Sharpe 0.77 vs 0.31); value and low-vol premia are earned
  intraday with the opposite overnight sign.
- Interpretation: clientele effects - individuals trade near the open,
  institutions toward the close.

## Criticisms

- Trading it directly means paying the close→open spread twice a day -
  transaction costs eat the raw effect for most implementations.
- Effect size varies by stock size, period, and venue; patterns this famous
  tend to decay.
- Overnight gaps carry the news/jump risk (you hold through earnings and
  geopolitics).

## AlphaOracle verdict

**Testable with data we already have** (OHLC in `data/historical_long/`):
overnight return = open/prev_close - 1, intraday = close/open - 1. The
backtest engine is close-to-close, so testing this needs a small variant
(daily strategy returns built from the two legs separately).

**Not yet implemented.** Flagged as a strategy-lab round-4 candidate:
overnight-only SPY/QQQ holding vs intraday-only vs buy-hold, zero-cost first,
then with a realistic spread assumption (the honest version likely kills it
for daily ETF trading - worth quantifying anyway for the decomposition
insight alone).
