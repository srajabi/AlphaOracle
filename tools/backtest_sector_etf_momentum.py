#!/usr/bin/env python3
"""Does finding 43's sector-momentum edge survive on TRADEABLE ETFs?

THE DECISIVE TEST
-----------------
Finding 43 measured +3.63pp/yr over equal-weight on French's 49 industry
portfolios (t=4.38, p=1.3e-5), but 43c showed the edge collapsing as the
universe coarsens: ~1.5pp at 10-12 buckets, p=0.10. Those coarse
universes are still French research portfolios, not things you can buy.

This runs the same 12-1 momentum on the 11 SPDR sector ETFs - the actual
investable universe - with real costs.

THE CONFOUND THIS CONTROLS FOR
------------------------------
43c compared 49 vs 12 vs 10 buckets over 1926-2026, but the SPDRs only
exist from 1998-12. If the edge simply died after 1998 for reasons
unrelated to granularity, the granularity conclusion is wrong. So the
French 49 and French 12 are ALSO re-run restricted to 1999+, which
separates "too coarse" from "too recent".

COSTS - and a correction to finding 43c
---------------------------------------
43c claimed 0.35-0.50% expense ratios. That is right for NICHE INDUSTRY
ETFs (the 49-bucket granularity) but wrong for the SPDR sectors, which
charge ~0.09%. The 11-sector version is CHEAP to trade; its problem is
that the edge is weak there, not that fees eat it. Charged here:
0.09%/yr expense plus 10bp per unit turnover (these are highly liquid).

Writes data/sector_etf_momentum.json.
"""
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OUT = REPO / "data" / "sector_etf_momentum.json"
HIST = REPO / "data" / "historical_long"
DEEP = REPO / "data" / "deep_history" / "french_daily.json"
BASE = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
        "%s_Industry_Portfolios_Daily_CSV.zip")

SECTORS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP",
           "XLU", "XLV", "XLY", "XLC", "XLRE"]
EXPENSE = 0.0009          # SPDR sector ETF, annual
TURN_BP = 10              # per unit turnover, one way
START = "1999-01-01"
LOOKBACK, SKIP = 11, 1


def load_prices(ticker):
    path = HIST / f"{ticker}.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text())["prices"]
    df = pd.DataFrame(raw)
    date_col = next((c for c in ("date", "Date", "timestamp") if c in df), None)
    px_col = next((c for c in ("adj_close", "adjClose", "close", "Close")
                   if c in df), None)
    if date_col is None or px_col is None:
        raise SystemExit(f"{ticker}: columns are {list(df.columns)}")
    s = pd.Series(pd.to_numeric(df[px_col], errors="coerce").values,
                  index=pd.to_datetime(df[date_col]))
    return s.sort_index().dropna()


def french(tag):
    raw = subprocess.run(
        ["curl", "-sS", "-L", "-m", "300", "--retry", "3",
         "-A", "Mozilla/5.0", BASE % tag], capture_output=True).stdout
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        text = zf.read(zf.namelist()[0]).decode("latin-1")
    hdr, rows = None, []
    for line in text.splitlines():
        p = [x.strip() for x in line.split(",")]
        if hdr is None:
            if len(p) > 3 and p[0] == "" and len(p) >= int(tag):
                hdr = ["date"] + p[1:]
            continue
        if len(p[0]) == 8 and p[0].isdigit():
            try:
                rows.append([p[0]] + [float(v) for v in p[1:]])
            except ValueError:
                continue
        elif rows:
            break
    d = pd.DataFrame([r for r in rows if len(r) == len(hdr)], columns=hdr)
    d["date"] = pd.to_datetime(d["date"], format="%Y%m%d")
    d = d.set_index("date").sort_index()
    for c in d.columns:
        d[c] = pd.to_numeric(d[c], errors="coerce")
        d.loc[d[c] <= -99.99, c] = np.nan
        d[c] = d[c] / 100.0
    return d


