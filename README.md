# AlphaOracle

AI-powered paper trading system running 6 automated strategies across Alpaca accounts with live analysis dashboard.

**Live Dashboard:** [https://srajabi.github.io/AlphaOracle/](https://srajabi.github.io/AlphaOracle/)

## What It Does

AlphaOracle runs fully automated paper trading with daily AI analysis:

- **Multi-Agent LLM Analysis**: Risk Manager, Technical Analyst, and Macro Strategist agents analyze markets using multiple AI models (DeepSeek, Gemini, Claude, GPT, GLM-5)
- **6 Automated Paper Trading Accounts**: Each running different strategies on Alpaca's API
- **Options Analysis**: Monitors unusual options flow and institutional activity
- **Intermarket Regime Detection**: Tracks 7 markets (SPY, VIX, USD, TLT, GLD, SLV, XLE) to detect regime changes
- **Comprehensive Backtesting**: Validates strategies across 30+ years of market data
- **Live Dashboard**: Astro-based static site deployed to GitHub Pages twice daily

## Trading Accounts

All 6 accounts trade on Alpaca's **paper trading API** (no real money):

| Account | Strategy | Execution Schedule |
|---------|----------|-------------------|
| **Dev** | Advanced LLM | 2x Daily (10 AM & 3:30 PM ET) |
| **Account 1** | Standard LLM | EOD (3:30 PM ET) |
| **Account 2** | TQQQ Momentum | EOD (3:30 PM ET) |
| **Account 3** | Dual Momentum | EOD (3:30 PM ET) |
| **Account 4** | Sector Rotation | EOD (3:30 PM ET) |
| **Account 5** | Mean Reversion | EOD (3:30 PM ET) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (2x daily)                 │
│                   10 AM ET & 3:30 PM ET                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Data Ingestion (Python)                                  │
│     - Stock prices (yfinance)                                │
│     - Options data (yfinance)                                │
│     - Technical indicators                                   │
│     - Intermarket signals                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Multi-Agent LLM Analysis (Python + LiteLLM)             │
│     - Risk Manager (deepseek, gemini, glm-5)                │
│     - Technical Analyst (deepseek, gemini, claude)          │
│     - Macro Strategist (deepseek, gemini, gpt-4o-mini)      │
│     - Portfolio Manager (glm-5) synthesizes all reports     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Trade Execution (Python + Alpaca API)                    │
│     - Advanced LLM strategy (Dev account, 2x daily)         │
│     - Standard LLM strategy (Account 1, EOD)                │
│     - Rule-based strategies (Accounts 2-5, EOD)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Dashboard Generation (Astro + TypeScript)                │
│     - Analysis reports                                       │
│     - Portfolio positions                                    │
│     - Paper trading performance                              │
│     - Backtest results                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       GitHub Pages
```

## Tech Stack

**Backend (Python)**
- Data: yfinance, pandas, numpy
- LLM: litellm (unified API for all AI providers)
- Trading: alpaca-py
- Analysis: ta-lib, pandas-ta

**Frontend (TypeScript/Astro)**
- Framework: Astro (static site generator)
- UI: Custom CSS with TradingView-inspired design
- Charts: Lightweight-charts
- Deployment: GitHub Pages

**Infrastructure**
- CI/CD: GitHub Actions (2x daily: 10 AM & 3:30 PM ET)
- Secrets: GitHub Secrets (API keys)
- Storage: GitHub Pages (static site)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/srajabi/AlphaOracle.git
cd AlphaOracle

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file:

```bash
# LLM API Keys
GEMINI_API_KEY=your_gemini_key
DEEPSEEK_API_KEY=your_deepseek_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
GLM_API_KEY=your_glm_key

# Alpaca Paper Trading (6 accounts)
ALPACA_DEV_API_KEY=your_dev_key
ALPACA_DEV_SECRET_KEY=your_dev_secret
ALPACA_PROD_1_API_KEY=your_prod1_key
ALPACA_PROD_1_SECRET_KEY=your_prod1_secret
ALPACA_PROD_2_API_KEY=your_prod2_key
ALPACA_PROD_2_SECRET_KEY=your_prod2_secret
ALPACA_PROD_3_API_KEY=your_prod3_key
ALPACA_PROD_3_SECRET_KEY=your_prod3_secret
ALPACA_PROD_4_API_KEY=your_prod4_key
ALPACA_PROD_4_SECRET_KEY=your_prod4_secret
ALPACA_PROD_5_API_KEY=your_prod5_key
ALPACA_PROD_5_SECRET_KEY=your_prod5_secret
```

See `.env.example` for full configuration options.

### 3. Run Data Ingestion & Analysis

```bash
# Activate virtual environment
source .venv/bin/activate

# Fetch market data
python src/data_ingestion.py
python src/options_ingestion.py

# Generate indicators
python src/generate_indicators.py
python src/generate_ticker_indicators.py
python src/generate_strategy_ratings.py

# Run LLM analysis
python src/llm_agents.py
```

### 4. Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:4321` to see the dashboard.

## Project Structure

```
AlphaOracle/
├── src/                        # Python backend
│   ├── data_ingestion.py       # Fetch market data
│   ├── options_ingestion.py    # Fetch options data
│   ├── generate_indicators.py  # Intermarket indicators
│   ├── llm_agents.py           # Multi-agent LLM analysis
│   ├── execute_advanced_llm.py # Advanced LLM trading (Dev)
│   ├── execute_trades.py       # Standard LLM trading (PROD_1)
│   └── strategies/             # Rule-based strategies
├── frontend/                   # Astro dashboard
│   ├── src/
│   │   ├── pages/              # Dashboard pages
│   │   ├── content/reports/    # LLM-generated reports
│   │   └── layouts/            # Page layouts
│   └── public/data/            # Static data for frontend
├── backtesting/                # Backtesting framework
├── spikes/                     # Research & experiments
├── tools/                      # Manual/ad-hoc scripts
├── .github/workflows/          # GitHub Actions
├── agents.md                   # AI coding agent docs
├── context.md                  # Detailed architecture
└── current.md                  # Current work status
```

## Documentation

- **For Developers**: See `agents.md` for AI coding conventions
- **Architecture Deep Dive**: See `context.md`
- **Research & Spikes**: Browse `spikes/` directory
- **Backtesting**: See `backtesting/` directory

## GitHub Actions Workflow

The system runs automatically twice daily via GitHub Actions:

**Schedule:**
- 10:00 AM ET (15:00 UTC) - Morning run
- 3:30 PM ET (20:30 UTC) - End of day run

**Both runs execute:**
1. Data ingestion (stocks, options, indicators)
2. Multi-agent LLM analysis
3. Advanced LLM trading (Dev account)
4. Portfolio fetch from all accounts
5. Dashboard build & deployment

**EOD run only (3:30 PM ET):**
- Standard LLM trading (Account 1)
- Rule-based strategy execution (Accounts 2-5)

**Manual trigger:** Go to Actions → AlphaOracle Daily Run → Run workflow

## License

Personal project for educational purposes. Use at your own risk.

## Disclaimer

**This system trades with paper money only (Alpaca paper trading API).** No real capital is deployed. This is an experimental learning project to understand algorithmic trading, AI-driven analysis, and systematic portfolio management. Past performance does not guarantee future results.
