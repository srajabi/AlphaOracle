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


## 31. Rate-correct LETF financing - I overstated the problem

Task 24, raised because every leveraged result used a flat 5.01%/yr drag
calibrated on the 2010-2026 ZIRP era. I flagged it as possibly changing
the core recommendation. It does not; it changes magnitudes.

Correct mechanics: a 3x fund holds 3 units of exposure per unit of
equity, borrows 2, and pays roughly (leverage-1) x short rate plus
expenses. Implemented against the French daily risk-free series from
1926, with the out-of-market leg earning rf rather than a flat 2%.

3x overlay CAGR, rate-correct against the flat-drag figure previously
quoted:

| Era | avg short rate | rate-correct | flat-drag error |
|---|---|---|---|
| 1927-2026 | 3.01% | 20.76% | +1.95pp |
| 1954-1981 rising | 4.81% | **19.66%** | +4.54pp |
| 1982-2000 | 5.92% | **26.48%** | +8.15pp |
| 2010-2026 ZIRP | 1.43% | 21.86% | **-0.90pp** |

- **"LETFs do not work when rates are high" is WRONG.** The 3x overlay
  returned 19.66%/yr through 1954-1981, an era containing the 1973-74
  crash and the stagflation grind, with honest time-varying financing.
- **Leverage multiplies the EQUITY RISK PREMIUM, not the total return.**
  levered = equity + (lev-1) x (equity - rf) - expenses. High rates
  historically arrived alongside high nominal equity returns, so the
  premium survived. The condition that kills leverage is a low or
  negative risk premium, which is NOT implied by a high short rate.
- **The flat assumption erred in both directions**: overstating
  high-rate eras by 2-8pp and understating ZIRP by 0.90pp, because real
  financing from 2010-2021 was cheaper than 5%.
- **Ranked threats to a leveraged sleeve**: (1) volatility drag from the
  daily reset, which is rate-independent and converts chop into
  permanent loss; (2) a low equity risk premium; (3) financing cost,
  real but third.
- **Standing correction**: findings 24, 26, 27, 30 and the 1927-2026
  century run quote flat-drag numbers and are therefore too generous
  pre-2010 and slightly too harsh post-2010. Directional conclusions
  stand; magnitudes should be taken from here.
- **Caveats**: real LETFs did not exist before 2006, so this models what
  one WOULD have cost rather than what was available - actual leverage
  then was margin debt with margin calls, which is strictly worse. The
  expense ratio is held at 0.95% throughout though it would have been
  higher in earlier eras.


## 32. H10 - vol targeting loses to the trend gate, and the architecture simplifies

ARCHITECTURE.md proposed two controls: a trend gate for IN/OUT and a
volatility target for HOW MUCH, citing finding 4's claim that vol
targeting was the only leverage scheme to survive the dot-com test. Built
and tested it. The claim does not carry.

French daily total return 1926-2026, rate-correct financing (finding 31),
60-day realised vol, leverage capped at 3x, signal lagged one day.
Tool: `tools/backtest_vol_target.py`.

| Strategy | avg lev | CAGR | maxDD | turnover/yr |
|---|---|---|---|---|
| fixed_1x_buyhold | 1.00x | 9.83% | -84.1% | 0.00x |
| fixed_1x_gate | 0.74x | **10.50%** | -38.0% | 0.71x |
| fixed_2x_gate | 1.47x | **16.01%** | -63.9% | 1.42x |
| voltarget_20%_gate | 1.40x | 14.03% | -61.1% | 5.19x |
| fixed_3x_gate | 2.21x | **20.89%** | -79.5% | 2.13x |
| voltarget_30% | 2.32x | 15.51% | -90.1% | 4.45x |
| voltarget_25% | 2.05x | 14.52% | -84.8% | 5.10x |

- **The gate beats vol targeting at equal average leverage, on both
  return and drawdown.** At ~1.4x: 16.01% vs 14.03%. At ~2.2x: 20.89%
  vs 15.51%, with drawdown -79.5% vs -90.1%. Comparing at equal average
  leverage is the whole point - a raw comparison is a leverage
  difference in disguise.
- **Gate + vol always beats vol alone** (e.g. 11.51% vs 10.87% at a 15%
  target), so the GATE is doing the work. The two-control architecture
  collapses to one control.
- **Vol targeting costs 2-6x the turnover**: 4.33-5.25x/yr against the
  gate's 0.71-2.13x. Commissions are ~zero at modern retail brokers and
  liquid-ETF spreads are 0.5-2bp, so the binding cost is realised
  capital gains in a taxable account - which scales with turnover.
- **A deadband improves vol targeting on BOTH axes.** At a 15% target,
  a 25% deadband cuts turnover 4.33x -> 1.25x AND raises CAGR
  10.87% -> 11.50%. Less trading, better returns; the continuous
  rebalancing was destroying value, not adding control.
- **The gate wins at 1x over the century**: 10.50% vs 9.83% buy-and-hold,
  with drawdown -38.0% vs -84.1%. This is the opposite of the
  modern-sample result (findings 24, 27) and is entirely the Depression.
- **This does not strictly refute finding 4**, which tested
  vol_target_qqq_2x on QQQ from 1999 - different asset, different
  window. But on a century of broad-market data the gate wins at every
  comparable leverage, so finding 4's claim should not be generalised
  beyond its original test.
- **Consequence for ARCHITECTURE.md**: the "two controls" design is
  wrong. One control - the trend gate - plus a fixed leverage ceiling
  chosen as a judgement about tail tolerance. Simpler, fewer parameters,
  and better on the evidence.
- **Caveats**: one vol lookback (60d) and one band (5%) - neither swept.
  Leverage capped at 3x, which binds on the vol-target variants in calm
  periods and is itself a parameter. US market only.


