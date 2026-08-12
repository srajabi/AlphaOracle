# AlphaOracle

AI-powered paper trading research system: 6 Alpaca paper accounts, daily
LLM analysis, a 50+ strategy backtesting lab with statistical validation,
and a research papers library. Astro dashboard on GitHub Pages.

## Context (read in this order when starting work)

1. **`claude/HANDOFF.md` - START HERE.** Organised state of the
   research: the conclusion, the strategy with exact parameters, every
   experiment and its outcome, data locations, and the traps. Read this
   before findings.md, which is 2,200 lines in chronological order.
2. `claude/agents.md` - workflow + the 8-step research loop
3. `claude/context.md` - architecture
4. `claude/current.md` - session log (newest first)
5. `claude/findings.md` - canonical registry of empirical findings
   (chronological; several entries are SUPERSEDED - check for a banner
   under the heading before acting on any of them)
6. `claude/REPRODUCE.md` - finding -> script -> output map, plus the
   KNOWN GAPS in reproducibility. **Findings 1-17 predate the protocol
   and are unverified;** one of them already failed to reproduce.

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

- Python: **repo-local `.venv` (3.12.13) - use `.venv/Scripts/python.exe`**,
  not the system install. It has pandas/numpy/scipy/pytest/yfinance/
  pyarrow. (This line previously claimed no .venv existed; it was created
  2026-08-09 and the claim was stale.)
- Frontend build needs Node >= 18: portable Node 20 lives in
  `$TEMP/node-v20.19.0-win-x64/` (see memory/alphaoracle-local-build-env).
- gh CLI at `C:\Program Files\GitHub CLI\gh.exe` (may need PATH export).
- Backtest data, small/committed: `data/historical_long/*.json` (79
  tickers + 10 FRED series). Standard validation run:
  `.venv/Scripts/python.exe backtesting/run_validation.py`.
- **Bulk data: `E:/ColdStorage/archive/`** - 195 GB, self-describing.
  Its `README.md` and `MANIFEST.json` are AUTHORITATIVE on schemas,
  coverage and data traps; prefer them over any doc in this repo.
  Daily/minute/reference masters live in `archive/derived/`.
  `src/archive_paths.py` resolves every path - do not hardcode.
