#!/usr/bin/env python3
"""Sector rotation: does trading BETWEEN segments beat holding the market?

WHY THIS IS NOT DETECTOR #7
---------------------------
Findings 33, 34, 41b, 42 and H9 all tested ideas I invented. This one is
different: industry momentum is documented (Moskowitz & Grinblatt 1999,
"Do Industries Explain Momentum?"), and cross-sectional momentum is among
the most replicated anomalies in finance. Other people have tried to kill
it and failed.

That cuts both ways. Published anomalies decay once arbitraged, and
momentum suffers severe crashes (2009). So the test below is built around
the two ways this fails in practice, not around whether it worked in
1970.

THE THREE QUESTIONS
-------------------
1. Does the momentum SPREAD exist? Winners minus losers. If top-10 does
   not beat bottom-10 the effect is absent and nothing else matters.

2. Does it SURVIVE PUBLICATION? Moskowitz-Grinblatt published in 1999.
   Splitting at 1999 gives a genuine out-of-sample test that costs
   nothing to run and is not available for most anomalies. Finding 35's
   lesson: an effect that only exists in-sample is not an effect.

3. Does it survive COSTS? Rotating 10 of 49 industries monthly implies
   real turnover. Charged at 0 / 10 / 25bp per unit turnover. A strategy
   that needs zero costs to win does not win.

Also tested: holding only segments above their OWN 200-day trend, which
is the natural portfolio form of finding 42's breadth idea, and stacking
rotation on top of the market gate.

Standard parameters, NOT tuned: 12-1 momentum (rank on months t-11..t-1,
skip the most recent month, hold t+1), monthly rebalance, equal weight.
Deviating from the published parameterisation would make any win
unattributable (finding 29).

Writes data/sector_rotation_study.json.
"""
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "sector_rotation_study.json"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"
CACHE = REPO / "data" / "_industries_daily.pkl"
URL = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
       "49_Industry_Portfolios_Daily_CSV.zip")

LOOKBACK, SKIP = 11, 1        # 12-1 momentum
TOP_NS = (5, 10, 15)
COSTS_BP = (0, 10, 25)
PUBLICATION = "1999-12-31"    # Moskowitz-Grinblatt
SMA_D = 200


