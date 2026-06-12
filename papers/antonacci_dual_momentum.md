# Dual Momentum (GEM - Global Equities Momentum)

**Citation:** Antonacci, G. (2012). *Risk Premia Harvesting Through Dual
Momentum.* (Expanded in *Dual Momentum Investing*, McGraw-Hill 2014.)

**Links:** [SSRN 2042750](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750)
| [Author site](https://www.optimalmomentum.com/)
(SSRN-gated; no free PDF found)

## Claims

- Combine RELATIVE momentum (pick the stronger of US vs international
  equities by 12-month return) with ABSOLUTE momentum (if the winner's
  12-month excess return over T-bills is negative, hold bonds instead).
- Absolute momentum provides the crash protection; relative momentum provides
  the upside selection.
- GEM backtest (1974-2013): ~17% CAGR with roughly half the drawdown of
  equities.

## Criticisms

- Post-publication decade was rough: international equities chronically
  lagged the US, so relative momentum whipsawed between markets while plain
  S&P buy-and-hold won.
- Binary monthly all-in switches = high tracking-error regret.
- The T-bill hurdle matters; implementations using 0% understate defense.

## AlphaOracle verdict

`gem_dual_momentum` (SPY vs EWA, TLT fallback, 2004-2026): **Sharpe 0.45 -
worst multi-asset strategy in our lab.**

Two implementation gaps explain it: EWA (Australia) is a poor proxy for broad
international equities, and our 0% cash hurdle weakens the absolute-momentum
gate. Even so, the known post-2010 GEM weakness (US-intl whipsaw) is the
dominant cause - our `tsmom_12_1_spy` (absolute momentum only, no relative
leg) scored 0.71 on a longer window.

**Takeaway:** absolute momentum validated; the relative US-vs-intl leg has
been the weak link for 15 years. Revisit with VXUS (2011+) or VGK if intl
leadership returns. Results: `backtesting/results_lab_g3/`.
