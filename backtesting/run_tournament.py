#!/usr/bin/env python3
"""The Strategy Tournament: census -> gauntlet -> deep tests -> champions.

A pyramid every strategy must climb:

  STAGE 0 - CENSUS: every strategy in the codebase. Untestable ones are
            excluded WITH A STATED REASON (nothing silently dropped).
  STAGE 1 - GAUNTLET (all testable): uniform 21y universe; promotion gates:
            G1 bootstrap p5 Sharpe > 0      (the edge survives resampling)
            G2 deflated Sharpe prob >= 0.95 (survives multiple testing)
            G3 breakeven cost >= 25 bps     (survives real-world friction)
            G4 Sharpe >= 60/40 baseline     (beats doing nothing clever)
  STAGE 2 - DEEP TESTS (survivors only):
            D1 split-sample: Sharpe > 0 in BOTH halves of the window
            D2 crisis floor: worst of {GFC, COVID, 2022} total return > -35%
            D3 cost stress: Sharpe at 10 bps still >= 0.40
            D4 lag robustness: T+2 Sharpe drop < 0.30
            D5 gap risk: 15% overnight gap loss bounded above -50%
  STAGE 3 - CHAMPIONS: pass everything.

Single-asset strategies (STRATEGIES registry) are adapted as SPY weights so
they face the same universe and gates.

Output: backtesting/results_tournament/tournament.json + tournament.md
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtesting.engine import compute_weighted_returns
from backtesting.periods import MARKET_PERIODS
from backtesting.portfolio_strategies import PORTFOLIO_STRATEGIES, _empty_weights
from backtesting.run_backtests import load_price_matrix
from backtesting.strategies import STRATEGIES
from backtesting.validation import (
    bootstrap_metrics,
    cost_sensitivity,
    deflated_sharpe_ratio,
    gap_risk,
    lag_sensitivity,
    risk_report,
    sharpe_ratio,
    stationary_bootstrap_indices,
)

UNIVERSE = ["SPY", "QQQ", "TLT", "GLD", "XLE", "XLU", "EWA",
            "XLB", "XLF", "XLI", "XLK", "XLP", "XLV", "XLY"]
BASELINES = {"buy_hold_spy", "buy_hold_qqq", "equal_weight_buy_hold",
             "spy_tlt_60_40", "permanent_portfolio", "all_weather_lite",
             "sa_buy_and_hold"}
CRISES = ["gfc_bear", "covid_crash", "inflation_bear_2022"]

EXCLUDED = {
    "advanced_llm (dev account)": "live LLM decisions - no deterministic signal function to backtest",
    "llm_recommendations (account 1)": "live LLM decisions - no deterministic signal function to backtest",
    "entry strategies (lump sum/DCA/...)": "capital-deployment rules, not portfolios - tested in entry_strategies.py across start-date cohorts instead",
    "decumulation rules (4% + overlays)": "withdrawal framework - tested in entry_strategies.py --withdrawal-rate instead",
    "overnight/intraday legs": "need open prices; engine is close-to-close - tested in overnight_decomposition.py instead",
    "options/VRP strategies": "no historical chain data yet (awaiting user's data purchase)",
}


def single_asset_adapter(signal_fn):
    """Wrap a single-asset signal (df -> Series in [0,1]) as SPY weights."""
    def strategy(prices: pd.DataFrame) -> pd.DataFrame:
        weights = _empty_weights(prices)
        if "SPY" not in prices.columns:
            return weights
        df = pd.DataFrame({"close": prices["SPY"]})
        weights["SPY"] = signal_fn(df).clip(0.0, 1.0).reindex(prices.index).fillna(0.0)
        return weights
    return strategy


def crisis_slice_return(returns: pd.Series, period_name: str):
    start, end = MARKET_PERIODS[period_name]
    sliced = returns.loc[start:end]
    if len(sliced) < 10:
        return None
    return float((1.0 + sliced).prod() - 1.0)


def main():
    prices = load_price_matrix(UNIVERSE)
    asset_returns = prices.pct_change().fillna(0.0)
    n = len(prices)
    rng = np.random.default_rng(42)
    boot_idx = stationary_bootstrap_indices(n, 1000, 21, rng)

    # ---- Stage 0: census ----
    contenders = dict(PORTFOLIO_STRATEGIES)
    for name, fn in STRATEGIES.items():
        contenders[f"sa_{name}"] = single_asset_adapter(fn)
    census = sorted(contenders)
    print(f"STAGE 0 - census: {len(census)} testable strategies "
          f"({len(PORTFOLIO_STRATEGIES)} portfolio + {len(STRATEGIES)} single-asset adapters)")
    print(f"          excluded with reasons: {len(EXCLUDED)}")

    # 60/40 reference for gate G4
    ref_returns = compute_weighted_returns(
        prices, PORTFOLIO_STRATEGIES["spy_tlt_60_40"](prices), 0.0)
    ref_sharpe = sharpe_ratio(ref_returns)

    # ---- Stage 1: gauntlet ----
    rows = []
    returns_by_name = {}
    for name in census:
        weights = contenders[name](prices)
        if weights.abs().sum().sum() == 0:
            rows.append({"strategy": name, "stage": 0,
                         "fail_reasons": ["produces no positions on this universe"]})
            continue
        returns = compute_weighted_returns(prices, weights, 0.0)
        returns_by_name[name] = (weights, returns)
        rows.append({"strategy": name, "weights_ok": True})

    trial_sharpes = [sharpe_ratio(r, annualize=False)
                     for _, r in returns_by_name.values()]

    survivors_1 = []
    for row in rows:
        name = row["strategy"]
        if name not in returns_by_name:
            continue
        weights, returns = returns_by_name[name]
        boot = bootstrap_metrics(returns, indices=boot_idx)
        costs = cost_sensitivity(prices, weights)
        report = risk_report(returns, benchmark=asset_returns["SPY"])
        row.update(report)
        row["bootstrap_p5_sharpe"] = boot["sharpe"]["p5"]
        row["dsr_prob"] = deflated_sharpe_ratio(returns, trial_sharpes)
        row["breakeven_cost_bps"] = min(costs["breakeven_cost_bps"], 9999.0)
        row["sharpe_at_10bps"] = costs["sharpe_at_10bps"]
        row["is_baseline"] = name in BASELINES

        fails = []
        if boot["sharpe"]["p5"] <= 0:
            fails.append("G1 bootstrap p5 Sharpe <= 0")
        if row["dsr_prob"] < 0.95:
            fails.append(f"G2 DSR {row['dsr_prob']:.2f} < 0.95")
        if row["breakeven_cost_bps"] < 25:
            fails.append(f"G3 breakeven {row['breakeven_cost_bps']:.0f}bps < 25")
        if row["sharpe"] < ref_sharpe:
            fails.append(f"G4 sharpe {row['sharpe']:.2f} < 60/40's {ref_sharpe:.2f}")
        row["stage"] = 1 if fails else 2
        row["fail_reasons"] = fails
        if not fails and not row["is_baseline"]:
            survivors_1.append(name)

    print(f"\nSTAGE 1 - gauntlet: {len(survivors_1)} of "
          f"{len(returns_by_name)} promoted (baselines compete but aren't promoted)")

    # ---- Stage 2: deep tests on survivors ----
    champions = []
    for row in rows:
        name = row["strategy"]
        if name not in survivors_1:
            continue
        weights, returns = returns_by_name[name]
        fails = []

        half = len(returns) // 2
        s1 = sharpe_ratio(returns.iloc[:half])
        s2 = sharpe_ratio(returns.iloc[half:])
        row["sharpe_half1"], row["sharpe_half2"] = s1, s2
        if s1 <= 0 or s2 <= 0:
            fails.append(f"D1 split-sample ({s1:.2f} / {s2:.2f})")

        crisis_rets = {c: crisis_slice_return(returns, c) for c in CRISES}
        row["crisis_returns"] = {k: (round(v, 4) if v is not None else None)
                                 for k, v in crisis_rets.items()}
        worst = min(v for v in crisis_rets.values() if v is not None)
        if worst < -0.35:
            fails.append(f"D2 crisis floor (worst {worst:.0%} < -35%)")

        if row["sharpe_at_10bps"] < 0.40:
            fails.append(f"D3 cost stress (10bps Sharpe {row['sharpe_at_10bps']:.2f} < 0.40)")

        lag = lag_sensitivity(prices, weights)
        row["lag_sharpe_drop"] = lag["lag_sharpe_drop"]
        if lag["lag_sharpe_drop"] >= 0.30:
            fails.append(f"D4 lag fragility (drop {lag['lag_sharpe_drop']:.2f})")

        gap = gap_risk(weights, 0.15)
        row["gap_loss_15pct"] = gap
        if gap < -0.50:
            fails.append(f"D5 gap risk ({gap:.0%} on a 15% gap)")

        row["fail_reasons"] = fails
        row["stage"] = 3 if not fails else 2
        if not fails:
            champions.append(name)

    print(f"STAGE 2 - deep tests: {len(champions)} champions of {len(survivors_1)}")

    # ---- Output ----
    out_dir = Path("backtesting/results_tournament")
    out_dir.mkdir(parents=True, exist_ok=True)
    results = pd.DataFrame([r for r in rows if "sharpe" in r])
    results = results.sort_values(["stage", "sharpe"], ascending=[False, False])

    with open(out_dir / "tournament.json", "w") as f:
        json.dump({
            "universe": UNIVERSE,
            "window": [str(prices.index[0].date()), str(prices.index[-1].date())],
            "census_size": len(census),
            "excluded": EXCLUDED,
            "gates": {
                "stage1": ["G1 bootstrap p5 Sharpe > 0", "G2 DSR >= 0.95",
                           "G3 breakeven >= 25bps", "G4 Sharpe >= 60/40"],
                "stage2": ["D1 split-sample both halves > 0",
                           "D2 worst crisis > -35%", "D3 Sharpe@10bps >= 0.40",
                           "D4 lag drop < 0.30", "D5 gap loss > -50%"],
            },
            "stage1_survivors": survivors_1,
            "champions": champions,
            "results": json.loads(results.to_json(orient="records")),
        }, f, indent=2)

    # human-readable pyramid
    lines = [
        "# Strategy Tournament Results", "",
        f"Window {prices.index[0].date()} to {prices.index[-1].date()}, "
        f"universe of {len(UNIVERSE)} assets, zero-cost base runs.", "",
        "```",
        f"  CENSUS     {len(census)} testable  (+{len(EXCLUDED)} excluded with reasons)",
        f"  STAGE 1    {len(survivors_1)} promoted  (gates: bootstrap, DSR, cost, beat-60/40)",
        f"  STAGE 2    {len(champions)} champions (gates: split-sample, crisis floor, 10bps, lag, gap)",
        "```", "",
        "## Champions", "",
    ]
    for name in champions:
        r = next(x for x in rows if x["strategy"] == name)
        lines.append(
            f"- **{name}**: Sharpe {r['sharpe']:.2f} "
            f"(halves {r['sharpe_half1']:.2f}/{r['sharpe_half2']:.2f}), "
            f"CAGR {r['cagr']:.1%}, maxDD {r['max_dd']:.0%}, "
            f"breakeven {r['breakeven_cost_bps']:.0f}bps, "
            f"crises {r['crisis_returns']}")
    lines += ["", "## Fell at stage 2", ""]
    for r in rows:
        if r.get("stage") == 2 and r["strategy"] in survivors_1:
            lines.append(f"- {r['strategy']}: {'; '.join(r['fail_reasons'])}")
    lines += ["", "## Excluded (with reasons)", ""]
    for k, v in EXCLUDED.items():
        lines.append(f"- {k}: {v}")
    with open(out_dir / "tournament.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    print("\n=== CHAMPIONS ===")
    for c in champions:
        print(" ", c)
    print(f"\nSaved {out_dir}/tournament.json + tournament.md")


if __name__ == "__main__":
    main()
