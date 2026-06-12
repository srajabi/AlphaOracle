# Allocation Study (2026-06): Two Mandates, One Family

**NOT financial advice.** AlphaOracle is research infrastructure and no one
here is a licensed advisor. This document evaluates the STRUCTURES the user
proposed against our own backtest evidence and states the open questions
that belong to a fee-only planner (especially for the near-retirement
household). Dollar decisions are the family's.

Scenario as described: ~$2M investable across the family. Younger investor
~$750k (≈$600k cash), risk-willing. Parents (55/60) ~$1.25M (≈$1M cash) +
$600k home, intending to work "until they can't." Inflation 4.2%; thesis
doc scenario weights: grind 50 / slow bear 30 / fast crash 20.

## Fact zero: cash is a position, and it's losing

At 4.2% CPI, $1.6M cash loses ~$25-45k/yr in real terms even with interest.
Our entry research says the cost of WAITING is real and the protection
from DCA is mostly psychological. Doing nothing is not the safe option;
it's a ~-1.5%/yr real bet on a crash arriving soon.

## Question 1: "100% XEQT for mom/dad?"

What the evidence says about that structure (not about your parents):

| At-top entry, 5y horizon | Median | Worst case | Worst maxDD |
|---|---|---|---|
| 100% equity (SPY proxy) | 1.73x | 0.82x | -55% |
| 75/25 | 1.60x | 0.94x | -40% |
| 60/40 | 1.50x | 1.05x | -30% |
| 60/40 + SMA200 overlay | 1.41x | **1.21x** | **-11%** |
| 75/25 + SMA200 overlay | 1.47x | **1.16x** | **-17%** |

- The Cederburg case FOR heavy equity at their age is real (finding #2:
  long horizons favor equity; bonds hedge inflation poorly - and we're IN
  an inflation regime). 100% XEQT is not crazy for people working 10+ more
  years.
- The case AGAINST is not returns - it's that **"working until they can't"
  makes the horizon STOCHASTIC**. Health events don't schedule themselves;
  if work stops the year after a -40% drawdown begins, sequence risk
  arrives with no recovery runway (finding #2: all-equity 4% rule ruin
  4.5%, 5th-percentile retiree ended with ~1%). A 55/60-year-old's true
  horizon is "probably 15 years, possibly 18 months."
- Two structures from our registry address exactly that profile without
  giving up the equity engine:
  a) **Equity-heavy + trend overlay** (75/25 + SMA200: worst at-top 5y
     outcome +16%, maxDD -17%) - keeps most upside, truncates the
     sequence-risk tail, costs ~0.13x median.
  b) **Core tournament champions** (canary smart_defense, dual_channel,
     blend): Sharpe 1.0-1.2, worst crisis -7 to -20%, all currently
     forward-testing on paper.
- Also structural, before any ticker: TFSA/RRSP room first (placement >
  product, finding: high-turnover only viable registered), 1-2 years of
  expenses liquid if work could stop, and note the home already makes
  their net worth ~32% real estate.

## Question 2: "Me: 80% XEQT + a crazier strategy?"

Core-satellite is exactly what the tournament's two divisions were built
for. Properties of the proposed structure (from scoreboard v4):

- 80% XEQT: maxDD ~-34% (2010+ era; -55% in GFC-class events), CAGR ~8-10%.
- 20% aggressive champion (e.g. canary_daa_2x: 18% CAGR backtest, -36%
  maxDD, GFC +13%, downside-corr to SPY ~0.21): because the satellite's
  downside correlation is LOW, the blend's drawdown is typically BETTER
  than 80% of XEQT's alone, while adding ~1.5-2pts of expected CAGR.
- The riskier satellites (vol_target_qqq_2x, regime_bands_3x) passed the
  aggressive division but carry -38 to -53% worst-crisis losses and
  -45% gap risk at 3x - sized at 10-20% of a portfolio those are
  survivable; sized bigger they're account-killers. The tournament's
  division gates ARE the sizing argument.
- Caveats that always apply: backtests are zero-cost, the 2004+ window is
  gold-friendly, and published strategies decay (PBO 0.36 = rankings are
  signal, not certainty). The paper accounts + attribution monitor exist
  to test exactly this before real dollars do.

## Question 3: how to enter, given the thesis (BoJ + war + IPO week)

Findings #1 stands regardless of the news: lump-sum wins the median even
at tops; DCA's protection is psychological; what truncates tails is the
ONGOING overlay/strategy, not the entry schedule. With scenario C at 20%
and three catalysts in one week, a 3-6 month DCA is a cheap psychological
hedge (costs ~1-2% of median outcome) - fine. What matters more: whatever
runs the money (overlay or champion strategy) should be LIVE FROM THE
FIRST TRANCHE, so a fast crash mid-deployment triggers de-risking rules
instead of panic.

## For a licensed planner (the list our research can't answer)

Parents' exact risk capacity (true expenses, pensions/CPP/OAS timing,
health/disability insurance, wills/estate), TFSA/RRSP contribution room
for all three, whether the home factors into retirement plans, and
spousal/family income-splitting. None of this is modelable from here, and
all of it changes the right answer.

## What we CAN do next (in scope)

1. Keep the paper accounts proving the champions (attribution monitor
   live as of this week).
2. Add a "family dashboard" view if real accounts ever connect (read-only
   aggregation).
3. Re-run this study's tables when the July thesis review updates scenario
   weights.
