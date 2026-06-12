# Strategy Lab (2026-06): 26 Strategies Researched + Backtested

**Goal:** minimize downturns, maximize returns. Researched the published TAA
literature (Faber GTAA, Antonacci GEM, Keller VAA/DAA/BAA canary universe,
vol-targeting), implemented 23 new strategies plus 3 second-generation hybrids,
and backtested everything against the always-on baselines with crisis-regime
stress tests.

All runs: zero transaction costs, signals computed on full history (no warmup
artifacts), monthly strategies trade the first session after month-end signal.
Full scoreboard: `backtesting/results_lab_final/scoreboard.csv`.

## The scoreboard (full sample, ranked by Sharpe)

| Rank | Strategy | Window | CAGR | Sharpe | MaxDD | Trades |
|---|---|---|---|---|---|---|
| 1 | **lab_winners_blend** | 2004+ | 11.4% | **1.21** | -23.7% | 254 |
| 2 | canary_daa_vol_target | 2004+ | 15.6% | 1.09 | -34.7% | 1826 |
| 3 | **canary_daa_2x** | 2004+ | **18.0%** | 1.08 | -36.1% | 183 |
| 4 | canary_daa_lite | 2004+ | 14.0% | 1.06 | -33.0% | 183 |
| 5 | risk_parity_spy_tlt_gld | 2004+ | 9.5% | 1.05 | -22.2% | 254 |
| 6 | permanent_portfolio | 2004+ | 7.1% | 0.97 | -17.5% | 0 |
| 7 | all_weather_lite | 2004+ | 8.7% | 0.91 | -20.8% | 0 |
| 8 | **gtaa_5_faber** | 2004+ | 7.2% | 0.80 | **-12.0%** | 126 |
| 9 | sma200_monthly_spy | 1993+ | 10.0% | 0.79 | -25.5% | 41 |
| 10 | spy_gld_switch | 2004+ | 12.2% | 0.78 | -28.0% | 73 |
| ... | buy_hold_spy (baseline) | | 10.4% | 0.55 | -55.2% | 0 |

Bottom of the table (what FAILED): tqqq_sma_vix_filter (0.27, -95% DD),
reddit_200sma_tqqq *from 1999* (0.36, -90% DD), dd_guard_qqq_2x (0.39, -85%),
donchian_55_20 (0.40), gem_dual_momentum (0.45 - EWA proxy too weak),
keller_vaa_lite (0.49 - same proxy problem), vix_spike_buyer (0.51, -67% DD).

## Crisis stress tests (the point of the exercise)

| Strategy | GFC 2008 | COVID crash maxDD | 2022 bear | AI bull CAGR |
|---|---|---|---|---|
| canary_daa_2x | **+12.6%** | -12.4% | -23.1% | +24.3% |
| canary_daa_lite | +6.6% | -12.4% | -23.1% | +18.5% |
| gtaa_5_faber | -0.0% | **-6.7%** | **-0.1%** | +4.1% |
| risk_parity | +2.9% | -13.5% | -19.5% | +14.9% |
| lab_winners_blend | +2.1% | -10.8% | -19.9% | +17.1% |
| spy_gld_switch | +10.5% | -18.2% | -9.6% | +11.0% |
| buy_hold_spy | -55% | -33.4% | -24.5% | +25.9% |

## Key findings

1. **The canary universe (Keller DAA) was the single best idea tested.**
   13612W momentum on a 2-asset canary basket (EWA+TLT) deciding the cash
   fraction, top-2 momentum picks for the risky sleeve. It was POSITIVE
   through the GFC and captured most of the AI bull. The levered variant
   (canary_daa_2x: 1.5x sleeve when both canaries are positive) added 4% CAGR
   for ~3pts of drawdown.
2. **Blending uncorrelated decision engines beats any single engine.**
   40% canary DAA + 30% risk parity + 30% monthly SMA200 = Sharpe 1.21 with
   -24% maxDD - the best risk-adjusted result in the lab.
3. **Monthly evaluation beats daily for trend rules.** sma200_monthly (41
   trades/33y, Sharpe 0.79) vs daily sma_200_trend (~99 trades, lower Sharpe).
   Faber was right about whipsaw reduction.
4. **Vol targeting is the only leverage approach that survived the dot-com
   test.** vol_target_qqq_2x from 1999: Sharpe 0.67 / -57% DD vs the Reddit
   TQQQ rule's 0.36 / -90%. Leverage gated by realized vol >> leverage gated
   by trend alone. (Caveat: daily exposure adjustment - needs futures or
   cheap margin to implement; as an LETF approximation, expect slippage.)
5. **2022 is the canary strategies' kryptonite** - the defensive asset (TLT)
   crashed with stocks. GTAA's per-sleeve trend filter handled 2022 best
   (-0.1%). A canary variant with GLD/cash defense instead of TLT is the
   obvious next experiment.
6. **Confirmed failures worth remembering:** VIX-laddered leverage made
   things worse (re-levering into bear rallies); buying VIX spikes with
   leverage deepens drawdowns; Donchian channels and GEM-with-EWA-proxy
   underperform simple trend rules on this data.

## Honest caveats

- The multi-asset window (2004+) coincides with a gold bull; GLD-heavy
  strategies are flattered. SPY-only results (1993+) are more robust.
- Zero fees + frictionless monthly rebalancing; momentum/TAA strategies are
  widely published (crowding risk); cash sleeves earn 0% in the engine
  (conservative for the defensive strategies).
- All of this is regime-dependent. The same caveat that applied to
  reddit_200sma_tqqq applies here: 2004-2026 contained specific crisis
  shapes (slow GFC, fast COVID, correlated 2022). A new shape can break any
  of these rules.

## Round 3: closing the 2022 hole

`canary_daa_smart_defense` routes the defensive fraction to the better of
TLT/GLD by momentum - and to actual cash when both are negative:

| | Full CAGR | Full maxDD | 2022 | GFC |
|---|---|---|---|---|
| canary_daa_lite | 14.0% | -33.0% | -23.1% | +6.6% |
| canary_daa_smart_defense | 14.1% | **-27.3%** | **-6.8%** | -11.0% |

Same return, smaller worst drawdown, 2022 fixed; the price is giving back some
GFC alpha (when TLT was the perfect defense). More balanced across crisis
shapes - the better default.

## Recommended forward-test candidates

- **Balanced (best all-around):** lab_winners_blend - Sharpe 1.21, -24% DD
- **Aggressive:** canary_daa_2x - 18% CAGR with GFC-positive history
- **Crisis-balanced:** canary_daa_smart_defense - 14.1% CAGR, no regime worse than -27%
- **Defensive:** gtaa_5_faber - never lost more than 12% in 21 years
- Accounts 4/5 are reserved for future strategies - these are the candidates.
