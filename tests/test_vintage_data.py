"""Contract tests for point-in-time macro access.

The bug this guards against is invisible: a backtest joining a macro
series on its period label looks correct, runs clean, passes every
causality test written against the CODE, and is still reading numbers
that had not been published on the date it claims to trade.

Tests needing the downloaded archive skip when it is absent; the
synthetic ones always run and cover the actual gating logic.
"""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vintage_data import (  # noqa: E402
    VINTAGE_DIR, load_vintage, naive_series_as_of, publication_lag,
    series_as_of, value_as_of,
)

needs_archive = pytest.mark.skipif(
    not (VINTAGE_DIR / "PAYEMS.json").exists(),
    reason="run tools/download_alfred_vintages.py first")


@pytest.fixture
def fake_series(tmp_path):
    """A series published one month after each period it describes."""
    (tmp_path / "FAKE.json").write_text(json.dumps({
        "series_id": "FAKE",
        "observations": [
            {"date": "2020-01-01", "value": 100.0,
             "first_available": "2020-02-05"},
            {"date": "2020-02-01", "value": 200.0,
             "first_available": "2020-03-05"},
            {"date": "2020-03-01", "value": 300.0,
             "first_available": "2020-04-05"},
        ],
    }), encoding="utf-8")
    load_vintage.cache_clear()
    yield tmp_path
    load_vintage.cache_clear()


def test_value_is_invisible_before_publication(fake_series):
    """The core rule: a February number is not knowable in February."""
    got = value_as_of("FAKE", "2020-02-28", vintage_dir=fake_series)
    assert got is not None
    value, obs_date, _ = got
    assert value == 100.0, "leaked the February value before it existed"
    assert obs_date == pd.Timestamp("2020-01-01")


def test_value_becomes_visible_on_its_publication_date(fake_series):
    value, obs_date, _ = value_as_of("FAKE", "2020-03-05",
                                     vintage_dir=fake_series)
    assert (value, obs_date) == (200.0, pd.Timestamp("2020-02-01"))


def test_nothing_published_yet_returns_none(fake_series):
    assert value_as_of("FAKE", "2020-01-15", vintage_dir=fake_series) is None


def test_naive_and_correct_disagree_exactly_where_expected(fake_series):
    """Quantifies the bug rather than merely avoiding it."""
    dates = ["2020-01-31", "2020-02-29", "2020-03-31"]
    correct = series_as_of("FAKE", dates, vintage_dir=fake_series)
    naive = naive_series_as_of("FAKE", dates, vintage_dir=fake_series)

    # Naive sees each period's value on the last day of that period.
    assert list(naive.values) == [100.0, 200.0, 300.0]
    # Correct lags by one release cycle, and knows nothing in January.
    assert pd.isna(correct.iloc[0])
    assert list(correct.values[1:]) == [100.0, 200.0]


def test_out_of_order_releases_pick_latest_period(tmp_path):
    """A delayed release can publish after a later period's.

    Taking "the last row published" would then return an older period.
    """
    (tmp_path / "ODD.json").write_text(json.dumps({
        "series_id": "ODD",
        "observations": [
            {"date": "2020-02-01", "value": 222.0,
             "first_available": "2020-03-10"},
            # January, delayed, published AFTER February's release
            {"date": "2020-01-01", "value": 111.0,
             "first_available": "2020-03-20"},
        ],
    }), encoding="utf-8")
    load_vintage.cache_clear()
    value, obs_date, _ = value_as_of("ODD", "2020-03-25",
                                     vintage_dir=tmp_path)
    assert (value, obs_date) == (222.0, pd.Timestamp("2020-02-01")), \
        "returned the stale period because it was published most recently"
    load_vintage.cache_clear()


def test_missing_series_raises_actionable_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="download_alfred_vintages"):
        load_vintage("NOPE", vintage_dir=tmp_path)


# ------------------------------------------------------------ archive

@needs_archive
def test_real_publication_lag_is_material():
    """If this ever approaches zero, the gating has silently broken."""
    lag = publication_lag("PAYEMS")
    assert lag.median() > 25, f"PAYEMS lag implausibly small: {lag.median()}"


@needs_archive
def test_covid_crash_saw_only_precrisis_macro():
    """2020-03-15 regression, with the numbers.

    Claims reached ~6.8M within two weeks. A decision on 2020-03-15 could
    only see the week of 2020-03-07 at 211k, and payrolls only through
    February. This is why macro cannot time a fast drawdown.
    """
    payems = value_as_of("PAYEMS", "2020-03-15")
    assert payems[1] <= pd.Timestamp("2020-02-01"), \
        "payrolls leaked a period that was not yet published"

    claims = value_as_of("ICSA", "2020-03-15")
    assert claims[0] < 400_000, \
        "claims value implies post-surge data leaked into a pre-surge date"


@needs_archive
def test_vintage_never_reads_a_later_period_than_naive():
    """Point-in-time may lag the naive join, never lead it.

    The invariant is about PERIODS, not values: comparing magnitudes
    would only hold for a monotonically rising series, and payrolls fall
    in every recession - which is exactly when this matters most.
    """
    df = load_vintage("PAYEMS").sort_values("date")
    dates = pd.date_range("2015-01-31", "2024-12-31", freq="ME")

    for decision_date in dates:
        got = value_as_of("PAYEMS", decision_date)
        if got is None:
            continue
        _, vintage_period, first_available = got
        naive_visible = df[df["date"] <= decision_date]
        naive_period = naive_visible.iloc[-1]["date"]

        assert vintage_period <= naive_period, (
            f"on {decision_date.date()} vintage used period "
            f"{vintage_period.date()} but naive used {naive_period.date()}")
        assert first_available <= decision_date, (
            f"used a value first published {first_available.date()}, "
            f"after the decision date {decision_date.date()}")


@needs_archive
def test_vintage_is_usually_a_full_period_behind():
    """The lag should bite most months, not be a rounding artefact."""
    dates = pd.date_range("2015-01-31", "2024-12-31", freq="ME")
    behind = 0
    for decision_date in dates:
        got = value_as_of("PAYEMS", decision_date)
        if got is None:
            continue
        naive_period = (load_vintage("PAYEMS").sort_values("date")
                        .query("date <= @decision_date").iloc[-1]["date"])
        if got[1] < naive_period:
            behind += 1
    assert behind / len(dates) > 0.9, (
        f"only {behind}/{len(dates)} months lagged - gating may be a no-op")
