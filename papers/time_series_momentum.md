# Time Series Momentum

**Citation:** Moskowitz, T., Ooi, Y. H., & Pedersen, L. H. (2012).
*Time Series Momentum.* Journal of Financial Economics 104(2).

**Links:** [Author PDF (NYU)](https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf)
| PDF: [pdfs/time_series_momentum_2012.pdf](pdfs/time_series_momentum_2012.pdf)

## Claims

- An asset's own past 12-month excess return predicts its next ~1-12 months
  across 58 futures markets (equities, FX, commodities, bonds).
- A diversified TSM strategy delivers large alpha with strong performance in
  extreme markets ("crisis alpha").
- Partial behavioral explanation: initial underreaction, delayed overreaction.

## Criticisms

- Post-publication performance decayed (crowding); the 2010s were hostile to
  trend on many assets.
- Single-asset TSM (what we can implement) loses the cross-asset
  diversification that drives the paper's headline Sharpe.
- 12-1 convention (skip the latest month) matters more for cross-sectional
  momentum than TSM; transaction-cost sensitivity at shorter lookbacks.

## AlphaOracle verdict

`tsmom_12_1_spy` (long SPY when 12-month return skipping the latest month is
positive, monthly; 1993-2026):

- Sharpe 0.71 vs 0.56 buy-and-hold; maxDD -33.7% vs -55.2%; CAGR 10.3% vs
  10.5% - nearly the full return with 40% less drawdown, 25 trades in 33y.
- Slightly behind `sma200_monthly_spy` (0.79) on the same window - on a single
  equity index, the SMA filter and TSM capture the same signal; SMA's version
  is marginally cleaner.

**Takeaway:** validated as a downturn-minimizer on SPY; the bigger prize
(diversified multi-asset TSM) needs futures data we don't have. Results:
`backtesting/results_lab_g1/`.
