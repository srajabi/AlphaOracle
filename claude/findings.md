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

## 10. Benchmark-relative + distribution metrics (scoreboard v4)

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

## 11. Options / volatility risk premium (researched, not started)

- **Renaissance-type returns: not replicable** - Medallion's edge geometry
  (tiny edge x ~100k trades/day x capacity cap) cannot be bought with data;
  even RenTech's public funds are ordinary.
- **The real options edge is the VRP**: IV (19.3% avg) > realized (15.1%),
  1990-2018. PUT index: 2/3 of SPY vol, beta 0.56, maxDD -33% vs -51%, with
  violent negative skew; weaker post-2012 (crowded). Realistic sleeve:
  Sharpe ~0.5-0.9, income overlay +1-3%/yr - diversifier, not money printer.
- Blocker: no historical chains in free data. Plan + vendor costs
  (~$50-100/mo): `spikes/options_data_vrp_plan.md`. Awaiting go/no-go.

## 12. Attribution monitor + track record (built 2026-06-12)

- `src/attribution.py` closes the forward-test loop: pulls each Alpaca
  account's daily equity (REST), computes live Sharpe/maxDD, places them in
  the mapped strategy's bootstrap bands from the gauntlet -> on_script /
  watch / off_script. Runs daily in the workflow; panel on /paper-trading.
- GIPS-style monthly composites per account -> `data/track_record.json`,
  committed daily: **git history is the tamper-evident track record** - the
  evidence file for any future managed-money ambition starts accumulating now.
- Account->strategy expectation mapping: prod_2->reddit_200sma_tqqq,
  prod_3->dual_momentum, prod_4->sector_momentum; LLM accounts have no
  backtest analogue (reported without bands).
- First real data lands on the next workflow run (backfills up to 1 year).

## 13. Round 5: macro-signal strategies (2026-06-12)

- **VIX term structure is the best FAST-crash defense ever tested here**:
  COVID -7.6% vs SMA200-monthly -12.1% vs SPY -33.4%. Backwardation fires in
  days - it covers exactly the gap-risk hole every trend rule has. But it
  loses slow bears (GFC -28%) and grinding bears (2022 -25%).
- **Trend and VIX-term are complementary channels** -> `trend_plus_vix_term_spy`
  (monthly SMA200 AND not-backwardation): COVID -7.6%, **GFC -1.8% (beats
  both parents)**, 2022 -16.6%. Worst crisis = -16.6% - the best crisis
  profile of any SPY-only strategy in the lab. Cost: ~0.02 Sharpe vs plain
  trend (0.77 vs 0.79) from extra whipsaws.
- **Credit-stress overlay (HYG/LQD)**: standalone Sharpe 0.56 = no better
  than buy-and-hold; helped COVID (-11%) but late/wrong in 2022 (-31%).
  Verdict: input signal, not a strategy.
- **Yield-curve de-risking is actively harmful as a timing rule** (Sharpe
  0.53 < B&H 0.56): inversion leads recessions by 12-18 months, so halving
  exposure at inversion misses late-cycle melt-ups (2006-07, 2019, 2023-24).
  Keep as context, never as a trigger.
- Results: `backtesting/results_lab_g9/`, `results_lab_g9b/`. Caveat:
  VIX3M/HYG signals only live from 2006/2007; earlier periods fall back to
  long (the GFC+ slices are the fair test windows).

## 14. The Tournament: census -> gauntlet -> champions (2026-06-12)

- **Every strategy now faces every test** (`backtesting/run_tournament.py`):
  65 testable (59 portfolio + 6 single-asset adapters), 6 excluded with
  stated reasons (LLM accounts, entry/decumulation rules, overnight legs,
  options pending data).
- **Pyramid: 65 -> 20 -> 13 champions.** Stage-1 gates: bootstrap p5 > 0,
  DSR >= 0.95, breakeven >= 25bps, beat 60/40. Stage-2: split-sample both
  halves positive, worst crisis > -35%, Sharpe@10bps >= 0.40, lag drop
  < 0.30, gap loss > -50%.
- **Two divisions** (user pushback on one-size crisis floor - correct call):
  same statistical gates, different risk mandates. CORE (holdable: -35%
  crisis floor, beat 60/40 on Sharpe): **13 champions** - canary family x5,
  dual_channel, gtaa_5, risk_parity, lab_winners_blend, trinity, changepoint
  momentum, regime bands, spy_gld_switch. AGGRESSIVE (must beat SPY on CAGR
  AND Sharpe; -60% crisis floor; recover within 5y): **15 champions** incl.
  the compensated-vol strategies CORE rejects - vol_target_qqq_2x,
  regime_bands_2x/3x, hfea_lite_2x, reddit_200sma_spy, tqqq_sma_vix_filter.
- **Even the aggressive division rejects hfea_55_45 (-65% worst crisis) and
  reddit_200sma_tqqq (-62%)** - high vol is admissible when compensated;
  near-wipeouts are not. The babies are kept; the bathwater still goes.
- lab_winners_blend champion line: Sharpe 1.19 (halves 1.24/1.14), GFC
  +2.4%, COVID -6.8%, 2022 -20%, breakeven 252bps.
