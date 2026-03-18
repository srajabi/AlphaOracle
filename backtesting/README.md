# Backtesting

This folder is the local strategy-evaluation workspace for AlphaOracle.

The immediate goal is straightforward:

1. backtest a small set of simple, transparent strategies
2. compare them on the same cached history data
3. choose one strategy family to paper trade forward in a separate account

## Current Scope

The initial setup uses the cached price history in `data/history/*.json` that the ingestion pipeline already produces.

Included strategies:

* `buy_and_hold`
* `sma_trend_following`
* `rsi_mean_reversion`
* `breakout_20d`

Included portfolio rotation strategies:

* `top2_relative_strength_rotation`
* `dual_momentum_rotation`
* `regime_defensive_rotation`

These are intentionally simple. They are baseline comparators, not final production logic.

## How To Run

Run the default comparison basket:

```bash
python3 backtesting/run_backtests.py
```

Run multiple short lookback periods plus rolling windows:

```bash
python3 backtesting/run_backtests.py \
  --periods 10,20,30,40,full \
  --rolling-window 20 \
  --rolling-step 10
```

Run against named market regimes when you have longer price history available:

```bash
python3 backtesting/run_backtests.py \
  --market-periods dotcom_bear,gfc_bear,inflation_bear_2022,ai_bull_2023_2024
```

Run specific tickers and strategies:

```bash
python3 backtesting/run_backtests.py \
  --tickers SPY,QQQ,GLD,XLE \
  --strategies buy_and_hold,sma_trend_following,breakout_20d
```

Outputs are written to:

* `backtesting/results/summary.csv`
* `backtesting/results/summary_by_period.csv`
* `backtesting/results/results_by_ticker.csv`
* `backtesting/results/summary.json`

## How To Use The Results

The point is not to overfit on one short sample. Use this folder to narrow down which strategy family deserves forward paper trading.

Suggested process:

1. compare strategy behavior across multiple ETFs and sectors
2. compare them across multiple short historical slices, not just one full sample
3. compare them across named market regimes:
   dot-com bear, GFC bear, 2022 inflation bear, post-crash rebounds, and choppy sideways periods
4. choose one simple strategy to paper trade forward first
5. only then connect that strategy to the live recommendation/execution path

## Important Caveats

This is a lightweight backtesting harness, not an institutional simulator.

Current limitations:

* no intraday fills
* close-to-close execution assumption
* simple transaction cost model
* no slippage model beyond fixed bps
* no portfolio-level allocation engine yet
* current cached history is short, so results are directionally useful but not robust

## Good Market Regimes To Test

If the goal is to choose a strategy for forward paper trading, these are the most useful regime buckets:

* `dotcom_bear`: prolonged equity unwind and leadership collapse
* `gfc_bear`: systemic crisis and violent deleveraging
* `post_gfc_bull`: long, trend-friendly bull market
* `covid_crash`: extremely fast shock event
* `covid_rebound`: high-beta rebound and liquidity surge
* `inflation_bear_2022`: rates shock, growth compression, defensive rotation
* `ai_bull_2023_2024`: momentum-led bull market
* `chop_2015_2016` and `chop_2018`: rangey and headline-driven periods where trend systems often struggle

## Next Useful Upgrades

* longer historical lookback downloads dedicated to backtesting
* portfolio-level rebalancing and cash management
* options strategy backtests
* walk-forward testing and train/test splits
* parameter sweeps with result ranking
