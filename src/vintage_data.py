#!/usr/bin/env python3
"""Point-in-time access to macro series.

The whole purpose of this module is one rule:

    A decision made on date D may only use values that were PUBLIC on D.

Macro data breaks that rule in two separate ways, and both have to be
handled or the backtest is fiction:

1. REVISION. FRED serves today's value. Payrolls, GDP and industrial
   production are revised for years, so a 2008 decision reading the
   current series sees numbers that did not exist until 2010. Fixed by
   using ALFRED initial releases - the value as first published.

2. PUBLICATION LAG. Even the initial release was not available on the
   date it describes. July payrolls are published around 7 August;
   median lag is 35 days, and HOUST has reached 130. Fixed by gating on
   `first_available` rather than the observation date.

Miss (2) and a monthly strategy rebalancing on the last day of the month
is reading a number that appears a week later. That is a small, entirely
invisible, and completely fatal amount of lookahead.

Data comes from tools/download_alfred_vintages.py.
"""
import functools
import json
from pathlib import Path

import pandas as pd

VINTAGE_DIR = Path("data/vintage")


@functools.lru_cache(maxsize=32)
def load_vintage(series_id, vintage_dir=None):
    """Initial-release observations for a series.

    Returns a DataFrame with columns value / first_available, indexed by
    observation date and sorted by publication order - which is the
    order a real observer learned them, and is NOT always observation
    order (a delayed release can publish after a later period's).
    """
    directory = Path(vintage_dir) if vintage_dir else VINTAGE_DIR
    path = directory / f"{series_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing. Run tools/download_alfred_vintages.py")

    payload = json.loads(path.read_text(encoding="utf-8"))
    df = pd.DataFrame(payload["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["first_available"] = pd.to_datetime(df["first_available"])
    return df.sort_values("first_available").reset_index(drop=True)


def value_as_of(series_id, decision_date, vintage_dir=None):
    """The most recent value PUBLIC on `decision_date`.

    Returns (value, observation_date, first_available) or None if
    nothing had been published yet.
    """
    df = load_vintage(series_id, vintage_dir)
    cutoff = pd.Timestamp(decision_date)
    visible = df[df["first_available"] <= cutoff]
    if visible.empty:
        return None
    # Latest OBSERVATION among those already published - not simply the
    # last row, because releases can arrive out of period order.
    row = visible.loc[visible["date"].idxmax()]
    return float(row["value"]), row["date"], row["first_available"]


def series_as_of(series_id, decision_dates, vintage_dir=None):
    """Vintage-correct series sampled at a sequence of decision dates.

    This is the function a backtest should use. Each point answers "what
    would I have known on this date", never "what do we now know about
    this date".
    """
    out = {}
    for decision_date in decision_dates:
        got = value_as_of(series_id, decision_date, vintage_dir)
        out[pd.Timestamp(decision_date)] = got[0] if got else float("nan")
    return pd.Series(out, name=series_id).sort_index()


def naive_series_as_of(series_id, decision_dates, vintage_dir=None):
    """The WRONG way, for measuring how wrong it is.

    Gates on the observation date instead of the publication date - the
    mistake made by any backtest that joins a macro series on its period
    label. Exists so studies can quantify the bias rather than assert it.
    """
    df = load_vintage(series_id, vintage_dir).sort_values("date")
    out = {}
    for decision_date in decision_dates:
        cutoff = pd.Timestamp(decision_date)
        visible = df[df["date"] <= cutoff]
        out[cutoff] = (float(visible.iloc[-1]["value"])
                       if not visible.empty else float("nan"))
    return pd.Series(out, name=series_id).sort_index()


def publication_lag(series_id, vintage_dir=None):
    """Days between the period a number describes and its release."""
    df = load_vintage(series_id, vintage_dir)
    return (df["first_available"] - df["date"]).dt.days


if __name__ == "__main__":
    for sid in ("PAYEMS", "ICSA", "HOUST"):
        try:
            lag = publication_lag(sid)
            got = value_as_of(sid, "2020-03-15")
            print(f"{sid:9} lag median {lag.median():.0f}d  "
                  f"as-of 2020-03-15 -> {got[0] if got else None} "
                  f"(period {got[1].date() if got else '-'})")
        except FileNotFoundError as exc:
            print(f"{sid:9} {exc}")
