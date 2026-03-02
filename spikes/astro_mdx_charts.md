# Spike: Astro + MDX + Lightweight Charts for Enhanced Visualization

**Objective:** Research and plan the migration from MkDocs to an Astro + MDX setup, specifically focusing on how to render dynamic charts (using Lightweight Charts) for each analyzed ticker, while ensuring compatibility with GitHub Pages.

## Why Astro + MDX + Lightweight Charts?
*   **Astro:** A modern static site builder known for its "island architecture" which allows client-side interactivity within static HTML. This is ideal for performance and SEO, while still enabling dynamic components like charts.
*   **MDX:** Extends Markdown to include JSX components. This allows us to write our analytical reports in Markdown but embed interactive React/Vue/Svelte components directly within them, where our charts can reside.
*   **Lightweight Charts:** A fast, responsive, and customizable charting library specifically designed for financial data. It's client-side, making it perfect for Astro's interactive "islands".

## Detailed Architecture Brief (User Provided)

### System Overview
We are building a static dashboard hosted on GitHub Pages to display daily AI-generated financial reports and interactive market data. A daily GitHub Actions cron job handles data ingestion, multi-LLM consensus generation, and the final Astro static site build. 

Your objective is to scaffold the frontend architecture using Astro, MDX, and Lightweight Charts.

### Astro Configuration
Set up the Astro project to support MDX and React. We need MDX to allow the LLMs to author markdown reports that seamlessly embed interactive React components.

### Data Pipeline Contract
The backend Python scripts will generate two types of artifacts during the daily build process. The first artifact type includes standard MDX files containing the textual LLM analysis. The second artifact type includes JSON files containing the time-series financial data (OHLCV for candlesticks and arrays for technical indicator overlays). Decide the optimal directory structure for these artifacts so the frontend can easily consume them.

### Chart Component Design
Build a React wrapper for TradingView Lightweight Charts. This component must accept a reference to a specific JSON data file, fetch or import that data on the client side, and render the canvas. 

### Client-Side Execution
Lightweight Charts requires browser APIs like HTML5 Canvas. Ensure Astro defers the rendering of these chart components entirely to the client using the appropriate hydration directives.

### Data Schema Requirements
Design the React chart component to accept a flexible JSON structure. We need to plot primary candlestick series alongside multiple potential line series for technical indicators (Moving Averages, RSI) or prediction market probability curves from Polymarket. 

### Implementation Handoff
Examine the current repository state. Implement the Astro scaffolding, the MDX integration, and the base React chart component. Structure the component props and data loading mechanism to handle static JSON files generated at build time.

## Core Functionality to Replicate / Migrate
1.  **Daily Synthesis (Homepage):** The main `index.md` report from the Portfolio Manager.
2.  **Live Portfolio:** The `portfolio.md` page with Alpaca data.
3.  **Individual Agent Reports:** `risk.md`, `tech.md`, `macro.md`.
4.  **Ticker-Specific Pages with Charts:** A new feature to have a dedicated page for each `watchlist.csv` ticker, displaying its data and charts.

## Architecture & Integration Strategy

### 1. Astro Project Setup
*   Initialize a new Astro project.
*   Configure MDX integration (Astro supports MDX natively).
*   Choose a UI framework for our chart components (e.g., React, Preact, Svelte, Vue). Given the goal, React is a strong candidate for wide component availability.

### 2. Data Flow for Charts
*   **Data Ingestion (`src/data_ingestion.py`):** Continues to run, producing `data/market_context.json`.
*   **LLM Agents (`src/llm_agents.py`):** Continues to produce Markdown reports and `data/trades.json`.
*   **New Data Output:** We'll need a way to process `data/market_context.json` into a format consumable by client-side chart components (e.g., converting the historical data into a clean JSON array of OHLCV data for each ticker). This might involve a Python script outputting `.json` files into Astro's `public/data/` directory.

### 3. Rendering Charts for Each Ticker
*   **Dynamic Route Generation:** Astro supports dynamic routing. We can set up a route like `src/pages/stocks/[ticker].astro` (or `[ticker].mdx`) that generates a page for each ticker.
*   **MDX Components:** Create a React (or chosen framework) component for Lightweight Charts. This component would take `ticker` and chart `data` as props.
*   **Embedding in MDX:** Within the `[ticker].mdx` page, we can import and use our chart component:
    ```mdx
    # {frontmatter.title} Analysis

    <ChartComponent ticker={frontmatter.ticker} data={chartData} client:load />

    ## Latest News
    ...
    ```
    The `client:load` directive tells Astro to hydrate the component on the client-side, making it interactive.

### 4. Migration of Existing Content
*   **Markdown Reports:** The existing `.md` files can be directly integrated into Astro's content collection.
*   **Portfolio Page:** `src/fetch_alpaca_portfolio.py` can continue to produce `docs/portfolio.md`, and Astro can serve it.

### 5. GitHub Pages Compatibility
*   Astro is a static site generator, so its output (`dist/` folder after `astro build`) is fully compatible with GitHub Pages. We would update the GitHub Actions workflow to run `astro build` instead of `mkdocs build`.

## Challenges & Considerations
*   **Learning Curve:** Astro's island architecture and MDX might require a learning curve for development.
*   **Build Process:** Integrating Astro's `npm run build` into our existing Python-heavy GitHub Actions workflow will need careful orchestration. We'll need Node.js set up in the workflow.
*   **Client-side Data Hydration:** Ensuring the chart data is efficiently loaded for each component.
*   **Design System:** Establishing a consistent design across the Astro site.

## Next Steps for This Spike
*   **Proof of Concept:**
    1.  Initialize a basic Astro project.
    2.  Create a simple MDX page.
    3.  Create a basic React component that wraps Lightweight Charts.
    4.  Demonstrate embedding the chart component in an MDX page with mock data.
    5.  Integrate the Astro build into the GitHub Action (replacing MkDocs).
    6.  Dynamically generate simple ticker pages based on `watchlist.csv`.