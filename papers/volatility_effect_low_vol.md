# The Volatility Effect: Lower Risk Without Lower Return

**Citation:** Blitz, D., & van Vliet, P. (2007). *The Volatility Effect:
Lower Risk Without Lower Return.* Journal of Portfolio Management 34(1).
Companion: Blitz & van Vliet (2008), *Global Tactical Cross-Asset Allocation*
(free PDF below).

**Links:** [SSRN 980865](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865)
(gated) | GTCAA PDF: [pdfs/robeco_gtcaa_2008.pdf](pdfs/robeco_gtcaa_2008.pdf)
| Found via [Robeco's most-important-papers list](https://www.robeco.com/en-us/about-us/key-strengths/quant/our-most-important-quant-papers).

## Claims

- **The low-volatility anomaly:** stocks with the LOWEST historical
  volatility earn similar or higher returns than high-vol stocks - the
  opposite of CAPM. Global, persistent since the 1930s (van Vliet's later
  work), strongest on a risk-adjusted basis.
- Behavioral explanations: lottery preference for high-vol stocks, leverage
  constraints (investors reach for beta instead of levering low-beta),
  benchmark-relative career risk for managers.
- GTCAA companion: value + momentum signals work ACROSS asset classes
  (12 assets), not just within equity universes - independent support for
  the cross-asset rotation our lab uses.

## Criticisms

- Low-vol funds (USMV etc.) absorbed huge AUM post-2010; valuation-dependent
  crowding episodes (2016, 2020 drawdown was NOT mild for min-vol funds).
- Overlaps with value/quality/duration exposures - debated how much is a
  distinct factor.

## AlphaOracle verdict

**Partially validated by accident:** our defensive sleeves lean on XLU/XLP
(the lowest-vol sectors) and `risk_parity_spy_tlt_gld` (inverse-vol
weighting IS a low-vol tilt across assets) - Sharpe 1.05, the lab's #5.

**Not yet tested directly:** a min-vol equity sleeve (USMV-style) as the
growth engine of a defensive allocation - we lack USMV history in the repo
(2011+ only via download). Flagged as a round-4-adjacent idea: compare
SPLV/USMV-proxy (inverse-vol weighted sector basket from our 9 SPDRs,
1999+) vs SPY as the risky sleeve inside canary DAA.
