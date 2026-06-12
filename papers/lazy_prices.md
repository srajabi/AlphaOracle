# Lazy Prices

**Citation:** Cohen, L., Malloy, C., & Nguyen, Q. (2020). *Lazy Prices.*
Journal of Finance 75(3). (NBER WP 25084, 2018.)

**Links:** [NBER WP](https://www.nber.org/papers/w25084)
| PDF: [pdfs/lazy_prices_2018.pdf](pdfs/lazy_prices_2018.pdf)
| Found via r/quant "papers that translate into strategies" thread.

## Claims

- Firms whose 10-K/10-Q filings CHANGE in language relative to the prior
  year subsequently underperform firms with unchanged filings by
  ~30-60 bps/month (changers signal trouble; markets underreact because
  nobody reads the documents).
- The effect concentrates in changes to risk-factor sections and negative-
  sentiment language; returns drift for months (slow information diffusion).
- One of the cleanest "alternative data" results - the data (EDGAR filings)
  is free and public.

## Criticisms

- Well-known since 2018; NLP-based filing analysis is now standard at quant
  funds - expect substantial decay.
- Single-stock long-short with hundreds of names; turnover and shorting
  costs are material.
- Document-similarity choices (cosine vs Jaccard, section scoping) move the
  results.

## AlphaOracle verdict

**Not implementable in our current setup** - requires single-stock
positions, shorting, and an EDGAR NLP pipeline; our system trades ETFs long
only. Kept in the library because it's the canonical proof that public text
+ patience = alpha, and because a long-only, watchlist-scoped version
(flagging our 25 single stocks whose filings changed materially) could
someday feed the LLM analysts as a risk signal rather than a strategy.
