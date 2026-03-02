# Research Spikes for AlphaOracle

This document outlines the initial research tasks ("spikes") required to validate and design the core components of AlphaOracle.

A spike is a time-boxed investigation to explore a technical approach, evaluate a tool, or answer a specific architectural question before committing to a full implementation.

## Completed / Active Spikes
The detailed findings for each spike are located in this directory.

1.  **[Project Idea & Vision](project_idea.md):** Initial concept and high-level design.
2.  **[High-Level Architecture](architecture.md):** Detailed system architecture.
3.  **[Data Sources Evaluation](data_sources.md):** What are the most reliable, cost-effective APIs for end-of-day stock prices, options chains, and financial news suitable for a daily GitHub Action?
4.  **[Technical Indicators Selection](technicals.md):** Which specific technical indicators (e.g., RSI, MACD) are most effective for identifying swing trade setups and sector rotations?
5.  **[Trading Strategies (Swing/Options)](trading_strategies.md):** How do we structure the LLM prompts to identify high-probability swing trades and basic options strategies (e.g., cash-secured puts, covered calls, long calls/puts on SPY/ETFs)?
6.  **[Market Seasonality & Regimes](seasonalities.md):** How do we programmatically define and calculate market seasonality (e.g., midterm election years, "Sell in May") and current market regimes (e.g., High Volatility Downtrend)?
7.  **[Broker Integration](broker_integration.md):** Research into automating trades with IBKR vs. Alpaca (leading to Alpaca selection).
8.  **[Static Site Generator for Data Visualization](static_site_generator.md):** Research into alternatives to MkDocs for better chart rendering (leading to Astro + MDX selection).
9.  **[Astro + MDX + Lightweight Charts](astro_mdx_charts.md):** Spike for implementing the new frontend stack.

## Future Spikes
*   **LLM Multi-Agent Orchestration:** Evaluate libraries like `litellm`, LangChain, or simple custom Python scripts for managing parallel LLM calls to different providers (Gemini, Anthropic, OpenAI).
*   **GitHub Actions Secrets & Workflow:** Test setting up a daily cron job in GitHub Actions, securely injecting API keys, and automatically committing the generated Markdown files back to the repository.
*   **MkDocs & GitHub Pages Deployment:** Create a basic MkDocs Material site and automate its deployment via GitHub Actions.
*   **Historical Accountability Loop:** Design the mechanism for storing past predictions and feeding them back into the next day's prompt for self-correction.