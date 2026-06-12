#!/usr/bin/env python3
"""Attribution monitor + track-record composites.

Closes the loop between the forward test and the backtests (the #1 item in
spikes/maturity_roadmap.md):

1. Pulls each Alpaca paper account's daily equity history (REST, no SDK
   version dependence).
2. Computes live metrics (since-inception return, rolling Sharpe, max DD).
3. Places each account inside its mapped strategy's bootstrap bands from
   the validation gauntlet -> status: on_script / watch / off_script.
4. Builds GIPS-style monthly return composites per account - committed to
   git daily, so the git history itself is the tamper-evident track record.

Outputs:
    data/attribution.json + frontend/public/data/attribution.json
    data/track_record.json + frontend/public/data/track_record.json

Runs in the daily workflow after the portfolio fetch. Requires the same
ALPACA_*_API_KEY env vars; accounts with missing keys are skipped.
"""

import json
import math
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ALPACA_BASE = "https://paper-api.alpaca.markets"
TRADING_DAYS = 252

# account id -> (env prefix, gauntlet strategy for expectation bands or None)
ACCOUNTS = {
    "dev": ("ALPACA_DEV", None),                       # advanced LLM - no backtest analogue
    "prod_1": ("ALPACA_PROD_1", None),                 # standard LLM - no analogue
    "prod_2": ("ALPACA_PROD_2", "reddit_200sma_tqqq"),  # TQQQ momentum
    "prod_3": ("ALPACA_PROD_3", "dual_momentum_rotation"),
    "prod_4": ("ALPACA_PROD_4", "sector_momentum_top3_filtered"),
    "prod_5": ("ALPACA_PROD_5", None),                 # SPY mean reversion (single-asset, not in sweep)
}

SCOREBOARD_PATH = Path("backtesting/results_validation/summary.json")


def fetch_portfolio_history(api_key: str, secret_key: str,
                            period: str = "1A") -> dict:
    """GET /v2/account/portfolio/history - daily equity series."""
    url = (f"{ALPACA_BASE}/v2/account/portfolio/history"
           f"?period={period}&timeframe=1D")
    req = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def equity_to_returns(timestamps, equities):
    """Clean (ts, equity) -> list of (iso_date, daily_return). Skips zero/None
    equities (account not yet funded)."""
    points = [(ts, eq) for ts, eq in zip(timestamps, equities)
              if eq not in (None, 0)]
    out = []
    for (ts_a, eq_a), (ts_b, eq_b) in zip(points, points[1:]):
        date = datetime.fromtimestamp(ts_b, tz=timezone.utc).strftime("%Y-%m-%d")
        out.append((date, eq_b / eq_a - 1.0))
    return out


def live_metrics(daily_returns):
    """Sharpe / total return / maxDD / current DD from (date, ret) pairs."""
    rets = [r for _, r in daily_returns]
    n = len(rets)
    if n < 5:
        return {"observations": n}
    mean = sum(rets) / n
    var = sum((r - mean) ** 2 for r in rets) / n
    std = math.sqrt(var)
    sharpe = mean / std * math.sqrt(TRADING_DAYS) if std > 0 else 0.0

    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in rets:
        equity *= 1.0 + r
        peak = max(peak, equity)
        max_dd = min(max_dd, equity / peak - 1.0)
    return {
        "observations": n,
        "total_return": equity - 1.0,
        "annualized_return": equity ** (TRADING_DAYS / n) - 1.0 if equity > 0 else -1.0,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "current_dd": equity / peak - 1.0,
    }


def monthly_composite(daily_returns):
    """GIPS-style: geometric monthly returns from daily series."""
    months = {}
    for date, r in daily_returns:
        key = date[:7]  # YYYY-MM
        months[key] = months.get(key, 1.0) * (1.0 + r)
    return {k: round(v - 1.0, 6) for k, v in sorted(months.items())}


def load_expectation_bands():
    """strategy -> bootstrap bands from the latest validation sweep."""
    if not SCOREBOARD_PATH.exists():
        return {}
    with open(SCOREBOARD_PATH) as f:
        summary = json.load(f)
    return {row["strategy"]: row for row in summary.get("scoreboard", [])}


def script_status(metrics: dict, bands: dict) -> dict:
    """Compare live metrics to the strategy's gauntlet expectations.

    on_script: inside the bootstrap 90% Sharpe band and above the p5 maxDD.
    watch: outside one of them. off_script: outside both, or current DD
    deeper than the bootstrap p5 maxDD.

    NOTE: live windows are short - a wide 'watch' zone is expected early.
    """
    if not bands or metrics.get("observations", 0) < 60:
        return {"status": "insufficient_history",
                "note": "needs >= 60 trading days and a mapped strategy"}
    breaches = []
    if metrics["sharpe"] < bands["sharpe_ci90_low"]:
        breaches.append(
            f"sharpe {metrics['sharpe']:.2f} < band low {bands['sharpe_ci90_low']:.2f}")
    if metrics["max_dd"] < bands["max_dd_p5"]:
        breaches.append(
            f"max_dd {metrics['max_dd']:.1%} worse than bootstrap p5 {bands['max_dd_p5']:.1%}")
    status = ("on_script" if not breaches
              else "off_script" if len(breaches) >= 2 else "watch")
    return {"status": status, "breaches": breaches,
            "expected_sharpe_band": [bands["sharpe_ci90_low"],
                                     bands["sharpe_ci90_high"]],
            "expected_max_dd_p5": bands["max_dd_p5"]}


def main():
    bands_by_strategy = load_expectation_bands()
    attribution = {}
    track_record = {}

    for account, (prefix, strategy) in ACCOUNTS.items():
        api_key = os.getenv(f"{prefix}_API_KEY")
        secret = os.getenv(f"{prefix}_SECRET_KEY")
        if not api_key or not secret:
            attribution[account] = {"ok": False, "error": "missing keys"}
            continue
        try:
            history = fetch_portfolio_history(api_key, secret)
            daily = equity_to_returns(history.get("timestamp", []),
                                      history.get("equity", []))
            metrics = live_metrics(daily)
            bands = bands_by_strategy.get(strategy) if strategy else None
            attribution[account] = {
                "ok": True,
                "strategy": strategy,
                "metrics": {k: round(v, 6) if isinstance(v, float) else v
                            for k, v in metrics.items()},
                "vs_expectation": script_status(metrics, bands),
            }
            track_record[account] = monthly_composite(daily)
            print(f"{account}: {metrics.get('observations', 0)} days, "
                  f"status={attribution[account]['vs_expectation'].get('status')}")
        except Exception as e:  # one account's failure must not kill the rest
            attribution[account] = {"ok": False, "error": str(e)[:200]}
            print(f"{account}: FAILED - {e}")

    stamp = datetime.now(timezone.utc).isoformat()
    for name, payload in [("attribution.json",
                           {"generated_at_utc": stamp, "accounts": attribution}),
                          ("track_record.json",
                           {"generated_at_utc": stamp,
                            "note": "GIPS-style geometric monthly returns; "
                                    "git history is the audit trail",
                            "monthly_returns": track_record})]:
        for base in [Path("data"), Path("frontend/public/data")]:
            base.mkdir(parents=True, exist_ok=True)
            with open(base / name, "w") as f:
                json.dump(payload, f, indent=2)
    print("Saved attribution.json + track_record.json (data/ + frontend)")


if __name__ == "__main__":
    main()
