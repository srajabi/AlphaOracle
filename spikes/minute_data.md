# The 1-Minute OHLCV Archive (2026-08)

Backup source: HuggingFace `mito0o852/OHLCV-1m`, mirrored to
`E:\ColdStorage\OHLCV-1m` (411 monthly parquet files, 81.7 GiB, verified
against the remote manifest - 411/411 files, zero size mismatches).

Access layer: `src/minute_data.py`. Tests: `tests/test_minute_data.py`.
**Nothing should read the parquet files directly.**

## What is actually in it

| Property | Value |
|---|---|
| Schema | `timestamp` (UTC), `open`, `high`, `low`, `close`, `volume`, `ticker` |
| Tickers | 22,057 distinct in 2026-03 |
| Rows | ~34.4M in a single recent month; ~4.6M in 1992-01 |
| Span | 1992-01 -> 2026-03 |
| Session | Extended, 04:00-20:00 ET |
| Regular session | **Complete** - exactly 60 bars/hour, no gaps |
| Extended hours | **Sparse** - 590-1,166 bars/hour, trades only |

Every ticker the project cares about is present: SPY, QQQ, TQQQ, TLT,
VT, VTI, VXUS, EWC, GLD, UPRO, SSO, HYG, LQD, IWM, VOO, SCHD, TMF.

Instrument launch dates are respected (SPY absent in 1992, TLT absent
before 2002, TQQQ before 2010), so absence is usually real rather than a
gap - with one large exception, trap 2 below.

## The five traps

Each of these corrupts a backtest **silently**. None raises an error.
All five are regression-tested.

### 1. Prices are unadjusted

TQQQ closes 152.50 on 2022-01-12 and 70.56 on 2022-01-13. That is its
2:1 split. A backtest reads a -54% day that never happened. TQQQ alone
has splits in 2018, 2021, 2022 and 2025; SOXL had a 15:1 in 2021.

Handled by backward split factors from cached yfinance corporate
actions. After adjustment the same day reads -7.5%, which is real.

### 2. Ticker symbols move

QQQ traded as **QQQQ** from 2004-12 to 2011-03. January 2010 holds zero
`QQQ` bars and 11,851 `QQQQ` bars. A naive filter silently drops seven
years of Nasdaq-100 history and looks like a shorter dataset rather than
a bug.

Handled by `SYMBOL_HISTORY`, which stitches eras for a canonical ticker.
This one generalises: any long backtest on any renamed instrument has
the same hole. The registry is currently minimal and should grow as
tickers are added.

### 3. Timestamps are UTC

Post-market bars run to 20:00 ET, which is past midnight UTC. Group by
UTC date and those bars land on the **following** trading day - an
off-by-one that produces plausible, wrong numbers.

Handled by converting to `America/New_York` before any grouping.

### 4. The bar grid is irregular

The regular session is complete, but extended-hours bars exist only
where trades occurred. Code that assumes fixed spacing, or that
reindexes onto a synthetic grid, will misalign and invent liquidity that
was not there.

Handled by aggregating observed bars only.

### 5. Bad prints, and they land in the tail

Found while measuring overnight gaps, not during the schema audit -
which is the point: this one only shows up when you look at extremes.

SPY on 2000-12-18 records an open **and** low of exactly `111.000`
against a prior close of `131.45`, then trades back to 133 within the
same session. Read naively that is a **-15.56% overnight gap - the worst
in SPY's recorded history**, larger than anything in 2008 or 2020. It is
one spurious round-number tick.

The damage is targeted rather than diffuse. Bad prints do not blur an
average; they manufacture outliers, and they land exactly where
tail-risk work is most sensitive. A gap-risk study, a stop-loss study,
and a max-drawdown study are all *specifically* measurements of the
extreme, so all three are maximally exposed to this.

Handled by `robust_session_edges()`, which takes the median of the first
and last N bars of a session rather than a single print. That is both
resistant to an isolated tick and closer to what a real market order at
the open actually fills at. On the SPY date above, the robust reading is
**+0.87%** - the day was slightly up overnight.

`overnight_gaps(..., robust=False)` reproduces the naive figure on
purpose, so studies can report the contamination rather than quietly
absorbing it.

## What minute data is and is not good for here

**It does not improve the existing signals.** The slow channel is a
month-end 200dma check, the canary is monthly 13612W, the VIX channel is
a 5-day median, dual momentum is monthly. Feeding minute bars to any of
them produces byte-identical signals for a large multiple of the
compute. Re-running the existing suite at 1-minute resolution is a
category error.

**It is decisive for execution and risk**, which is where the project
currently relies on assumptions:

1. **Stop losses** (`backtesting/backtest_stop_losses.py`). Daily OHLC
   says the low was reached but not *when*, nor whether it came before
   or after the high. For a stop, path is the entire question - daily
   bars cannot distinguish "stopped at the bottom, missed the recovery"
   from "never stopped".
2. **Overnight gap risk** (finding 14). The satellite sizing rule rests
   on an assumed 15% underlying gap. With extended-hours bars the real
   distribution is measurable. See finding 18.
3. **LETF path dependency**
   (`backtesting/leveraged_etf_simulation.py`). Daily reset makes
   volatility decay a function of the intraday path, not the
   close-to-close return.
4. **Execution realism** (`tests/test_execution_realism.py`). Fill
   assumptions become measurable rather than asserted.

## Cost of use

Filtered reads are ~5.5s per six months of one ticker, so a full TQQQ
history is ~3 minutes and SPY's 33 years is ~6. Sweeps should cache
derived series rather than re-reading the archive per parameter
combination.

## Open

- `SYMBOL_HISTORY` covers QQQ only. Any ticker added to a long backtest
  needs its rename history checked first.
- Dividends are not adjusted, only splits. Total-return work needs the
  distribution series added.
- No corporate-action source is bundled; `splits_for()` depends on
  yfinance being reachable, and warns rather than failing when it is
  not. A vendored actions file would make backtests fully reproducible
  offline.
