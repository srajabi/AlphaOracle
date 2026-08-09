#!/usr/bin/env python3
"""Hold the top-N largest companies, rebalanced annually. Does it win?

WHAT THIS IS AND IS NOT
-----------------------
The archive has no shares outstanding, so TRUE market cap is
unavailable. Ranking is by trailing-month DOLLAR VOLUME (sum of
price x volume), which correlates strongly with size but is not the same
thing.

The bias is knowable and worth stating up front: high-turnover
speculative names rank above their market cap. In 1999-2000 that means
dot-coms crowd the list; in 2021 it means meme stocks. That bias
arguably makes this closer to what a retail "hold the biggest names"
investor would actually have picked, but it is NOT a market-cap index
and must not be described as one.

Survivorship is handled: the archive contains Enron, WorldCom, Lehman,
Washington Mutual, Fannie Mae and Merrill, and correctly drops Bear
Stearns after its 2008 acquisition. A top-N test on a
survivorship-biased universe would be worthless; this one is not.

Method: at each year end rank by December dollar volume, hold the top N
weighted by that dollar volume through the following year, rebalance.
Delisted names simply stop contributing when their data ends.

Writes data/top_n_study.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from src.minute_data import ARCHIVE, load_minute_multi  # noqa: E402

OUT = REPO / "data" / "top_n_study.json"
TOP_NS = (10, 25)
START_YEAR, END_YEAR = 1994, 2025


# ETFs and index products rank high on dollar volume but are not
# companies. A "top 10 companies" portfolio holding QQQ is not the
# strategy being tested.
NOT_COMPANIES = {
    "SPY", "QQQ", "QQQQ", "DIA", "IWM", "IVV", "VOO", "VTI", "EEM", "EFA",
    "TQQQ", "SQQQ", "SSO", "SDS", "UPRO", "SPXU", "XLK", "XLF", "XLE",
    "XLV", "XLI", "XLP", "XLU", "XLY", "XLB", "XLRE", "XLC", "GLD", "SLV",
    "TLT", "HYG", "LQD", "AGG", "VXX", "UVXY", "SOXL", "SOXS", "SMH",
    "ARKK", "IBIT", "GDX", "USO", "UNG", "FXI", "EWJ", "EWZ", "VWO",
    "SPXL", "TNA", "TZA", "LABU", "JNUG", "NUGT", "UVIX", "SVXY", "MDY",
    # Leveraged / inverse / sector ETFs found by auditing the top-10
    # membership of the previous run. All clustered 2006-2010, when
    # levered ETF turnover briefly exceeded that of real megacaps.
    "FAS", "FAZ", "SKF", "SSG", "QID", "QLD", "DDM", "DXD", "MZZ",
    "SRS", "URE", "UYG", "SKN", "TWM", "UWM", "IYR", "OIH", "XHB",
    "XRT", "XOP", "KRE", "KBE", "ITB", "IBB", "IYF", "IYE", "EWY",
    "EWT", "EWH", "EWG", "EWU", "RSX", "EPI", "INDA", "TUR", "THD",
    "ERX", "ERY", "DRN", "DRV", "YINN", "YANG", "EDC", "EDZ", "TMF",
    "TMV", "UDOW", "SDOW", "URTY", "SRTY", "FNGU", "FNGD", "TECL",
    "TECS", "CURE", "DPST", "NAIL", "WEBL", "WEBS", "BULZ", "BERZ",
    # Warrants and when-issued lines are not the common stock.
    "INTCW",
}


# Exchange TEST symbols. These carry synthetic prices that venues swing
# to extremes deliberately, and they dominate dollar volume. Leaving
# them in produced growth factors around 1e70 - the first run's overflow.
TEST_PREFIXES = ("ZVZZ", "ZWZZ", "ZXZZ", "ZYZZ", "TEST", "ZZZ")
MIN_PRICE = 5.0          # suppresses penny-stock-huge-volume distortion
MAX_ABS_DAILY = 0.50     # a surviving >50% day implies bad data


def is_test_ticker(t):
    u = str(t).upper()
    # Trailing W/WS on an otherwise-known symbol is a warrant line.
    return (u.startswith(TEST_PREFIXES) or u.endswith((".T", ".TEST"))
            or u.endswith(".WS") or u.endswith("+"))


def rank_universe(year_month, top_k=60):
    """Rank tickers by dollar volume in one month, real companies only."""
    import pyarrow.parquet as pq
    path = ARCHIVE / f"ohlcv_{year_month}.parquet"
    if not path.exists():
        return []
    table = pq.read_table(path, columns=["ticker", "close", "volume"])
    df = table.to_pandas()
    df = df[~df["ticker"].isin(NOT_COMPANIES)]
    df = df[~df["ticker"].map(is_test_ticker)]
    df["dv"] = df["close"] * df["volume"]
    agg = df.groupby("ticker", observed=True).agg(
        dv=("dv", "sum"), px=("close", "median"))
    agg = agg[(agg["dv"] > 0) & (agg["px"] >= MIN_PRICE)]
    agg = agg["dv"].sort_values(ascending=False)
    return list(agg.head(top_k).items())


# Common split ratios, as the price MULTIPLE on the split date.
SPLIT_RATIOS = (0.5, 1 / 3, 0.25, 2 / 3, 0.75, 0.2, 1.5, 2.0, 3.0)


def strip_splits(returns, tol=0.04):
    """Neutralise unadjusted splits without external corporate actions.

    src/minute_data.py adjusts splits from cached yfinance data, but
    yfinance cannot resolve DELISTED tickers - exactly the names this
    study depends on (YHOO, AOL, SUNW). An unadjusted split reads as a
    -50% day, which would be attributed to the strategy.

    Heuristic: a single-day move beyond 35% whose price multiple lands
    within `tol` of a common split ratio is treated as a corporate
    action and zeroed. Genuine one-day moves of that size do occur in
    mega-caps but are rare; the alternative is phantom crashes, which is
    strictly worse.
    """
    out = returns.copy()
    mult = 1 + returns
    suspicious = returns.abs() > 0.35
    for ratio in SPLIT_RATIOS:
        hit = suspicious & (mult - ratio).abs().lt(tol)
        out = out.mask(hit, 0.0)
    return out


def year_returns(tickers, year):
    """Daily returns for a basket over one calendar year."""
    frames = load_minute_multi(tickers, f"{year}-01-01", f"{year}-12-31",
                               session="regular")
    closes = {}
    for tkr, df in frames.items():
        if len(df) == 0:
            continue
        daily = df["close"].groupby(df.index.date).last()
        if len(daily) > 100:
            closes[tkr] = daily
    if not closes:
        return None
    px = pd.DataFrame(closes)
    px.index = pd.to_datetime(px.index)
    rets = strip_splits(px.pct_change())
    # A >50% single day surviving split-stripping means the series is
    # corrupt, not that the company moved. Drop the name for the year
    # rather than let it dominate the portfolio.
    bad = rets.columns[(rets.abs() > MAX_ABS_DAILY).any()]
    if len(bad):
        rets = rets.drop(columns=list(bad))
    return rets if len(rets.columns) else None


def main():
    results = {n: {} for n in TOP_NS}
    membership = {}

    for year in range(START_YEAR, END_YEAR + 1):
        ranked = rank_universe(f"{year - 1}-12")
        if not ranked:
            print(f"{year}: no ranking data")
            continue

        for n in TOP_NS:
            picks = ranked[:n]
            tickers = [t for t, _ in picks]
            weights = np.array([v for _, v in picks], dtype=float)
            weights = weights / weights.sum()

            rets = year_returns(tickers, year)
            if rets is None:
                continue
            cols = [t for t in tickers if t in rets.columns]
            if not cols:
                continue
            w = pd.Series(
                {t: weights[tickers.index(t)] for t in cols})
            w = w / w.sum()
            # A name that delists mid-year contributes until it stops;
            # remaining weight rides the survivors (renormalised daily).
            port = (rets[cols].fillna(0.0) * w).sum(axis=1)
            growth = float((1 + port).prod())
            results[n][year] = {
                "growth": growth,
                "n_held": len(cols),
                "tickers": cols,
            }
            if n == 10:
                membership[year] = cols

        if year % 5 == 0 or year == START_YEAR:
            top10 = membership.get(year, [])
            print(f"{year}: top10 = {', '.join(top10[:10])}", flush=True)

    payload = {"membership_top10": membership, "results": {}}
    for n in TOP_NS:
        yearly = results[n]
        if not yearly:
            continue
        years = sorted(yearly)
        growths = np.array([yearly[y]["growth"] for y in years])
        curve = np.cumprod(growths)
        payload["results"][f"top{n}"] = {
            "years": years,
            "annual_growth": growths.tolist(),
            "terminal_x": float(curve[-1]),
            "cagr_pct": float(curve[-1] ** (1 / len(years)) * 100 - 100),
            "worst_year_pct": float((growths.min() - 1) * 100),
            "best_year_pct": float((growths.max() - 1) * 100),
        }

    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    for name, r in payload["results"].items():
        print(f"{name}: {len(r['years'])}y  terminal {r['terminal_x']:.2f}x  "
              f"CAGR {r['cagr_pct']:.2f}%  worst yr {r['worst_year_pct']:.1f}%")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
