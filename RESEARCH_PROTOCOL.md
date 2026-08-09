# RESEARCH PROTOCOL - how an agent picks up this work

You are one of many sessions. Sessions run often and do not share
memory. This file is the handoff.

Read order, every session, before doing anything:
1. `MANIFESTO.md` - the mandate. What counts as success.
2. This file - the standards and the queue.
3. `claude/findings.md` - what is already known. **Do not re-derive.**
4. `RULED_OUT.md` - what has already failed. **Do not retry.**
5. `TODO.md` - open work.

Then pick ONE hypothesis from the queue, run it, record it, commit.
One hypothesis per session beats five half-finished ones.

---

## The bar

From `MANIFESTO.md`: beat **100% XEQT bought and held**, on **terminal
wealth after tax and costs**, over the full period. 27-year horizon,
contributions ongoing, no withdrawals.

Consequences that trip people up:
- **Lower drawdown is not success.** It is only success if terminal
  wealth also holds up. Findings 1, 19, 20 all traded return for
  drawdown; for this mandate that trade is backwards.
- **Higher Sharpe is not success.** Finding 3: SMA200 matched buy-hold's
  Sharpe exactly (0.56) while giving up a third of the CAGR.

---

## Anti-overfitting rules - NOT OPTIONAL

The failure mode of running research every hour for a week is
generating a mountain of confident, fitted noise. PBO across the
existing 48 strategies is already **0.36** (0.5 = pure noise). Every
strategy added raises the multiple-testing burden on all of them.

**A result that violates any rule below does not go in
`claude/findings.md` as a positive result.**

1. **Warmup must be live.** Load price history from well before the test
   window so every signal is emitting from the first test day. Finding 3
   was flattered to ~18% by a 200-day warmup that happened to sit on a
   crash; the fair test gave 6.4%. **Check this first, every time.**
2. **Walk-forward, not full-sample.** Fit on a window, test on the next,
   roll. A full-sample result is a hypothesis, not evidence.
3. **Report the whole sweep, not the winner.** If 40 parameter sets were
   tried, say so and give the distribution. A best-of-40 with no
   denominator is meaningless.
4. **Declare the hypothesis before running it.** Write it in the queue
   entry first. Post-hoc explanations of what the data showed are how
   fitted results get laundered into findings.
5. **Negative results are findings.** Record them in `RULED_OUT.md` with
   the numbers. They are what stops session 47 repeating session 3.
6. **Costs, always.** Slippage, spread, and for LETFs the daily-reset
   decay. A gross-return edge that dies at 10bp of cost is not an edge.
7. **State n.** Five drawdown episodes is not a sample. Say so.
8. **No promotion on forward data alone.** Months of paper trading
   cannot distinguish skill from luck. The attribution monitor's
   `off_script` flag is the forward-test signal, not P&L.
9. **A number in markdown is not evidence.** `claude/findings.md` is
   prose written by LLM sessions. Every quantitative claim must be
   re-derivable by a test in `tests/test_findings_reproduce.py`. A
   finding that no test reproduces **may not be cited as evidence for a
   decision** - quote it as an open question instead.
10. **Never report a raw p-value on overlapping forward returns.**
    Forward-12m returns from consecutive months share 11 of 12 months,
    so 387 monthly observations are ~32 independent ones and
    significance is inflated by roughly sqrt(12). Finding 29 is the
    case: a VIX result at p=0.048 became p=0.42-0.96 at every
    non-overlapping offset. Report non-overlapping samples, or
    Newey-West / block-bootstrap errors. **State the effective sample
    size, not the row count.**
11. **State the minimum detectable effect before believing a null.**
    With ~6 independent observations per bucket the smallest detectable
    difference is ~19pp; a 10pp spread is invisible either way. An
    underpowered test is not evidence of absence, and an underpowered
    test that finds something is usually finding noise.
12. **Record the SPECIFICATION, not just the number.** State the tool,
    the parameters, the window, the warmup and the check frequency.
    Finding 3 is the cautionary case: buy-hold reproduces to a decimal
    place, but its overlay claim of -19% maxDD comes out at -34.8% on an
    independent monthly-checked build. Almost certainly it used daily
    checking and never said so - finding 24 shows frequency alone moves
    maxDD by ~12pp. The number was probably right and is now
    unfalsifiable, which is nearly as bad as being wrong.

---

## Experiment lifecycle

