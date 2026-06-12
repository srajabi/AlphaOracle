# Bold Asset Allocation (BAA)

**Citation:** Keller, W. J. (2022). *Relative and Absolute Momentum in Times
of Rising/Low Yields: Bold Asset Allocation (BAA).*

**Links:** [SSRN 4166845](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4166845)
| [Allocate Smartly review](https://allocatesmartly.com/bold-asset-allocation/)
(SSRN-gated; no free PDF found)

## Claims

- Successor to PAA/VAA/DAA, designed after rising-rate regimes (2022) exposed
  bond-heavy defenses.
- Combines SLOW relative momentum (12-month, for picking risky assets) with
  FAST absolute momentum (13612W, for the canary risk switch).
- Defensive universe is itself momentum-selected and includes cash-like
  assets - the strategy can hide in T-bills when bonds fall (the 2022 fix,
  formalized).
- Two variants: BAA-Aggressive (top-1 of a small risky set) and BAA-Balanced
  (top-6 of a 12-asset set).

## Criticisms

- Published after observing 2022 - the rising-rate robustness is partly
  in-sample by construction.
- Many parameters (universes, lookbacks, top-N) = overfitting surface.
- Allocate Smartly's live tracking shows strong but more modest results than
  the backtest (as with all published TAA).

## AlphaOracle verdict

**Not yet implemented as published.** Independently, our
`canary_daa_smart_defense` converged on BAA's core fix - momentum-select the
defensive asset and allow actual cash - and it repaired 2022 (-6.8% vs -23%)
exactly as BAA's design predicts.

**Next step if pursued:** implement the slow-relative/fast-absolute split
(we currently use 13612W for both decisions) and a top-6 balanced variant.
