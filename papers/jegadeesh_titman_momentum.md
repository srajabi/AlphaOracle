# Returns to Buying Winners and Selling Losers (Cross-Sectional Momentum)

**Citation:** Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners
and Selling Losers: Implications for Stock Market Efficiency.* Journal of
Finance 48(1).

**Links:** [Hosted PDF (U. Houston)](https://www.bauer.uh.edu/rsusmel/phd/jegadeesh-titman93.pdf)
| PDF: [pdfs/jegadeesh_titman_1993.pdf](pdfs/jegadeesh_titman_1993.pdf)
| The canonical r/quant "papers that made money" answer.

## Claims

- Stocks with the best 3-12 month past returns outperform the worst over the
  next 3-12 months (~1%/month long-short), 1965-1989 US equities.
- The effect partially reverses beyond ~12 months (distinct from long-term
  reversal and short-term reversal).
- Foundation of the entire momentum literature - later confirmed across
  countries, asset classes, and centuries of data (Geczy & Samonov).

## Criticisms

- Momentum crashes: the long-short factor lost ~70%+ in 1932 and 2009
  rebounds (short leg rips). Raw momentum has fat left tails.
- High turnover; after costs the retail-implementable share shrinks.
- Post-2000 US momentum factor returns weakened substantially.

## AlphaOracle verdict

The intellectual ancestor of half our lab. Our implementations are
TIME-SERIES and CROSS-ASSET variants rather than single-stock long-short:
relative momentum in `canary_daa_lite` (top-2 of 4 assets, 13612W),
`sector_momentum_top3_filtered` (Sharpe 0.56), `top2_relative_strength`
(0.62), `spy_gld_switch` (0.78).

Pattern across our results: momentum SELECTION works best when paired with an
absolute/trend FILTER (the canary or an SMA) - naked relative momentum
(top2_relative_strength, GEM) was mid-table. Consistent with the momentum-
crash literature: the filter is what removes the left tail.

No plan to implement single-stock long-short momentum (no shorting in the
paper-trading setup; turnover too high).