- Full table: `backtesting/results_tournament/tournament.{json,md}`.

## 15. Market thesis 2026 H2 (written 2026-06-12)

- Full framework: `thesis/market_thesis_2026H2.md` (distilled into
  `thesis/macro_view.md` -> feeds the daily LLM analysts).
- Setup researched 2026-06-12: active Iran war + 4.2% CPI + cornered Fed
  (new Chair) + BoJ carry-risk hike June 15-16 (~$500B exposure) + $75B
  SpaceX IPO same week + AI capex 2nd derivative already negative.
- Scenarios: grind-with-violence 50% / slow bear 30% / fast crash 20%.
  "When does it implode" = unanswerable; the edge is tripwires (VIX term
  structure, credit rel-mom, canary breadth, trend, USDJPY) all on daily
  dashboards + champions that react in days.
- Falsifiable markers dated for 2026-07-12 review.

## 16. System state (operational, 2026-06-12)

- 6 Alpaca paper accounts; forward test UNCHANGED by user instruction.
  Promotion candidates queued: lab_winners_blend, canary_daa_smart_defense,
  dual_channel_cash_overlay, trend_plus_vix_term_spy.
- **Attribution monitor + GIPS-style track record live in the daily
  workflow** (first real data backfills ~1y on next run); panel on
  /paper-trading; git history = audit trail.
- LLM pipeline single-provider deepseek-v4-flash. **DEADLINE: legacy
  deepseek aliases retire 2026-07-24** - already migrated, nothing to do.
- Workflow failure-isolated; stale-trades guard active; 296 tests green.
- Site: /research page sections 1-4; shared nav; all rendering bugs fixed.
- User procuring options data -> VRP thread next (finding 11).
- Strategic docs: spikes/maturity_roadmap.md (3-tier plan),
  spikes/fund_path_and_data_roi.md (registration ladder + experiments),
  spikes/options_data_vrp_plan.md.

## 17. XEQT.TO US-listed proxy for paper/live parity (2026-08-08)

The live account can hold XEQT.TO; Alpaca is US-only, so the paper
account needs a tradeable proxy. Fitted long-only, weights sum to 1,
79 month-ends 2019-09 -> 2026-03. Tool: `tools/fit_xeqt_proxy.py`.

- **VT 77% / EWC 23% is the recommended proxy**: TE 2.53%/yr, corr
  0.9883, cumulative drift +0.6pp over 6.5y.
- **VTI 52% / VXUS 24% / EWC 25% wins TE by 0.15pp (2.38%) but drifts
  +5.8pp** - a systematic US overweight. Lower TE is not worth a proxy
  that quietly diverges from the live position; drift is the metric that
  matters for parity, not TE alone.
- **VT alone is a serviceable one-ticker fallback**: TE 3.06%/yr, corr
  0.9827, drift -1.4pp.
- **EWC lands at 23-25% in every fit**, independently recovering XEQT's
  ~24% prospectus Canada weight. Evidence the fit is structural, not
  overfitted.
- **Daily fitting is invalid here and produces a wrong answer.** XEQT.TO
  has 88 zero-return days (thin early trading) vs VT's 9; its measured
  daily vol (0.98%) is *below* VT's (1.22%), which is implausible for two
  global all-equity funds. Daily correlation caps at ~0.92 regardless of
  basket, and the daily fit assigns EWC 0% - an artefact. Month-end
  sampling removes it, and month-end is the slow channel's own cadence.
- **Standing caveat - CAD/USD is an irreducible 6.12%/yr gap.** The live
  position earns in CAD, the paper proxy in USD. The fit is
  FX-neutralised so it measures allocation tracking; the currency
  difference is real and will show up as live-vs-paper divergence. The
  attribution monitor must be told, or it will flag this as off_script.
- **Sample is short and single-regime**: 79 months, all post-2019. No
  GFC, no prolonged bear. Expect TE to widen in stress.

## 18. Overnight gap risk measured, not assumed (2026-08-09)

Finding 14 sizes the satellite sleeve on an ASSUMED 15% underlying
overnight gap (-22.5% at 2x, -45% at 3x). Now measured from 1-minute
bars: 09:30 open vs prior 16:00 close, regular session both ends, using
`robust_session_edges` (median of first/last 5 bars) so a single bad
tick cannot manufacture a tail. Tool: `tools/measure_overnight_gaps.py`;
data: `data/overnight_gaps.json`.

| Ticker | n | from | worst | p0.1 | p1 | breaches <=-15% |
|---|---|---|---|---|---|---|
| SPY | 8,348 | 1993-02 | -10.46% | -4.42% | -1.94% | 0 |
| QQQ | 6,806 | 1999-03 | -10.32% | -5.81% | -2.61% | 0 |
| TQQQ | 4,057 | 2010-02 | -28.90% | -14.85% | -6.51% | 4 |
| UPRO | 4,471 | 2000-03 | -32.08% | -14.63% | -6.58% | 4 |
| SOXL | 4,038 | 2010-03 | -31.25% | -17.96% | -9.27% | 9 |
| TLT | 5,957 | 2002-07 | -3.23% | -2.29% | -1.62% | 0 |
| GLD | 6,103 | 1994-06 | -5.66% | -4.14% | -2.35% | 0 |

