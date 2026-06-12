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

**TESTED (2026-06, `backtesting/overnight_decomposition.py`) - the effect
replicates dramatically on our data:**

| | CAGR | Sharpe (90% CI) | MaxDD |
|---|---|---|---|
| SPY overnight-only | 9.8% | 0.94 [0.65, 1.24] | -33% |
| SPY intraday-only | 0.7% | 0.12 [-0.13, 0.38] | -69% |
| QQQ overnight-only | 13.5% | 0.96 [0.64, 1.31] | -33% |
| QQQ intraday-only | **-2.9%** | -0.01 | **-88%** |

Essentially ALL of the 27-33y equity premium was earned overnight; the CIs
don't overlap. BUT with just 1bp/leg switching cost, QQQ overnight drops to
7.9% CAGR / 0.61 Sharpe - below buy-and-hold's return. As predicted, costs
eat the tradable edge; the decomposition survives as an insight (drawdowns
are an intraday phenomenon; overnight holding is where the premium lives),
not as a retail strategy. Results: `data/overnight_decomposition.json`.