## 33. H11 - Markov regime switching: the edge is entirely lookahead

Tests the claim heard constantly, that practitioners identify bull/bear
regimes and adjust within them. Hamilton-style two-state Markov
switching with switching variance, fitted by EM on French monthly total
returns, out-of-sample window 1946-07 onward (first 20 years reserved
for training). Tool: `tools/backtest_markov_regime.py`.

Two variants, and the gap between them IS the finding:
- **smoothed**: fitted on all history, using smoothed regime
  probabilities. This is how the analysis is normally presented.
- **walk-forward**: refit on an expanding window every 12 months, using
  only the FILTERED probability at the last observed point, decision
  lagged one month.

| Variant | CAGR | maxDD | %invested | switches/yr |
|---|---|---|---|---|
| buy_hold 1x | 11.16% | -50.2% | 100% | 0.01 |
| trend_gate 1x | 10.57% | **-24.4%** | 79% | 0.49 |
| markov_smoothed 1x (LOOKAHEAD) | 12.71% | -27.6% | 93% | 0.29 |
| markov_walkforward 1x | 10.07% | -50.2% | 95% | 0.11 |
| buy_hold 2x | 15.20% | -80.8% | 100% | 0.01 |
| trend_gate 2x | 15.14% | **-51.0%** | 79% | 0.49 |
| markov_smoothed 2x (LOOKAHEAD) | **19.14%** | -55.2% | 93% | 0.29 |
| markov_walkforward 2x | **13.13%** | **-84.9%** | 95% | 0.11 |

- **The in-sample model looks excellent and the honest one is worse than
  buy-and-hold.** At 2x: 19.14% smoothed vs 13.13% walk-forward, against
  buy-hold's 15.20%. Drawdown -55.2% smoothed vs -84.9% walk-forward
  against buy-hold's -80.8%. Every apparent advantage was lookahead.
- **Smoothed probabilities are a DESCRIPTION of history, not a signal.**
  The smoothed probability at time t incorporates data from t+1 onward.
  Presenting it as a strategy is the same class of error as finding 23's
  `signal[T]` vs `returns[T]` bug, but harder to spot because the model
  is sophisticated.
- **The honest model barely de-risks**: 95% invested, 0.11 switches/yr.
  It does not identify a bear until the bear is essentially over, which
  is the known behaviour of filtered regime probabilities.
- **The crude trend gate beats it on the thing that matters.** At 2x it
  cuts drawdown -80.8% -> -51.0% for 0.06pp of CAGR, while the
  sophisticated model made drawdown WORSE.
- **Reconciles the folklore.** Regime detection is real and this project
  already does it - the trend gate IS a regime classifier expressed as a
  position. What does not work is regime PREDICTION, and the published
  charts that appear to show it working are usually smoothed in-sample
  fits.
- **Detection and the trading rule are the same object.** There is no
  "detect the regime, then adjust" - by the time detection fires, the
  adjustment has happened. Describing them as two steps invents a
  separation that does not exist.
- **Caveats**: two states only; a three-state model (bull/bear/chop) is
  untested. Monthly frequency. Refit every 12 months rather than every
  month, for EM cost - more frequent refitting could help the
  walk-forward variant somewhat, though it cannot manufacture
  information the filtered probability does not have.


## 34. Rule slate v2 - the family works, the specific rule does not matter

v1 (`tools/backtest_rule_slate.py`) concluded nothing beats SMA200+5%.
The conclusion was unsupportable and partly wrong. Four defects, fixed
in `tools/backtest_rule_slate_v2.py`:

1. **Unequal average exposure** - rules were invested 0.59x to 0.74x of
   the time, so comparing raw CAGR compared risk levels rather than
   rules. This is precisely the error called out in finding 32, made two
   experiments later.
2. **One number per rule**, violating finding 27's own rule, in a tool
   whose docstring claimed multi-window reporting it did not do.
3. **A rigged fight** - finding 24 swept the band on this same data, so
   5% is a SELECTED parameter, while each challenger got one arbitrary
   value. v2 sweeps a small grid per rule and reports the MEDIAN of the
   grid, not the best: best-of-grid is what overfitting looks like.
4. **No confidence interval.** v2 adds a stationary block bootstrap
   (500 resamples, 63-day blocks).

All rules normalised to 1.00x average exposure, French daily total
return 1926-2026, rate-correct financing:

| Rule | CAGR | maxDD | bootstrap 5-95% |
|---|---|---|---|
| buy_hold | 9.83% | -84.1% | 6.37-13.02% |
| **sma200_band5** | **12.30%** | -46.7% | 9.27-14.93% |
| sma_window | 12.03% | -46.6% | 9.15-15.26% |
| abs_momentum | 12.07% | -45.9% | 8.70-15.18% |
| sma_ensemble | 11.71% | -43.7% | 8.97-14.69% |
| sma_volband | 9.96% | -59.3% | 6.65-13.07% |
| drawdown | 8.87% | -51.1% | 5.25-12.24% |

- **Trend rules beat buy-and-hold by ~2.5pp at equal exposure.** v1
  showed them as comparable at 1x because they carried LESS risk for
  similar return; normalising revealed an edge that unequal comparison
  had hidden. v1 was biased toward buy-and-hold.
- **The top three are statistically indistinguishable**: 12.30 / 12.07 /
  12.03 with bootstrap intervals overlapping almost entirely. Different
  lookbacks and different formulations give the same answer within
  noise.
- **This is a STRONGER result than "200/5% is best".** If the edge were
  a fitted parameter its neighbours would fail; they do not. What works
  is the family - slow-lookback trend following with hysteresis - not
  any specific member. Stop tuning the member.
