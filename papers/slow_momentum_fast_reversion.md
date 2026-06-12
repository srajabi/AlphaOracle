# Slow Momentum with Fast Reversion (Changepoint-Gated Momentum)

**Citation:** Wood, K., Roberts, S., & Zohren, S. (2021). *Slow Momentum with
Fast Reversion: A Trading Strategy Using Deep Learning and Changepoint
Detection.* Journal of Financial Data Science 4(1). Oxford-Man Institute.

**Links:** [arXiv 2105.13727](https://arxiv.org/abs/2105.13727)
| PDF: [pdfs/slow_momentum_fast_reversion_2021.pdf](pdfs/slow_momentum_fast_reversion_2021.pdf)
| Found via the user's Oxford-Man Institute publications pointer.

## Claims

- Classic time-series momentum suffers most around regime changes: the slow
  signal stays positioned the wrong way after a turn (exactly our COVID
  finding for SMA strategies).
- Fix: run Bayesian online changepoint detection (CPD) alongside the momentum
  model; when a changepoint is detected, fast mean-reversion logic overrides
  slow momentum until the new regime establishes.
- Reported: meaningful Sharpe improvement over standard TSMOM on futures,
  concentrated in regime-turn periods.

## Criticisms

- Deep-learning component (LSTM) on top of CPD - hard to disentangle which
  part earns the improvement; replication burden is high.
- Futures universe with institutional costs; not directly a retail ETF
  result.
- Oxford-Man output is generally ML-heavy (see their pubs list) - elegant,
  but the simpler ablation (CPD gate on plain TSMOM, no deep nets) is what a
  retail implementation would actually want, and the paper doesn't isolate it
  cleanly.

## AlphaOracle verdict

**TESTED (2026-06, `changepoint_gated_momentum`):** simplified version - 200d
SMA trend on SPY, exposure halved while 20d realized vol exceeds 2x its 100d
median (the changepoint proxy). 1993-2026:

- Sharpe 0.73 vs 0.69 for the plain golden cross; maxDD -27.6% vs -33.7%.
- A real but modest improvement - consistent with the paper's claim that the
  gains concentrate at regime turns. Our crude vol-step proxy captures part
  of what their Bayesian CPD captures; the deep-learning layer remains
  unreplicated (and per our note, probably unnecessary for the retail
  version).
