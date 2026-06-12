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

**Not yet implemented.** The IDEA maps directly onto our known failure mode:
every trend strategy in our lab (SMA200, TSMOM, GTAA) bleeds at fast regime
turns - COVID hit them before the signal could move. A simplified version is
testable with our stack: a changepoint proxy (e.g. rolling z-score of 5-day
returns breaching a threshold, or realized-vol step changes) that temporarily
flips the trend rule toward mean-reversion. Flagged as a strategy-lab round-4
candidate alongside the cash-overlay and overnight papers.
