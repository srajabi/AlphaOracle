# Continuous Cash-Overlay Filters for a Static Growth-Defensive Risk Sleeve

**Citation:** Xiong, Z. (2026). *Continuous Cash-Overlay Filters for a Static
Growth-Defensive Risk Sleeve.* arXiv working paper.

**Links:** [arXiv 2606.09025](https://arxiv.org/abs/2606.09025)
| PDF: [pdfs/cash_overlay_filters_2026.pdf](pdfs/cash_overlay_filters_2026.pdf)
| Found scanning arXiv q-fin.PM recent (2026-06).

## Claims

- Two CONTINUOUS (not binary) cash-overlay filters on a static 50/50
  growth/defensive ETF sleeve:
  1. "Slow-tail compensation" - shifts toward cash as cash yields rise and
     the sleeve's risk-adjusted return deteriorates,
  2. "V-shape crash-brake" - fast de-risk on rapid drawdowns with explicit
     re-entry timing.
  Combined by a max-cash rule (take the larger cash weight daily).
- Reported (2017-2026): 20.45% CAGR vs 16.62% static, maxDD -16.8% vs -33.6%;
  walk-forward OOS 18.05% CAGR, -22.1% maxDD.
- Signals: VIX, rates, credit stress.

## Criticisms

- 9-year backtest, recent-period only (no GFC, no dot-com).
- Author concedes multiple-testing-adjusted inference is future work - the
  exact failure mode the [deflated Sharpe](deflated_sharpe.md) paper warns
  about.
- Working paper, not peer-reviewed; single author.

## AlphaOracle verdict

**Not yet implemented.** Interesting to us for two design ideas we haven't
tested rather than the headline numbers:

1. CONTINUOUS cash fraction (our overlays are mostly binary or 3-step;
   `mom_ensemble_spy` and `composite_regime_spy` are our closest analogues
   and both showed graded exposure is viable),
2. Distinct slow vs fast de-risking channels combined by max() - our
   `target_dd_guard_spy` has the fast brake but no slow channel.

**TESTED (2026-06, `dual_channel_cash_overlay` in portfolio_strategies.py)**
on 2004+ - through the GFC the paper never saw:

- Full sample: 9.3% CAGR, Sharpe 1.07, **maxDD -15.8%** (vs SPY -55%)
- GFC: -5.8% | COVID crash maxDD: -14.1% | 2022: -12.7%

The max(slow, fast) two-channel design GENERALIZES - single-digit-to-teens
losses in all three crisis shapes, which no single-channel strategy in our
lab achieved. Returns are defensive-class (like GTAA) but with ~2pts more
CAGR. The paper's specific 2017+ numbers remain untrustworthy, but its
architecture is validated and adopted. Best defensive candidate in the lab
alongside gtaa_5_faber.
