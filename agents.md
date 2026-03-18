# Coding Agent Workflow Management

## Overview
This document describes how we manage the development workflow with AI coding agents to ensure continuity, context preservation, and systematic progress.

## Core Principles

### 1. Python Environment Management
**This project uses a virtual environment in `.venv/`**

**Setup (first time):**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Daily usage:**
```bash
source .venv/bin/activate  # Always activate before running scripts
python3 src/data_ingestion.py
deactivate  # When done
```

**Why .venv:**
- Isolates project dependencies from system Python
- Ensures reproducible environment
- Prevents dependency conflicts
- Standard practice for Python projects

**Important:** Always activate `.venv` before running any Python scripts or installing packages.

### 2. Iterative Development
- Work in small, testable increments
- Validate each change before moving to the next
- Use backtesting to validate strategies before deployment

### 2. Context Preservation
If the terminal session dies or context is lost, the agent can quickly rebuild understanding by reading:
1. `agents.md` (this file) - workflow instructions
2. `context.md` - overall project context
3. `current.md` - current work state
4. `spikes/` folder - research spikes and design decisions

### 3. Documentation-Driven Development
Documentation is not an afterthought—it drives the workflow.

## File Structure

### `context.md`
**Purpose:** High-level project overview and architecture

**Contents:**
- What AlphaOracle is and why it exists
- System architecture overview
- Key components and their responsibilities
- Data flow through the pipeline
- Current deployment state

**Update frequency:** When major architecture changes occur

### `current.md`
**Purpose:** Current work state and immediate next steps

**Contents:**
- What just changed (recent commits/work)
- Current state of key features
- Known issues and limitations
- Recommended next steps
- Current backtest results if relevant

**Update frequency:** At the end of each work session or when switching tasks

### `spikes/` folder
**Purpose:** Research and design explorations

**Contents:**
- Technical investigations (spikes)
- Design decisions and tradeoffs
- API evaluations
- Strategy research
- Architecture proposals

**File naming:** Use descriptive names like `options_execution_expansion.md`, `technical_analysis_improvements.md`

**Update frequency:** When researching new features or evaluating approaches

## Development Workflow

### Starting a Session
1. Read `agents.md` (this file) to understand the workflow
2. Read `context.md` to understand the overall system
3. Read `current.md` to understand what was just completed and what's next
4. Read relevant spikes for the task at hand

### During Development
1. Use TodoWrite tool to track multi-step tasks
2. Make incremental changes with clear commit messages
3. Test changes locally before committing
4. Update relevant documentation as you go

### Ending a Session
1. Update `current.md` with:
   - What changed
   - Current state
   - Local validation results
   - Next recommended steps
2. Create or update spike documents if design decisions were made
3. Ensure git status is clean or changes are appropriately staged

## Three System Functionalities

AlphaOracle is designed to support three distinct modes:

### 1. General Recommendations (LLM Analysis)
**Current state:** Implemented
- Daily analysis by Risk Manager, Macro Strategist, Tech Analyst, PM
- Outputs markdown reports
- Considers news, technicals, portfolio state, market regime

**Output:** `frontend/src/content/reports/*.md`

### 2. Strategy-Specific Ratings (Rule-Based)
**Current state:** Partially implemented (backtester exists, not yet integrated)
- Systematic buy/sell/hold ratings based on specific technical strategies
- Examples:
  - 200 SMA trend following
  - Dual momentum rotation
  - RSI mean reversion
  - 3x leveraged ETF strategies
- Each ticker gets ratings from multiple strategies
- No LLM involved—pure rule-based

**Planned output:**
- `data/strategy_ratings.json`
- `frontend/public/data/strategy_ratings.json`
- Display on ticker detail pages

### 3. Forward Paper Trading
**Current state:** Not yet implemented
- Track performance of strategies in real-time without real money
- Compare LLM recommendations vs. rule-based strategies
- Measure:
  - Win rate
  - Sharpe ratio
  - Maximum drawdown
  - vs. buy-and-hold benchmark
- Maintain accountability ledger

**Planned output:**
- `data/paper_trades_history.json`
- `data/paper_performance.json`
- Frontend dashboard showing live performance

## Backtesting Before Deployment

**Key principle:** Never deploy a strategy to paper trading without backtesting first.