- **Two candidates genuinely failed**: vol-adjusted bands (9.96%) and
  drawdown-triggered (8.87%), both near buy-and-hold with worse
  drawdown than the trend family. The vol-band was my strongest
  candidate on principle, which is a useful reminder that a principled
  argument is not evidence.
- **Crash-contingency holds throughout**: every trend rule loses in
  `no_crash_era`, `letf_era` and `post_gfc_full`, and wins in
  `two_crashes` and `lost_decade`.
- **The remaining threat is not fixed and is the big one.** Nothing here
  is out-of-sample: the 200-day convention was fitted to this exact
  history by decades of practitioners, so the entire family could be one
  large in-sample selection. The only real test is other countries -
  JST's 17 economies and the French developed-market factors are both
  downloaded and unused.
- **Also not fixed**: single asset, and no transaction or tax cost,
  which matters most for abs_momentum at 6.48x/yr turnover in a
  non-registered account.


## 35. Out-of-sample geography - the trend family is real, as a RISK tool

Finding 34's unfixable defect was that the 200-day convention was fitted
to US history by decades of practitioners, so every US result might be
one large in-sample selection. This is the test.

### First attempt failed by confounding, and the control caught it

`tools/backtest_international_trend.py` used JST annual data for 18
countries, 1870-2020. Trend lost in 14/14 non-US countries (median
-1.51pp). But the USA control ALSO lost 1.82pp - where the same rule
family on DAILY US data gains 2.24pp (finding 34).

**Same rule, same country, opposite sign.** The test changed geography
AND frequency at once, and annual decisions carry up to a 12-month
reaction lag, so 1987, 2020 and most of 2008 are invisible. Recorded
because building the US control into the design is what exposed it - a
cross-sectional test without an in-sample control cannot distinguish
"the rule fails here" from "the test is broken".

### The clean test: frequency held constant, US removed

French daily regional factors, 1990-2026, 200-day gate with 5% bands,
warmup live before scoring. Tool: `tools/backtest_oos_geography.py`.

| Region | B&H CAGR | trend | edge | B&H maxDD | trend maxDD |
|---|---|---|---|---|---|
| developed_ex_us | 6.52% | 5.86% | -0.66 | -59.2% | **-27.2%** |
| japan | 3.45% | 3.13% | -0.32 | -59.8% | **-44.5%** |
| europe | 8.01% | 7.34% | -0.67 | -62.1% | **-29.1%** |
| asia_pac_ex_japan | 8.41% | 7.62% | -0.80 | -62.5% | **-34.8%** |
| developed (contaminated, has US) | 8.57% | 8.50% | -0.07 | -57.0% | -24.8% |

- **Trend beats buy-and-hold on CAGR in 0 of 4 clean markets**, median
  edge -0.67pp. **Median drawdown improvement +29.8pp.**
- **The family survives out-of-sample - as a RISK REDUCER, not a return
  generator.** Four markets that played no part in creating the
  200-day convention all show the same trade: give up ~0.67pp/yr, halve
  the drawdown. That is a real repeatable effect with the return claim
  stripped out.
- **The contaminated control has the smallest cost** (-0.07pp with the
  US included vs -0.66 to -0.80 without), which is the in-sample
  advantage appearing exactly where predicted.
- **Japan disappointed.** The lost-decade market was where trend should
  have shone; it cut drawdown -59.8% -> -44.5% but still lost 0.32pp,
  because the 1990-2026 window includes the post-2012 recovery.
- **This CONFIRMS the architecture rather than undermining it.**
  ARCHITECTURE.md's claim is that the gate buys cheap drawdown reduction
  and leverage converts that into return. Out-of-sample, the gate buys
  ~30pp of drawdown for ~0.67pp - which is the cheap insurance the
  leveraged sleeve depends on.
- **NOT exposure-normalised, and this matters.** The trend variants are
  only 56-74% invested. Finding 34 showed normalising exposure is what
  revealed the US edge, turning an apparent tie into +2.5pp. Doing the
  same here would likely flip these signs, so the -0.67pp should be read
  as "at lower risk", not "worse".
- **Caveats**: 36 years, one window, no separate crash/no-crash split
  per region; regional factor series rather than tradeable indices; no
  costs. Four regions are not four independent samples - global equity
  markets are heavily correlated, so this is fewer effective
  observations than it looks.


## 36. Gate the entry phase, not the whole life - the user was right

The user proposed using the trend gate for the first 2-3 years to
cushion entry, then holding unhedged. I argued it was backwards: with
800k deployed and ~2.2M of future contributions, most capital is not yet
invested, so an early crash is a discount and a LATE crash is the
damaging one - implying the gate is worth more later.

Tested. **The user was right and I was wrong.**

73 rolling 27-year windows, 1926-2026, 800k initial + 80k/yr, monthly
gate. Tool: `tools/backtest_entry_phase_gate.py`.

| Policy | median terminal | vs hold | p10 | med maxDD | worst first-3y DD |
|---|---|---|---|---|---|
| always_hold | 24.55M | - | 17.63M | -44.8% | **-75.5%** |
| always_gate | 24.95M | +1.6% | 17.19M | -23.8% | -25.7% |
| **gate_early (3y)** | **24.97M** | **+1.7%** | 16.73M | -44.8% | **-25.7%** |
| gate_late (3y) | 24.55M | +0.0% | 16.18M | -44.2% | -75.5% |

- **Terminal wealth is essentially identical across all four policies** -
  a 1.7% spread. At this contribution rate and horizon the gate barely
  moves the endpoint, which is finding 23 restated: contributions
  dominate.
