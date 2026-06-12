# A Quantitative Approach to Tactical Asset Allocation (QTAA / GTAA)

**Citation:** Faber, M. (2007, updated 2013). *A Quantitative Approach to
Tactical Asset Allocation.* Journal of Wealth Management.

**Links:** [SSRN 962461](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461)
| [Author FAQ/update](https://mebfaber.com/2013/06/14/qtaa-update-conclustions-and-faqs/)
| PDF: [pdfs/faber_qtaa_2013.pdf](pdfs/faber_qtaa_2013.pdf)

## Claims

- Hold each of 5 asset classes (US stocks, intl stocks, bonds, gold/commodities,
  REITs) only while above its own 10-month SMA (~200d), evaluated monthly;
  the sleeve goes to cash otherwise.
- Result (per paper): equity-like returns with bond-like volatility;
  max drawdown cut from ~46% to single digits.
- Monthly evaluation is deliberate: it cuts whipsaw versus daily signals.

## Criticisms

- Vulnerable to fast crashes between month-ends (COVID-style gaps).
- Cash sleeves drag in long bull markets (big upside sacrifice).
- Published 2007 - widely known/crowded since; live results post-publication
  have been weaker than the backtest.

## AlphaOracle verdict

`gtaa_5_faber` (SPY/EWA/TLT/GLD/XLE adaptation, 2004-2026):

- **-12.0% max drawdown over 21 years** - the defense champion of the strategy
  lab, almost exactly matching the paper's single-digit claim.
- CAGR 7.2%, Sharpe 0.80: the price of that safety is ~3%/yr vs SPY.
- 2022: -0.1% (best of everything tested); COVID crash maxDD -6.7%.
- Separately, `sma200_monthly_spy` validated the monthly-evaluation claim:
  Sharpe 0.79 with 41 trades/33y vs the daily version's ~99 trades and lower
  Sharpe.

**Takeaway:** confirmed as advertised. Use when drawdown minimization is the
binding constraint. Results: `backtesting/results_lab_g3/`, `results_lab_g1/`.
