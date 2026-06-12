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

# Two mandates, two gate sets - same statistical rigor, different risk
# preferences. High volatility is allowed in the aggressive division as
# long as it is COMPENSATED (must beat SPY on both CAGR and Sharpe) and
# SURVIVABLE (no wipeouts, recovers within a market cycle).
DIVISIONS = {
    "core": {  # holdable money: parents, retirement, the 75%
        "reference": "spy_tlt_60_40",
        "ref_metric": "sharpe",
        "crisis_floor": -0.35,
        "cost_stress_min": 0.40,
        "gap_floor": -0.50,
        "max_underwater_days": None,
    },
    "aggressive": {  # the 25% sleeve: growth first, ruin still forbidden
        "reference": "buy_hold_spy",
        "ref_metric": "cagr_and_sharpe",   # must dominate SPY on both
        "crisis_floor": -0.60,             # excludes wipeouts, not vol
        "cost_stress_min": 0.30,
        "gap_floor": -0.60,                # ~allows 2x-3x with caps
        "max_underwater_days": 1260,       # must recover within ~5 years
    },
}

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

    # division references
    refs = {}
    for div, cfg in DIVISIONS.items():
        r = compute_weighted_returns(
            prices, PORTFOLIO_STRATEGIES[cfg["reference"]](prices), 0.0)
        refs[div] = risk_report(r)

    # ---- compute all metrics once per strategy ----
    rows = []
    returns_by_name = {}
    for name in census:
        weights = contenders[name](prices)
        if weights.abs().sum().sum() == 0:
            rows.append({"strategy": name, "stage": 0,
                         "fail_reasons": {"all": ["produces no positions on this universe"]}})
            continue
        returns = compute_weighted_returns(prices, weights, 0.0)
        returns_by_name[name] = (weights, returns)
        rows.append({"strategy": name})

    trial_sharpes = [sharpe_ratio(r, annualize=False)
                     for _, r in returns_by_name.values()]

    for row in rows:
        name = row["strategy"]
        if name not in returns_by_name:
            continue
        weights, returns = returns_by_name[name]
        boot = bootstrap_metrics(returns, indices=boot_idx)
        costs = cost_sensitivity(prices, weights)
        lag = lag_sensitivity(prices, weights)
        row.update(risk_report(returns, benchmark=asset_returns["SPY"]))
        row["bootstrap_p5_sharpe"] = boot["sharpe"]["p5"]
        row["dsr_prob"] = deflated_sharpe_ratio(returns, trial_sharpes)
        row["breakeven_cost_bps"] = min(costs["breakeven_cost_bps"], 9999.0)
        row["sharpe_at_10bps"] = costs["sharpe_at_10bps"]
        row["lag_sharpe_drop"] = lag["lag_sharpe_drop"]
        row["gap_loss_15pct"] = gap_risk(weights, 0.15)
        row["is_baseline"] = name in BASELINES
        half = len(returns) // 2
        row["sharpe_half1"] = sharpe_ratio(returns.iloc[:half])
        row["sharpe_half2"] = sharpe_ratio(returns.iloc[half:])
        crisis_rets = {c: crisis_slice_return(returns, c) for c in CRISES}
        row["crisis_returns"] = {k: (round(v, 4) if v is not None else None)
                                 for k, v in crisis_rets.items()}
        row["worst_crisis"] = min(v for v in crisis_rets.values() if v is not None)

    # ---- apply division gates ----
    survivors_1 = {div: [] for div in DIVISIONS}
    champions = {div: [] for div in DIVISIONS}
    for row in rows:
        name = row["strategy"]
        if name not in returns_by_name:
            continue
        row["fail_reasons"] = {}
        row["division_result"] = {}
        for div, cfg in DIVISIONS.items():
            ref = refs[div]
            fails = []
            # Stage 1: statistical reality + cost + beat-the-reference
            if row["bootstrap_p5_sharpe"] <= 0:
                fails.append("G1 bootstrap p5 Sharpe <= 0")
            if row["dsr_prob"] < 0.95:
                fails.append(f"G2 DSR {row['dsr_prob']:.2f} < 0.95")
            if row["breakeven_cost_bps"] < 25:
                fails.append(f"G3 breakeven {row['breakeven_cost_bps']:.0f}bps < 25")
            if cfg["ref_metric"] == "sharpe":
                if row["sharpe"] < ref["sharpe"]:
                    fails.append(f"G4 sharpe {row['sharpe']:.2f} < ref {ref['sharpe']:.2f}")
            else:  # cagr_and_sharpe: must dominate SPY on both
                if row["cagr"] <= ref["cagr"] or row["sharpe"] <= ref["sharpe"]:
                    fails.append(
                        f"G4 must beat SPY on CAGR AND Sharpe "
                        f"({row['cagr']:.1%}/{row['sharpe']:.2f} vs "
                        f"{ref['cagr']:.1%}/{ref['sharpe']:.2f})")
            stage1_pass = not fails
            if stage1_pass and not row["is_baseline"]:
                survivors_1[div].append(name)
                # Stage 2: division-specific survivability
                if row["sharpe_half1"] <= 0 or row["sharpe_half2"] <= 0:
                    fails.append(f"D1 split-sample ({row['sharpe_half1']:.2f}/"
                                 f"{row['sharpe_half2']:.2f})")
                if row["worst_crisis"] < cfg["crisis_floor"]:
                    fails.append(f"D2 crisis floor (worst {row['worst_crisis']:.0%}"
                                 f" < {cfg['crisis_floor']:.0%})")
                if row["sharpe_at_10bps"] < cfg["cost_stress_min"]:
                    fails.append(f"D3 cost stress ({row['sharpe_at_10bps']:.2f}"
                                 f" < {cfg['cost_stress_min']})")
                if row["lag_sharpe_drop"] >= 0.30:
                    fails.append(f"D4 lag fragility ({row['lag_sharpe_drop']:.2f})")
                if row["gap_loss_15pct"] < cfg["gap_floor"]:
                    fails.append(f"D5 gap risk ({row['gap_loss_15pct']:.0%})")
                if (cfg["max_underwater_days"] is not None
                        and row["max_dd_duration_days"] > cfg["max_underwater_days"]):
                    fails.append(f"D6 underwater {row['max_dd_duration_days']}d"
                                 f" > {cfg['max_underwater_days']}d")
                if not fails:
                    champions[div].append(name)
            row["fail_reasons"][div] = fails
            row["division_result"][div] = (
                "champion" if name in champions[div]
                else "stage2_fail" if stage1_pass and not row["is_baseline"]
                else "baseline" if row["is_baseline"]
                else "stage1_fail")

    for div in DIVISIONS:
        print(f"\n[{div.upper()}] stage 1: {len(survivors_1[div])} promoted; "
              f"champions: {len(champions[div])}")
        for c in sorted(champions[div]):
            print(f"   {c}")

    # ---- Output ----
    out_dir = Path("backtesting/results_tournament")
    out_dir.mkdir(parents=True, exist_ok=True)
    results = pd.DataFrame([r for r in rows if "sharpe" in r])
    results = results.sort_values("sharpe", ascending=False)

    with open(out_dir / "tournament.json", "w") as f:
        json.dump({
            "universe": UNIVERSE,
            "window": [str(prices.index[0].date()), str(prices.index[-1].date())],
            "census_size": len(census),
            "excluded": EXCLUDED,
            "divisions": {k: {kk: vv for kk, vv in v.items()}
                          for k, v in DIVISIONS.items()},
            "stage1_survivors": survivors_1,
            "champions": champions,
            "results": json.loads(results.to_json(orient="records")),
        }, f, indent=2)

    lines = [
        "# Strategy Tournament Results", "",
        f"Window {prices.index[0].date()} to {prices.index[-1].date()}, "
        f"universe of {len(UNIVERSE)} assets, zero-cost base runs.",
        "",
        f"Census: {len(census)} testable (+{len(EXCLUDED)} excluded with "
        "reasons). Two divisions - same statistical gates, different risk "
        "mandates: CORE (holdable: crisis floor -35%) and AGGRESSIVE "
        "(growth: must beat SPY on CAGR AND Sharpe; crisis floor -60%; "
        "must recover within ~5y).", "",
    ]
    for div in DIVISIONS:
        lines += [f"## {div.upper()} division - "
                  f"{len(champions[div])} champions "
                  f"(of {len(survivors_1[div])} stage-1 survivors)", ""]
        for name in sorted(champions[div]):
            r = next(x for x in rows if x["strategy"] == name)
            lines.append(
                f"- **{name}**: CAGR {r['cagr']:.1%}, Sharpe {r['sharpe']:.2f} "
                f"(halves {r['sharpe_half1']:.2f}/{r['sharpe_half2']:.2f}), "
                f"maxDD {r['max_dd']:.0%}, worst crisis {r['worst_crisis']:.0%}, "
                f"breakeven {r['breakeven_cost_bps']:.0f}bps")
        lines += ["", f"### Fell at stage 2 ({div})", ""]
        for r in rows:
            if r.get("division_result", {}).get(div) == "stage2_fail":
                lines.append(f"- {r['strategy']}: "
                             f"{'; '.join(r['fail_reasons'][div])}")
        lines.append("")
    lines += ["## Excluded (with reasons)", ""]
    for k, v in EXCLUDED.items():
        lines.append(f"- {k}: {v}")
    with open(out_dir / "tournament.md", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nSaved {out_dir}/tournament.json + tournament.md")


if __name__ == "__main__":
    main()
