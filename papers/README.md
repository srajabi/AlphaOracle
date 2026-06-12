# Papers Library

Academic and practitioner research underpinning AlphaOracle's strategies.
Each note records: citation, where to get it, the paper's claims, known
criticisms, and - most importantly - **what happened when we tested it on our
own data** (with pointers to the backtest results).

PDFs live in `pdfs/` where a freely-hosted copy exists; SSRN-gated papers are
notes-only with links.

## Index

| Note | Paper | Our implementation | Our verdict |
|---|---|---|---|
| [beyond_status_quo.md](beyond_status_quo.md) | Anarkulova, Cederburg & O'Doherty (2023) | `entry_strategies.py` decumulation mode | Equity edge real at long horizons; ruin tail matches critics; SMA overlay fixes the behavioral problem |
| [faber_qtaa.md](faber_qtaa.md) | Faber (2007, upd. 2013) | `gtaa_5_faber`, `sma200_monthly_spy` | Confirmed: -12% maxDD over 21y; monthly beats daily |
| [time_series_momentum.md](time_series_momentum.md) | Moskowitz, Ooi & Pedersen (2012) | `tsmom_12_1_spy` | Works: Sharpe 0.71 vs 0.56 B&H over 33y |
| [volatility_managed_portfolios.md](volatility_managed_portfolios.md) | Moreira & Muir (2017) | `vol_target_spy_15`, `vol_target_qqq_2x` | Only leverage scheme that survived dot-com |
| [keller_vaa.md](keller_vaa.md) | Keller & Keuning (2017) | `keller_vaa_lite` | Underperformed with our proxies (Sharpe 0.49) |
| [keller_daa.md](keller_daa.md) | Keller & Keuning (2018) | `canary_daa_lite` + variants | Best idea in the strategy lab (Sharpe 1.06-1.21) |
| [keller_baa.md](keller_baa.md) | Keller (2022) | not yet implemented | Candidate: BAA's dual-momentum refinement |
| [antonacci_dual_momentum.md](antonacci_dual_momentum.md) | Antonacci (2012) | `gem_dual_momentum` | Weak with EWA proxy (Sharpe 0.45); needs better intl data |

## Conventions

- File name: short slug of the paper, `.md`
- Note structure: Citation / Links / Claims / Criticisms / AlphaOracle verdict
- When a strategy from a paper is implemented, link the note from the
  strategy's docstring and record the backtest verdict here after running it
- Add PDFs only when freely/legally hosted (arXiv, NBER, author sites)