- **Gating ONLY the first three years captures the entire entry
  benefit.** Worst first-3-year drawdown falls -75.5% -> -25.7%,
  identical to gating forever, at no cost to median terminal wealth.
- **My "worth more later" hypothesis is dead.** gate_late has an
  identical median to holding and a WORSE p10 (16.18M vs 17.63M). Most
  3-year windows contain no crash so it rarely fires, and when it does
  it whipsaws or misses the recovery.
- **The -75.5% figure is the behavioural crux.** Deploying a lump sum
  into 1929, 2000 or 2007 without the gate means watching three quarters
  of it evaporate before contributions can help. That is the scenario
  where a person abandons the strategy permanently - a risk terminal
  wealth cannot see, and the reason MANIFESTO.md lists "a rule the user
  actually follows for 27 years" as the first success criterion.
- **Honest cost**: gate_early's p10 terminal is 16.73M against holding's
  17.63M, so roughly 5% of terminal wealth in the bad tail buys the
  protection. Cheap, not free.
- **Caveats**: monthly gate (10-month SMA) rather than the daily
  200-day rule, so this understates the daily version's
  responsiveness. Rolling windows overlap heavily - 73 starts across a
  century is far fewer independent observations (finding 29). US only.
  No costs or taxes, which matters slightly for the gated variants.


## 37. 2x + PERMANENT gate on the whole portfolio - and finding 36 reverses

Finding 36 concluded the gate earns its keep only during the entry phase.
That holds for 1x and **inverts under leverage**.

73 rolling 27-year windows, 1926-2026, 800k initial + 80k/yr,
rate-correct financing, monthly gate. Total contributed over the
horizon: 2.96M. Tool: `tools/backtest_levered_lifetime.py`.

| Policy | median | p10 | worst | med DD | worst DD | worst 3y |
|---|---|---|---|---|---|---|
| 1x_hold | 24.5M | 17.6M | 13.0M | -44.8% | -80.7% | -75.5% |
| 1x_gate_entry | 25.0M | 16.7M | 12.6M | -44.8% | -80.7% | -25.7% |
| **2x_gate_always** | **65.4M** | **34.3M** | **29.7M** | -48.5% | **-70.8%** | -55.4% |
| 2x_gate_entry | 46.0M | 22.3M | **9.4M** | -76.4% | **-98.2%** | -55.4% |
| 2x_hold_ungated | 48.5M | 22.8M | 10.1M | -76.4% | -98.2% | -96.3% |
| 3x_gate_always | 135.2M | 45.5M | 24.5M | -72.1% | -89.1% | -78.1% |

- **2x with a permanent gate dominates 1x at EVERY percentile including
  the worst case**, and has a better worst drawdown (-70.8% vs -80.7%).
  Median 65.4M vs 25.0M; worst-ever 29.7M vs 12.6M. No window in any
  policy ended below total contributions.
- **Under leverage the gate must be PERMANENT.** 2x_gate_entry's worst
  case is 9.4M against 2x_gate_always's 29.7M, with -98.2% drawdown.
  Finding 36's entry-only conclusion applies to 1x ONLY - at leverage a
  late crash arrives levered and unprotected, which is precisely the
  wipeout finding 30 documented for 1929.
- **3x is not the answer.** Higher median (135M) but a WORSE worst case
  than 2x (24.5M vs 29.7M) and -89.1% drawdown. More pain for a lower
  floor - the tail gets worse faster than the median improves.
- **The decisive number is -70.8%, not 65.4M.** MANIFESTO.md's first
  success criterion is "a rule the user actually follows for 27 years".
  This policy requires watching roughly two thirds of net worth
  disappear while still contributing 80k/yr and not touching it.
- **2x_gate_always makes the ENTRY experience worse, not better**:
  -55.4% in the first three years against 1x_gate_entry's -25.7%. The
  behavioural protection finding 36 bought is spent by leverage.
- **This is not a question about returns.** The data says the strategy
  works. Whether the holder works under it is the untested variable, and
  it is the same variable that decided the user's Bitcoin and NVDA
  positions.
