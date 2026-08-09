#!/usr/bin/env python3
"""Access layer for the 1-minute OHLCV archive.

The archive is 411 monthly parquet files (~82 GiB, 22k tickers,
1992-2026) living outside the repo. It is genuinely useful data, but it
carries four traps, each of which corrupts a backtest silently rather
than loudly. Nothing should read the parquet files directly; go through
here.

TRAP 1 - prices are UNADJUSTED.
    TQQQ closes 152.50 on 2022-01-12 and 70.56 on 2022-01-13. That is
    its 2:1 split, not a -54% day. Backtests read it as a crash.

TRAP 2 - ticker symbols move.
    QQQ traded as QQQQ from 2004-12 to 2011-03. January 2010 holds zero
    QQQ bars and 11,851 QQQQ bars, so a naive filter drops seven years
    of history and raises no error.

TRAP 3 - timestamps are UTC.
    Post-market bars run to 20:00 ET, which is past midnight UTC. Group
    by UTC date and those bars land on the following trading day.

TRAP 4 - the bar grid is irregular.
    The regular session is complete (exactly 60 bars/hour), but
    extended-hours bars exist only where trades occurred. Code that
    assumes fixed spacing will misalign.

Usage:
    from src.minute_data import load_minute
    df = load_minute("TQQQ", "2022-01-10", "2022-01-18")
"""

import functools
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

ARCHIVE = Path(os.environ.get("OHLCV_1M_ROOT",
                              r"E:\ColdStorage\OHLCV-1m\data"))
ACTIONS_CACHE = Path("data/corporate_actions.json")
ET = "America/New_York"

# Historical symbols, newest last. A request for the canonical ticker
# reads every symbol it has ever traded under and stitches the result.
# Ranges are inclusive of start, exclusive of end; None means unbounded.
SYMBOL_HISTORY = {
    "QQQ": [("QQQQ", None, "2011-03-23"), ("QQQ", "2011-03-23", None)],
}

# Regular US equity session in ET.
REGULAR_OPEN = (9, 30)
REGULAR_CLOSE = (16, 0)


def _months(start, end):
    """Monthly file stems spanning [start, end]."""
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    return [d.strftime("%Y-%m")
            for d in pd.date_range(s.normalize().replace(day=1),
                                   e.normalize().replace(day=1), freq="MS")]


def _symbols_for(ticker, start, end):
    """Which raw symbols cover [start, end] for this canonical ticker."""
    history = SYMBOL_HISTORY.get(ticker)
    if not history:
        return [ticker]
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    out = []
    for symbol, sym_start, sym_end in history:
        if sym_end is not None and pd.Timestamp(sym_end) <= s:
            continue
        if sym_start is not None and pd.Timestamp(sym_start) > e:
            continue
        out.append(symbol)
    return out or [ticker]


def _load_actions():
    if ACTIONS_CACHE.exists():
        try:
            return json.loads(ACTIONS_CACHE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_actions(actions):
    ACTIONS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    ACTIONS_CACHE.write_text(json.dumps(actions, indent=2, sort_keys=True),
                             encoding="utf-8")


@functools.lru_cache(maxsize=64)
def splits_for(ticker):
    """{iso_date: ratio} for a ticker, cached on disk then in memory.

    Cached because a backtest sweep would otherwise hammer the provider
    once per parameter combination.
    """
    actions = _load_actions()
    if ticker in actions:
        return actions[ticker]
    try:
        import yfinance as yf
        raw = yf.Ticker(ticker).splits
        found = {str(d.date()): float(r) for d, r in raw.items()
                 } if len(raw) else {}
    except Exception as exc:  # network optional; absence must not crash
        print(f"WARNING: split lookup for {ticker} failed ({exc}); "
              "assuming none. Prices may be unadjusted.")
        return {}
    actions[ticker] = found
    _save_actions(actions)
    return found


def adjustment_factors(index_et, splits):
    """Backward split factors aligned to `index_et`.

    A 2:1 split on date d means every bar strictly before d is quoted in
    pre-split units and must be divided by 2 to sit on the same scale as
    today. Factors compound across multiple splits.
    """
    factor = pd.Series(1.0, index=index_et)
    for iso, ratio in sorted(splits.items()):
        if not ratio or ratio <= 0:
            continue
        effective = pd.Timestamp(iso, tz=ET)
        factor.loc[index_et < effective] *= ratio
    return factor


def _read_symbol(symbol, months, columns):
    import pyarrow.parquet as pq
    frames = []
    for stem in months:
        path = ARCHIVE / f"ohlcv_{stem}.parquet"
        if not path.exists():
            continue
        table = pq.read_table(path, columns=columns,
                              filters=[("ticker", "==", symbol)])
        if table.num_rows:
            frames.append(table.to_pandas())
    return frames


def load_minute(ticker, start, end, session="regular", adjust=True):
    """Adjusted minute bars in ET for one canonical ticker.

    session: "regular" (09:30-16:00 ET) or "extended" (everything).
    adjust:  apply backward split adjustment.

    Returns a DataFrame indexed by tz-aware ET timestamp with columns
    open/high/low/close/volume, sorted, de-duplicated.
    """
    if session not in ("regular", "extended"):
        raise ValueError(f"session must be regular|extended, got {session!r}")

    months = _months(start, end)
    columns = ["timestamp", "open", "high", "low", "close", "volume"]
    frames = []
    for symbol in _symbols_for(ticker, start, end):
        frames.extend(_read_symbol(symbol, months, columns))

    if not frames:
        return pd.DataFrame(columns=columns[1:],
                            index=pd.DatetimeIndex([], tz=ET, name="timestamp"))

    df = pd.concat(frames, ignore_index=True)
    # TRAP 3: convert before any date-based grouping.
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True
                                     ).dt.tz_convert(ET)
    df = (df.set_index("timestamp").sort_index()
            .loc[~df.set_index("timestamp").index.duplicated(keep="last")])
    df = df.loc[str(start):str(end)]

    if session == "regular":
        df = df.between_time("%02d:%02d" % REGULAR_OPEN,
                             "%02d:%02d" % REGULAR_CLOSE,
                             inclusive="left")

    if adjust and len(df):
        # TRAP 1: without this a split reads as a crash.
        factor = adjustment_factors(df.index, splits_for(ticker))
        for col in ("open", "high", "low", "close"):
            df[col] = df[col] / factor
        df["volume"] = df["volume"] * factor

    return df


