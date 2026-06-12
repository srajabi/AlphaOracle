# Beyond the Status Quo: A Critical Assessment of Lifecycle Investment Advice

**Citation:** Anarkulova, A., Cederburg, S., & O'Doherty, M. S. (2023).
*Beyond the Status Quo: A Critical Assessment of Lifecycle Investment Advice.*

**Links:** [SSRN 4590406](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4590406)
| PDF: [pdfs/beyond_status_quo_2023.pdf](pdfs/beyond_status_quo_2023.pdf)

## Claims

- A fixed ~33% domestic / 67% international all-equity portfolio dominates
  every stock/bond lifecycle strategy - including in retirement - for wealth,
  capital preservation, and bequests.
- Target-date fund investors need ~63% more savings for the same retirement
  utility.
- Method: block-bootstrap over ~2,500 country-years across 38 developed
  markets (designed to avoid US survivorship bias).

## Criticisms (see ERN's detailed takedown)

- The paper's own US-only table shows 60/40 with a LOWER ruin rate than 100%
  stocks (4.5% vs ~5%).
- Bootstrap mixes post-war Germany/Japan return sequences into the sample.
- Real retirement cohorts (1972, 2000, 2007) did better with bonds; the worst
  equity crashes were deflationary - exactly when bonds shine.
- Compares only static allocations; assumes retirees hold through 50%+
  drawdowns without capitulating.
- ERN critique: [100% Stocks for the Long Run?](https://earlyretirementnow.com/2024/02/12/100-percent-stocks-for-the-long-run/)

## AlphaOracle verdict

Tested with `backtesting/entry_strategies.py --withdrawal-rate 0.04`
(25y retirements, SPY, starts 1993-2001 - every window contains dot-com + GFC):

- 100% equity: **4.5% ruin rate** (matches the paper's US numbers), 5th-pctile
  ending ~1% of starting wealth, maxDD -64%.
- 100% equity + SMA200 overlay: **0% ruin**, maxDD -31%, at the cost of lower
  median ending wealth (1.42x vs 1.89x for at-top retirees).

**Takeaway:** the paper's long-horizon equity logic is real, but sequence risk
at spending horizons is exactly as bad as critics say. Our synthesis: bucket
by horizon, more equity in the long bucket, trend overlay as the disaster
brake. Full analysis: research page section 4; `data/decumulation_spy.json`.
