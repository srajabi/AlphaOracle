# Findings Registry

The canonical record of every empirical result this project has produced.
One entry per finding: the number, the caveat, the pointer. Update this
RELIGIOUSLY - any session that produces a result adds it here.

All backtests zero-cost unless stated. Multi-asset window 2004-11+ unless
stated (gold-friendly - standing caveat). Detailed session narrative:
[current.md](current.md). Paper-level verdicts: [../papers/README.md](../papers/README.md).

## 1. Deploying cash near market highs (the entry question)

- **Lump sum beats DCA on the median, even at all-time highs** (SPY, 328
  monthly starts 1993-2021, 5y horizon, at-top cohort median 1.73x).
  Matches Morgan Stanley/Vanguard published research.
- **DCA does NOT protect the tail**: worst maxDD still -50%+ once deployed.
  It's a psychological tool, not a risk tool.
- **Waiting for a 10% dip is the worst rule tested** (lowest median wealth).
- **The SMA200 overlay - not the entry schedule - truncates the left tail**:
  at-top entries, worst case 0.94x vs 0.82x, maxDD -22% vs -55%, cost
  ~0.14x median. On a 60/40 it's nearly free: worst 5y outcome +21%, maxDD
  -11%, beat lump sum 53% of the time.
- Results: `data/entry_strategies_spy.json`, `data/entry_strategies_6040.json`;
  tool: `backtesting/entry_strategies.py`; published: site /research sec. 1.

## 2. Retirement decumulation (4% rule)