- **The 15% underlying assumption is conservative and was never
  breached.** SPY's worst is -10.46% (2020-03-16), QQQ's -10.32%
  (2015-08-24).
- **The -45% 3x ceiling is conservative by 13-16pp.** Worst observed:
  UPRO -32.08%, SOXL -31.25%, TQQQ -28.90%, all on 2020-03-16.
- **Leverage tracks cleanly through a gap.** SPY -10.46% against UPRO
  -32.08% on the same date is 3.07x - the LETF did not decouple when it
  mattered, which is the case the sizing rule was worried about.
- **DO NOT relax the rule on this evidence.** The conservatism is doing
  real work: every 3x product's tail rests on essentially ONE event
  (2020-03-16). TQQQ and SOXL start in 2010, so 2008 and 1987 are not in
  the sample at all. Measured worst x 25% weight = -8.0%, inside the
  -10% budget, which would nominally permit ~31% sizing rather than 22%.
  That headroom is an artefact of a sample with one crisis in it.
- **SOXL is the fat tail**: p0.1 -17.96% and 9 breaches past -15%,
  materially worse than TQQQ or UPRO. Sector 3x is not portfolio 3x.
- **Methodology note - bad prints move the answer.** Naive
  single-print gaps put SPY's worst at -15.56% (2000-12-18), a 5.10pp
  contamination and the difference between "the 15% assumption was
  breached once" and "it never was". That date records open and low of
  exactly 111.000 against a 131.45 prior close, then trades back to 133
  the same session. See `spikes/minute_data.md` trap 5.
- **Caveat - UPRO's start date is wrong.** The series begins 2000-03-20
  but UPRO launched in 2009, and n=4,471 over 26 years is far short of
  the ~6,500 sessions that span implies. Pre-2009 UPRO records are
  suspect; the 2020 tail figure is unaffected but its full-history
  percentiles should not be trusted.

## 19. Macro lookahead hides in the tail, not the return (2026-08-09)

