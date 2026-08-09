"""Re-derive the numbers claimed in claude/findings.md.

WHY THIS EXISTS
---------------
findings.md is prose written by LLM sessions. Prose is not evidence. A
number in a markdown file that no code reproduces is an unfalsifiable
claim, and over many sessions those compound: session 40 cites session
12's unchecked number as established fact and builds on it.

This file is the falsifier. Every claim encoded here re-derives from raw
data. When one fails, either the finding is wrong or its SPECIFICATION
was never recorded precisely enough to reproduce - and both are defects
worth failing a test over.

Known live example: finding 3 claims SMA200 on VT gives -19% maxDD and a
Sharpe identical to buy-hold (0.56). An independent monthly-checked
reimplementation gives -34.8% and 0.44. Buy-hold reproduces exactly, so
the data is fine; the overlay's spec (almost certainly check frequency,
which finding 24 shows moves maxDD by ~12pp on its own) was never
written down. That claim is quarantined below rather than asserted.

Rule going forward: a finding that cannot be re-derived by a test here
does not get cited as evidence for a decision.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

DATA = REPO / "data" / "historical_long"
needs_data = pytest.mark.skipif(
    not (DATA / "VT.json").exists(),
    reason="historical_long data not present")


def load(ticker):
    payload = json.loads((DATA / f"{ticker}.json").read_text())
    s = pd.Series({p["date"]: p["close"] for p in payload["prices"]},
                  dtype=float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def perf(returns, cash_annual=0.02, active=None):
    cash = (1 + cash_annual) ** (1 / 252) - 1
    r = returns if active is None else pd.Series(
        np.where(active, returns, cash), index=returns.index)
    curve = (1 + r).cumprod()
    years = len(r) / 252
    cagr = curve.iloc[-1] ** (1 / years) - 1
    vol = r.std() * np.sqrt(252)
    return {
        "cagr_pct": cagr * 100,
        "sharpe": cagr / vol,
        "max_dd_pct": (curve / curve.cummax() - 1).min() * 100,
        "terminal_x": curve.iloc[-1],
    }


# ------------------------------------------------- finding 3 (VT/SMA200)

@needs_data
def test_finding3_buy_hold_reproduces():
    """VT buy-hold 2010+: claimed 9.8% CAGR / 0.56 Sharpe / -34% maxDD."""
    ret = load("VT").loc["2010-01-01":"2026-03-31"].pct_change().dropna()
    got = perf(ret)
    assert 9.0 < got["cagr_pct"] < 10.5, got
    assert 0.50 < got["sharpe"] < 0.65, got
    assert -38 < got["max_dd_pct"] < -30, got


@needs_data
def test_finding3_overlay_drawdown_claim_does_not_reproduce():
    """QUARANTINE: finding 3 claims -19% maxDD for the SMA200 overlay.

    A monthly-checked reimplementation gives ~-35%. This test asserts the
    DISCREPANCY so it cannot be quietly forgotten. If someone later
    recovers the original spec and it genuinely yields -19%, this test
    should fail and be replaced with a reproduction.
    """
    from tools.backtest_check_frequency import build_signal

    prices = load("VT").loc["2008-11-01":"2026-03-31"]
    ret = prices.pct_change().dropna().loc["2010-01-01":]
    sig = build_signal(prices, "monthly", 0.0).reindex(ret.index).ffill()
    got = perf(ret, active=sig.fillna(True))

    assert got["max_dd_pct"] < -28, (
        "monthly SMA200 on VT now shows a shallow drawdown; finding 3's "
        f"-19% may be reproducible after all. Got {got['max_dd_pct']:.1f}%")


# ----------------------------------------- finding 24 (check frequency)

@needs_data
def test_finding24_bands_invert_the_frequency_answer():
    """Without bands monthly beats daily; with bands daily wins.

    This is the load-bearing claim of finding 24 and the reason finding
    5's "monthly beats daily" needed qualifying.
    """
    from tools.backtest_check_frequency import (
        build_signal, levered_daily_returns, load as load_freq)

    prices = load_freq("SPY").loc["1992-11-01":"2026-03-31"]
    underlying = prices.pct_change().dropna()
    lev = levered_daily_returns(underlying, 3).loc["1994-01-01":]

    def run(freq, band):
        sig = build_signal(prices, freq, band).reindex(lev.index).ffill()
        return perf(lev, active=sig.fillna(True))["terminal_x"]

    assert run("daily", 0.0) < run("monthly", 0.0), \
        "without bands, daily should whipsaw and lose to monthly"
    assert run("daily", 0.05) > run("monthly", 0.05) * 1.5, \
        "with 5% bands, daily should decisively beat monthly"


@needs_data
def test_finding24_band_plateau_is_not_a_knife_edge():
    """2-6% must all beat 3x buy-hold, or the result is a fitted point."""
    from tools.backtest_check_frequency import (
        build_signal, levered_daily_returns, load as load_freq)

    prices = load_freq("SPY").loc["1992-11-01":"2026-03-31"]
    lev = levered_daily_returns(prices.pct_change().dropna(),
                                3).loc["1994-01-01":]
    buy_hold = perf(lev)["terminal_x"]

    for band in (0.02, 0.03, 0.04, 0.05, 0.06):
        sig = build_signal(prices, "daily", band).reindex(lev.index).ffill()
        got = perf(lev, active=sig.fillna(True))["terminal_x"]
        assert got > buy_hold * 2, (
            f"band {band:.0%} gives {got:.0f}x vs buy-hold {buy_hold:.0f}x - "
            "plateau has collapsed, treat the result as fitted")


@needs_data
def test_finding24_wide_bands_collapse():
    """The cliff past ~8% is part of the finding and must stay true."""
    from tools.backtest_check_frequency import (
        build_signal, levered_daily_returns, load as load_freq)

    prices = load_freq("SPY").loc["1992-11-01":"2026-03-31"]
    lev = levered_daily_returns(prices.pct_change().dropna(),
                                3).loc["1994-01-01":]
    buy_hold = perf(lev)["terminal_x"]
    sig = build_signal(prices, "daily", 0.15).reindex(lev.index).ffill()
    assert perf(lev, active=sig.fillna(True))["terminal_x"] < buy_hold, \
        "a 15% band should underperform buy-hold; the cliff has moved"


# --------------------------------------------- finding 21 (CAD hedging)

@needs_data
def test_finding21_cad_usd_is_negatively_correlated_with_spy():
    """Claimed corr -0.569; the sign is what the conclusion rests on."""
    spy, fx = load("SPY"), load("CAD=X")
    df = pd.concat([spy.rename("spy"), fx.rename("usdcad")], axis=1,
                   sort=True).dropna()
    r = df.resample("ME").last().pct_change().dropna()
    corr = r["spy"].corr(r["usdcad"])
    assert -0.70 < corr < -0.45, f"claimed ~-0.569, got {corr:.3f}"


@needs_data
def test_finding21_unhedged_cad_reduces_drawdown():
    spy, fx = load("SPY"), load("CAD=X")
    df = pd.concat([spy.rename("spy"), fx.rename("usdcad")], axis=1,
                   sort=True).dropna()
    usd = df["spy"].pct_change().dropna()
    cad = (df["spy"] * df["usdcad"]).pct_change().dropna()
    assert perf(cad)["max_dd_pct"] > perf(usd)["max_dd_pct"] + 5, \
        "unhedged CAD should show a materially shallower drawdown"
