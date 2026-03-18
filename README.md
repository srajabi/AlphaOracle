# AlphaOracle: Automated AI Investment Analyst & Portfolio Manager

## Overview
AlphaOracle is an AI-driven system designed to automate stock analysis, backtest trading strategies, and validate them through paper trading. It leverages large language models (LLMs) to analyze market data, news, and predefined investment theses, publishing daily insights and strategy validation results to a static website hosted on GitHub Pages.

**Current Phase**: Paper trading and backtesting validation. No live capital deployment yet. After 6-12 months of validation, the system may be used with real capital.

## Features
*   **Automated Data Ingestion:** Fetches EOD stock prices, technical indicators, and news.
*   **Intermarket Regime Detection:** Tracks 7 uncorrelated markets (SPY, VIX, UUP, TLT, GLD, SLV, XLE) to detect regime changes.
*   **Multi-Agent LLM Analysis:** Uses a "Mixture of Experts" approach where multiple LLMs (Risk Manager, Technical Analyst, Macro Strategist) provide specialized insights.
*   **Portfolio Management LLM:** A final LLM synthesizes agent reports against a user-defined investment thesis.
*   **Strategy Backtesting:** Validates trading strategies across 33 years of market history (1993-2026) covering all major market regimes.
*   **Paper Trading Validation:** Forward-tests strategies in simulation across multiple accounts ($100k each) to track real-time performance.
*   **GitHub Pages Deployment:** Publishes daily analysis reports, backtest results, and paper trading performance to a static website.
*   **Secure API Handling:** Uses `.env` for local secrets and GitHub Secrets for CI/CD.
*   **Local Development Workflow:** Includes scripts and unit tests for efficient local testing and iteration.

## Architecture Highlights
The system runs daily via GitHub Actions:
1.  **Data Ingestion:** Python scripts gather market data (yfinance) and news.
2.  **Context Generation:** Market data and predefined investment theses are compiled into LLM prompts.
3.  **LLM Agents:** Multiple Gemini 2.5 Flash agents generate specialized reports.
4.  **Portfolio Manager:** A final Gemini 2.5 Flash agent synthesizes reports, generates markdown summaries, and a JSON list of trades.
5.  **Trade Execution:** Python script executes trades via Alpaca's API.
6.  **Website Generation:** MkDocs builds a static site from the generated markdown reports.
7.  **Deployment:** The static site is deployed to GitHub Pages.

## Getting Started

### 1. Repository Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/srajabi/AlphaOracle.git
    cd AlphaOracle
    ```
2.  **Create Python Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install Node.js Dependencies (for Astro - *Future*):**
    *(Note: This step will be added once Astro is integrated.)*

### 2. API Key Configuration

*   **Google Gemini:** Obtain a `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/).
*   **Alpaca:** Sign up for an Alpaca Paper Trading account and get your `ALPACA_API_KEY` (Key ID) and `ALPACA_SECRET_KEY` (Secret Key).

#### Local Development (`.env` file)
1.  Create a file named `.env` in the root of your project:
    ```bash
    touch .env
    ```
2.  Edit `.env` and add your API keys (this file is ignored by Git):
    ```ini
    GEMINI_API_KEY="your_actual_gemini_api_key"
    ALPACA_API_KEY="your_actual_alpaca_key_id"
    ALPACA_SECRET_KEY="your_actual_alpaca_secret_key"
    ```
3.  **Load Keys into Environment:** In your terminal, run `source .env` before executing any scripts.

#### GitHub Actions (Repository Secrets)
1.  Go to your GitHub repository **Settings > Secrets and variables > Actions**.
2.  Click **New repository secret** and add your `GEMINI_API_KEY`, `ALPACA_API_KEY`, and `ALPACA_SECRET_KEY`.

### 3. Customize Investment Theses & Watchlist
*   Edit `watchlist.csv` to define the tickers you want the AI to analyze.
*   Modify the Markdown files in the `thesis/` directory to define your investment philosophy, macro views, and sector preferences.
*   Note: `portfolio.csv` is auto-generated from your Alpaca paper trading account state and should not be manually edited.

### 4. Local Development & Testing

To prevent broken builds and failed GitHub Actions runs, always follow this local validation process before committing and pushing code.

#### Run Full Pipeline Locally
Execute the `run_local.sh` script to perform the entire analysis, trade generation, and website build process. This script will automatically activate your virtual environment, install dependencies, and run all Python steps before building the MkDocs site.

*   **To run with LIVE API calls (uses your actual API key, consumes credits):**
    ```bash
    # Ensure .venv is activated and .env is sourced
    ./run_local.sh
    ```
    *Expected output:* You should see agent reports being generated from actual Gemini API calls.

*   **To run in MOCK mode (no API calls, saves credits):**
    ```bash
    # Ensure .venv is activated and .env is sourced
    ./run_local.sh --mock
    ```
    *Expected output:* You will see `MOCK_LLM is true. Using mocked completion for [Agent Name].` for each agent.

#### Run Unit Tests
```bash
# Run all tests (including mocked LLM calls)
pytest

# Run only tests that make live API calls (requires GEMINI_API_KEY set)
pytest -m live_api tests/test_gemini.py
```

#### Preview Site Locally
After `run_local.sh` completes (either live or mocked), you can preview the generated website:
```bash
mkdocs serve
```
Open the provided local URL (usually `http://127.0.0.1:8000`) in your browser to inspect the generated reports and portfolio dashboard.

### 5. GitHub Actions & Deployment
The `daily_analysis.yml` workflow is configured to run automatically every weekday at 22:00 UTC and on `workflow_dispatch` (manual trigger).
*   **Trigger Manually:** Go to your GitHub repository **Actions > AlphaOracle Daily Run > Run workflow**.
*   **View Live Site:** Once the action completes successfully, your site will be live at `https://<YOUR_GITHUB_USERNAME>.github.io/AlphaOracle/`.

## Future Enhancements
*   Integration with Astro + MDX for advanced charting.
*   Backtesting and performance tracking.
*   Expanded data sources (FRED, options data, alternative data).
*   More sophisticated LLM agent orchestration.