def daily_from_minute(df):
    """Collapse minute bars into daily OHLCV on ET calendar days.

    TRAP 3 again: grouping is on the ET date, so a 19:30 ET post-market
    bar stays on its own trading day instead of migrating forward.
    TRAP 4: uses observed bars only - no reindexing onto a fixed grid.
    """
    if not len(df):
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    grouped = df.groupby(df.index.date)
    out = pd.DataFrame({
        "open": grouped["open"].first(),
        "high": grouped["high"].max(),
        "low": grouped["low"].min(),
        "close": grouped["close"].last(),
        "volume": grouped["volume"].sum(),
    })
    out.index = pd.to_datetime(out.index)
    out.index.name = "date"
    return out


def robust_session_edges(df, minutes=5):
    """Per-day opening and closing levels resistant to a single bad tick.

    TRAP 5 - the archive contains bad prints, and they land exactly where
    tail-risk work is most sensitive. SPY on 2000-12-18 records an open
    of 111.000 (low also 111.000) against a prior close of 131.45, then
    trades back to 133 within the session: a -15.6% "gap" that is really
    one spurious round-number tick. Taken naively it becomes the worst
    overnight gap in SPY's history.

    Using the median of the first/last `minutes` bars instead of a single
    print is both robust to that and closer to what a real market order
    at the open or close actually fills at.
    """
    if not len(df):
        return pd.DataFrame(columns=["open_robust", "close_robust"])
    grouped = df.groupby(df.index.date)["close"]
    edges = pd.DataFrame({
        "open_robust": grouped.apply(lambda s: s.iloc[:minutes].median()),
        "close_robust": grouped.apply(lambda s: s.iloc[-minutes:].median()),
    })
    edges.index = pd.to_datetime(edges.index)
    edges.index.name = "date"
    return edges


def overnight_gaps(ticker, start, end, robust=True, minutes=5):
    """Overnight return per trading day: today's open vs yesterday's close.

    Uses the regular session, so "open" is the 09:30 area rather than a
    thin 04:00 pre-market tick.

    robust=True (default) uses the median of the first/last `minutes`
    bars rather than single prints. Set False only to reproduce the
    naive figure - it is contaminated by bad ticks (see
    robust_session_edges).
    """
    df = load_minute(ticker, start, end, session="regular")
    if robust:
        edges = robust_session_edges(df, minutes)
        if len(edges) < 2:
            return pd.Series(dtype=float)
        gap = edges["open_robust"] / edges["close_robust"].shift(1) - 1.0
    else:
        daily = daily_from_minute(df)
        if len(daily) < 2:
            return pd.Series(dtype=float)
        gap = daily["open"] / daily["close"].shift(1) - 1.0
    return gap.dropna()


if __name__ == "__main__":
    df = load_minute("TQQQ", "2022-01-10", "2022-01-18")
    print(daily_from_minute(df).round(2).to_string())