```
hypothesis (in queue, written BEFORE running)
   -> tools/<name>.py            reproducible, no notebook-only work
   -> data/<name>.json           raw numbers
   -> tests/                     if it adds a reusable component
   -> claude/findings.md         if positive, WITH caveats and n
      RULED_OUT.md               if negative, with the numbers
   -> conventional commit explaining what changed and why
```

Every tool takes its inputs from `data/`, writes JSON, and prints a
table. No result exists until it is a committed file.

---

## What we have

**Data**
| Source | What | Caveats |
|---|---|---|
| `data/historical_long/*.json` | 60+ tickers daily, plus 11 macro price series and 10 FRED series | FRED_* are current-vintage, context only |
| `data/vintage/*.json` | 8 ALFRED point-in-time macro series | Use `src/vintage_data.py`, never join on period label |
| `E:\ColdStorage\OHLCV-1m` | 82 GiB, 22k tickers, 1-minute, 1992-2026 | Use `src/minute_data.py`. FIVE traps - see `spikes/minute_data.md` |
| `E:\ColdStorage\*.tar` | 63 GiB, 2019 vintage | **NEVER OPENED.** Unknown contents. |
| Alpaca | 6 paper accounts, live forward test | Never change the live test unprompted |

**Code**
- `src/minute_data.py` - minute archive, handles splits/symbol history/TZ/bad prints
- `src/vintage_data.py` - point-in-time macro, publication-date gating
- `backtesting/` - engine, 50+ strategies, validation, PBO machinery
- `src/alerts.py` - signal-change alerting

**Environment**: `.venv` in repo root. `python -m pytest tests/ -q`
before any commit touching `backtesting/`. 378 tests currently pass.

---

## Honest notes on the tempting ideas

**Machine learning (boosted trees, etc.).** The binding constraint is
sample size, not model class. Monthly rebalancing over 30 years is ~400
observations, and regime-correlated, so the effective independent sample
is far smaller - maybe 20-40 regime episodes. A GBM with 30 features on
400 rows will fit noise perfectly and generalise nothing, and feature
importances will look convincing while meaning nothing. If ML is tried:
few features, heavy regularisation, walk-forward only, and compare
against a linear baseline. **If it cannot beat regularised linear
regression, it has learned nothing real.**

**Low latency.** Irrelevant here. These strategies rebalance monthly.
Latency matters for execution-sensitive intraday alpha, which is not
this mandate.

**Buying data.** Possibly worth it, but only after the free data is
exhausted - and the tar has never even been opened.

**LLMs.** Good for reading papers, generating hypotheses, and writing
tooling. Bad as a signal source: they cannot be backtested honestly
because their training data overlaps the test period. Do not put an LLM
in a trading rule.

---

## The queue

Format: hypothesis, how it will be judged, status. Add to the bottom.
Claim one by marking `[~]` with a session date.

- [ ] **H1. Re-verify `canary_daa_2x` (18% CAGR) with live warmup and
  walk-forward.** Judged by: does it still beat buy-hold on terminal
  wealth after costs when the signal is live from day one? This is the
  current champion and the single highest-value open question.
- [ ] **H2. Re-run all leveraged trend strategies on full history with
  live warmup.** Finding 3 says timing pays on leveraged funds but not
  1x. Judged by: does the leveraged result survive the same warmup fix
  that destroyed the 1x result?
- [ ] **H3. Yield curve as a leading signal.** T10Y3M is a market price
  (no publication lag) and economically leading - the one macro shape
  findings 19/20 did not rule out. Judged by: does it add terminal
  wealth over buy-hold, or only reduce drawdown?
- [ ] **H4. LETF whipsaw cost from real intraday paths.** Daily bars
  cannot measure daily-reset decay. Judged by: how much does chop
  actually cost a 2x/3x trend strategy vs the daily approximation?
- [ ] **H5. Cross-source data validator.** yfinance vs HuggingFace vs
  the tar. Two known errors to catch: `BAMLH0A0HYM2` truncated to
  2023-08 (series starts 1996) and UPRO claiming a 2000 start for a 2009
  fund. Judged by: does it catch both without flagging good data?
- [ ] **H6. Open the tar.** 63 GiB, never inspected. Judged by: what is
  in it, and is it a usable third source?
- [ ] **H7. Contribution-aware backtests.** Every existing backtest is
  lump-sum. The mandate has ongoing contributions, which changes the
  value of drawdowns (they become purchases). Judged by: do any
  rankings change when contributions are modelled?
- [ ] **H8. Regularised linear baseline for trend.** Before any ML,
  establish what a simple regularised model achieves on the same
  features, walk-forward. Judged by: it becomes the bar ML must clear.