def momentum(mret, n, expense=0.0, turn_bp=0):
    """12-1 momentum, equal weight top n, monthly rebalance."""
    score = ((1 + mret).rolling(LOOKBACK).apply(np.prod, raw=True)).shift(SKIP)
    rets, prev = {}, set()
    months = list(mret.index)
    for i, dt in enumerate(months[:-1]):
        s = score.loc[dt].dropna()
        if len(s) < n:
            continue
        picks = set(s.nlargest(n).index)
        nxt = months[i + 1]
        row = mret.loc[nxt, list(picks)]
        if not row.notna().any():
            continue
        turn = len(picks ^ prev) / max(len(picks | prev), 1)
        rets[nxt] = (float(row.mean()) - expense / 12
                     - turn * turn_bp / 10000.0)
        prev = picks
    return pd.Series(rets)


def perf(r):
    r = r.dropna()
    c = (1 + r).cumprod()
    y = len(r) / 12
    return {"cagr_pct": float((c.iloc[-1] ** (1 / y) - 1) * 100),
            "max_dd_pct": float((c / c.cummax() - 1).min() * 100),
            "vol_pct": float(r.std() * np.sqrt(12) * 100),
            "months": int(len(r))}


def report(label, mret, bench, expense, turn_bp, ns):
    print(f"\n=== {label} ===")
    ew = mret.mean(axis=1) - expense / 12
    rows = {"EW all (control)": perf(ew)}
    if bench is not None:
        rows["benchmark"] = perf(bench)
    best = {}
    for n in ns:
        if n >= mret.shape[1]:
            continue
        r = momentum(mret, n, expense, turn_bp)
        rows[f"mom_top{n}"] = perf(r)
        best[n] = r
    print(f"{'strategy':20}{'CAGR':>9}{'maxDD':>9}{'vol':>8}{'vs EW':>9}")
    base = rows["EW all (control)"]["cagr_pct"]
    for k, v in rows.items():
        print(f"{k:20}{v['cagr_pct']:>8.2f}%{v['max_dd_pct']:>8.1f}%"
              f"{v['vol_pct']:>7.1f}%{v['cagr_pct']-base:>8.2f}pp")
    stats_out = {}
    for n, r in best.items():
        com = r.index.intersection(ew.index)
        d = (r.loc[com] - ew.loc[com]).dropna()
        t, p = stats.ttest_1samp(d, 0)
        stats_out[f"top{n}"] = {"excess_pct_yr": float(d.mean() * 1200),
                                "t": float(t), "p": float(p), "n": int(len(d))}
        print(f"  top{n} - EW: {d.mean()*1200:+6.2f}%/yr  t={t:5.2f}  "
              f"p={p:.4f}  n={len(d)}")
    return {"perf": rows, "spread": stats_out}


def main():
    results = {}

    # ---- 1. The tradeable universe -------------------------------
    px = {t: load_prices(t) for t in SECTORS}
    px = {t: s for t, s in px.items() if s is not None and len(s) > 250}
    print(f"sector ETFs loaded: {len(px)} -> {sorted(px)}")
    for t, s in sorted(px.items()):
        print(f"  {t}: {s.index.min():%Y-%m-%d} -> {s.index.max():%Y-%m-%d}")
    wide = pd.DataFrame(px).sort_index()
    mret = wide.resample("ME").last().pct_change().loc[START:]

    spy = load_prices("SPY")
    spy_m = spy.resample("ME").last().pct_change().reindex(mret.index)
    results["etf_11sector"] = report(
        "11 SPDR sector ETFs, real costs (0.09% + 10bp/turn)",
        mret, spy_m, EXPENSE, TURN_BP, (2, 3, 4, 5))

    # ---- 2. Granularity vs recency control -----------------------
    # Same period, French research portfolios, zero cost. If the 49
    # bucket edge ALSO dies post-1999 the granularity story is wrong.
    for tag in ("49", "12"):
        d = french(tag)
        m = ((1 + d).resample("ME").prod() - 1).loc[START:]
        results[f"french{tag}_post1999"] = report(
            f"French {tag} industries, 1999+ (granularity vs recency control)",
            m, None, 0.0, TURN_BP, (3, 5, 10))

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