One strategy, run two ways over 386 months (1994-02 to 2026-03). Signal:
at each month end, hold SPY if payrolls grew over 3 months, else cash at
the 13-week bill. NAIVE joins payrolls on the period label (assumes
July's number is knowable on 31 July); VINTAGE gates on the ALFRED
publication date and uses the value as first released.
Tool: `tools/backtest_macro_lookahead.py`.

| | CAGR | vol | maxDD | growth |
|---|---|---|---|---|
| naive (lookahead) | 10.05% | 12.71% | **-26.79%** | 21.77x |
| vintage (correct) | 10.11% | 12.93% | **-32.34%** | 22.13x |
| buy & hold SPY | 10.42% | 14.88% | -50.79% | 24.25x |

- **The lookahead premium in CAGR is -0.06pp - effectively zero.** A
  reviewer checking returns alone would conclude the bias is immaterial.
  That conclusion is wrong.
- **The bias lives in the drawdown: 5.55pp.** Lookahead flattered maxDD
  from -32.34% to -26.79%. Anyone using this to size a position, or to
  claim the overlay's tail protection, is quoting a number the strategy
  could not have achieved.
- **Signals disagree in only 6.5% of months (25 of 386), and they
  cluster at turning points**: 2000-2003 (10), 2008 (1), 2010-2011 (5),
  2020 (2), 2025-2026 (5). Rare, and concentrated exactly where the
  decision carries the most money.
- **Concrete instance: September 2001.** The naive run was out of the
  market; the vintage run could not be, because the payroll release that
  would have triggered the exit had not happened yet. Vintage lost
  8.44pp more that month. The lookahead version "dodged" 9/11 by reading
  a number published afterwards.
- **The disagreements roughly cancel on return** (+2.46pp cumulative in
  vintage's favour), which is why CAGR barely moves while the drawdown
  path differs materially. Averages cancel; sequences do not.
- **Strategy verdict: the payroll filter is a risk tool, not an alpha
  tool.** It gives up 0.31pp of CAGR against buy-and-hold (10.11% vs
  10.42%) and cuts maxDD from -50.79% to -32.34%. Same shape as finding
  1's SMA200 result - the overlay truncates the left tail rather than
  raising the median.
- **Publication lags measured** (median / max days, ALFRED initial
  release): ICSA 5/54, UMCSENT 26/57, UNRATE 34/80, PAYEMS 35/80,
  RSAFS 44/85, INDPRO 45/93, CPIAUCSL 46/62, HOUST 47/130.
- **Why macro cannot time a fast drawdown.** On 2020-03-15 the newest
  published payrolls described February, and the newest jobless claims
  the week of 2020-03-07 at 211k. Claims reached ~6.8M within a
  fortnight. Every macro series was showing pre-crisis numbers while the
  crisis was underway.
- **Caveat**: one strategy, one signal, one asset. The size of the bias
  is specific to a 3-month payroll rule; a signal with a shorter lag
  (ICSA at 5 days) or a faster trigger would show a different gap.

## 20. When the payroll filter works, and why (2026-08-09)

Tests the obvious follow-up to finding 19: if macro cannot time 2020,
does it work when the drawdown is slow? Every SPY drawdown worse than
15% since 1994, against the vintage-correct payroll filter.
Tool: `tools/analyze_drawdown_speed.py`.

| Peak -> trough | Depth | Months | Exit | Decline avoided |
|---|---|---|---|---|
| 1998-06 -> 1998-08 | -15.3% | 3 | never | 0% |
| 2019-12 -> 2020-03 | -19.4% | 4 | never | 0% |
| 2021-12 -> 2022-09 | -23.9% | 10 | **never** | 0% |
| 2007-10 -> 2009-02 | -50.8% | 17 | 2008-02 | **-43.4%** |
| 2000-08 -> 2002-09 | -44.7% | 26 | 2000-09 | **-41.5%** |

- **Speed alone does not explain it.** The two catches were the two
  slowest episodes, and both were caught EARLY - after only 5% (2000)
  and 13% (2008) of the fall, avoiding 41-43% of the decline. That is
  the overlay working exactly as designed.
- **2022 refutes the simple "slow = works" reading.** Ten months and
  -23.9%, and the filter never fired, because payrolls kept GROWING
  throughout. It was a rate and inflation repricing, not an employment
  recession.
- **The actual rule needs BOTH conditions**: the drawdown must be slow
  enough to outlast a ~35-day publication lag, AND be accompanied by
  labour-market deterioration. 2020 failed the first, 2022 failed the
  second. Only 2000 and 2008 satisfied both.
- **Practical consequence: the payroll filter is a recession detector,
  not a drawdown detector.** It will sit through any decline that does
  not show up in employment. Sizing an overlay as though it catches
  drawdowns generally would be a category error - on this sample it
  caught 2 of 5.
- **This is an argument FOR the existing two-channel design, not for
  adding macro.** The fast channel (VIX term structure) exists precisely
  for the 2020 shape, and the slow channel (200dma trend) is a price and
  therefore fires on 2022-style declines that employment never sees.
  A payroll overlay would have added nothing in 3 of these 5 episodes
  that the existing channels do not already cover.
- **Caveat**: 5 episodes is a small sample for a two-condition rule, and
  the two successes are the two events every trend rule catches. Do not
  read 41-43% avoided as an expectation.

## 21. For a CAD investor, unhedged USD exposure is a hedge (2026-08-09)

The user is Canadian, spends CAD, and asked whether to hold CAD. Testing
what unhedged US equity actually does in CAD terms. 270 monthly
observations, 2003-10 to 2026-03.

- **corr(SPY, USD/CAD) = -0.569.** The CAD is a risk-on commodity
  currency and the USD a risk-off reserve currency, so they move against
  each other when equities fall.

| Measured in | vol | maxDD |
|---|---|---|
| USD (what a US investor gets) | 14.48%/yr | -50.79% |
| CAD, unhedged (what a Canadian gets) | **12.01%/yr** | **-41.82%** |

- **In the 10 worst SPY months the USD rose +3.77% on average**, turning
  a mean -10.08% USD loss into -6.77% in CAD. Roughly a third of the
  drawdown absorbed by currency.
- **This reverses the framing in finding 17.** That entry recorded
  CAD/USD vol at 6.12%/yr as an irreducible live-vs-paper gap, which is
  true for TRACKING but wrong as a risk statement: the FX exposure is
  negatively correlated with the thing it is attached to, so it reduces
  portfolio risk rather than adding it.
- **Practical consequence: do NOT buy currency-hedged products.** A
  CAD-hedged S&P fund strips out the cushion and hands back the US
  investor's -50.79% drawdown. The correct structure is CAD-denominated
  but currency-UNHEDGED, which is what XEQT already is - it holds its
  foreign assets unhedged.
- **This is a point in XEQT's favour that tracking error alone missed.**
  Finding 17 evaluated XEQT as a proxy problem; as a holding for a
  CAD-based investor it captures this cushion natively.
- **Caveat**: 2003-2026 only, and the relationship rests on the CAD
  behaving as a commodity/risk currency. A regime where Canada is the
  haven, or an oil shock that lifts CAD during an equity selloff, would
  weaken or invert it. It is a tendency, not a guarantee.

## 22. The cost of advised funds and GICs (2026-08-09)

Baseline for the parents' mandate. SPY in CAD, 2015-08 to 2026-03
(10.6y): 3.92x total, 13.74% CAGR. On 1.8M:

| | Terminal |
|---|---|
| index at 0.20% MER | 6,933,000 |
| advised fund at 2.20% MER | 5,740,000 |
| GIC at ~2.5%/yr | 2,340,000 |

- **The 2.0pp fee differential alone cost ~1.19M.** The GIC allocation
  cost ~4.6M against the index.
- **Separate the two, they are not the same claim.** The GIC opportunity
  cost is regime-dependent - it reflects one of the strongest bull runs
  in history and is NOT a forward expectation. The fee drag is
  regime-independent: 2pp of MER costs 2pp whatever the market does.
- **Strategic consequence: the largest CERTAIN edge available to this
  project is fee reduction, not alpha.** It requires no backtest,
  carries no PBO, and is available immediately. The tournament champion
  at 18% CAGR carries 0.36 PBO; a 2pp fee saving carries none.

## 23. H7 - contributions make overlays worse, but modestly (2026-08-09)

Every prior backtest here is lump-sum while both mandates contribute
~80k/yr, so ~73% of the son's eventual capital arrives after t0. The
hypothesis was that a trend overlay is worse under contributions,
because it sits in cash exactly when deposits would buy cheapest.
SPY in CAD, 2003-10 to 2026-03, 800k initial, 80k/yr, signal live from
day one. Tool: `tools/backtest_with_contributions.py`.

| Strategy | lump sum | with contributions | maxDD (contrib) |
|---|---|---|---|
| buy_hold | 8.10M | **18.16M** | -33.4% |
| sma200 | 6.62M (-18.3%) | 14.52M (**-20.1%**) | -16.8% |
| sma200_bands | 6.96M (-14.1%) | 15.23M (**-16.2%**) | -16.1% |

- **Hypothesis confirmed but the effect is small.** Contributions widen
  the overlay's shortfall by 1.8pp (sma200) and 2.1pp (bands). Real,
  directionally as predicted, not decisive.
- **The dominant fact is the level, not the delta.** The overlay costs
  16-20% of terminal wealth under either accounting - roughly 3.6M on
  these numbers. Contributions are a second-order aggravation of a
  first-order problem.
- **Ranking does NOT flip.** buy_hold wins both ways, so H7 does not
  overturn the existing scoreboard; it sharpens the margin.
- **Contributions mechanically damp drawdown**: buy_hold maxDD is -41.8%
  lump-sum but -33.4% with contributions, because fresh capital dilutes
  the peak. Reported drawdowns for a contributing investor are not the
  lump-sum figures.
- **A causality bug was caught and fixed mid-study, and it is worth
  recording.** Aligning `signal[T]` with `returns[T]` lets the rule see
  the month it is trading. That produced sma200 at **+271% over
  buy-hold with -8.0% maxDD across 2008** - impossible for a monthly
  trend rule, and the implausibility is what exposed it. Correct
  alignment is `signal.shift(1)`. Any result showing a trend overlay
  beating buy-hold by a large margin with a tiny drawdown should be
  assumed to have this bug until proven otherwise.
- **Caveats**: window starts 2003-10 because `CAD=X` history does, so
  dot-com is excluded and the sample contains one fewer bear market than
  it should. Uses SPY in CAD rather than XEQT. Flat 2% cash yield.

## 24. Check frequency: bands invert the answer (2026-08-09)

Resolves a contradiction in this registry. Finding 5 says "monthly
evaluation beats daily for trend"; finding 13 has the DAILY VIX channel
beating monthly SMA200 in COVID (-7.6% vs -12.1%). Both are right,
because the answer depends on hysteresis.

SPY 1994-2026, signal live from day one, causality-checked
(`signal.shift(1)`). Leverage simulated with daily reset plus 1.25%/yr
drag. Tool: `tools/backtest_check_frequency.py`.

| 1x | terminal | CAGR | maxDD | trades/yr |
|---|---|---|---|---|
| buy_hold | **25.1x** | 10.54% | -55.2% | 0 |
| daily_band5 | 23.5x | 10.31% | **-23.3%** | 0.7 |
| monthly | 19.0x | 9.59% | -35.7% | 1.2 |

| 3x | terminal | CAGR | maxDD | trades/yr |
|---|---|---|---|---|
| buy_hold | 336.9x | 19.83% | **-96.8%** | 0 |
| monthly_band5 | 502.4x | 21.33% | -77.9% | 0.6 |
| **daily_band5** | **1474.5x** | **25.46%** | **-58.3%** | 0.7 |

- **Finding 5 needs qualifying, not overturning.** Without bands, daily
  loses to monthly (-16.3% at 3x) exactly as it claims. With 5% bands,
  daily beats monthly by +193.5% at 3x.
- **The mechanism is trade count, not reaction speed.** Raw daily
  checking trades 6.6x/yr; daily with 5% bands trades 0.7x/yr - FEWER
  than monthly's 1.2. Bands filter noise by requiring a meaningful move;
  monthly filters it by discarding 30 days of information. Bands are
  strictly the better instrument.
- **At 1x there is no edge**, and this is the important negative. The
  overlay's best variant returns 23.5x against buy-hold's 25.1x. On the
  manifesto's stated bar - terminal wealth - it loses.
- **But it loses cheaply, and that is what matters.** Daily+bands costs
  0.23pp of CAGR to halve drawdown (-23.3% vs -55.2%); monthly costs
  0.95pp for less protection.
- **The two results are one result.** 3x buy-and-hold is uninvestable at
  -96.8% (finding 4). Near-free drawdown reduction is what buys the
  headroom to lever at all; the leverage then compounds. Bands do not
  generate return - they make leverage survivable, and leverage
  generates the return.
- **Band sensitivity: a plateau with a cliff.** At 3x: 2% -> 1162x,
  3% -> 1252x, 4% -> 2043x, 5% -> 1474x, 6% -> 1051x, all far above
  buy-hold's 337x. Then 8% -> 306x, BELOW buy-hold. The 2-6% plateau is
  the claim; the 4% peak is noise (a 38% swing to its neighbour) and
  selecting it would be overfitting.
- **Caveats that matter**: the 3x is SIMULATED from SPY daily returns
  with a flat 1.25% drag, not actual TQQQ/UPRO - real funds carry
  tracking error and variable financing. One asset, one 32-year window.
  Six variants tested, so the winner is best-of-six. No transaction
  costs, though at 0.7 trades/yr they are close to irrelevant.

## 25. findings.md is not evidence until a test re-derives it

Prompted by the user pointing out - correctly - that this registry is
LLM-generated prose and may not be true.

- **All 23 file paths cited by findings.md exist.** Necessary but not
  sufficient.
- **Finding 3's buy-hold reproduces to a decimal place**: claimed 9.8%
  CAGR / 0.56 Sharpe / -34% maxDD, measured 9.9% / 0.57 / -34.2%. The
  data and basic method are sound.
- **Finding 3's OVERLAY claim does not reproduce.** Claimed -19% maxDD
  and a Sharpe identical to buy-hold; an independent monthly-checked
  build gives **-34.8% and 0.44**. Its headline, "a third of CAGR for
  identical Sharpe", is not what an independent implementation produces.
- **Most likely cause is an unrecorded specification, not a fabrication.**
  Finding 24 shows check frequency alone moves maxDD by ~12pp, the right
  order of magnitude; finding 3 almost certainly used daily checking and
  never wrote it down. The number may well be right and is now
  unfalsifiable, which for decision-making is nearly as bad as wrong.
- **`tests/test_findings_reproduce.py` now re-derives claims from raw
  data**, including a quarantine test that asserts the finding 3
  discrepancy so it cannot be quietly forgotten.
- **Protocol rules added**: a claim no test reproduces may not be cited
  as evidence for a decision, and findings must record the
  specification - tool, params, window, warmup, check frequency - not
  just the number.

## 26. H2 - the LETF simulator was wrong, and the edge is crash-contingent

Finding 24's 1474x used a SIMULATED 3x with an assumed 1.25%/yr drag.
Validated against real fund prices, 2010-06 to 2026-03.
Tool: `tools/validate_letf_simulator.py`.

### The simulator's mechanics are right; its cost assumption was not

| Fund | daily corr | TE/yr | real CAGR | sim CAGR | assumed drag | **implied drag** |
|---|---|---|---|---|---|---|
| UPRO (3x) | 0.9982 | 3.11% | 29.69% | 34.67% | 1.25% | **5.03%** |
| TQQQ (3x) | 0.9914 | 8.09% | 40.36% | 45.56% | 1.25% | **5.01%** |
| SSO (2x) | 0.9985 | 1.90% | 23.13% | 25.15% | 1.25% | **2.85%** |

- **The real cost of holding a 3x fund is ~5%/yr, four times what
  finding 24 assumed.** Daily correlation of 0.998 says the daily-reset
  mechanic is modelled correctly; the error was entirely in the expense
  and financing assumption.
- **Corrected long-window result: 593x, not 1474x.** But the RATIO to
  buy-and-hold improves from 4.38x to 5.69x, because the strategy is out
  of the market ~22% of the time and therefore pays less drag than the
  holder does. Higher costs hurt buy-and-hold more than they hurt the
  timer. 3x buy-hold drops 337x -> 104x.
- **2x with its measured 2.85% drag**: strategy 140x vs buy-hold 81x
  (1.73x), maxDD -42.9% vs -86.7%.

### On REAL fund prices the strategy LOSES - and that is the finding

| Fund | strategy | buy & hold | strat maxDD | B&H maxDD |
|---|---|---|---|---|
| UPRO | 16.79x | **60.28x** | -58.4% | -76.8% |
| TQQQ | 39.77x | **209.55x** | -65.9% | -81.7% |
| SSO | 8.92x | **26.60x** | -42.8% | -59.4% |

- **This is not a contradiction of the long-window result. It is the
  same result seen through a window with no crash in it.** Real LETF
  history starts ~2010, so it contains neither dot-com nor the GFC. The
  strategy's entire edge comes from avoiding those.
- **The strategy is crash insurance, and in a 16-year bull run the
  premium is enormous** - it gave up two thirds of TQQQ's return to
  avoid a drawdown that never came.
- **Practical reading: the leveraged overlay is a bet that the next 27
  years contain at least one 2000/2008-scale event.** If they do, it
  wins by ~5.7x on the simulated long window. If they look like
  2010-2026, buy-and-hold 3x wins by ~4x. That is the actual choice, and
  it is a judgement about the world rather than about the data.
- **Countervailing point that does not depend on forecasting**: 3x
  buy-and-hold reaches -96.8% simulated / -76.8% realised. Over a 27-year
  horizon that almost certainly contains a major crash, that is a
  drawdown very few people hold through, and selling at the bottom
  converts a paper loss into a permanent one.
- **Caveats**: the 2010-2026 real window is a single bull regime, n=1 on
  the question that matters. The long window remains simulated, now with
  an empirically calibrated drag rather than a guessed one. TQQQ's 8.09%
  tracking error is materially worse than UPRO's 3.11%, so the Nasdaq 3x
  is modelled least reliably of the three.
- **SUPERSEDED IN FRAMING by finding 27.** "Crash-contingent" was too
  loose: the sweep shows the overlay also loses through COVID and 2022.
  The dependency is on SLOW DEEP bears specifically.

## 27. The regime sweep - stop quoting single windows

Findings 24 and 26 each quoted one window and reached opposite-sounding
conclusions. Both were right about their window and neither was a
verdict. A trend overlay is crash insurance, so it wins any window
containing a crash and loses any window without one MECHANICALLY, before
skill enters. Single-window results therefore describe the window.

Fix: `backtesting/periods.py` gains `MULTI_REGIME_WINDOWS`, and
`tools/backtest_regime_sweep.py` reports every strategy across all of
them. SPY underlying, leverage drag calibrated to real funds
(finding 26: 5.01%/yr at 3x, 2.85% at 2x), signal live from day one.

CAGR %, and overlay-minus-buyhold at matching leverage:

| Window | yrs | 3x B&H | 3x overlay | 1x | 2x | 3x |
|---|---|---|---|---|---|---|
| **full_sample** | 32.2 | 15.5% | **22.0%** | -0.2pp | +2.0pp | **+6.4pp** |
| two_crashes | 13.0 | **-7.9%** | 13.8% | +4.1 | +11.6 | +21.6 |
| lost_decade | 10.0 | **-20.6%** | 12.9% | +8.1 | +19.8 | +33.5 |
| no_crash_era | 10.1 | 31.6% | 19.3% | -4.6 | -8.6 | -12.3 |
| letf_era | 15.8 | 29.4% | 19.0% | -4.8 | -8.3 | -10.4 |
| modern_shocks | 8.2 | 24.0% | 15.2% | -5.0 | -8.0 | -8.8 |
| post_gfc_full | 17.0 | 36.8% | 20.0% | -6.7 | -12.5 | -16.9 |

- **The overlay loses in every window since 2009 and still wins the full
  sample.** Two slow bear markets do all the work across 32 years.
- **It is not crashes generally - it is SLOW DEEP bears.**
  `modern_shocks` contains both COVID and the 2022 rate shock, and the
  overlay lost at every leverage there. Fast crashes it cannot react to;
  moderate ones it whipsaws through. Independent confirmation of
  finding 20's slow/fast split, arrived at from price data rather than
  macro.
- **Leveraged buy-and-hold is the real casualty of a lost decade**:
  -20.6%/yr for ten years at 3x, roughly a 90% loss, and -7.9%/yr across
  `two_crashes`. The overlay's case rests on this far more than on
  beating a bull market.
- **1x confirms it has no edge**: -0.2pp on the full sample. The overlay
  only pays once leverage makes drawdowns existential, exactly as
  finding 3 claimed.
- **Drawdowns, full sample**: 1x 55.3% -> 23.3%, 2x 86.7% -> 42.9%,
  3x 97.7% -> 58.4%. Roughly halved at every leverage, in every window.
- **How to use this**: quote `full_sample` as the default, and NEVER
  quote a sub-window without also quoting one of opposite character.
  `two_crashes` and `no_crash_era` are the designated pair.
- **Caveats**: SPY underlying only; simulated leverage even though the
  drag is now calibrated; no transaction costs (immaterial at 0.7
  trades/yr); one band value, though finding 24 showed a 2-6% plateau.
  Seven windows is not seven independent samples - they overlap heavily
  and share the same two bear markets.

## 28. "Overdue for a crash" is not a signal (2026-08-09)

Tested directly rather than argued. Months since SPY was last 20% below
its running peak, against forward returns. SPY monthly, 1993-2026,
n=375.

- **corr(months-since-crash, forward 12m) = -0.087, p=0.091.** Not
  significant.
- **At 24 months, -0.164, p=0.001** - statistically real but R^2 ~2.7%,
  which is no basis for an allocation decision.

| Calm streak | n | mean fwd 12m | median | worst |
|---|---|---|---|---|
| 0-2y | 169 | +13.62% | +14.83% | -24.74% |
| 2-5y | 95 | +10.30% | +14.33% | -43.43% |
| 5-10y | 99 | +11.76% | +13.76% | -26.39% |
| 10y+ | **12** | -2.29% | -7.80% | -18.17% |

- **The alarming 10y+ row is n=12** - effectively one episode, and it is
  the kind of cell that gets quoted as if it were evidence. It is not.
- **As of 2026-03 the streak is 42 months**, squarely in the 2-5y bucket
  at +10.30% mean forward return. Unremarkable.
- **Elapsed time is not a mechanism.** Nothing makes a crash more likely
  because one has not happened recently. Valuation and concentration are
  real arguments for caution; "we're due" is not one, and it is
  precisely the intuition that makes people de-risk into bull markets.
- **Caveat**: this tests calendar spacing only. It says nothing about
  whether valuation-based measures (CAPE and similar) predict forward
  returns - a different question this repo has not tested, and one that
  needs earnings data we do not currently hold.
- **CORRECTION (see finding 29): the p-values above are inflated.** They
  come from overlapping forward windows. The direction (no usable signal)
  stands and is strengthened; the fwd24 "p=0.001" does not.

## 29. Overlapping windows inflate every forward-return p-value

The most important methodological finding so far, and it invalidates
work in this file including my own from the same session.

Testing whether the VIX level predicts forward 12-month returns, SPY
monthly 1993-2026:

| Method | n | corr | p |
|---|---|---|---|
| Overlapping monthly | 387 | +0.101 | **0.048** |
| Non-overlapping, offset 0 | 33 | +0.030 | 0.870 |
| Non-overlapping, offset 4 | 32 | +0.147 | 0.421 |
| Non-overlapping, offset 8 | 32 | +0.009 | 0.960 |

- **Forward-12m returns from consecutive months share 11 of 12 months.**
  387 monthly observations are therefore ~32 independent ones. Treating
  them as independent inflates significance by roughly sqrt(12).
- **The "significant" result vanishes at every non-overlapping offset.**
  Not weakened - gone, with p from 0.42 to 0.96.
- **Power is the binding constraint, not cleverness.** With ~6
  independent observations per quintile the smallest detectable
  difference is ~19pp; the spread being examined was ~10pp. The
  experiment could not have detected the effect even if it existed.
- **Quintile findings retracted**: "VIX ~22 is the weakest zone" and
  "panic is the best entry point" were both noise, and I presented them
  before running this check.
- **Finding 28 is affected identically** - same overlapping method, so
  its fwd24 p=0.001 is not trustworthy. Its conclusion (elapsed time is
  not a usable signal) survives, since correcting for overlap can only
  weaken an already-weak result.

**Rule: any predictive claim on overlapping forward returns must report
either non-overlapping samples or Newey-West corrected errors.** Raw
p-values on overlapping windows are not evidence.

**On the underlying problem - we are data-poor for this class of
question, and it cannot be fixed by trying harder.** ~32 independent
annual observations is what 32 years of one index provides. Options,
honestly ranked:
1. **Newey-West / block bootstrap** - keeps the data, corrects the
   inference. The right default, and cheap.
2. **Shorter forward horizons** - forward 1-month returns give ~387
   nearly-independent observations instead of 32. Changes the question
   being asked, but makes it answerable.
3. **More markets** - international indices add samples, though heavily
   correlated ones, so they add less than their count suggests.
4. **Longer history** - pre-1990 needs different sources; the minute
   archive starts 1992 and does not help with macro-horizon questions.


## 30. The Depression is the case for the overlay, and SPY-era data hides it

Deep history ingested (finding 31). Kenneth French daily US market total
return from 1926-07 turns the lost-decade sample from n=1 into n~4 and
adds the only observation that actually decides the leveraged sleeve.

US market drawdowns worse than -40%, total return, 1926-2026:

| Onset | Trough | Recovered |
|---|---|---|
| 1930-09 | **-83.9%** | 1944-12 (**14 years**) |
| 1974-09 | -46.4% | 1976-06 |
| 2002-09 | -44.7% | 2006-01 |
| 2008-11 | -50.2% | 2011-02 |

The SPY-era sample contains two of these; the century contains four, and
the worst is twice the depth of anything modern.

### 1929-1935, daily-reset leverage at the calibrated 5.01% drag

| | maxDD | terminal |
|---|---|---|
| 1x buy-hold | -84.07% | 0.72x |
| 2x buy-hold | -98.54% | 0.155x |
| **3x buy-hold** | **-99.89%** | **0.0225x** |
| 1x overlay | -30.96% | 1.75x |
| 2x overlay | -57.77% | 1.69x |
| **3x overlay** | -75.85% | **1.44x** |

- **3x buy-and-hold through the Depression is a 97.75% PERMANENT loss.**
  Not a drawdown to ride out - an unrecoverable wipeout. The same window
  with the overlay finishes 44% ahead.
- **This is the strongest evidence in the repo for the overlay, and it
  is unobtainable from post-1993 data.** Findings 24, 26 and 27 all
  argued the case on 2000 and 2008; those are mild by comparison.
- **The overlay does not make 3x comfortable.** It still drew down
  -75.85%. Surviving is not the same as holdable, and the manifesto
  test is whether the position is actually held.
- **1937-1940 is a lost decade worse than 2000-2010**: -5.63%/yr
  nominal over ten years, against -2.48%/yr for the 2008-2010 window.
- **Methodological note**: French is TOTAL return (Mkt-RF + RF); the SPY
  series used elsewhere in this repo is price-only. Mixing them silently
  understates the older history by the dividend yield, which was far
  higher pre-war. Do not join these two series without adjusting.
- **Caveats**: the 3x is simulated, and no 3x fund existed in 1929 - in
  practice leverage then was margin debt with margin calls, which is
  worse, not better. Daily-reset mechanics are applied to an era whose
  market microstructure was entirely different.
