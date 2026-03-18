# AlphaOracle: Context & Architecture

## What Is AlphaOracle?

AlphaOracle is an AI-powered portfolio management and market analysis system that combines:
- Multi-agent LLM analysis (risk, macro, technical, portfolio management)
- Rule-based technical strategies
- Options analysis
- Backtesting framework
- Paper trading capability
- Static site dashboard for visualization

The system runs daily via GitHub Actions, analyzes market data, generates trade recommendations, and optionally executes trades through Alpaca.

## Core Philosophy

### Three Modes of Operation

1. **LLM Analysis Mode**: Multi-agent system provides nuanced market commentary, considering macro news, technicals, portfolio state, and risk
2. **Strategy Rating Mode**: Rule-based strategies provide buy/sell/hold signals per ticker (200 SMA, dual momentum, RSI mean reversion, etc.)
3. **Paper Trading Mode**: Forward validation of strategies to track real-world performance without capital risk

### Design Principles

- **Validation before deployment**: Backtest strategies across multiple market regimes before paper trading
- **Transparency**: All analysis, trades, and performance metrics are visible on the static site
- **Accountability**: Track predictions vs. outcomes to enable self-correction
- **Multi-timeframe**: Consider both tactical (swing trades) and strategic (portfolio allocation) decisions
- **Risk-aware**: Explicit risk management through position sizing, regime detection, and hedging

## System Architecture

### Data Pipeline

```
Data Sources → Ingestion → Analysis → Execution → Frontend Display
```

#### Data Sources
- **Yahoo Finance**: EOD prices, basic news, options chains
- **Alpaca**: Portfolio state, trade execution, paper trading
- **Future**: RSS feeds for macro news, additional data providers

#### Ingestion (`src/data_ingestion.py`)
- Fetches EOD prices for watchlist tickers
- Computes technical indicators (SMAs, RSI, MACD, Bollinger Bands)
- Gathers news at three layers:
  - Macro news (Fed, rates, CPI, geopolitics, energy)
  - Theme news (semiconductors, gold, utilities, international)
  - Ticker-specific news
- Detects market regime (bull, bear, chop, volatility)
- Outputs: `data/market_context.json`

#### Options Ingestion (`src/options_ingestion.py`)
- Fetches options chains for selected tickers
- Identifies opportunities:
  - Covered calls
  - Cash-secured puts
  - Protective puts
  - Long calls/puts on liquid ETFs
- Outputs: `data/options_context.json`

#### Portfolio State (`src/fetch_alpaca_portfolio.py`)
- Syncs current holdings from Alpaca
- Outputs: `data/portfolio_status.json`, `portfolio.csv`

#### LLM Analysis (`src/llm_agents.py`)
Four specialized agents:
1. **Risk Manager**: Identifies risks, suggests hedges
2. **Macro Strategist**: Analyzes macro environment, regime, sector rotation
3. **Technical Analyst**: Evaluates charts, setups, momentum
4. **Portfolio Manager**: Synthesizes inputs, generates trade recommendations

Outputs:
- `frontend/src/content/reports/risk.md`
- `frontend/src/content/reports/macro.md`
- `frontend/src/content/reports/tech.md`
- `frontend/src/content/reports/pm_synthesis.md`
- `data/trades.json`

#### Trade Execution (`src/execute_trades.py`)
- Reads `data/trades.json`
- Submits orders to Alpaca (market orders for equities)
- Currently equity-only; options are analysis-only

#### Frontend (Astro + React)
Static site built from:
- LLM-generated markdown reports
- Historical price data
- Options analysis
- Performance metrics (future)

Hosted on GitHub Pages.

### Backtesting Framework

Located in `backtesting/` directory:

#### Components
- `engine.py`: Core backtesting engine
- `strategies.py`: Single-asset strategies
- `portfolio_strategies.py`: Portfolio-level strategies
- `periods.py`: Market regime definitions
- `run_backtests.py`: Orchestration script

#### Strategies Implemented

**Single-Asset:**
- Buy and hold baseline
- SMA trend following
- RSI mean reversion
- 20-day breakout

**Portfolio-Level:**
- Top-2 relative strength rotation
- Dual momentum rotation
- Regime-based defensive rotation

#### Period Testing
- Named lookbacks: 10, 20, 30, 40 days, full history
- Rolling windows for robustness testing
- Market regime slices:
  - Dot-com bear (2001)
  - GFC bear (2008)
  - Post-GFC bull
  - COVID crash/rebound
  - Inflation bear (2022)
  - AI bull (2023-2024)
  - Chop periods (2015-2016, 2018)

#### Current Limitation
Only ~4 months of recent cached data available. Long historical data needed to validate strategies across all defined regimes.

## Data Flow

### Daily Automated Workflow (GitHub Actions)

1. Sync Alpaca portfolio state
2. Run data ingestion (prices, news, technicals, regime)
3. Run options ingestion
4. Run LLM analysis (4 agents)
5. Generate trade recommendations
6. (Optional) Execute trades
7. Copy data to frontend
8. Build static site
9. Deploy to GitHub Pages

