# Maturity Roadmap: Taking AlphaOracle to the Next Level (2026-06)

User question: what else can we do, how do we mature, what do sophisticated
funds do that we don't, and what can a small player do that funds can't?

## Where we honestly are

Strong: a research factory (papers -> hypothesis-first strategies -> causal
tests -> validation gauntlet -> honest verdicts) that most retail operations
and some small funds don't have. Weak: the loop is OPEN - we validate
strategies but the forward test runs older, mid-tier strategies, and nobody
checks whether live behavior matches backtest expectations. We have no
portfolio-level risk system, market orders for execution, no tax layer in
headline numbers, and one data vendor (yfinance) as a single point of failure.

## What sophisticated funds do that we don't (ranked by adoptability)

1. **Live-vs-expected attribution (the open loop).** Funds reconcile every
   day's P&L against model expectation; strategy drift triggers review.
   We never compare Alpaca account curves to backtest distributions.
   -> ADOPT FIRST. `src/attribution.py`: pull account equity from Alpaca,
   compute rolling Sharpe/DD, place them in the strategy's bootstrap
   percentile bands from the gauntlet; publish a "on script / off script"
   panel to the site; alert (red workflow) when an account breaches its
   5th-percentile band. This closes the loop and makes the paper-trading
   phase actually decisive.
2. **Portfolio-level risk governor.** Funds have pre-trade checks, exposure
   caps, and kill switches ABOVE the strategy layer. Our executors trust
   their strategies completely.
   -> ADOPT: a risk module in the execution path - max account DD trigger
   (de-risk to cash + require manual re-arm), gross exposure cap, sanity
   bounds on order notional vs equity. Cheap insurance against both market
   events and our own bugs.
3. **Strategy decay monitoring.** Published premia decay; funds re-validate
   continuously. Our gauntlet runs when we remember.
   -> ADOPT: monthly scheduled re-run of run_validation.py on fresh data in
   CI; diff the scoreboard; flag any strategy whose rolling 2y Sharpe falls
   below its bootstrap p5 ("decay alarm").
4. **Meta-allocation (strategy-of-strategies).** Funds size sleeves
   dynamically by risk/correlation; our lab_winners_blend is static
   40/30/30. -> RESEARCH: inverse-vol or regime-conditional weights across
   the validated sleeves; test vs the static blend in the gauntlet.
5. **Execution quality.** TWAP/limit orders, auction awareness; we market-
   order. At our size this is small but free: switch executors to
   marketable limit orders away from the open/close.
6. **Macro nowcasting.** Funds run regime models on macro flow (rates,
   credit, growth surprises). Our inputs are queued (^TNX/^IRX, HYG/LQD,
   VIX term structure) - round-5 strategies + a macro layer for the LLM
   analysts.
7. **Tail-hedging programs** (Universa-style convexity overlays). Ties to
   the options/VRP thread - the BUY side of the vol market, small ladder of
   far-OTM puts funded by the VRP sleeve. Research only after options data.
8. **Red-team discipline.** Funds institutionalize adversarial review; our
   gauntlet automates part of it. ADOPT as cadence: a quarterly "kill
   session" whose only goal is to break the current winners.

Not worth chasing at our scale: co-location/HFT, alt-data ($$$, crowded),
prime-broker leverage, securities lending.

## The small-player edges (what funds CANNOT do)

1. **No career risk = we can hold what institutions can't.** Our winners
   spend 2.2-3.2 YEARS underwater (finding #6). A PM gets fired for that;
   we just... wait. Strategies with long underwater periods are
   structurally underpriced because institutions can't own them. This is
   our single biggest edge and our lab already selects for it.
2. **No redemptions, no monthly marking.** We optimize 10-year outcomes,
   not quarterly letters. Time arbitrage is real and free.
3. **Tax alpha (Canada).** TFSA/RRSP make our high-turnover strategies
   (22 trades/yr regime rotation, 24bps breakeven) viable tax-free, and
   asset location is worth ~0.5-1%/yr - personal, unscalable, invisible to
   funds. ADOPT: a tax-placement note per strategy in the scoreboard
   (registered-only vs taxable-ok, using the breakeven-cost lens).
4. **No benchmark hugging / tracking-error freedom.** A 40% GLD allocation
   month is a non-event for us and a career event for a PM.
5. **Zero market impact.** Patient limit orders at any size we'll ever trade.
6. **Behavioral edge via automation.** Most retail alpha is lost to panic;
   ours executes on schedule regardless of mood. Already built - protect it
   (the risk governor's manual re-arm is deliberately the only human step).
7. **We can change our minds in a day.** No IC, no mandate letters -
   research-to-deployment in one session (with the gauntlet as the only
   gatekeeper).

## The roadmap

**Tier 1 - now, free (maturity):**
- [ ] Attribution monitor (live vs bootstrap bands) + site panel  <- biggest
- [ ] Portfolio-level risk governor with manual re-arm
- [ ] Monthly decay-alarm re-validation in CI
- [ ] Round-5 strategies: VIX term structure, credit momentum, curve regime
- [ ] Meta-allocator research (dynamic sleeve weights)
- [ ] Limit-order execution upgrade
- [ ] Tax-placement column in the scoreboard

**Tier 2 - small spend:**
- [ ] Options data ($50-100/mo) -> VRP sleeve + later tail-hedge research
- [ ] FRED API key (free) -> macro nowcast layer
- [ ] Second EOD data source as integrity check vs yfinance

**Tier 3 - structural:**
- [ ] Investment Policy Statement: written mandates per account, risk
      limits, intervention rules, graduation criteria (paper -> real)
- [ ] Quarterly kill session (red-team the winners)
- [ ] Graduation framework: predefine the evidence that promotes a paper
      strategy to real capital (e.g. 6mo on-script attribution + gauntlet
      survival + IPS fit) so the decision is made by criteria, not mood

## The one-sentence thesis

We can't out-scale, out-speed, or out-data the funds - but we can hold what
they can't hold, wait what they can't wait, compound tax-free where they
can't, and (rarest of all at retail) measure ourselves with their rigor.
The next level is closing the loop: attribution, governor, decay alarms,
and written rules for promotion to real money.
