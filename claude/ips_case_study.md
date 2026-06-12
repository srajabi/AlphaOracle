# IPS-as-Code: The Family Case Study (2026-06)

Research artifact, not advice; the user (principal data scientist) makes
the decisions and asked for evidence-grounded RULES precise enough to
automate. This is the project's grounding case study. Implemented signal
feed: `src/family_signals.py` -> `data/family_signals.json` daily.

Correction from prior study: capital sits in short-term treasuries
(~inflation-neutral), not cash - no urgency penalty; entries are rule-gated,
not calendar-rushed.

## Mandate P - stochastic-horizon household (the parents pattern)

**Objective:** equity engine with a hard sequence-risk brake; horizon is
"probably 15y, possibly 18mo" so the rules must work in both.

- **Structure (evidence basis):** 75% global equity ETF / 25% short-term
  treasuries, with the two-channel overlay on the equity sleeve.
  Evidence: at-top entries 75/25+overlay = worst 5y outcome +16%, worst
  maxDD -17% (findings #1 + allocation study); two-channel design wins
  all three crisis shapes (finding #13).
- **Slow channel (monthly):** at month-end close, equity sleeve vs its
  200-day SMA. Below -> sleeve to treasuries. Above -> sleeve invested.
  One check per month, first trading day execution. (~41 trades/33y
  historically; whipsaw cost ~0.5%/yr; finding #5.)
- **Fast channel (daily):** 5d-median ^VIX/^VIX3M > 1.0 -> sleeve to
  treasuries NOW regardless of trend; re-enter when ratio < 1.0 AND
  monthly trend allows. (COVID-class protection: finding #13, -7.6%.)
- **Rebalance:** bands ±5% on the 75/25 split, checked monthly.
- **Entry rule = management rule:** deploy the sleeve per the channels'
  CURRENT state (if risk-on today, deploy; if not, the treasuries
  position IS the strategy's current instruction). No DCA logic needed -
  the channels already encode "when to be in."
- **Tax note:** registered room is maxed (user-stated); overlay exits in
  taxable accounts realize gains. Accepted trade-off per mandate
  (sequence-risk protection > tax drag), revisit if turnover exceeds
  ~2 round trips/yr.

## Mandate Y - risk-willing individual (the user pattern)

**Objective:** max growth subject to no-ruin; tournament aggressive
division is the eligible set.

- **Core (75-80%):** global equity ETF, same two-channel overlay
  (optional - the user may run the core unhedged given risk tolerance;
  both variants' stats are in the registry).
- **Satellite (20-25%):** ONE aggressive-division champion, run exactly
  as registered in the repo. Candidates by temperament:
  - canary_daa_2x: 18% CAGR backtest, GFC +13%, monthly cadence
  - vol_target_qqq_2x: the dot-com survivor, daily vol scaling
- **Sizing rule = gap math (finding #14):** satellite gap-risk at 15%
  overnight x weight must stay > -10% of portfolio. (canary_daa_2x:
  -22.5% x 0.25 = -5.6% OK; a 3x rule at -45% caps at 22%.)
- **Promotion discipline:** satellites must be tournament champions AND
  on-script in the attribution monitor; an off_script flag = freeze
  additions, review.

## The automation contract (built)

`src/family_signals.py` runs in the daily workflow and emits
`data/family_signals.json` + a human-readable block in the run log:

- slow_channel: equity vs 200dma at last month-end (risk_on/risk_off)
- fast_channel: VIX/VIX3M 5d-median state
- credit: HYG/LQD 63d relative momentum vs -2%
- canary: 13612W breadth (EWA, TLT)
- composite instruction per mandate: INVESTED / SLEEVE_TO_TREASURIES /
  (for Y-satellite: champion's own published state)

The user can consume the JSON from their own GitHub Action (email/
notification/order tickets - their side). This repo only ever
emits signals; it does not touch external accounts.

## Standing honesty

Backtests zero-cost; 2004+ window gold-friendly; published rules decay
(PBO 0.36); the overlay's worst historical enemy is sideways chop
(whipsaw years cost 1-3% each). The attribution monitor exists to catch
live divergence - trust it over conviction, ours or anyone's.