Workflow file: `.github/workflows/daily_analysis.yml`

### Local Development Workflow

```bash
# Test data ingestion without network
MOCK_LLM=true python3 src/data_ingestion.py

# Test LLM agents without execution
MOCK_LLM=true python3 src/llm_agents.py

# Run backtests
python3 backtesting/run_backtests.py --periods 10,20,30,40,full

# Fetch live portfolio state
python3 src/fetch_alpaca_portfolio.py
```

## File Structure

```
.
├── agents.md                    # Coding agent workflow (this guide)
├── context.md                   # Overall project context (this file)
├── current.md                   # Current work state
├── spikes/                      # Research and design docs
├── src/                         # Main pipeline code
│   ├── data_ingestion.py        # Market data + news + technicals
│   ├── options_ingestion.py     # Options chain analysis
│   ├── fetch_alpaca_portfolio.py # Portfolio state sync
│   ├── llm_agents.py            # Multi-agent LLM analysis
│   └── execute_trades.py        # Trade execution
├── backtesting/                 # Strategy validation
│   ├── engine.py
│   ├── strategies.py
│   ├── portfolio_strategies.py
│   ├── periods.py
│   └── run_backtests.py
├── data/                        # Generated data (gitignored for large files)
│   ├── history/                 # Historical price data per ticker
│   ├── market_context.json      # Daily market snapshot
│   ├── options_context.json     # Options opportunities
│   ├── portfolio_status.json    # Current holdings
│   └── trades.json              # Trade recommendations
├── frontend/                    # Astro static site
│   ├── src/content/reports/     # LLM-generated markdown
│   └── public/data/             # Data files for charts
└── .github/workflows/           # Automation
    └── daily_analysis.yml
```

## Key Technologies

- **Python**: Data ingestion, analysis, backtesting
- **LLMs**: Gemini, Anthropic, OpenAI (via API)
- **Yahoo Finance API**: Market data
- **Alpaca API**: Brokerage integration
- **Astro**: Static site framework
- **React + TradingView Lightweight Charts**: Frontend visualization
- **GitHub Actions**: Daily automation
- **GitHub Pages**: Hosting

## Current Portfolio State

As of last sync:
- CASH: -100,000.00 (margin used)
- GLD: 210.216523018 shares
- XLU: 2,125.806740615 shares

The negative cash indicates margin borrowing for positions.

## Watchlist

The system tracks a curated watchlist (`watchlist.csv`):
- Major indices: SPY, QQQ, VTI, VOO, VT, VXUS
- Sector ETFs: XLE, XLF, XLU
- International: EWA, EWC, VGK
- Bonds: TLT, SCHD, QUAL
- Commodities: GLD, IAU
- Tech leaders: NVDA, AAPL, MSFT, GOOGL, META, AMZN, TSLA
- Semiconductors: AMD, AVGO, INTC, KLAC, MU, TSM
- Other growth: NFLX, PLTR, CRWD, ORCL
- Utilities: CEG
- Storage: WDC, STX, PSTG
- Theme-specific: IBIT (Bitcoin ETF), NBIS, MTZ, TLN
- Volatility: ^VIX

## Three Planned Functionalities

### 1. General Recommendations (Implemented)
Daily LLM analysis across risk, macro, technical, and portfolio management perspectives. Outputs narrative reports with trade ideas.

**Status**: Live and running daily

### 2. Strategy-Specific Ratings (In Progress)
Rule-based buy/sell/hold ratings for each ticker from multiple technical strategies:
- 200 SMA trend following
- Dual momentum
- RSI mean reversion
- 3x leveraged ETF strategies
- Others as validated by backtesting

**Status**: Backtester exists, not yet integrated into main pipeline

**Planned output**: `data/strategy_ratings.json` with structure like:
```json
{
  "NVDA": {
    "sma_200_trend": "buy",
    "dual_momentum": "hold",
    "rsi_mean_reversion": "sell",
    "breakout_20d": "buy"
  }
}
```

### 3. Forward Paper Trading (Not Yet Implemented)
Track real-time performance of:
- LLM recommendations
- Individual rule-based strategies
- Portfolio strategies

Metrics to track:
- Total return
- Sharpe ratio
- Win rate
- Max drawdown
- vs. SPY benchmark

**Planned output**:
- `data/paper_trades_history.json`: Trade log
- `data/paper_performance.json`: Performance metrics
- Frontend dashboard showing live results

## Major Remaining Gaps

### 1. Historical Data for Backtesting
Current data only covers ~4 months (late 2025 - March 2026). Need multi-year data to validate strategies across:
- 2000-2002 dot-com crash
- 2007-2009 GFC
- 2015-2016 sideways market
- 2018 correction
- 2020 COVID crash and recovery
- 2022 inflation bear market
- 2023-2024 AI bull market

**Solution needed**: Long-history downloader that fetches 20+ years of data for backtesting purposes

