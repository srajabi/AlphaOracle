# Optimization of Conditional Value-at-Risk

**Citation:** Rockafellar, R. T., & Uryasev, S. (2000). *Optimization of
Conditional Value-at-Risk.* Journal of Risk 2(3).

**Links:** [Author PDF (UW)](https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf)
| PDF: [pdfs/rockafellar_uryasev_cvar.pdf](pdfs/rockafellar_uryasev_cvar.pdf)

## Claims

- CVaR (expected shortfall) - the MEAN loss in the worst (1-alpha) tail -
  is a better risk measure than VaR: coherent (subadditive), convex, and
  it sees how bad the tail IS, not just where it starts.
- Key result: CVaR can be optimized by linear programming via a simple
  auxiliary function - making minimum-CVaR portfolio construction tractable.
- Now the regulatory standard (Basel moved from VaR to expected shortfall).

## Criticisms

- Tail estimates from historical data are noisy exactly where they matter;
  CVaR(95) on daily data is decent, CVaR(99.9) is guesswork.
- Optimizing CVaR directly tends to produce concentrated hedged portfolios
  sensitive to the sample.

## AlphaOracle verdict

**Adopted as a metric (2026-06):** `cvar()` in `backtesting/validation.py`
(95% expected shortfall on daily returns) now reports on every strategy in
the scoreboard, alongside Sortino, Calmar, Ulcer Index, drawdown duration,
and tail ratio. Rationale: our old Sharpe/maxDD pair misses both tail shape
(CVaR/tail ratio) and time-underwater (Ulcer/duration) - the dimensions
retirees and leveraged accounts actually feel.

CVaR-OPTIMIZED portfolio construction (the paper's main contribution) is not
implemented - our strategies are rule-based, not optimized, partly by design
(optimization = more overfitting surface per the deflated-Sharpe note).