- 25y retirements, SPY, starts 1993-2001 (every window contains dot-com AND
  GFC; windows overlap - illustrative): **all-equity ruin 4.5%** (matches
  Cederburg's US numbers), 5th-pctile ending ~1% of start.
  **Equity+SMA200 overlay: 0% ruin**, maxDD -31% vs -64%, cost = lower
  median ending (1.42x vs 1.89x at-top).
- Synthesis vs the "most controversial paper": equities win long horizons,
  sequence risk wins short ones - bucket by horizon, trend-brake the equity.
- Results: `data/decumulation_spy.json`; site /research sec. 4.

## 3. SMA200 timing on diversified funds (XEQT/VEQT)

- **Verdict: don't.** Fair test (VT 2010+, signal live throughout):
  SMA200 6.4% CAGR / Sharpe 0.56 / -19% maxDD vs buy-hold 9.8% / 0.56 /
  -34%. A third of CAGR for identical Sharpe.
- **Warmup artifact warning**: short backtests flattered SMA200 because the
  200-day warmup happened to cover COVID (XEQT) / GFC tail (VT). Check for
  this in every short-history test.
- Timing earns its costs on LEVERAGED funds (drawdowns existential), not
  1x diversified ones. Results: `backtesting/results_xeqt_veqt/`,
  `results_vt_proxy/`; site /research sec. 3.

## 4. Leveraged ETF strategies

- **TQQQ buy-and-hold is uninvestable**: -94% maxDD (GFC), -83% (dot-com era
  from 1999).
- **The 200SMA filter makes leveraged equity survivable** (GFC -94% -> -36%)
  BUT is regime-dependent: the same rule run from 1999 shows -90% maxDD.
  Its celebrated 33y stats depend on starting before the dot-com bubble.
- **HFEA died in 2022 as critics predicted** (-62%; stocks+bonds crashed
  together). Its long-run record rides a 30y bond bull.
- **Vol targeting is the only leverage scheme that survived the dot-com
  test**: vol_target_qqq_2x from 1999: Sharpe 0.67 / -57% vs SMA-rule
  0.36 / -90%.
- **No timing signal saves you from gap crashes** (COVID: -61% on
  TQQQ+SMA before the signal could move). Gap risk (15% overnight):
  3x sleeve = -45%.
- Real-world drag warning: clean-leverage backtests ignore ~1% ER +
  financing ~2x short rate (~8-9%/yr for 3x at 2026 rates).
- Results: `backtesting/results_letf/`, `results_lab_g2/`; site /research sec. 2.

## 5. Strategy lab (27 strategies, sessions 4-5) - the winners

| Strategy | CAGR | Sharpe | maxDD | Crisis profile |
|---|---|---|---|---|
| lab_winners_blend (40% canary DAA + 30% risk parity + 30% mo-SMA200) | 11.4% | **1.19** | -24% | GFC +2%, 2022 -20% |
| canary_daa_2x | 18.0% | 1.08 | -36% | **GFC +13%**, 2022 -23% |
| canary_daa_smart_defense | 14.1% | 1.04 | -27% | 2022 fixed: **-6.8%** |
| dual_channel_cash_overlay | 9.3% | 1.07 | **-15.8%** | single-digit-to-teens in ALL crises |
| gtaa_5_faber | 7.2% | 0.80 | **-12.0%** | 2022 -0.1% (best) |
| buy_hold_spy (baseline) | 10.4% | 0.55 | -55% | |

- **Best idea tested: Keller's canary universe** (DAA). Blending uncorrelated
  engines beats any single engine. Monthly evaluation beats daily for trend.
- **Confirmed failures** (kept on the scoreboard deliberately): VIX-laddered
  TQQQ (-95% DD), VIX-spike leverage buying (perm p=0.977 - worse than
  random), Donchian 55/20, GEM/VAA with EWA proxies (proxy quality kills
  them), low-vol at sector granularity (it's a single-stock effect).
- Full writeup: [../spikes/strategy_lab_2026_06.md](../spikes/strategy_lab_2026_06.md);
  scoreboard: `backtesting/results_validation/scoreboard_v2.csv`.

## 6. Statistical validation (the honesty layer)

- **PBO = 0.36** across 48 strategies (0.5 = noise): rankings carry real
  signal; selection bias exists but is not fatal.
- Top strategies survive deflation: DSR prob >= 0.998, bootstrap 5th-pctile
  Sharpe 0.67-0.85, permutation p 0.000-0.02 (dual_channel p=0.123 - its
  edge is allocation, not timing).
- **Parameter plateaus 0.96-0.97** (SMA window, vol target, changepoint
  multiplier): results are properties of the ideas, not the numbers.
- **Cost lens redrew the rankings**: regime_defensive breakeven only
  **24bps** (Sharpe 0.93->0.74 at 5bps) vs canary family 130-155bps,
  dual_channel 354bps, risk_parity 992bps. Lag drops <= 0.11 everywhere.
- **Underwater reality: even the best strategies spent 2.2-3.2 YEARS below
  peak** at their worst.
- Tools: `backtesting/validation.py`, `run_validation.py`,
  `run_parameter_stability.py`; results: `results_validation/`.

## 7. Overnight / intraday / day trading

- **The equity premium is earned overnight** (Lou/Polk/Skouras replicated):
  QQQ overnight-only 13.5% CAGR / Sharpe 0.96; intraday-only NEGATIVE over
  27 years (maxDD -88%). Non-overlapping bootstrap CIs. 1bp/leg costs eat
  the tradable version. `data/overnight_decomposition.json`.
- **Retail day trading is negative-edge by the best evidence**: Taiwan
  audit-trail <1% persistently profitable; Brazil 97% of 300+-day traders
  lose. The winners run institutional mechanics (spread capture, speed,
  order flow, structural arb). Out of scope by evidence.
- Intraday momentum (Gao et al: first half-hour predicts last) - blocked on
  intraday data; Alpaca bars flagged for future replication.

## 8. Bugs found by our own testing (methodology wins)

- **Engine never charged initial position entry cost** (pandas NaN row
  silently summed to 0) - caught by the test suite's first run, fixed.
- **Drawdown metrics missed first-day losses** (equity curve lacked the 1.0
  starting point) - caught by metric tests, fixed.
- **ticker_indicators.json contained literal NaN** (Python json.dump
  default) - every ticker page silently dropped its indicator panel. Fixed
  generator + data.
- **Daily ingestion starved indicators**: 365d fetch minus 200d SMA warmup
  dropna left ~52 usable days; 3 of 5 per-ticker indicators showed "No
  Data" since inception. Now fetches 730d.
- **Warmup artifact** (see finding 3) - a recurring class of backtest flattery.

## 9. Data assets ready for round-5 strategies

- ^VIX3M (2006+), ^VIX9D (2011+): VIX term-structure regime signal
- HYG/LQD (2007+/2002+): credit-stress momentum (the Xiong paper's signal)
- ^TNX/^IRX (1962+/1960+): yield-curve inversion with 60y of history
- Alpaca intraday bars: accessible, unpulled (Gao replication)

## 11. Benchmark-relative + distribution metrics (scoreboard v4)

- **Convexity confirmed directly**: every lab winner captures more upside
  than downside (canary_daa_2x up/down capture 0.57/0.45; blend 0.45/0.38).
  Downside correlation to SPY stays 0.20-0.40 for the canary family - still
  diversifying when it matters.
- **Rolling 1y Sharpe positive 83-92%** of windows for the winners - the
  lived-experience consistency number.
- Metrics now reported per strategy: Sharpe, Sortino, Calmar, Martin, Omega,
  gain-to-pain, K-ratio, CAGR, maxDD, DD-duration, Ulcer, CVaR/CDaR-95,
  tail ratio, skew/kurtosis, rolling consistency, up/down capture, downside
  corr + the execution suite (costs/breakeven/lag/gap) + the statistical
  suite (DSR/bootstrap/permutation/PBO/plateau).

## 12. Options / volatility risk premium (researched, not started)

- **Renaissance-type returns: not replicable** - Medallion's edge geometry
  (tiny edge x ~100k trades/day x capacity cap) cannot be bought with data;
  even RenTech's public funds are ordinary.
- **The real options edge is the VRP**: IV (19.3% avg) > realized (15.1%),
  1990-2018. PUT index: 2/3 of SPY vol, beta 0.56, maxDD -33% vs -51%, with
  violent negative skew; weaker post-2012 (crowded). Realistic sleeve:
  Sharpe ~0.5-0.9, income overlay +1-3%/yr - diversifier, not money printer.
- Blocker: no historical chains in free data. Plan + vendor costs
  (~$50-100/mo): `spikes/options_data_vrp_plan.md`. Awaiting go/no-go.

## 10. System state (operational)

- 6 Alpaca paper accounts; forward test UNCHANGED by user instruction
  (candidates queued: lab_winners_blend, canary_daa_smart_defense,
  dual_channel_cash_overlay).
- LLM pipeline single-provider (deepseek-v4-flash; aliases retire
  2026-07-24). Workflow failure-isolated; stale-trades guard active.
- 268 tests green. Site: /research page carries sections 1-4 above.
