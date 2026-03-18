# Research Spikes for AlphaOracle

This document outlines the research tasks ("spikes") required to validate and design the core components of AlphaOracle.

A spike is a time-boxed investigation to explore a technical approach, evaluate a tool, or answer a specific architectural question before committing to a full implementation.

---

## 🔥 Latest Research (2026-03-17)

### Intermarket Indicator System

**Key Development:** Built comprehensive intermarket analysis system for market regime detection using 7 uncorrelated markets.

**Philosophy:** Build individual reusable indicators first, combine into strategies later. Focus on regime change detection for dashboards.

**New Spike:**
- **[intermarket_indicators.md](intermarket_indicators.md)** - Individual indicators (Risk Sentiment, Dollar Strength, Real Rates, Commodity Strength) + Market Regime Detector

**Current Market State (2026-03-17):**
- **Regime:** Bear Volatile (high confidence)
- **Risk:** Risk-off (SPY downtrend + VIX 23.5 elevated)
- **Dollar:** Strong and rising (+3.4% momentum)
- **Rates:** Rising (TLT falling, headwind for growth)
- **Commodities:** Defensive rally (gold leading)

**Advantages:**
- 7 uncorrelated markets (less saturated than single-asset technicals)
- Individual indicators are testable and reusable
- Display-ready for ticker dashboards
- Foundation for future trading strategies

**Next:** Display on frontend, build per-ticker indicators, validate predictive power historically.

---

## 🔥 Latest Research (2026-03-16)

### Zero-Fee Leveraged Strategy Breakthrough

**Key Discovery:** Transaction costs were destroying rotation strategies. With zero-fee brokers, leveraged rotation strategies become extraordinarily profitable.

**Critical Spikes:**
- **[transaction_cost_analysis.md](transaction_cost_analysis.md)** - Why 5 bps assumption was 5-10x too high; realistic is 0-1 bps
- **[zero_fee_leveraged_backtest_results.md](zero_fee_leveraged_backtest_results.md)** - Full 33-year results: +7,999% to +54,793% with leverage
- **[leveraged_etf_implementation.md](leveraged_etf_implementation.md)** - Complete guide to executing 2x/3x ETF rotation strategies
- **[config_based_backtesting.md](config_based_backtesting.md)** - YAML configuration system for reproducible backtests
- **[reddit_letf_vs_regime_approach.md](reddit_letf_vs_regime_approach.md)** - Comparison: Reddit 200 SMA strategies vs our multi-factor regime approach
- **[tolerance_bands_vs_reddit_results.md](tolerance_bands_vs_reddit_results.md)** - Results: Reddit strategies crush ours 3-27x with 30x fewer trades
- **[walk_forward_validation_results.md](walk_forward_validation_results.md)** - Out-of-sample validation: ALL strategies improved (NOT overfit!)
- **[high_liquidity_etf_analysis.md](high_liquidity_etf_analysis.md)** - ETF liquidity tiers: Stick to TQQQ/UPRO/TMF for live trading
- **[leverage_comparison_timing_vs_buy_hold.md](leverage_comparison_timing_vs_buy_hold.md)** - ⚠️ CRITICAL FIX: Proper apples-to-apples comparison at same leverage levels

**Key Results:**
- regime_defensive: +597% (5 bps) → **+1,106% (0 bps)** → +85% improvement!
- regime_defensive_2x: **+7,999% (leveraged ETFs)** or +9,785% (margin) over 33 years
- regime_defensive_3x: **+44,879%** ($10k → $4.5M!) with -64% max drawdown
- **reddit_200sma_tqqq: +26,860%** ($10k → $2.7M!) with only **23 trades** over 33 years!
- **reddit_200sma_spy: +8,709%** ($10k → $881k!) with only **17 trades** over 33 years!
- Leveraged ETFs cheaper than margin (0.95% vs 5-7% annually)

**NEW: Tolerance Bands & Reddit Comparison (2026-03-16)**
- ✅ Tolerance bands reduced trades 66% (714 → 243) but cost 28% in returns
- 🚀 Reddit strategies dominate in absolute returns (27x advantage) and tax efficiency (30x fewer trades)
- ⚠️ **REGIME-DEPENDENT**: All strategies excelled in 2011-2026 bull market but struggled 1993-2010
- ⚠️ reddit_200sma_tqqq LOST MONEY 1993-2010 (-0.8%) but gained +35.8% CAGR 2011-2026
- ⚠️ ETF liquidity matters: TQQQ/UPRO/TMF (excellent), UGL/UTSL (poor)

