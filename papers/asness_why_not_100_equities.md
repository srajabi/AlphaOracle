# Why Not 100% Equities

**Citation:** Asness, C. (1996). *Why Not 100% Equities.* Journal of Portfolio
Management 22(2). Updated: AQR Perspective (2023),
[Why Not 100% Equities (again)](https://www.aqr.com/Insights/Perspectives/Why-Not-100-Equities).

**Links:** AQR perspective above; 1996 original is JPM-paywalled (no free PDF
found). Top answer in the r/quant favorite-papers thread.

## Claims

- Investors who want equity-level returns should NOT buy 100% equities:
  a diversified 60/40 levered up to equity volatility historically delivered
  HIGHER returns than 100% stocks at the same risk.
- The objection "I can't/won't use leverage" is the actual constraint - and
  Asness's point is that refusing cheap leverage while accepting concentration
  risk is incoherent: 100% equities IS an aggressive bet, just an inefficiently
  diversified one.
- Direct intellectual opposite of Anarkulova/Cederburg/O'Doherty
  ([beyond_status_quo.md](beyond_status_quo.md)) - this debate is 30 years old.

## Criticisms

- Levered 60/40 IS HFEA-lite - and 2022 demonstrated the failure mode:
  leverage on stocks+bonds when both crash (rising rates) is brutal.
  Asness's reply: still better diversified than 100% equities over full
  cycles; size the leverage modestly.
- Borrow costs at retail (margin/LETF financing ≈ 2x short rate for 3x) eat
  much of the theoretical edge.
- Modern implementations exist as cheap ETFs: NTSX (90/60 stocks/bond
  futures), the "return stacking" lineup (RSST etc.) - retail can now get
  modest leverage without margin accounts.

## AlphaOracle verdict

We tested the thesis without knowing it: `hfea_lite_2x` (2x 55/45 SPY/TLT)
scored Sharpe 0.74 over 21y vs 0.55 for buy-hold SPY - Asness's risk-adjusted
claim held - but with a -49% maxDD including 2022's -41%. At 1x, our
`spy_tlt_60_40` baseline (0.76) also beat SPY's Sharpe.

**Takeaway:** diversification-then-lever beats concentration on Sharpe, as
claimed, BUT unconditional leverage has no crisis brake. Our lab suggests the
modern version should be: diversify, lever modestly, AND gate the leverage
(vol targeting or canary) - see `canary_daa_2x` (Sharpe 1.08, 18% CAGR).
NTSX-style funds are the practical wrapper worth a look for the aggressive
sleeve.