- **Caveats**: monthly gate rather than the daily 200-day rule;
  simulated leverage with calibrated financing but no real LETF tracking
  error (finding 26: TQQQ's is 8.09%/yr); US only; 73 rolling windows
  overlap heavily so this is far fewer independent observations than it
  appears (finding 29); no taxes, which matter for a permanently gated
  strategy in a non-registered account.


## 38. The dot-com analogue - you do not need to predict the hype cycle

The user's central worry: AI likely follows a Gartner hype cycle
(railways, dot-com), so there is short-term bust risk even though the
technology wins long-term. This was the exact conviction failure that
cost them 2022-2026.

Tested against the closest available analogue rather than argued.
QQQ and SPY, 1999-01 to 2003-12, daily 200-day gate with 5% bands,
warmup live, rate-correct financing.

| | ends at | maxDD |
|---|---|---|
| QQQ 1x buy-hold | **0.714x** | -83.0% |
| QQQ 1x + gate | **2.076x** | -41.1% |
| QQQ 2x buy-hold | **0.174x** | -98.6% |
| QQQ 2x + gate | **2.651x** | -69.6% |
| SPY 1x buy-hold | 0.966x | -47.5% |
| SPY 1x + gate | 1.524x | **-11.7%** |
| SPY 2x + gate | 1.801x | -23.3% |

- **The gate turned a -98.6% wipeout into +165% at 2x on QQQ.** It rode
  the 1999 melt-up, exited in 2000, sat out the collapse and re-entered
  in 2003.
- **The strategic point: prediction is not required.** The gate does not
  know whether AI is 1996 or 1999, and does not need to. A hype-cycle
  bust is SLOW, which finding 27 identifies as exactly the shape the
  gate catches (2 of 5 drawdowns caught - both slow ones). The user's
  conviction problem was needing certainty before acting; the rule
  replaces certainty with a response.
- **Concentration amplifies both directions even when gated.** QQQ+gate
  returned 2.076x with -41.1% drawdown against SPY+gate's 1.524x with
  -11.7%. That is 36% more return for 3.5x the drawdown. The choice is
  not "will AI bust" but "how much pain per unit of upside".
- **The technology winning does not imply the equities win.** Railways
  transformed Britain while investors lost ~85%; the internet
  transformed everything while NASDAQ fell 78% and took 15 years to
  recover. In 2000 the obvious winners were Cisco, Intel, Sun and
  Nortel, while much of the value later accrued to firms that did not
  exist at the peak (Google IPO 2004, Facebook 2012). Being right about
  a technology says little about what to own, which is an argument from
  the user's own thesis FOR broad diversification over a concentrated
  Nasdaq bet.
- **Caveats, and they are severe.** n=1. This is a single episode and
  the gate's timing through it is partly luck - a bust that gapped down
  rather than grinding would have caught it (finding 27: COVID and 2022
  both beat the gate). QQQ history begins 1999 so the earlier run-up is
  not in the window. Do NOT read 2.651x as an expectation; read it as
  evidence that the mechanism does not require a forecast.


## 41. Band width: the tight end wins, and adaptive bands fail twice

Two questions, one script (`tools/backtest_adaptive_bands.py`),
US 1926-2026 daily plus the four clean out-of-sample regions of
finding 35 (French developed_ex_US, Japan, Europe, Asia-Pacific ex-Japan).

### 41a. 2% beats the 4-5% that finding 24 selected

CAGR by band, 200-day gate, signal shifted one day:

| band | US_1926 | dev_ex_US | japan | europe | asia_pac |
|---|---|---|---|---|---|
| buy_hold | 9.77% | 6.52% | 3.45% | 8.01% | 8.41% |
| **fixed_2%** | **10.65%** | **7.44%** | 3.59% | **8.59%** | **8.76%** |
| fixed_3% | 10.50% | 5.95% | **3.73%** | 7.72% | 8.47% |
| fixed_4% | 10.58% | 5.75% | 3.51% | 7.78% | 8.54% |
| fixed_5% | 10.44% | 5.86% | 3.13% | 7.34% | 7.62% |
| fixed_6% | 10.04% | 5.15% | 3.05% | 7.34% | 7.42% |

- **2% is best in 4 of 5 markets** (Japan prefers 3%). This CONTRADICTS
  finding 24, which swept SPY 1993-2026 and put 4% top at 2043x against
  5% at 1474x. That sweep ran on 33 years of one market; this runs on a
  century plus four independent regions. Prefer this one.
- **2% also has the shallower drawdown in 4 of 5** (dev_ex_US -18.3% vs
  -28.2% at 4%; asia_pac -25.4% vs -28.9%; europe -26.5% vs -34.2%;
  japan -35.5% vs -41.9%). Better return AND better drawdown is unusual
  and is the reason this is not being dismissed as noise.
- **Cost is switching, and it is affordable.** 2% trades 1.48-2.43
  switches/yr against 0.90-1.46 at 4% - under one extra round trip per
  year. At 1-3bp per side on a liquid ETF that is <10bp/yr against a
  100-170bp CAGR gap. In registered accounts there is no tax drag.
  In a TAXABLE account this conclusion may reverse; not tested.
- **Narrow 4% vs 5% check:** 4% wins 3 of 4 OOS regions. So the user's
  instinct to take 4% over 5% was correct - but both are beaten by a
  value neither sweep nominated.
### 41c. AMENDMENT - on US data specifically, 4% is the right pick

41a chose 2% on a 5-market vote, but the US row is a near-tie (10.65%
vs 10.58%, 7bp over a century) and the money is going into a US-heavy
portfolio. A 7bp gap does not select a parameter, so the question was
re-asked as a DISTRIBUTION rather than a point estimate.
`tools/backtest_band_upside_us.py`: 77 rolling 27y windows, 1926-2026,
800k initial + 80k/yr so sequence-of-returns is live.

| band | p10 | median | p90 (upside) | worst | worstDD | sw/yr |
|---|---|---|---|---|---|---|
| 2% | 16.3M | 23.3M | 43.4M | **12.5M** | -39.3% | 1.47 |
| 3% | 17.6M | 22.8M | 37.8M | 10.7M | -37.1% | 1.08 |
| **4%** | 16.0M | 23.9M | **43.7M** | 10.7M | **-33.4%** | 0.89 |
| 5% | 15.7M | **24.2M** | 40.7M | 10.9M | -33.8% | 0.72 |
| buy_hold | 16.3M | 22.3M | 38.5M | 8.0M | -80.2% | 0.01 |

- **Band width is not what produces the upside.** Gating adds ~5M at
  p90 over buy-hold (38.5M -> 40.7-43.7M) at EVERY width. The gate's
  existence is the edge; its width is a second-order choice.
- **On upside 4% is top (43.7M) but 2% is within 0.5% (43.4M).** Tied.
- The bands differ in the TAILS, and they trade against each other:
  4% has the shallowest worst drawdown (-33.4% vs 2%'s -39.3%) and 40%
  less trading; 2% has the best worst-case terminal (12.5M vs 10.7M,
  +17% on the single worst century path). Tighter bands exit grinding
  bears earlier (better terminal) but whipsaw more (deeper equity
  curve).
- **Verdict: 4% for a US-heavy 27y+ accumulation sleeve.** Top upside,
  shallowest drawdown, least trading. 41a's 2% was driven by the
  international vote and does not hold on US data.
- **NOT extrapolated to a 10-15y horizon** (the parents' sleeve). The
  worst-case column argues 2% there, but this is a 27y test; that
  horizon needs its own run before acting.

- **Caveat.** Adjacent-parameter gaps of 100-170bp are inside the
  bootstrap noise finding 34 measured (~38% swings). The evidence here
  is not the size of the gap, it is that FIVE independent markets agree
  on direction. Treat 2-3% as the region, not 2.00% as the number.

### 41b. Efficiency-ratio adaptive bands fail 0 for 4

Hypothesis: widen bands during whipsaw only. Kaufman Efficiency Ratio
(net move / path length over 20d) separates DIRECTIONLESS movement from
LARGE movement, which is the flaw that sank the volatility version
(finding 34). band = lo + (hi-lo) x (1-ER), so chop widens, trend
narrows. Tested (2,8), (3,10), (2,12).

| region | best fixed | best adaptive |
|---|---|---|
| developed_ex_us | fixed_2% **7.44%** | 6.25% |
| japan | fixed_3% **3.73%** | 3.68% |
| europe | fixed_2% **8.59%** | 7.98% |
| asia_pac_ex_japan | fixed_2% **8.76%** | 7.57% |

- Loses in every out-of-sample market despite fixing the diagnosed
  mechanism of the previous failure. **Two independent adaptive-band
  formulations failing is evidence against the idea, not against the
  implementations.**
- Why it cannot work: whipsaw is only identifiable after it has
  happened. By the time ER registers chop, the whipsaw has already been
  paid for - and you now carry a WIDE band into whatever follows, which
  is sometimes a real bear.
- **Practical rule: fixed bands. Do not adapt them.**


## 42. Breadth leads price by ~14 days - and it is still not tradeable

The sixth regime detector. The previous five (Markov 33, vol bands 34,
credit H9, macro 19/20, efficiency ratio 41b) all consumed the index
return series or something lagging it, so none could be faster than
price by construction. Breadth is different in kind: it asks how many
COMPONENTS are holding up, which the index level cannot express.

Data: French 49 industry daily portfolios, 1927-03 to 2026-06 (26,075
days). Breadth = fraction of industries above their OWN trailing 200-day
mean. Signal threshold 50%, price gate 200d/4%, both shifted one day.

### 42a. The lead is real and statistically strong

16 drawdowns worse than -20%. Breadth crossed 50% BEFORE price crossed
its band in **15 of 16**; sign test p ~ 0.0005. Median lead 14 trading
days, mean 26.

| peak | depth | price sig | breadth sig | lead (d) |
|---|---|---|---|---|
| 2000-03-27 | -49.2% | 2000-10-10 | **2000-03-27** | **137** |
| 1968-12-02 | -36.8% | 1969-06-17 | 1969-02-25 | 77 |
| 1973-01-12 | -48.2% | 1973-03-22 | 1973-01-24 | 39 |
| 2021-11-09 | -25.6% | 2022-01-25 | 2021-12-01 | 37 |
| 1946-05-31 | -28.3% | 1946-08-27 | 1946-07-23 | 25 |
| 2020-02-20 | -34.2% | 2020-03-09 | 2020-02-27 | 7 |
| 1929-09-04 | -84.1% | 1929-10-23 | 1929-10-21 | 2 |
| 1987-08-26 | -33.1% | 1987-10-16 | 1987-10-16 | 0 |

- At the dot-com top breadth fired **on the exact peak day**, 137
  trading days before price. The mechanism is visible: a handful of
  megacaps held the index up while the average stock had already turned.
- **The lead is large for slow, narrow-topped bears (2000, 1969, 1973,
  2022) and ~zero for fast crashes (1987, 1929, COVID).** This is the
  same fast/slow split as finding 27. Nothing detects a gap-down.
- **CORRECTION - the SIZE of the lead is mostly a property of the price
  band, not of breadth.** Re-measured against every band width:

  | price band | median lead | breadth first | breadth late | sign p | dot-com |
  |---|---|---|---|---|---|
  | 2% | 8d | 12/16 | 2 | 0.0129 | 14d |
  | 3% | 12d | 14/16 | 0 | 0.0001 | 14d |
  | **4%** | **14d** | **15/16** | 0 | **0.0001** | **137d** |
  | 5% | 24d | 16/16 | 0 | <0.0001 | 137d |

  The DIRECTION is robust - breadth is first at every width, including
  the tightest (12/16, p=0.013). The MAGNITUDE is not: the headline
  "137 days at the dot-com top" exists only at 4-5% bands, where price
  did not cross until 2000-10. Against a 3% band price was 14 days
  behind. That 137 was the price gate being slow, not breadth being
  fast. What IS band-independent: breadth crossed on 2000-03-27, the
  exact peak, in every configuration.
  The numbers quoted above (14d, 15/16) are correct FOR the 4% band
  chosen in 41c, and should always be quoted with the band stated.

### 42b. The lead does not convert into return

| variant | CAGR | maxDD | sw/yr |
|---|---|---|---|
| price 4% alone | **10.59%** | **-37.8%** | **0.89** |
| breadth 50% alone | 10.10% | -43.6% | 5.99 |
| either-exits (fastest) | 9.61-10.05% | -38.7% | 3.0-4.6 |
| both-must-exit | 10.53-10.65% | -38.7% | 1.9-2.9 |

Acting EARLIER on breadth - the entire point - is WORSE (9.61-10.05%
against 10.59%). The best blend beats price alone by 6bp on 2.1x the
turnover, which is noise.

**Why: the sensitivity that makes breadth fast makes it noisy.** It
fires ~6x/yr against price's 0.89. It catches all 16 bears early AND
cries wolf continuously between them. Filtering the false positives
reintroduces exactly the lag being removed.

### 42c. As a leverage modulator - also not worth it

Softer action (2x -> 1x on weak breadth) so false positives cost less.
27y windows, 800k + 80k/yr, 76 starts:

| policy | p10 | median | p90 | worst | worstDD |
|---|---|---|---|---|---|
| 2x_gated | 49.4M | **85.5M** | **154.4M** | 27.6M | -61.6% |
| 2x_gated + breadth delever | **52.4M** | 78.4M | 144.8M | **28.2M** | **-60.2%** |

+6% at p10 and +2% at worst, for -8% of median and -6% of p90, at 4.42
switches/yr against 0.89. The tail gain is inside the +/-38% bootstrap
band of finding 34 and trading costs are not charged. **Rejected.**

### 42d. What it IS good for

Breadth is real information that cannot be traded. That makes it an
**INFO alert, not an ACTION alert** (the split src/alerts.py already
implements): "the average stock is rolling over while the index holds
up". It would have said that on 2000-03-27. It does not say sell.

**Six detectors, six failures to beat a fixed-band price gate. The
crude gate remains undefeated. Stop building detectors.**


## 43. Sector rotation - a real historical effect, NOT tradeable (see 45)

> **SUPERSEDED IN PART BY FINDING 45.** The decisive test on the actual
> investable universe (11 SPDR sector ETFs) found NO edge - every
> momentum variant loses to equal-weighting. Read 45 before acting on
> anything below. The century-scale effect in 43a is real; the claim
> that it is exploitable is not.

Not detector #7. Findings 33/34/41b/42/H9 tested ideas I invented;
industry momentum is documented (Moskowitz & Grinblatt 1999) and
cross-sectional momentum is among the most replicated anomalies in
finance. Data: French 49 industry portfolios, daily 1926-07 to 2026-06.
Standard 12-1 spec, NOT tuned: rank on months t-11..t-1 skipping the
most recent month, equal weight, monthly rebalance.

### 43a. The effect is real and survives its controls

| strategy | CAGR@0bp | @25bp | maxDD | turnover/mo |
|---|---|---|---|---|
| cap-wtd market | 10.27% | 10.27% | -83.9% | 0.00 |
| **EW all 49 (control)** | **10.72%** | 10.72% | -80.8% | 0.00 |
| mom_top5 | 16.85% | 15.45% | -69.0% | 0.41 |
| mom_top10 | 15.53% | 14.36% | -62.3% | 0.34 |
| mom_bottom10 | 4.66% | 3.63% | -90.3% | 0.33 |

- **Monotonic**: top5 > top10 > top15 > EW > bottom10. Winners minus
  losers +9.02%/yr, t=4.70, p=2.9e-6 over 1,188 NON-OVERLAPPING months
  (so no finding-29 overlap inflation).
- **The equal-weight confound was checked and is not the explanation.**
  mom_top10 beats EW-all-49 by +3.63pp after 25bp, t=4.38, p=1.3e-5.
  EW itself adds only 0.45pp over cap-weight.
- **Survives publication.** Split at 1999: mom_top10 excess over market
  fell from +5.3pp to +3.8pp. Decay, not disappearance - consistent
  with McLean & Pontiff's ~50% post-publication decay.

### 43b. It composes with the gate - different jobs

| strategy | CAGR | maxDD |
|---|---|---|
| market buy-hold | 9.83% | -84.1% |
| market + daily 4% gate | 10.63% | -37.8% |
| mom_top10 ungated | 13.90% | -74.9% |
| **mom_top10 + daily gate** | **13.11%** | **-36.6%** |
| mom_top5 + daily gate | 13.62% | -38.1% |

**+2.5pp/yr over the gated market at the SAME drawdown.** Momentum
supplies return and NO protection; the gate supplies protection and
little return. They solve different problems, which is why they stack.
Every earlier idea tried to do the gate's job better and lost.
NOTE: a MONTHLY gate hurts (12.12% vs 15.53%) - it is too slow. Use the
daily gate.

### 43c. Why it may not be tradeable - the granularity cliff

| universe | best mom vs EW (25bp) | spread significance |
|---|---|---|
| 49 industries | +3.63 to +4.93pp | t=4.38, **p=1.3e-5** |
| 12 industries | +0.23 to +1.88pp | t=2.77, p=0.006 |
| 10 industries | +1.23 to +1.59pp | t=1.63, **p=0.10 (ns)** |

- **The edge lives in fine distinctions that vanish when bucketed.**
  At the ~11-sector granularity of real SPDR sector ETFs it is worth
  ~1.5pp and is NOT statistically distinguishable from zero.
- Trading 49 industries needs niche ETFs at 0.35-0.50% expense against
  SPY's 0.03%; most did not exist before 2000. That fee gap alone eats
  ~10% of the gross edge and is NOT charged above.
- **Momentum has its own crash mode.** 12m to 2009-02: momentum -47.8%
  vs market -42.5%. It underperformed DURING the crash and again in the
  rebound. Ungated maxDD -62% to -77% - this is a return enhancer
  carrying full equity risk, not a risk tool.

**Realistic expectation for an implementable version: +1 to +1.5pp over
the gated market, with a real chance of zero. Promising, not
actionable.** Next: test on an actual tradeable ETF universe with real
fees, post-2000 only.

### 43d. Process note - a lookahead bug was caught mid-run

The first run showed market_gated_4% at 16.97% CAGR / -20.7% maxDD
against ~10.6% / -37.8% everywhere else in this repo. Cause:
`.resample("ME").last()` takes the gate state on the FINAL day of month
T, which was then applied to month T's return. Same causality class as
the +271% SMA200 bug. **Heuristic confirmed again: a familiar strategy
printing an unfamiliar number is a bug until proven otherwise.** The
momentum figures never touched the gate and were unaffected.


## 44. Top-10 concentration - no edge, and the bias points at the answer

Redo of the concentration test with the contamination fixed. Archive
minute data 1994-2025, ranked annually by trailing-December dollar
volume, held equal-weight-by-dollar-volume through the year.

Fixes over the first attempt: exchange TEST symbols (ZVZZ.T, TESTB)
removed - they caused a 1e196 overflow; levered/inverse ETFs blocklisted
after auditing top-10 membership (FAS, SKF, QID, IYR, OIH all appeared,
clustered 2006-2010); INTCW (an Intel WARRANT, not the stock) removed;
MIN_PRICE 5.00 and a >50%-single-day corruption drop.

| portfolio | terminal | CAGR | worst yr |
|---|---|---|---|
| US market 1994-2025 | 26.92x | 10.85% | (maxDD -54.6%) |
| top10 | 56.48x | 13.43% | -54.9% |
| top25 | 17.18x | **9.29%** | -53.6% |

Looks like a large win. It is not.

| portfolio | mean excess/yr | sd | t | p | beat mkt |
|---|---|---|---|---|---|
| top10 | +8.46pp | 26.8pp | 1.76 | **0.089** | 21/32 |
| top25 | +2.94pp | 20.7pp | 0.79 | **0.435** | 18/32 |

- **Not significant, and fragile.** Dropping the single best year (2023,
  +83pp) takes top10 to +6.07pp, t=1.41.
- **Top-25 shows nothing (p=0.435).** A genuine size effect would not
  vanish between N=10 and N=25. The non-monotonicity is the tell.
- **The ranking bias points the same way as the result.** No shares
  outstanding in the archive, so ranking is by DOLLAR VOLUME, which
  overweights high-turnover speculative names. In this sample those were
  TSLA, NVDA, AMD, MSTR, PLTR - all large winners. A bias aligned with
  the hypothesis cannot be used to support it.
- **Arithmetic +8.46pp compounds to only +2.58pp.** Volatility eats
  5.9pp. Worst year -54.9% against the market's -54.6%: identical pain,
  no reliable gain.
- Consistent with Bessembinder (2018): ~4% of stocks create all net
  wealth, so 10 names most likely holds NONE of them. Concentration
  widens the distribution rather than shifting it.

**Verdict: no evidence that holding the largest names beats the market.
RULED OUT.** Caveat: yfinance began returning HTTP 401 on split lookups
mid-run, so split adjustment for delisted names rests entirely on the
strip_splits heuristic. Treat magnitudes as directional.


## 45. Sector momentum on tradeable ETFs - no edge. Finding 43 closed.

The decisive test of finding 43. Same 12-1 momentum, run on the 11 SPDR
sector ETFs (the universe actually purchasable) 1999-2026, charging real
costs: 0.09%/yr expense plus 10bp per unit turnover.

**Correction to 43c**: it claimed 0.35-0.50% expense ratios. That is
right for niche INDUSTRY ETFs but wrong for the SPDR sectors, which
charge ~0.09%. The tradeable version is CHEAP. Fees are not what kills
it - there is simply nothing there.

| strategy | CAGR | maxDD | vs EW | t | p |
|---|---|---|---|---|---|
| **EW all 11 (control)** | **8.64%** | -49.2% | - | - | - |
| SPY | 8.22% | -50.8% | -0.42pp | | |
| mom_top2 | 8.44% | -45.3% | -0.20pp | 0.21 | 0.83 |
| mom_top3 | 8.29% | -41.5% | -0.35pp | -0.01 | 0.99 |
| mom_top4 | 8.33% | -43.6% | -0.31pp | -0.06 | 0.95 |
| mom_top5 | 7.97% | -42.1% | -0.66pp | -0.46 | 0.65 |

**Every variant LOSES to equal-weighting all 11 and never trading.**
Not weak - negative, t indistinguishable from zero.

### Granularity vs recency - the control that changed the conclusion

43c blamed granularity, but the SPDRs only start in 1998-12, so
"too coarse" was confounded with "too recent". Re-running the French
portfolios restricted to 1999+ separates them:

| universe, 1999+ | top3 excess | t | p |
|---|---|---|---|
| French 49 | +5.73%/yr | 1.58 | **0.11** |
| French 12 | +2.60%/yr | 1.49 | 0.14 |

- **The 49-industry edge is NOT significant post-1999 either** (full
  century: t=4.38, p=1.3e-5). Power alone does not explain it: if the
  effect size were unchanged, t should fall to ~2.3 on 318 months, not
  to 0.95 (top10). The effect roughly HALVED.
- So both mechanisms are operating - coarse buckets AND post-publication
  decay - and neither leaves anything to trade.

### Verdict

**Sector rotation is RULED OUT for this portfolio.** The century-scale
effect in 43a is real and survives its controls; it is simply not
available at tradeable granularity in the modern era. 43's "+2.5pp over
the gated market" should not be quoted without this finding attached.

### The one usable residue

**Equal-weighting the 11 sectors beat SPY by +0.42pp/yr with a shallower
drawdown (-49.2% vs -50.8%), with no timing and no forecasting.** Same
equal-weight premium visible in the French data (EW-49 10.72% vs
cap-weight 10.27%). Small, free, and implementable - RSP exists. Worth a
proper test as a core-holding substitute, NOT as a rotation strategy.

### Process note

This is the third time a promising result has died on the control rather
than on the headline (see 35, 44). The pattern to keep: never report an
effect without running the benchmark that shares its structure -
equal-weight for a concentrated portfolio, same-period for a
different-universe claim.
