# AlphaOracle

AI-powered paper trading research system: 6 Alpaca paper accounts, daily
LLM analysis, a 50+ strategy backtesting lab with statistical validation,
and a research papers library. Astro dashboard on GitHub Pages.

## Context (read in this order when starting work)

1. `claude/agents.md` - workflow + the 8-step research loop
2. `claude/context.md` - architecture
3. `claude/current.md` - session log (newest first)
4. `claude/findings.md` - canonical registry of empirical findings

## Hard rules

- **Never change the live forward test** (config/accounts.json, workflow
  execution steps, account strategies) unless explicitly asked.
- **Tests are non-negotiable**: `python -m pytest tests/ -q` before any
  commit touching backtesting/. The contract tests include no-lookahead
  causality checks - a strategy failing causality does not get backtested.
- **Document religiously**: results -> `claude/findings.md` (numbers, not
  adjectives), session narrative -> `claude/current.md`, paper verdicts ->
  `papers/`. Failures are findings too.
- **Legal paper sources only** (no sci-hub); personally-licensed material
  goes in `papers/private/` (gitignored), never the public repo.
- Conventional commits (feat/fix/refactor/chore/test/docs).

## Environment notes

- Python: system install (no .venv on this machine); pandas/numpy/scipy/
  pytest/yfinance/pypdf installed globally.
- Frontend build needs Node >= 18: portable Node 20 lives in
  `$TEMP/node-v20.19.0-win-x64/` (see memory/alphaoracle-local-build-env).
- gh CLI at `C:\Program Files\GitHub CLI\gh.exe` (may need PATH export).
- Backtest data: `data/historical_long/*.json` (60+ tickers incl. ^VIX,
  ^VIX3M, HYG/LQD, ^TNX/^IRX). Standard validation run:
  `python backtesting/run_validation.py`.