**Recommendations by Account Type:**
- **Taxable accounts:** reddit_200sma_spy (0.5 trades/year, minimal tax drag)
- **IRA/Roth accounts:** regime_defensive_2x (best risk-adjusted returns, no tax drag)
- **Aggressive:** reddit_200sma_tqqq or regime_defensive_3x
- **Always paper trade first (6-12 months)**

### Strategy Validation & Baseline Comparison
- **[strategies_vs_spy_baseline.md](strategies_vs_spy_baseline.md)** - Honest comparison: SPY beats rotation in absolute returns
- **[survivorship_bias.md](survivorship_bias.md)** - Why we use ETFs instead of individual stocks for backtesting
- **[backtest_ticker_selection.md](backtest_ticker_selection.md)** - Which universes for different strategy types
- **[long_history_download.md](long_history_download.md)** - How we got 33 years of daily data for validation
- **[backtesting_libraries_comparison.md](backtesting_libraries_comparison.md)** - VectorBT, Backtrader, etc vs custom

### System Architecture
- **[strategy_rating_system.md](strategy_rating_system.md)** - Mode 2: Rule-based buy/sell/hold ratings per ticker
- **[paper_trading_tracker.md](paper_trading_tracker.md)** - Mode 3: Forward validation without capital risk

---

## Completed / Active Spikes
The detailed findings for each spike are located in this directory.

1.  **[Project Idea & Vision](project_idea.md):** Initial concept and high-level design.
2.  **[High-Level Architecture](architecture.md):** Detailed system architecture.
3.  **[Data Sources Evaluation](data_sources.md):** What are the most reliable, cost-effective APIs for end-of-day stock prices, options chains, and financial news suitable for a daily GitHub Action?
4.  **[Technical Indicators Selection](technicals.md):** Which specific technical indicators (e.g., RSI, MACD) are most effective for identifying swing trade setups and sector rotations?
5.  **[Technical Analysis Improvements](technical_analysis_improvements.md):** How should the current technical-analysis layer evolve from raw indicators into setup classification, relative strength, and scoring?
6.  **[Trading Strategies (Swing/Options)](trading_strategies.md):** How do we structure the LLM prompts to identify high-probability swing trades and basic options strategies (e.g., cash-secured puts, covered calls, long calls/puts on SPY/ETFs)?
7.  **[Options Execution Expansion](options_execution_expansion.md):** What is the safe path from equity-only execution toward recommendation and eventual automation of options strategies?
8.  **[Market Seasonality & Regimes](seasonalities.md):** How do we programmatically define and calculate market seasonality (e.g., midterm election years, "Sell in May") and current market regimes (e.g., High Volatility Downtrend)?
9.  **[Broker Integration](broker_integration.md):** Research into automating trades with IBKR vs. Alpaca (leading to Alpaca selection).
10. **[Static Site Generator for Data Visualization](static_site_generator.md):** Research into alternatives to MkDocs for better chart rendering (leading to Astro + MDX selection).
11. **[Astro + MDX + Lightweight Charts](astro_mdx_charts.md):** Spike for implementing the new frontend stack.
12. **[News Ingestion Gaps And Macro Shock Coverage](news_ingestion_gaps.md):** Why the current ticker-news path misses major macro events and how to add a proper macro/sector news layer.

## Future Spikes
*   **LLM Multi-Agent Orchestration:** Evaluate libraries like `litellm`, LangChain, or simple custom Python scripts for managing parallel LLM calls to different providers (Gemini, Anthropic, OpenAI).
*   **GitHub Actions Secrets & Workflow:** Test setting up a daily cron job in GitHub Actions, securely injecting API keys, and automatically committing the generated Markdown files back to the repository.
*   **MkDocs & GitHub Pages Deployment:** Create a basic MkDocs Material site and automate its deployment via GitHub Actions.
*   **Historical Accountability Loop:** Design the mechanism for storing past predictions and feeding them back into the next day's prompt for self-correction.
