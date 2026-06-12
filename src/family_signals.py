#!/usr/bin/env python3
"""Daily family-mandate signals (claude/ips_case_study.md).

Computes the IPS rule states from fresh daily data and emits
data/family_signals.json + frontend copy. Pure signal feed - this never
touches any account; the user's own automation consumes the JSON.

Signals:
  slow_channel  - equity (XEQT.TO, SPY fallback) vs 200d SMA at month-end
  fast_channel  - 5d-median ^VIX/^VIX3M backwardation
  credit        - HYG/LQD 63d relative momentum vs -2%
  canary        - 13612W breadth on (EWA, TLT)
Mandates:
  P (stochastic horizon): sleeve invested iff slow risk_on AND fast clear
  Y core: same; Y satellite: see the registered champion's own state
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def load_closes(ticker: str):
    """Daily closes: prefer fresh data/history, fall back to historical_long."""
    daily = Path(f"data/history/{ticker}.json")
    if daily.exists():
        rows = json.loads(daily.read_text())
        pairs = [(r["time"], float(r["close"])) for r in rows]
        if len(pairs) >= 210:
            return pairs
    long = Path(f"data/historical_long/{ticker}.json")
    if long.exists():
        data = json.loads(long.read_text())
        return [(r["date"], float(r["close"])) for r in data["prices"]]
    return []


def sma(values, window):
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def slow_channel(closes):
    """Equity vs 200d SMA using the LAST MONTH-END observation (the IPS
    evaluates monthly; intra-month wobble is deliberately ignored)."""
    if len(closes) < 210:
        return {"state": "insufficient_data"}
    # last month-end = last date whose next date is a new month
    idx = len(closes) - 1
    for i in range(len(closes) - 2, 0, -1):
        if closes[i][0][:7] != closes[i + 1][0][:7]:
            idx = i
            break
    values = [c for _, c in closes[: idx + 1]]
    sma200 = sma(values, 200)
    price = values[-1]
    return {
        "state": "risk_on" if price > sma200 else "risk_off",
        "as_of_month_end": closes[idx][0],
        "price": round(price, 2),
        "sma200": round(sma200, 2),
        "distance_pct": round((price / sma200 - 1) * 100, 2),
    }


def fast_channel(vix_closes, vix3m_closes):
    if len(vix_closes) < 5 or len(vix3m_closes) < 5:
        return {"state": "insufficient_data"}
    v = dict(vix_closes)
    v3 = dict(vix3m_closes)
    common = sorted(set(v) & set(v3))[-5:]
    if len(common) < 5:
        return {"state": "insufficient_data"}
    ratios = sorted(v[d] / v3[d] for d in common)
    median = ratios[2]
    return {
        "state": "backwardation" if median > 1.0 else "clear",
        "vix_vix3m_5d_median": round(median, 3),
        "as_of": common[-1],
    }


def credit_signal(hyg_closes, lqd_closes):
    if len(hyg_closes) < 64 or len(lqd_closes) < 64:
        return {"state": "insufficient_data"}
    hyg = [c for _, c in hyg_closes]
    lqd = [c for _, c in lqd_closes]
    rel = (hyg[-1] / hyg[-64]) - (lqd[-1] / lqd[-64])
    return {"state": "stress" if rel < -0.02 else "clear",
            "hyg_lqd_63d_relmom": round(rel, 4)}


def mom_13612w(closes):
    c = [x for _, x in closes]
    if len(c) < 253:
        return None
    return (12 * (c[-1] / c[-22] - 1) + 4 * (c[-1] / c[-64] - 1)
            + 2 * (c[-1] / c[-127] - 1) + 1 * (c[-1] / c[-253] - 1)) / 19


def canary_signal(ewa_closes, tlt_closes):
    moms = {"EWA": mom_13612w(ewa_closes), "TLT": mom_13612w(tlt_closes)}
    if any(v is None for v in moms.values()):
        return {"state": "insufficient_data"}
    negative = [k for k, v in moms.items() if v < 0]
    return {
        "state": ["risk_on", "half_defensive", "full_defensive"][len(negative)],
        "negative_canaries": negative,
        "momentum": {k: round(v, 4) for k, v in moms.items()},
    }


def main():
    equity = load_closes("XEQT.TO") or load_closes("SPY")
    signals = {
        "slow_channel": slow_channel(equity),
        "fast_channel": fast_channel(load_closes("^VIX"), load_closes("^VIX3M")),
        "credit": credit_signal(load_closes("HYG"), load_closes("LQD")),
        "canary": canary_signal(load_closes("EWA"), load_closes("TLT")),
    }
    slow_on = signals["slow_channel"].get("state") == "risk_on"
    fast_clear = signals["fast_channel"].get("state") == "clear"
    instruction = "SLEEVE_INVESTED" if (slow_on and fast_clear) else "SLEEVE_TO_TREASURIES"
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "ips": "claude/ips_case_study.md",
        "signals": signals,
        "mandates": {
            "P_sleeve": instruction,
            "Y_core_sleeve": instruction,
            "Y_satellite": "see registered champion state (canary signal above "
                           "for canary_daa_*)",
        },
    }
    for base in [Path("data"), Path("frontend/public/data")]:
        base.mkdir(parents=True, exist_ok=True)
        (base / "family_signals.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
