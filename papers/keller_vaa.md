# Vigilant Asset Allocation (VAA)

**Citation:** Keller, W. J., & Keuning, J. W. (2017). *Breadth Momentum and
Vigilant Asset Allocation (VAA).*

**Links:** [SSRN 2959708](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2959708)
| [Allocate Smartly review](https://allocatesmartly.com/vigilant-asset-allocation-dr-wouter-keller-jw-keuning/)
(SSRN-gated; no free PDF found)

## Claims

- Aggressive monthly all-in rotation: hold the single best offensive asset
  (SPY/EFA/EEM/AGG in VAA-G4) by 13612W momentum - but if ANY offensive asset
  has negative momentum, flee 100% to the best defensive asset (LQD/IEF/SHY).
- "Breadth momentum": the count of weak assets, not just the average, signals
  regime danger.
- 13612W momentum = (12·r1m + 4·r3m + 2·r6m + 1·r12m)/19 - fast-weighted.

## Criticisms

- Extremely concentrated (one asset at a time) - high tracking error, single
  bad month hurts.
- The any-negative trigger is twitchy; in mixed regimes it spends most of its
  time in defense.
- Heavily backtest-tuned universe; sensitive to asset substitutions.

## AlphaOracle verdict

`keller_vaa_lite` (offense SPY/EWA/VGK, defense TLT/GLD - proxy-limited,
2005-2026): **Sharpe 0.49, worse than 60/40.**

Our offensive proxies are the problem: EWA and VGK are weak stand-ins for
EFA/EEM, and with chronically lagging intl equities the any-negative trigger
kept the strategy defensive through US bull legs. The DAA successor (separate
canary basket) fixed exactly this flaw - and dominated our lab. See
[keller_daa.md](keller_daa.md).

**Takeaway:** the breadth-momentum idea is right (proved by DAA); VAA's
specific all-or-nothing form doesn't survive proxy substitution. Results:
`backtesting/results_lab_g5/`.
