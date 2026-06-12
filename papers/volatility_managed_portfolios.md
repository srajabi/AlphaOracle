# Volatility-Managed Portfolios

**Citation:** Moreira, A., & Muir, T. (2017). *Volatility-Managed Portfolios.*
Journal of Finance 72(4). (NBER WP 22208.)

**Links:** [NBER WP](https://www.nber.org/papers/w22208)
| PDF: [pdfs/volatility_managed_portfolios_2017.pdf](pdfs/volatility_managed_portfolios_2017.pdf)

## Claims

- Scaling exposure by the inverse of recent realized variance increases Sharpe
  ratios and alpha across factors (market, value, momentum...).
- Works because volatility spikes don't come with proportionally higher
  expected returns - so de-levering in storms costs little expected return
  while cutting a lot of risk.
- Contradicts naive risk-return intuition; robust across markets.

## Criticisms

- High turnover: daily/weekly exposure adjustments (transaction costs eat the
  edge in less liquid implementations).
- Later replications (e.g. Cederburg et al. 2020) find the effect weaker
  out-of-sample and sensitive to implementation details.
- Tail behavior: de-levers AFTER vol arrives - doesn't protect against the
  first gap day (COVID Feb 2020).

## AlphaOracle verdict

`vol_target_spy_15` (15% target, cap 1.5x) and `vol_target_qqq_2x`
(20% target, cap 2x):

- SPY 1993-2026: CAGR 10.8% (ABOVE buy-and-hold's 10.5%), Sharpe 0.71 vs 0.56.
  MaxDD only modestly better (-47% vs -55%) - it de-levers late in slow bears.
- QQQ 1999-2026 (the acid test): Sharpe 0.67 / -57% maxDD vs the Reddit
  TQQQ-SMA rule's 0.36 / -90%. **The only leverage scheme tested that
  survived the dot-com crash.**
- Cost: ~6,000 daily exposure adjustments; implementable with futures/margin,
  expensive as LETF switches.

**Takeaway:** validated, especially as the safe way to run leverage. Best
combined with a trend filter rather than replacing one. Results:
`backtesting/results_lab_g1/`, `results_lab_g2/`.
