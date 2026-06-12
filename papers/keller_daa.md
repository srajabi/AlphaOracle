# Defensive Asset Allocation (DAA) - the Canary Universe

**Citation:** Keller, W. J., & Keuning, J. W. (2018). *Breadth Momentum and
the Canary Universe: Defensive Asset Allocation (DAA).*

**Links:** [SSRN 3212862](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3212862)
| [TuringTrader review](https://www.turingtrader.com/portfolios/keller-defensive-asset-allocation/)
(SSRN-gated; no free PDF found)

## Claims

- Key innovation over VAA: separate the SIGNAL universe from the TRADED
  universe. A small "canary" basket (VWO + BND) decides risk posture by
  13612W momentum breadth; capital is deployed elsewhere.
- Canary breadth → cash fraction: 0 negative = fully risk-on, 1 = 50%
  defensive, 2 = fully defensive.
- Risky capital goes to the top-N momentum assets of a broad offensive set.
- EM equities + aggregate bonds are chosen as canaries because they're the
  most rate/risk-sensitive assets - they break first.

## Criticisms

- Canary choice is itself a fitted parameter (why VWO+BND and not others?).
- Monthly cadence misses gap crashes (COVID hit between rebalances).
- Defensive asset selection still matters: 2022 punished anything that fled
  to long bonds.

## AlphaOracle verdict

**The best idea in our entire strategy lab.** Adaptations (canary EWA+TLT,
risky SPY/QQQ/GLD/XLE, 2004-2026):

| Variant | CAGR | Sharpe | MaxDD | Notes |
|---|---|---|---|---|
| canary_daa_lite | 14.0% | 1.06 | -33% | +12.6% through GFC (2x: positive) |
| canary_daa_2x | 18.0% | 1.08 | -36% | 1.5x sleeve when both canaries positive |
| canary_daa_smart_defense | 14.1% | 1.03 | -27% | defense = best of TLT/GLD/cash; fixed 2022 (-6.8% vs -23%) |
| lab_winners_blend (40% DAA) | 11.4% | **1.21** | -24% | blended with risk parity + SMA200 |

All beat SPY's 10.4% CAGR / 0.55 Sharpe / -55% maxDD on the same window.

**Caveats:** 2004+ window includes a gold bull (GLD in the risky basket is
flattered); published strategy = crowding risk; monthly cadence gap risk.

**Takeaway:** validated and adopted - forward-test candidate for Alpaca
accounts 4/5. Results: `backtesting/results_lab_final/`, `results_lab_v2/`.
