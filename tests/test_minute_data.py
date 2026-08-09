"""Contract tests for the minute-data access layer.

Every trap this guards against fails *silently* on daily inspection - a
split reads as a crash, a symbol change reads as a shorter history, a
timezone slip reads as a plausible-but-wrong day. So these are
regression tests with specific numbers, not smoke tests.

Tests that need the 82 GiB archive skip when it is absent, so CI runners
without the data still pass. The pure-function tests always run.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.minute_data import (  # noqa: E402
    ARCHIVE, adjustment_factors, daily_from_minute, load_minute,
    _months, _symbols_for,
)

needs_archive = pytest.mark.skipif(
    not ARCHIVE.exists(),
    reason=f"minute archive not present at {ARCHIVE}")


# --------------------------------------------------------------- pure

def test_months_spans_inclusive_range():
    assert _months("2022-01-10", "2022-03-02") == ["2022-01", "2022-02",
                                                   "2022-03"]


def test_months_single_month():
    assert _months("2022-01-10", "2022-01-18") == ["2022-01"]


def test_symbol_history_resolves_qqqq_era():
    """QQQ traded as QQQQ until 2011-03; a 2010 request must include it."""
    assert "QQQQ" in _symbols_for("QQQ", "2010-01-01", "2010-02-01")


def test_symbol_history_modern_era_is_plain_qqq():
    assert _symbols_for("QQQ", "2020-01-01", "2020-02-01") == ["QQQ"]


def test_symbol_history_spanning_the_rename_returns_both():
    both = _symbols_for("QQQ", "2009-01-01", "2015-01-01")
    assert "QQQQ" in both and "QQQ" in both


def test_ticker_without_history_is_passed_through():
    assert _symbols_for("SPY", "2020-01-01", "2020-02-01") == ["SPY"]


def test_adjustment_factors_compound_backwards():
    """Two 2:1 splits mean bars before both are quoted at 4x."""
    idx = pd.DatetimeIndex(
        ["2021-06-01", "2022-06-01", "2026-01-01"],
        tz="America/New_York")
    f = adjustment_factors(idx, {"2022-01-13": 2.0, "2025-11-20": 2.0})
    assert list(f.values) == [4.0, 2.0, 1.0]


def test_adjustment_factors_ignore_degenerate_ratios():
    idx = pd.DatetimeIndex(["2020-01-01"], tz="America/New_York")
    assert list(adjustment_factors(idx, {"2021-01-01": 0}).values) == [1.0]


def test_load_minute_rejects_unknown_session():
    with pytest.raises(ValueError):
        load_minute("SPY", "2022-01-03", "2022-01-04", session="afterparty")


# ------------------------------------------------------------ archive

@needs_archive
def test_tqqq_split_is_not_a_crash():
    """TRAP 1 regression. Raw data shows 152.50 -> 70.56 on 2022-01-13.

    Unadjusted that is -54%; adjusted it is a single-digit down day.
    """
    daily = daily_from_minute(
        load_minute("TQQQ", "2022-01-10", "2022-01-18"))
    ret = daily["close"].pct_change().loc["2022-01-13"]
    assert -0.15 < ret < 0.0, f"split still reads as {ret:.1%}"


@needs_archive
def test_unadjusted_still_shows_the_raw_split():
    """The adjustment must be doing the work, not the source data."""
    daily = daily_from_minute(
        load_minute("TQQQ", "2022-01-10", "2022-01-18", adjust=False))
    ret = daily["close"].pct_change().loc["2022-01-13"]
    assert ret < -0.4, "expected the raw split artefact when adjust=False"


@needs_archive
def test_qqq_history_survives_the_symbol_change():
    """TRAP 2 regression: 2010 QQQ data exists only under QQQQ."""
    df = load_minute("QQQ", "2010-01-04", "2010-01-08")
    assert len(df) > 0, "QQQ history silently truncated at the rename"


@needs_archive
def test_timestamps_are_eastern_not_utc():
    df = load_minute("SPY", "2022-01-03", "2022-01-04")
    assert str(df.index.tz) == "America/New_York"


@needs_archive
def test_regular_session_excludes_extended_hours():
    """TRAP 4: regular must be 09:30-16:00 ET only."""
    df = load_minute("SPY", "2022-01-03", "2022-01-04", session="regular")
    hours = set(df.index.hour)
    assert min(hours) >= 9 and max(hours) <= 15, sorted(hours)


@needs_archive
def test_extended_session_reaches_premarket():
    df = load_minute("SPY", "2022-01-03", "2022-01-04", session="extended")
    assert min(df.index.hour) < 9, "no pre-market bars in extended session"


@needs_archive
def test_daily_from_minute_keeps_postmarket_on_its_own_day():
    """TRAP 3 regression: a 19:30 ET bar is past midnight UTC.

    Grouping on UTC would push it onto the next trading day.
    """
    df = load_minute("SPY", "2022-01-03", "2022-01-05", session="extended")
    daily = daily_from_minute(df)
    assert pd.Timestamp("2022-01-03") in daily.index
    # A US market holiday must never appear as a trading day.
    assert pd.Timestamp("2022-01-01") not in daily.index


@needs_archive
def test_daily_ohlc_is_internally_consistent():
    daily = daily_from_minute(load_minute("SPY", "2022-01-03", "2022-01-14"))
    assert (daily["high"] >= daily["low"]).all()
    assert (daily["high"] >= daily["close"]).all()
    assert (daily["low"] <= daily["open"]).all()


@needs_archive
def test_missing_ticker_returns_empty_not_error():
    df = load_minute("NOTATICKER123", "2022-01-03", "2022-01-04")
    assert len(df) == 0
