# Strategy Tournament Results

Window 2004-11-18 to 2026-03-18, universe of 14 assets, zero-cost base runs.

Census: 65 testable (+6 excluded with reasons). Two divisions - same statistical gates, different risk mandates: CORE (holdable: crisis floor -35%) and AGGRESSIVE (growth: must beat SPY on CAGR AND Sharpe; crisis floor -60%; must recover within ~5y).

## CORE division - 13 champions (of 20 stage-1 survivors)

- **canary_daa_2x**: CAGR 18.0%, Sharpe 1.08 (halves 1.01/1.14), maxDD -36%, worst crisis -23%, breakeven 139bps
- **canary_daa_lite**: CAGR 14.0%, Sharpe 1.06 (halves 1.02/1.10), maxDD -33%, worst crisis -23%, breakeven 141bps
- **canary_daa_low_vol_sleeve**: CAGR 11.6%, Sharpe 0.99 (halves 0.92/1.07), maxDD -26%, worst crisis -14%, breakeven 69bps
- **canary_daa_smart_defense**: CAGR 14.1%, Sharpe 1.04 (halves 0.83/1.27), maxDD -27%, worst crisis -10%, breakeven 156bps
- **canary_daa_vol_target**: CAGR 15.6%, Sharpe 1.08 (halves 1.03/1.13), maxDD -35%, worst crisis -24%, breakeven 133bps
- **changepoint_gated_momentum**: CAGR 8.5%, Sharpe 0.80 (halves 0.64/0.95), maxDD -21%, worst crisis -14%, breakeven 151bps
- **dual_channel_cash_overlay**: CAGR 9.3%, Sharpe 1.07 (halves 1.09/1.05), maxDD -16%, worst crisis -13%, breakeven 354bps
- **gtaa_5_faber**: CAGR 7.2%, Sharpe 0.82 (halves 0.82/0.82), maxDD -12%, worst crisis -3%, breakeven 435bps
- **lab_winners_blend**: CAGR 11.4%, Sharpe 1.19 (halves 1.24/1.14), maxDD -24%, worst crisis -20%, breakeven 252bps
- **regime_defensive_rotation_with_bands**: CAGR 10.7%, Sharpe 0.84 (halves 0.89/0.79), maxDD -32%, worst crisis -21%, breakeven 101bps
- **risk_parity_spy_tlt_gld**: CAGR 9.5%, Sharpe 1.05 (halves 1.13/0.99), maxDD -22%, worst crisis -20%, breakeven 992bps
- **spy_gld_switch**: CAGR 12.2%, Sharpe 0.82 (halves 0.95/0.69), maxDD -28%, worst crisis -14%, breakeven 228bps
- **trinity_blend**: CAGR 9.2%, Sharpe 0.79 (halves 0.69/0.90), maxDD -32%, worst crisis -31%, breakeven 1101bps

### Fell at stage 2 (core)

- hfea_55_45: D2 crisis floor (worst -65% < -35%)
- hfea_lite_2x: D2 crisis floor (worst -48% < -35%)
- reddit_200sma_tqqq: D2 crisis floor (worst -62% < -35%)
- regime_defensive_rotation_with_bands_2x: D2 crisis floor (worst -38% < -35%)
- regime_defensive_rotation_with_bands_3x: D2 crisis floor (worst -53% < -35%)
- vol_target_qqq_2x: D2 crisis floor (worst -38% < -35%)
- vol_target_spy_15: D2 crisis floor (worst -36% < -35%)

## AGGRESSIVE division - 15 champions (of 17 stage-1 survivors)

- **canary_daa_2x**: CAGR 18.0%, Sharpe 1.08 (halves 1.01/1.14), maxDD -36%, worst crisis -23%, breakeven 139bps
- **canary_daa_lite**: CAGR 14.0%, Sharpe 1.06 (halves 1.02/1.10), maxDD -33%, worst crisis -23%, breakeven 141bps
- **canary_daa_low_vol_sleeve**: CAGR 11.6%, Sharpe 0.99 (halves 0.92/1.07), maxDD -26%, worst crisis -14%, breakeven 69bps
- **canary_daa_smart_defense**: CAGR 14.1%, Sharpe 1.04 (halves 0.83/1.27), maxDD -27%, worst crisis -10%, breakeven 156bps
- **canary_daa_vol_target**: CAGR 15.6%, Sharpe 1.08 (halves 1.03/1.13), maxDD -35%, worst crisis -24%, breakeven 133bps
- **hfea_lite_2x**: CAGR 15.6%, Sharpe 0.79 (halves 0.85/0.74), maxDD -49%, worst crisis -48%, breakeven 9999bps
- **lab_winners_blend**: CAGR 11.4%, Sharpe 1.19 (halves 1.24/1.14), maxDD -24%, worst crisis -20%, breakeven 252bps
- **reddit_200sma_spy**: CAGR 23.3%, Sharpe 0.78 (halves 0.81/0.76), maxDD -58%, worst crisis -50%, breakeven 1122bps
- **regime_defensive_rotation_with_bands**: CAGR 10.7%, Sharpe 0.84 (halves 0.89/0.79), maxDD -32%, worst crisis -21%, breakeven 101bps
- **regime_defensive_rotation_with_bands_2x**: CAGR 20.5%, Sharpe 0.84 (halves 0.89/0.79), maxDD -56%, worst crisis -38%, breakeven 101bps
- **regime_defensive_rotation_with_bands_3x**: CAGR 28.8%, Sharpe 0.84 (halves 0.89/0.79), maxDD -72%, worst crisis -53%, breakeven 101bps
- **spy_gld_switch**: CAGR 12.2%, Sharpe 0.82 (halves 0.95/0.69), maxDD -28%, worst crisis -14%, breakeven 228bps
- **tqqq_sma_vix_filter**: CAGR 27.3%, Sharpe 0.78 (halves 0.72/0.83), maxDD -63%, worst crisis -52%, breakeven 190bps
- **vol_target_qqq_2x**: CAGR 17.9%, Sharpe 0.88 (halves 0.77/0.99), maxDD -39%, worst crisis -38%, breakeven 177bps
- **vol_target_spy_15**: CAGR 11.5%, Sharpe 0.79 (halves 0.67/0.91), maxDD -36%, worst crisis -36%, breakeven 188bps

### Fell at stage 2 (aggressive)

- hfea_55_45: D2 crisis floor (worst -65% < -60%)
- reddit_200sma_tqqq: D2 crisis floor (worst -62% < -60%)

## Excluded (with reasons)

- advanced_llm (dev account): live LLM decisions - no deterministic signal function to backtest
- llm_recommendations (account 1): live LLM decisions - no deterministic signal function to backtest
- entry strategies (lump sum/DCA/...): capital-deployment rules, not portfolios - tested in entry_strategies.py across start-date cohorts instead
- decumulation rules (4% + overlays): withdrawal framework - tested in entry_strategies.py --withdrawal-rate instead
- overnight/intraday legs: need open prices; engine is close-to-close - tested in overnight_decomposition.py instead
- options/VRP strategies: no historical chain data yet (awaiting user's data purchase)
