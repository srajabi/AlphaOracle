#!/usr/bin/env python3
"""H2: is the simulated 3x trustworthy, and does the edge survive on real funds?

Finding 24's headline (daily+5% bands on 3x SPY -> 1474x vs buy-hold
337x) rests on a SIMULATED leveraged fund: daily-reset compounding of
SPY returns minus a flat 1.25%/yr drag. That is a model, and the whole
result depends on it.

Real LETFs only start around 2009-2010, so they cannot see dot-com or
the GFC - precisely the episodes that decide whether a leveraged
strategy is survivable. We cannot test the long window directly. What we
CAN do is the next best thing:

  STEP 1  measure how well the simulator tracks the real fund over the
          period where both exist
  STEP 2  run the actual strategy on real fund prices over that period
  STEP 3  only extend conclusions to the long window if step 1 shows the
          simulator is faithful

If the simulator drifts badly, the 1474x is an artefact of the model and
must not be quoted.

Pairs tested: UPRO/SPY (3x), TQQQ/QQQ (3x), SSO/SPY (2x).

Writes data/letf_validation.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.backtest_check_frequency import (  # noqa: E402
    LETF_ANNUAL_DRAG, build_signal, load, simulate,
)

OUT = Path("data/letf_validation.json")

PAIRS = [
    ("UPRO", "SPY", 3),
    ("TQQQ", "QQQ", 3),
    ("SSO", "SPY", 2),
]

# UPRO's stored history claims a 2000 start though the fund launched in
# 2009 (RULED_OUT.md). Clip every real series to a date we trust.
REAL_START = "2010-06-01"
END = "2026-03-31"
BAND = 0.05


def simulated_returns(underlying_ret, leverage, drag=LETF_ANNUAL_DRAG):
    daily_drag = (1 + drag) ** (1 / 252) - 1
    return underlying_ret * leverage - daily_drag


def compare(real_ret, sim_ret):
    joined = pd.concat([real_ret.rename("real"), sim_ret.rename("sim")],
                       axis=1).dropna()
    diff = joined["real"] - joined["sim"]
    real_cum = float((1 + joined["real"]).prod())
    sim_cum = float((1 + joined["sim"]).prod())
    years = len(joined) / 252
    return {
        "n_days": int(len(joined)),
        "start": str(joined.index.min().date()),
        "end": str(joined.index.max().date()),
        "daily_corr": float(joined["real"].corr(joined["sim"])),
        "tracking_error_pct_yr": float(diff.std() * np.sqrt(252) * 100),
        "real_cagr_pct": float((real_cum ** (1 / years) - 1) * 100),
        "sim_cagr_pct": float((sim_cum ** (1 / years) - 1) * 100),
        "cagr_gap_pp": float(((real_cum ** (1 / years))
                              - (sim_cum ** (1 / years))) * 100),
        "real_terminal_x": real_cum,
        "sim_terminal_x": sim_cum,
    }


def implied_drag(real_ret, underlying_ret, leverage):
    """The annual drag that would make the simulator match reality."""
    joined = pd.concat([real_ret.rename("real"),
                        underlying_ret.rename("u")], axis=1).dropna()
    residual = joined["real"] - joined["u"] * leverage
    return float(-residual.mean() * 252 * 100)


def strategy_on(returns, prices, band=BAND):
    sig = build_signal(prices, "daily", band)
    return simulate(returns, sig)


def main():
    results = {}
    for letf, underlying, leverage in PAIRS:
        try:
            real_px = load(letf).loc[REAL_START:END]
            und_px = load(underlying).loc[:END]
        except FileNotFoundError as exc:
            print(f"{letf}: {exc}")
            continue

        real_ret = real_px.pct_change().dropna()
        und_ret = und_px.pct_change().dropna()
        sim_ret = simulated_returns(und_ret, leverage).loc[REAL_START:END]

        fit = compare(real_ret, sim_ret)
        fit["implied_drag_pct_yr"] = implied_drag(
            real_ret, und_ret.loc[REAL_START:END], leverage)
        fit["assumed_drag_pct_yr"] = LETF_ANNUAL_DRAG * 100

        # Same strategy, real vs simulated series, identical signal
        # (built from the UNDERLYING in both cases, as the rule specifies).
        common = real_ret.index.intersection(sim_ret.index)
        fit["strategy_real"] = strategy_on(real_ret.loc[common], und_px)
        fit["strategy_sim"] = strategy_on(sim_ret.loc[common], und_px)
        fit["buyhold_real"] = simulate(
            real_ret.loc[common],
            pd.Series(True, index=common))

        results[letf] = fit

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("STEP 1 - does the simulator track the real fund?\n")
    print(f"{'fund':6}{'window':24}{'corr':>7}{'TE/yr':>8}"
          f"{'real CAGR':>11}{'sim CAGR':>10}{'gap':>8}")
    for letf, f in results.items():
        print(f"{letf:6}{f['start'] + ' - ' + f['end']:24}"
              f"{f['daily_corr']:>7.4f}{f['tracking_error_pct_yr']:>7.2f}%"
              f"{f['real_cagr_pct']:>10.2f}%{f['sim_cagr_pct']:>9.2f}%"
              f"{f['cagr_gap_pp']:>+7.2f}")

    print("\ndrag: assumed vs what the real fund actually charged")
    for letf, f in results.items():
        print(f"  {letf:6} assumed {f['assumed_drag_pct_yr']:.2f}%/yr   "
              f"implied {f['implied_drag_pct_yr']:.2f}%/yr")

    print("\nSTEP 2 - the strategy on REAL fund prices "
          f"(daily, {BAND:.0%} bands)\n")
    print(f"{'fund':6}{'real strat':>12}{'sim strat':>12}"
          f"{'real B&H':>11}{'strat maxDD':>13}{'B&H maxDD':>12}")
    for letf, f in results.items():
        sr, ss, bh = f["strategy_real"], f["strategy_sim"], f["buyhold_real"]
        print(f"{letf:6}{sr['terminal_x']:>11.2f}x{ss['terminal_x']:>11.2f}x"
              f"{bh['terminal_x']:>10.2f}x"
              f"{sr['max_drawdown_pct']:>12.1f}%"
              f"{bh['max_drawdown_pct']:>11.1f}%")

    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
