# Developing & Backtesting Systematic Trading Strategies

**Citation:** Peterson, B. G. (2017, living document). *Developing &
Backtesting Systematic Trading Strategies.* (Author of R's quantstrat /
PerformanceAnalytics / blotter.) CC BY-NC-SA.

**Links:** [GitHub source](https://github.com/braverock/quantstrat/tree/master/sandbox/backtest_musings)
| PDF: [pdfs/peterson_strat_dev_process.pdf](pdfs/peterson_strat_dev_process.pdf)
| Companion: [pdfs/peterson_research_replication.pdf](pdfs/peterson_research_replication.pdf)
| His 60-entry BibTeX bibliography: [../papers/peterson_bibliography.bib](peterson_bibliography.bib)
| Found via r/quant thread (the 403'd braverock.com bibliography lives in this repo).

## Claims

- A complete practitioner methodology for strategy development: hypothesis
  FIRST (before touching data), then specification, then testing - the
  opposite of mine-then-rationalize.
- Key disciplines: define the business case and expected properties up front;
  test components (signals, rules) separately before the full strategy;
  walk-forward and parameter-region stability (a strategy whose performance
  collapses one parameter-step away is curve-fit); deflated Sharpe and
  White's reality check for multiple testing; treat the backtest as an
  experiment log, not a sales document.
- The research_replication companion: how to replicate published research
  skeptically (most published results weaken on replication).

## Criticisms

- A methodology document, not a peer-reviewed result - its authority is
  Peterson's practitioner standing (DV Trading / R finance stack).
- Aimed at intraday/futures contexts in places; some tooling specifics are
  R-ecosystem.

## AlphaOracle verdict

The closest thing to a METHODOLOGY BIBLE for what this repo does, and we
already follow much of it accidentally (hypothesis from published papers
first, baselines always-on, regime slices ~ walk-forward, honest failure
documentation in the strategy lab). Gaps it exposes in our process:

1. No parameter-region stability tests (our strategies use single fixed
   parameters - we don't know how sharp the peaks are),
2. No deflated Sharpe yet (flagged in [deflated_sharpe.md](deflated_sharpe.md)),
3. Backtest assumptions (zero cost, month-end fills) not stress-tested per
   strategy.

His .bib file (60 entries) doubles as a reading list for future library
rounds.