### Backtesting Workflow
1. Define strategy in `backtesting/strategies.py` or `backtesting/portfolio_strategies.py`
2. Run across multiple market regimes (see `backtesting/periods.py`)
3. Evaluate on rolling windows to avoid overfitting
4. Check performance metrics:
   - Total return
   - Sharpe ratio
   - Max drawdown
   - Win rate
   - Volatility
5. Compare to buy-and-hold baseline
6. Only promote to paper trading if:
   - Sharpe > 0.5 across multiple regimes
   - Max drawdown acceptable
   - Logic is robust (not curve-fit)

### Current Backtesting Gap
- Backtester exists with good strategy framework
- Only has ~4 months of recent data (late 2025 - March 2026)
- Need long-history downloader to test across:
  - 2001 dot-com bear
  - 2008 GFC
  - 2015-2016 chop
  - 2018 chop
  - COVID crash/rebound
  - 2022 inflation bear
  - 2023-2024 AI bull

## Git Workflow

### Commit Messages
Follow conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `chore:` - Maintenance tasks (docs, data updates)
- `test:` - Adding tests

Examples:
```
feat: add paper trading performance tracker
fix: handle missing options data gracefully
refactor: extract setup scoring into separate module
chore: update daily analysis reports
```

### What to Commit
- Code changes
- Configuration updates
- Documentation updates
- Test additions

### What NOT to Commit (Usually)
- Large historical data files (unless essential)
- Generated reports (unless they're part of static site)
- API keys or secrets
- Temporary test files

## Agent Best Practices

### Use TodoWrite Tool
For any multi-step task, create a todo list to:
- Track progress
- Ensure nothing is forgotten
- Give user visibility into what's happening

### Ask Questions Early
If requirements are ambiguous or there are multiple valid approaches:
- Use AskUserQuestion tool to clarify
- Don't guess on architectural decisions
- Present tradeoffs when relevant

### Test Locally First
- Run ingestion scripts with `MOCK_LLM=true` when testing data pipeline
- Run backtests before changing strategy logic
- Verify JSON outputs are well-formed
- Check git status before committing

### Read Before Writing
- Always use Read tool before Edit or Write
- Use Grep/Glob to understand codebase structure
- Check existing patterns before adding new code

## Common Tasks

### Adding a New Strategy
1. Research in `spikes/` folder (create spike document)
2. Implement in `backtesting/strategies.py` or `backtesting/portfolio_strategies.py`
3. Run backtest across multiple periods
4. Document results in spike or current.md
5. If validated, integrate into main pipeline

### Adding a New Data Source
1. Research API in spike document
2. Add ingestion logic to `src/data_ingestion.py` or new module
3. Define output schema
4. Test locally
5. Add to GitHub Actions workflow
6. Update prompts to use new data

### Updating LLM Prompts
1. Identify which agent needs changes (Risk, Macro, Tech, PM)
2. Edit in `src/llm_agents.py`
3. Run with `MOCK_LLM=true` to verify data flow
4. Test with real API if needed
5. Review generated reports

### Adding Paper Trading Strategy
1. Validate in backtester first
2. Add to strategy rating system
3. Initialize paper trading tracker
4. Add to daily workflow
5. Monitor performance for at least 20 trading days before trusting

## Troubleshooting

### Session Lost Context
Read in order:
1. This file (agents.md)
2. context.md
3. current.md
4. Relevant spikes

### Can't Find Where Something Is Implemented
- Use `Grep` tool to search for keywords
- Check git log for recent changes: `git log --oneline -20`
- Look in `src/` for main pipeline code
- Look in `backtesting/` for strategy code
- Look in `frontend/` for display code

### Data Pipeline Not Working
- Check `data/market_context.json` for errors
- Run individual scripts in isolation
- Use `MOCK_LLM=true` to test without API calls
- Check GitHub Actions logs if it's a workflow issue

### Backtest Results Seem Wrong
- Verify input data quality
- Check for look-ahead bias
- Ensure warmup period is sufficient
- Compare to known baseline (buy-and-hold SPY)
- Review strategy logic for bugs

## Current Focus

As of the latest session, we are focusing on:
1. Building out the backtester with long historical data
2. Validating strategies for paper trading deployment
3. Creating the strategy rating system (buy/sell/hold per strategy)
4. Designing the forward paper trading tracker

See `current.md` for detailed status and next steps.