def fetch_industries():
    if CACHE.exists():
        return pd.read_pickle(CACHE)
    raw = subprocess.run(
        ["curl", "-sS", "-L", "-m", "300", "--retry", "3",
         "-A", "Mozilla/5.0", URL], capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")
    header, rows = None, []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if header is None:
            if len(parts) > 40 and parts[0] == "":
                header = ["date"] + parts[1:]
            continue
        if len(parts[0]) == 8 and parts[0].isdigit():
            try:
                rows.append([parts[0]] + [float(v) for v in parts[1:]])
            except ValueError:
                continue
        elif rows:
            break
    df = pd.DataFrame([r for r in rows if len(r) == len(header)],
                      columns=header)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.set_index("date").sort_index()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df.loc[df[c] <= -99.99, c] = np.nan
        df[c] = df[c] / 100.0
    df.to_pickle(CACHE)
    return df


def load_market():
    payload = json.loads(DEEP.read_text())
    d = pd.DataFrame(payload["observations"])
    d["date"] = pd.to_datetime(d["date"])
    return d.set_index("date").sort_index()


def market_gate_monthly(daily_level, month_index, band=0.04):
    """200-day/4% gate (finding 41c) collapsed to a month-end state."""
    sma = daily_level.rolling(SMA_D).mean()
    lv, mv = daily_level.values, sma.values
    out, state = np.ones(len(lv)), True
    for i in range(len(lv)):
        m = mv[i]
        if m == m:
            if state and lv[i] < m * (1 - band):
                state = False
            elif (not state) and lv[i] > m * (1 + band):
                state = True
        out[i] = 1.0 if state else 0.0
    s = pd.Series(np.r_[1.0, out[:-1]], index=daily_level.index)
    # .last() is the state on the FINAL day of month T. Applying that to
    # month T's return trades on information from the end of the month
    # being traded - the causality bug that once produced a +271% SMA200
    # result in this repo. Shift one month: month T is traded on the
    # state as at the close of month T-1.
    m = s.resample("ME").last().shift(1)
    return m.reindex(month_index).ffill().fillna(1.0)


def stats(r, turnover=None, cost_bp=0):
    r = r.dropna()
    if turnover is not None:
        r = r - turnover.reindex(r.index).fillna(0.0) * cost_bp / 10000.0
    curve = (1 + r).cumprod()
    years = len(r) / 12
    dd = curve / curve.cummax() - 1
    return {
        "cagr_pct": float((curve.iloc[-1] ** (1 / years) - 1) * 100),
        "max_dd_pct": float(dd.min() * 100),
        "vol_pct": float(r.std() * np.sqrt(12) * 100),
        "sharpe_ish": float(r.mean() / r.std() * np.sqrt(12)) if r.std() else 0.0,
        "months": int(len(r)),
    }


def momentum_portfolio(mret, n, ascending=False, overlay=None):
    """Equal-weight top (or bottom) n industries by 12-1 momentum.

    Ranked on months t-11..t-1 (the most recent month is SKIPPED, the
    standard specification - including it picks up short-term reversal).
    Held in month t+1. Returns (monthly return, monthly turnover).
    """
    cum = (1 + mret).rolling(LOOKBACK).apply(np.prod, raw=True)
    score = cum.shift(SKIP)                     # skip most recent month
    rets, turns, prev = {}, {}, set()
    for i, dt in enumerate(mret.index):
        if i + 1 >= len(mret.index):
            break
        s = score.loc[dt].dropna()
        if len(s) < n:
            continue
        picks = set(s.nsmallest(n).index if ascending
                    else s.nlargest(n).index)
        nxt = mret.index[i + 1]
        r = float(mret.loc[nxt, list(picks)].mean())
        if overlay is not None and overlay.get(nxt, 1.0) == 0.0:
            r = 0.0                              # gated to cash
            picks = set()
        turns[nxt] = len(picks ^ prev) / max(len(picks | prev), 1)
        rets[nxt] = r
        prev = picks
    return pd.Series(rets), pd.Series(turns)


def trend_sectors(dret, mret):
    """Hold every segment above its OWN 200-day trend, equal weight.

    The portfolio form of finding 42's breadth signal: instead of
    counting how many segments are healthy and gating the index, just
    own the healthy ones.
    """
    lv = (1 + dret.fillna(0.0)).cumprod().where(dret.notna())
    above = (lv > lv.rolling(SMA_D, min_periods=SMA_D).mean())
    sel = above.resample("ME").last().shift(1)   # act on last month's state
    sel = sel.reindex(mret.index).fillna(False)
    rets, turns, prev = {}, {}, set()
    for dt in mret.index:
        picks = set(sel.columns[sel.loc[dt].values.astype(bool)])
        row = mret.loc[dt, list(picks)] if picks else None
        rets[dt] = float(row.mean()) if picks and row.notna().any() else 0.0
        turns[dt] = len(picks ^ prev) / max(len(picks | prev), 1)
        prev = picks
    return pd.Series(rets), pd.Series(turns)


def main():
    ind = fetch_industries()
    mkt = load_market()
    mret = (1 + ind).resample("ME").prod() - 1
    mkt_m = (1 + mkt["market_return"]).resample("ME").prod() - 1
    rf_m = (1 + mkt["rf"]).resample("ME").prod() - 1
    mret = mret.loc[mret.index.intersection(mkt_m.index)]
    mkt_m = mkt_m.reindex(mret.index)
    print(f"industries {ind.shape[1]}, months {len(mret)}  "
          f"{mret.index.min():%Y-%m} -> {mret.index.max():%Y-%m}\n")

    lvl = (1 + mkt["market_return"]).cumprod()
    gate = market_gate_monthly(lvl, mret.index)

    book = {}
    book["market_buyhold"] = (mkt_m, pd.Series(0.0, index=mret.index))
    book["market_gated_4%"] = (
        pd.Series(np.where(gate.values > 0, mkt_m.values, rf_m.values),
                  index=mret.index),
        (gate != gate.shift(1)).astype(float))
    for n in TOP_NS:
        book[f"mom_top{n}"] = momentum_portfolio(mret, n)
    book["mom_bottom10"] = momentum_portfolio(mret, 10, ascending=True)
    book["mom_top10_gated"] = momentum_portfolio(
        mret, 10, overlay=gate.to_dict())
    book["trend_sectors"] = trend_sectors(ind, mret)

    results = {}
    print(f"{'strategy':20}{'CAGR@0bp':>10}{'@10bp':>9}{'@25bp':>9}"
          f"{'maxDD':>9}{'vol':>8}{'turn/mo':>9}")
    print("-" * 74)
    for name, (r, t) in book.items():
        row = {f"cagr_{c}bp": stats(r, t, c)["cagr_pct"] for c in COSTS_BP}
        base = stats(r, t, 0)
        row.update(max_dd_pct=base["max_dd_pct"], vol_pct=base["vol_pct"],
                   months=base["months"],
                   avg_turnover=float(t.reindex(r.index).fillna(0).mean()))
        results[name] = row
        print(f"{name:20}{row['cagr_0bp']:>9.2f}%{row['cagr_10bp']:>8.2f}%"
              f"{row['cagr_25bp']:>8.2f}%{row['max_dd_pct']:>8.1f}%"
              f"{row['vol_pct']:>7.1f}%{row['avg_turnover']:>8.2f}")

    # ---- Q1: does the spread exist? --------------------------------
    top, bot = book["mom_top10"][0], book["mom_bottom10"][0]
    common = top.index.intersection(bot.index)
    spread = top.loc[common] - bot.loc[common]
    from scipy import stats as st
    t_stat, p = st.ttest_1samp(spread.dropna(), 0)
    print(f"\nQ1 SPREAD  top10 - bottom10: {spread.mean()*12*100:+.2f}%/yr  "
          f"t={t_stat:.2f}  p={p:.2e}  n={len(spread)} months")

    # ---- Q2: does it survive publication? --------------------------
    print(f"\nQ2 PUBLICATION SPLIT (Moskowitz-Grinblatt 1999)")
    print(f"{'strategy':20}{'pre-2000':>12}{'post-2000':>12}{'decay':>10}")
    print("-" * 54)
    era = {}
    for name, (r, t) in book.items():
        pre = stats(r.loc[:PUBLICATION], t, 10)
        post = stats(r.loc[PUBLICATION:], t, 10)
        era[name] = {"pre_2000_cagr": pre["cagr_pct"],
                     "post_2000_cagr": post["cagr_pct"],
                     "pre_dd": pre["max_dd_pct"], "post_dd": post["max_dd_pct"]}
        print(f"{name:20}{pre['cagr_pct']:>11.2f}%{post['cagr_pct']:>11.2f}%"
              f"{post['cagr_pct']-pre['cagr_pct']:>9.2f}pp")

    # ---- Q3: momentum crash check ----------------------------------
    print(f"\nQ3 WORST 12 MONTHS for mom_top10 vs market")
    roll = (1 + top).rolling(12).apply(np.prod, raw=True) - 1
    rollm = (1 + mkt_m).rolling(12).apply(np.prod, raw=True) - 1
    worst = roll.nsmallest(5)
    for dt, v in worst.items():
        print(f"  12m to {dt:%Y-%m}: momentum {v*100:>7.1f}%   "
              f"market {rollm.get(dt, float('nan'))*100:>7.1f}%")

    OUT.write_text(json.dumps({"full": results, "eras": era,
                               "spread": {"annual_pct": float(spread.mean()*12*100),
                                          "t": float(t_stat), "p": float(p)}},
                              indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
