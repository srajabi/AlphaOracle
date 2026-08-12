"""Canonical locations for the ColdStorage archive.

WHY THIS EXISTS
---------------
Six tools hardcoded `E:/ColdStorage/market-data-7859.tar.pigz`. Then
package_archive.py renamed the originals into `archive/raw/` with
self-describing names, and every one of those paths became wrong. The
archive README promises `derived/` can be rebuilt from `raw/`; that
promise is only true if the builders can still find their inputs.

Resolve through here. Each function returns the first location that
exists, so tools keep working before AND after archival renaming.
"""
from pathlib import Path

COLD = Path("E:/ColdStorage")
ARCHIVE = COLD / "archive"
RAW = ARCHIVE / "raw"
DERIVED = ARCHIVE / "derived"

MINUTE_MASTER = DERIVED / "minute_master" / "alpaca"
DAILY_MASTER = DERIVED / "daily_master"
DAILY_OHLCV1M = DAILY_MASTER / "ohlcv1m"
DAILY_ALPACA = DAILY_MASTER / "alpaca" / "daily_all.parquet"
DAILY_YFINANCE = DAILY_MASTER / "yfinance" / "daily_all.parquet"
REFERENCE = DERIVED / "reference_master" / "reference.parquet"
REFERENCE_INDEX = DERIVED / "reference_master" / "reference_index.parquet"
OHLCV_1M = COLD / "OHLCV-1m" / "data"

_GZIP = ("alpaca-minute-bars_1999-01_2019-09_7859tickers"
         "_snap2019-09-23.tar.gz")
_BZ2 = ("alpaca-minute-bars_1999-01_2019-09_7859tickers"
        "_snap2019-09-19.tar.bz2")


def _first(*candidates):
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]          # so the error message names the new path


def alpaca_tar_gzip():
    """The COMPLETE 2019 capture. 7,859 tickers, 1,957,238 members."""
    return _first(RAW / _GZIP, COLD / "market-data-7859.tar.pigz")


def alpaca_tar_bzip2():
    """The 2019-09-19 capture. VERIFIED a strict subset (finding 49) -
    6,273 tickers, zero unique. Multi-stream bzip2: open it as
    tarfile.open(fileobj=bz2.open(p, "rb"), mode="r|"), never "r|*"."""
    return _first(RAW / _BZ2, COLD / "market-data.tar")
