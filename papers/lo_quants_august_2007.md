# What Happened to the Quants in August 2007?

**Citation:** Khandani, A. E., & Lo, A. W. (2007/2011). *What Happened to the
Quants in August 2007? Evidence from Factors and Transactions Data.*
Journal of Financial Markets 14(1).

**Links:** [MIT author PDF](https://web.mit.edu/Alo/www/Papers/august07.pdf)
| PDF: [pdfs/lo_quants_august_2007.pdf](pdfs/lo_quants_august_2007.pdf)
| r/quant thread's "easiest read" pick.

## Claims

- In August 2007, market-neutral quant equity funds lost catastrophically in
  THREE DAYS while the overall market was calm - then snapped back.
- Reconstruction: a large multi-strategy fund unwound positions rapidly;
  because everyone's factor models held overlapping positions, the unwind
  cascaded through every quant book simultaneously ("crowded trade
  deleveraging").
- The risk wasn't in any fund's model - it was in everyone running the SAME
  model. Factor crowding is an invisible systemic exposure.

## Criticisms

- Forensic reconstruction from returns, not direct position data - the
  specific unwind narrative is inferred.
- Lessons partially absorbed since (funds now monitor crowding), which itself
  changes the dynamics.

## AlphaOracle verdict

Not a strategy - a WARNING LABEL for our whole library, and the reason our
notes keep repeating "published = crowded." Most applicable lesson: our lab
winners (canary DAA, GTAA, vol targeting) are widely published retail TAA
rules; their failure mode wouldn't be August-2007-style three-day cascades
(monthly rebalancing, liquid ETFs, no leverage-forced unwinds), but
simultaneous regime-flips by thousands of followers on the same month-end
signal could degrade entry prices. One more reason monthly-signal strategies
should execute with limit orders away from the open.

Companion read in the library: [deflated_sharpe.md](deflated_sharpe.md)
(your backtest lies to you) + this paper (your neighbors' positions hurt
you) = the two ways a good-looking strategy fails live.