### 2. Technical Analysis Improvements
Current technical indicators are basic (SMAs, RSI, MACD, Bollinger Bands). Missing:
- Setup classification (pullback vs. breakout vs. squeeze)
- Relative strength scoring
- Volume confirmation
- Multi-timeframe analysis
- Support/resistance detection

See `spikes/technical_analysis_improvements.md` for detailed plan.

### 3. Options Execution
Currently analysis-only. To enable auto-execution:
- Strict liquidity filters (min volume, OI, bid-ask spread)
- Risk limits per strategy
- Position tracking for option legs
- Alpaca API integration for option orders

See `spikes/options_execution_expansion.md` for phased approach.

### 4. Strategy Rating System Integration
Backtester has validated strategies, but they're not integrated into daily pipeline. Need:
- Script to run strategies against latest data
- Generate ratings per ticker per strategy
- Display on frontend ticker pages

### 5. Paper Trading Tracker
Need complete system to:
- Initialize paper trading positions
- Track daily P&L
- Calculate performance metrics
- Compare strategy performance
- Display results on frontend

## Risk Management Approach

### Position Sizing
Not yet systematically implemented. Current approach is ad-hoc based on LLM recommendations.

**Planned**: Volatility-adjusted position sizing using ATR

### Stop Losses
Not automated. LLM agents suggest invalidation levels, but execution is manual.

**Planned**: Automated stop-loss orders based on technical levels or ATR multiples

### Portfolio Limits
No hard limits currently enforced.

**Planned**:
- Max position size: 15% of portfolio
- Max sector exposure: 40%
- Max single-ticker risk: 5% portfolio value
- Correlation limits to avoid concentration

### Regime-Based Adjustments
Partially implemented through market regime detection (bull/bear/chop/high volatility).

**Planned**: Automatic exposure reduction in high-volatility or bear regimes

## News and Macro Coverage

### Current Implementation
Three-layer news structure:

1. **Macro news**: Fed, rates, inflation, energy, geopolitics, tariffs, bonds
2. **Theme news**: Sectors and themes (semiconductors, gold, utilities, software, international)
3. **Ticker news**: Company-specific events (earnings, guidance, M&A, analyst actions)

### Data Sources
- Yahoo Finance ticker news
- (Future) RSS feeds for macro coverage

### Known Issues
- `HXSC.F` ticker is problematic in Yahoo Finance (may need removal)
- News quality varies; some items lack summaries

## Performance Tracking

### Current State
No systematic performance tracking yet. Trades are recommended and sometimes executed, but historical performance is not measured.

### Planned Metrics

**Strategy-level**:
- Total return
- Annualized return
- Sharpe ratio
- Sortino ratio
- Max drawdown
- Win rate
- Average win / average loss
- Profit factor

**Portfolio-level**:
- Total portfolio return
- vs. SPY benchmark
- vs. 60/40 benchmark
- Volatility (annualized)
- Beta to SPY
- Alpha vs. benchmark

**Accountability**:
- Track LLM predictions vs. outcomes
- Feed results back into next day's prompt for self-correction
- Maintain "lessons learned" ledger

## Deployment

### Current Setup
- GitHub repository: `sohail.rajabi/github_io_stock_analysis`
- Automation: GitHub Actions (daily cron)
- Hosting: GitHub Pages
- Broker: Alpaca (paper trading and live)

### API Keys (stored in GitHub Secrets)
- `ALPHAVANTAGE_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`

### Daily Workflow Timing
Runs at market close + buffer time to ensure EOD data availability

## Future Enhancements

### Short-term (Next 1-3 Months)
1. Long-history data downloader for robust backtesting
2. Strategy rating system integration
3. Paper trading performance tracker
4. Improved technical analysis (setup scoring, relative strength)

### Medium-term (3-6 Months)
1. Options execution automation (covered calls, CSPs, protective puts)
2. Automated position sizing based on volatility
3. Multi-timeframe technical analysis
4. Enhanced macro news ingestion (RSS feeds)

### Long-term (6-12 Months)
1. Machine learning for setup quality scoring
2. Portfolio optimization using modern portfolio theory
3. Seasonal and cyclical pattern detection
4. Integration with additional data providers
5. Real-money execution with strict risk controls

## Success Metrics

The system will be considered successful if:

1. **Backtested strategies** show positive Sharpe ratios (>0.5) across multiple market regimes
2. **Paper trading** outperforms buy-and-hold SPY over 6+ months
3. **LLM recommendations** demonstrate learning from past mistakes via accountability loop
4. **Risk management** prevents catastrophic drawdowns (max -20% portfolio-wide)
5. **Transparency** enables full audit trail of decisions and outcomes

## Contributing

This is a personal project, but the approach is:
1. Research in `spikes/` folder first
2. Validate with backtesting
3. Deploy to paper trading
4. Monitor for at least 1-3 months
5. Only then consider real-money execution

The goal is systematic, evidence-based portfolio management augmented by AI, not speculative gambling.
