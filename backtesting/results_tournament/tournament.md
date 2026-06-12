# Strategy Tournament Results

Window 2004-11-18 to 2026-03-18, universe of 14 assets, zero-cost base runs.

```
  CENSUS     65 testable  (+6 excluded with reasons)
  STAGE 1    20 promoted  (gates: bootstrap, DSR, cost, beat-60/40)
  STAGE 2    13 champions (gates: split-sample, crisis floor, 10bps, lag, gap)
```

## Champions

- **canary_daa_2x**: Sharpe 1.08 (halves 1.01/1.14), CAGR 18.0%, maxDD -36%, breakeven 139bps, crises {'gfc_bear': 0.1399, 'covid_crash': -0.0116, 'inflation_bear_2022': -0.2344}
- **canary_daa_lite**: Sharpe 1.06 (halves 1.02/1.10), CAGR 14.0%, maxDD -33%, breakeven 141bps, crises {'gfc_bear': 0.0744, 'covid_crash': -0.0116, 'inflation_bear_2022': -0.2344}
- **canary_daa_low_vol_sleeve**: Sharpe 0.99 (halves 0.92/1.07), CAGR 11.6%, maxDD -26%, breakeven 69bps, crises {'gfc_bear': -0.1213, 'covid_crash': -0.1422, 'inflation_bear_2022': -0.0919}
- **canary_daa_smart_defense**: Sharpe 1.04 (halves 0.83/1.27), CAGR 14.1%, maxDD -27%, breakeven 156bps, crises {'gfc_bear': -0.1027, 'covid_crash': -0.0116, 'inflation_bear_2022': -0.0671}
- **canary_daa_vol_target**: Sharpe 1.08 (halves 1.03/1.13), CAGR 15.6%, maxDD -35%, breakeven 133bps, crises {'gfc_bear': 0.049, 'covid_crash': -0.0328, 'inflation_bear_2022': -0.2408}
- **changepoint_gated_momentum**: Sharpe 0.80 (halves 0.64/0.95), CAGR 8.5%, maxDD -21%, breakeven 151bps, crises {'gfc_bear': -0.1397, 'covid_crash': -0.1124, 'inflation_bear_2022': -0.1261}
- **dual_channel_cash_overlay**: Sharpe 1.07 (halves 1.09/1.05), CAGR 9.3%, maxDD -16%, breakeven 354bps, crises {'gfc_bear': -0.0566, 'covid_crash': -0.135, 'inflation_bear_2022': -0.1323}
- **gtaa_5_faber**: Sharpe 0.82 (halves 0.82/0.82), CAGR 7.2%, maxDD -12%, breakeven 435bps, crises {'gfc_bear': 0.0025, 'covid_crash': -0.0308, 'inflation_bear_2022': -0.0017}
- **lab_winners_blend**: Sharpe 1.19 (halves 1.24/1.14), CAGR 11.4%, maxDD -24%, breakeven 252bps, crises {'gfc_bear': 0.0241, 'covid_crash': -0.0684, 'inflation_bear_2022': -0.2015}
- **regime_defensive_rotation_with_bands**: Sharpe 0.84 (halves 0.89/0.79), CAGR 10.7%, maxDD -32%, breakeven 101bps, crises {'gfc_bear': -0.1469, 'covid_crash': -0.0938, 'inflation_bear_2022': -0.2065}
- **risk_parity_spy_tlt_gld**: Sharpe 1.05 (halves 1.13/0.99), CAGR 9.5%, maxDD -22%, breakeven 992bps, crises {'gfc_bear': 0.0303, 'covid_crash': -0.0873, 'inflation_bear_2022': -0.2046}
- **spy_gld_switch**: Sharpe 0.82 (halves 0.95/0.69), CAGR 12.2%, maxDD -28%, breakeven 228bps, crises {'gfc_bear': 0.1094, 'covid_crash': -0.1366, 'inflation_bear_2022': -0.0912}
- **trinity_blend**: Sharpe 0.79 (halves 0.69/0.90), CAGR 9.2%, maxDD -32%, breakeven 1101bps, crises {'gfc_bear': -0.3112, 'covid_crash': -0.1917, 'inflation_bear_2022': -0.1252}

## Fell at stage 2

- hfea_55_45: D2 crisis floor (worst -65% < -35%)
- hfea_lite_2x: D2 crisis floor (worst -48% < -35%)
- reddit_200sma_tqqq: D2 crisis floor (worst -62% < -35%)
- regime_defensive_rotation_with_bands_2x: D2 crisis floor (worst -38% < -35%)
- regime_defensive_rotation_with_bands_3x: D2 crisis floor (worst -53% < -35%)
- vol_target_qqq_2x: D2 crisis floor (worst -38% < -35%)
- vol_target_spy_15: D2 crisis floor (worst -36% < -35%)

## Excluded (with reasons)

- advanced_llm (dev account): live LLM decisions - no deterministic signal function to backtest
- llm_recommendations (account 1): live LLM decisions - no deterministic signal function to backtest
- entry strategies (lump sum/DCA/...): capital-deployment rules, not portfolios - tested in entry_strategies.py across start-date cohorts instead
- decumulation rules (4% + overlays): withdrawal framework - tested in entry_strategies.py --withdrawal-rate instead
- overnight/intraday legs: need open prices; engine is close-to-close - tested in overnight_decomposition.py instead
- options/VRP strategies: no historical chain data yet (awaiting user's data purchase)
