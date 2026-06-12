import json
from pathlib import Path

import pandas as pd


DEFAULT_RISK_ON = ["SPY", "QQQ", "XLE"]  # SPY is S&P 500 (33 years of history)
DEFAULT_DEFENSIVE = ["GLD", "TLT", "XLU"]

_AUX_CACHE = {}


def _aux_close(ticker: str) -> pd.Series:
    """Close series for a non-investable signal input (e.g. ^VIX).

    Loaded directly from data/historical_long so it never enters the
    investable price matrix (keeps baselines clean).
    """
    if ticker not in _AUX_CACHE:
        path = Path("data/historical_long") / f"{ticker}.json"
        with open(path) as f:
            data = json.load(f)
        df = pd.DataFrame(data["prices"])
        series = pd.Series(df["close"].values, index=pd.to_datetime(df["date"]))
        _AUX_CACHE[ticker] = series.sort_index()
    return _AUX_CACHE[ticker]


def _vix_for(index: pd.Index) -> pd.Series:
    return _aux_close("^VIX").reindex(index).ffill()


def _monthly(weights: pd.DataFrame) -> pd.DataFrame:
    """Hold positions constant within each month (month-end signal).

    The engine applies weights with a 1-day shift, so the month-end signal
    trades on the first session of the next month - no lookahead.
    """
    month_ends = weights.groupby([weights.index.year, weights.index.month]).tail(1)
    out = pd.DataFrame(float("nan"), index=weights.index, columns=weights.columns)
    out.loc[month_ends.index] = month_ends
    return out.ffill().fillna(0.0)


def _mom_13612w(prices: pd.DataFrame) -> pd.DataFrame:
    """Keller's 13612W momentum: weighted avg of 1/3/6/12-month returns."""
    r1 = prices / prices.shift(21) - 1.0
    r3 = prices / prices.shift(63) - 1.0
    r6 = prices / prices.shift(126) - 1.0
    r12 = prices / prices.shift(252) - 1.0
    return (12 * r1 + 4 * r3 + 2 * r6 + 1 * r12) / 19.0


def _empty_weights(prices: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(0.0, index=prices.index, columns=prices.columns)


def top2_relative_strength_rotation(prices: pd.DataFrame) -> pd.DataFrame:
    lookback_returns = prices.pct_change(20)
    weights = _empty_weights(prices)

    for idx in prices.index:
        scores = lookback_returns.loc[idx].dropna().sort_values(ascending=False)
        winners = scores[scores > 0].head(2).index.tolist()
        if winners:
            weights.loc[idx, winners] = 1.0 / len(winners)
    return weights


def dual_momentum_rotation(prices: pd.DataFrame) -> pd.DataFrame:
    offensive = [ticker for ticker in ["SPY", "QQQ", "XLE"] if ticker in prices.columns]
    defensive = [ticker for ticker in DEFAULT_DEFENSIVE if ticker in prices.columns]
    lookback_returns = prices.pct_change(20)
    weights = _empty_weights(prices)

    for idx in prices.index:
        offensive_scores = lookback_returns.loc[idx, offensive].dropna().sort_values(ascending=False)
        defensive_scores = lookback_returns.loc[idx, defensive].dropna().sort_values(ascending=False)
        if not offensive_scores.empty and offensive_scores.iloc[0] > 0:
            winner = offensive_scores.index[0]
            weights.loc[idx, winner] = 1.0
        elif not defensive_scores.empty:
            winner = defensive_scores.index[0]
            weights.loc[idx, winner] = 1.0
    return weights


def regime_defensive_rotation(prices: pd.DataFrame) -> pd.DataFrame:
    """Original regime rotation without tolerance bands."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights

    spy = prices["SPY"]
    spy_sma50 = spy.rolling(50).mean()
    spy_mom20 = spy.pct_change(20)
    xle_mom20 = prices["XLE"].pct_change(20) if "XLE" in prices.columns else pd.Series(index=prices.index, dtype=float)

    risk_on = [ticker for ticker in DEFAULT_RISK_ON if ticker in prices.columns]
    defensive = [ticker for ticker in DEFAULT_DEFENSIVE if ticker in prices.columns]

    for idx in prices.index:
        if pd.isna(spy_sma50.loc[idx]) or pd.isna(spy_mom20.loc[idx]):
            continue
        risk_on_regime = spy.loc[idx] > spy_sma50.loc[idx] and spy_mom20.loc[idx] > 0
        if risk_on_regime:
            selected = []
            for ticker in risk_on:
                if ticker == "XLE":
                    if pd.notna(xle_mom20.loc[idx]) and xle_mom20.loc[idx] > 0:
                        selected.append(ticker)
                else:
                    selected.append(ticker)
            if selected:
                weights.loc[idx, selected] = 1.0 / len(selected)
        elif defensive:
            weights.loc[idx, defensive] = 1.0 / len(defensive)
    return weights


def regime_defensive_rotation_with_bands(
    prices: pd.DataFrame,
    upper_band: float = 0.05,
    lower_band: float = 0.03
) -> pd.DataFrame:
    """
    Regime rotation with tolerance bands to reduce whipsaws.

    Uses asymmetric bands (default 5% up / 3% down) inspired by Reddit LETF strategies.
    - To switch TO risk-on: Requires stronger signal (SPY > SMA * (1 + upper_band))
    - To switch TO defensive: Requires weaker signal (SPY < SMA * (1 - lower_band))

    This creates hysteresis that reduces false signals during sideways markets.
    """
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights

    spy = prices["SPY"]
    spy_sma50 = spy.rolling(50).mean()
    spy_mom20 = spy.pct_change(20)
    xle_mom20 = prices["XLE"].pct_change(20) if "XLE" in prices.columns else pd.Series(index=prices.index, dtype=float)

    risk_on = [ticker for ticker in DEFAULT_RISK_ON if ticker in prices.columns]
    defensive = [ticker for ticker in DEFAULT_DEFENSIVE if ticker in prices.columns]

    # Track current regime state
    current_regime = "DEFENSIVE"  # Start conservative

    for idx in prices.index:
        if pd.isna(spy_sma50.loc[idx]) or pd.isna(spy_mom20.loc[idx]):
            continue

        # Calculate distance from SMA
        sma_ratio = (spy.loc[idx] - spy_sma50.loc[idx]) / spy_sma50.loc[idx]

        # Asymmetric band logic
        if current_regime == "DEFENSIVE":
            # Require strong signal to switch to risk-on (5% above SMA + positive momentum)
            if sma_ratio > upper_band and spy_mom20.loc[idx] > 0:
                current_regime = "RISK_ON"
        else:  # current_regime == "RISK_ON"
            # Faster exit on weakness (3% below SMA OR negative momentum)
            if sma_ratio < -lower_band or spy_mom20.loc[idx] < -0.05:
                current_regime = "DEFENSIVE"

        # Allocate based on regime
        if current_regime == "RISK_ON":
            selected = []
            for ticker in risk_on:
                if ticker == "XLE":
                    if pd.notna(xle_mom20.loc[idx]) and xle_mom20.loc[idx] > 0:
                        selected.append(ticker)
                else:
                    selected.append(ticker)
            if selected:
                weights.loc[idx, selected] = 1.0 / len(selected)
        elif defensive:
            weights.loc[idx, defensive] = 1.0 / len(defensive)

    return weights


def reddit_200sma_tqqq(prices: pd.DataFrame, upper_band: float = 0.05, lower_band: float = 0.03) -> pd.DataFrame:
    """
    Reddit-style simple 200 SMA strategy with asymmetric bands.

    Buy signal: QQQ closes > 5% above 200 SMA → 100% TQQQ
    Sell signal: QQQ closes > 3% below 200 SMA → 100% cash

    This is the most popular retail LETF strategy, producing ~80% CAGR with only 13 trades over 25 years.

    Since we don't have TQQQ data historically, we simulate it as 3x QQQ.
    """
    weights = _empty_weights(prices)

    # This strategy only works if we have QQQ
    if "QQQ" not in prices.columns:
        return weights

    qqq = prices["QQQ"]
    qqq_sma200 = qqq.rolling(200).mean()

    # Track current position state
    in_position = False

    for idx in prices.index:
        if pd.isna(qqq_sma200.loc[idx]):
            continue

        # Calculate distance from 200 SMA
        sma_ratio = (qqq.loc[idx] - qqq_sma200.loc[idx]) / qqq_sma200.loc[idx]

        # Asymmetric band logic
        if not in_position:
            # Buy signal: 5% above 200 SMA
            if sma_ratio > upper_band:
                in_position = True
        else:
            # Sell signal: 3% below 200 SMA
            if sma_ratio < -lower_band:
                in_position = False

        # Allocate: 3x QQQ when in position, cash when out
        if in_position:
            weights.loc[idx, "QQQ"] = 3.0  # 3x leverage

    return weights


def reddit_200sma_spy(prices: pd.DataFrame, upper_band: float = 0.05, lower_band: float = 0.03) -> pd.DataFrame:
    """
    Reddit-style 200 SMA strategy for SPY → UPRO.

    Buy signal: SPY closes > 5% above 200 SMA → 100% UPRO (3x)
    Sell signal: SPY closes > 3% below 200 SMA → 100% cash
    """
    weights = _empty_weights(prices)

    if "SPY" not in prices.columns:
        return weights

    spy = prices["SPY"]
    spy_sma200 = spy.rolling(200).mean()

    in_position = False

    for idx in prices.index:
        if pd.isna(spy_sma200.loc[idx]):
            continue

        sma_ratio = (spy.loc[idx] - spy_sma200.loc[idx]) / spy_sma200.loc[idx]

        if not in_position:
            if sma_ratio > upper_band:
                in_position = True
        else:
            if sma_ratio < -lower_band:
                in_position = False

        if in_position:
            weights.loc[idx, "SPY"] = 3.0  # 3x leverage

    return weights


def regime_defensive_rotation_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """2x leveraged version of regime_defensive_rotation."""
    base_weights = regime_defensive_rotation(prices)
    return base_weights * 2.0


def regime_defensive_rotation_3x(prices: pd.DataFrame) -> pd.DataFrame:
    """3x leveraged version of regime_defensive_rotation."""
    base_weights = regime_defensive_rotation(prices)
    return base_weights * 3.0


def regime_defensive_rotation_with_bands_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """2x leveraged version of regime_defensive_rotation_with_bands."""
    base_weights = regime_defensive_rotation_with_bands(prices)
    return base_weights * 2.0


def regime_defensive_rotation_with_bands_3x(prices: pd.DataFrame) -> pd.DataFrame:
    """3x leveraged version of regime_defensive_rotation_with_bands."""
    base_weights = regime_defensive_rotation_with_bands(prices)
    return base_weights * 3.0


def dual_momentum_rotation_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """2x leveraged version of dual_momentum_rotation."""
    base_weights = dual_momentum_rotation(prices)
    return base_weights * 2.0


def dual_momentum_rotation_3x(prices: pd.DataFrame) -> pd.DataFrame:
    """3x leveraged version of dual_momentum_rotation."""
    base_weights = dual_momentum_rotation(prices)
    return base_weights * 3.0


def top2_relative_strength_rotation_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """2x leveraged version of top2_relative_strength_rotation."""
    base_weights = top2_relative_strength_rotation(prices)
    return base_weights * 2.0


def buy_hold_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Buy and hold SPY (1x leverage)."""
    weights = _empty_weights(prices)
    if "SPY" in prices.columns:
        weights["SPY"] = 1.0
    return weights


def buy_hold_spy_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """Buy and hold SPY with 2x leverage."""
    weights = _empty_weights(prices)
    if "SPY" in prices.columns:
        weights["SPY"] = 2.0
    return weights


def buy_hold_spy_3x(prices: pd.DataFrame) -> pd.DataFrame:
    """Buy and hold SPY with 3x leverage (equivalent to UPRO)."""
    weights = _empty_weights(prices)
    if "SPY" in prices.columns:
        weights["SPY"] = 3.0
    return weights


def buy_hold_qqq(prices: pd.DataFrame) -> pd.DataFrame:
    """Buy and hold QQQ (1x leverage)."""
    weights = _empty_weights(prices)
    if "QQQ" in prices.columns:
        weights["QQQ"] = 1.0
    return weights


def buy_hold_qqq_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """Buy and hold QQQ with 2x leverage."""
    weights = _empty_weights(prices)
    if "QQQ" in prices.columns:
        weights["QQQ"] = 2.0
    return weights


def buy_hold_qqq_3x(prices: pd.DataFrame) -> pd.DataFrame:
    """Buy and hold QQQ with 3x leverage (equivalent to TQQQ)."""
    weights = _empty_weights(prices)
    if "QQQ" in prices.columns:
        weights["QQQ"] = 3.0
    return weights


def hfea_55_45(prices: pd.DataFrame) -> pd.DataFrame:
    """HFEA (Hedgefundie's Excellent Adventure): 55/45 UPRO/TMF.

    Modeled as clean 3x leverage on SPY/TLT, daily rebalanced (the real
    strategy rebalances quarterly; daily-rebalanced constant weights are a
    close approximation). No expense ratio or financing drag - real 3x ETFs
    cost ~1% ER plus ~2x the short rate in financing, which is material.
    """
    weights = _empty_weights(prices)
    if "SPY" in prices.columns and "TLT" in prices.columns:
        weights["SPY"] = 0.55 * 3.0
        weights["TLT"] = 0.45 * 3.0
    return weights


def hfea_lite_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """HFEA at 2x leverage (SSO/UBT equivalent): 55/45 with half the risk."""
    weights = _empty_weights(prices)
    if "SPY" in prices.columns and "TLT" in prices.columns:
        weights["SPY"] = 0.55 * 2.0
        weights["TLT"] = 0.45 * 2.0
    return weights


def equal_weight_buy_hold(prices: pd.DataFrame) -> pd.DataFrame:
    """Equal-weight the full ticker universe, rebalanced daily.

    Baseline for rotation strategies: rotating between assets should beat
    simply holding all of them. Constant weights mean near-zero turnover
    after the initial entry, so this is an idealized (low-cost) benchmark.
    """
    n_assets = len(prices.columns)
    if n_assets == 0:
        return _empty_weights(prices)
    return pd.DataFrame(1.0 / n_assets, index=prices.index, columns=prices.columns)


def spy_tlt_60_40(prices: pd.DataFrame) -> pd.DataFrame:
    """Classic 60/40 stocks/bonds portfolio (SPY/TLT), rebalanced daily."""
    weights = _empty_weights(prices)
    if "SPY" in prices.columns and "TLT" in prices.columns:
        weights["SPY"] = 0.6
        weights["TLT"] = 0.4
    return weights


# ============================================================================
# STRATEGY LAB (2026-06): researched + brainstormed candidates targeting
# minimized drawdowns / maximized returns. Sources: Faber GTAA (10m SMA),
# Antonacci GEM, Keller VAA/DAA (13612W momentum + canary universe),
# vol-targeting literature, plus original hybrids.
# ============================================================================

# ---- Batch 1: trend / momentum (SPY-centric, longest history) ----

def golden_cross_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Long SPY when 50d SMA > 200d SMA, cash otherwise."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    fast = prices["SPY"].rolling(50).mean()
    slow = prices["SPY"].rolling(200).mean()
    weights["SPY"] = ((fast > slow) & slow.notna()).astype(float)
    return weights


def tsmom_12_1_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Time-series momentum: long SPY if 12-month return (skipping the most
    recent month) is positive. Monthly evaluation."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    mom = prices["SPY"].shift(21) / prices["SPY"].shift(252) - 1.0
    weights["SPY"] = (mom > 0).astype(float)
    return _monthly(weights)


def sma200_monthly_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Faber-style: SPY vs 200d SMA evaluated only at month-end.
    Cuts whipsaws vs the daily version."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    sma = prices["SPY"].rolling(200).mean()
    weights["SPY"] = ((prices["SPY"] > sma) & sma.notna()).astype(float)
    return _monthly(weights)


def mom_ensemble_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Exposure = fraction of positive {3m, 6m, 12m} momentum signals.
    Scales in/out gradually instead of binary switching."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    spy = prices["SPY"]
    signals = sum(
        (spy / spy.shift(n) - 1.0 > 0).astype(float) for n in (63, 126, 252)
    )
    valid = spy.shift(252).notna()
    weights["SPY"] = (signals / 3.0).where(valid, 0.0)
    return _monthly(weights)


def donchian_55_20_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Turtle-style channel: enter on a 55d high, exit on a 20d low."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    spy = prices["SPY"]
    hh55 = spy.rolling(55).max().shift(1)
    ll20 = spy.rolling(20).min().shift(1)
    signal = pd.Series(float("nan"), index=prices.index)
    signal[spy > hh55] = 1.0
    signal[spy < ll20] = 0.0
    weights["SPY"] = signal.ffill().fillna(0.0)
    return weights


def gem_dual_momentum(prices: pd.DataFrame) -> pd.DataFrame:
    """Antonacci GEM-lite: monthly, pick SPY vs EWA (intl proxy) by 12m
    relative momentum; if the winner's absolute momentum is negative,
    retreat to TLT."""
    weights = _empty_weights(prices)
    needed = [t for t in ("SPY", "EWA") if t in prices.columns]
    if "SPY" not in needed:
        return weights
    r12 = prices / prices.shift(252) - 1.0
    for idx in prices.index:
        scores = r12.loc[idx, needed].dropna()
        if scores.empty:
            continue
        winner = scores.idxmax()
        if scores[winner] > 0:
            weights.loc[idx, winner] = 1.0
        elif "TLT" in prices.columns and pd.notna(r12.loc[idx].get("TLT")):
            weights.loc[idx, "TLT"] = 1.0
    return _monthly(weights)


# ---- Batch 2: volatility-based ----

def vol_target_spy_15(prices: pd.DataFrame) -> pd.DataFrame:
    """Volatility targeting: SPY exposure = 15% target / realized 20d vol,
    capped at 1.5x. De-levers automatically in storms."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    vol = prices["SPY"].pct_change().rolling(20).std() * (252 ** 0.5)
    weights["SPY"] = (0.15 / vol).clip(0.0, 1.5).fillna(0.0)
    return weights


def vix_regime_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """VIX ladder: full SPY when 5d-median VIX < 20, half below 30, else cash."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    vix = _vix_for(prices.index).rolling(5).median()
    exposure = pd.Series(0.0, index=prices.index)
    exposure[vix < 30] = 0.5
    exposure[vix < 20] = 1.0
    weights["SPY"] = exposure.fillna(0.0)
    return weights


def vix_spike_buyer(prices: pd.DataFrame) -> pd.DataFrame:
    """Contrarian overlay: always hold SPY, lever to 1.5x while the 5d-median
    VIX is above 35 (panic premium harvesting)."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    vix = _vix_for(prices.index).rolling(5).median()
    weights["SPY"] = pd.Series(1.0, index=prices.index).where(vix <= 35, 1.5)
    return weights


def risk_parity_spy_tlt_gld(prices: pd.DataFrame) -> pd.DataFrame:
    """Unlevered risk parity: inverse 63d-vol weights across SPY/TLT/GLD."""
    weights = _empty_weights(prices)
    assets = [t for t in ("SPY", "TLT", "GLD") if t in prices.columns]
    if len(assets) < 2:
        return weights
    vol = prices[assets].pct_change().rolling(63).std()
    inv = (1.0 / vol).replace([float("inf")], float("nan"))
    norm = inv.div(inv.sum(axis=1), axis=0).fillna(0.0)
    for t in assets:
        weights[t] = norm[t]
    return _monthly(weights)


def target_dd_guard_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Drawdown brake: 100% SPY; cut to 50% beyond a 10% drawdown from the
    running peak, to cash beyond 15%. Re-enter fully only when SPY closes
    back above its 200d SMA."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    spy = prices["SPY"]
    sma200 = spy.rolling(200).mean()
    peak = spy.cummax()
    dd = spy / peak - 1.0
    exposure = []
    state = 1.0
    for idx in prices.index:
        if state > 0.0:
            if dd.loc[idx] <= -0.15:
                state = 0.0
            elif dd.loc[idx] <= -0.10:
                state = min(state, 0.5)
        if state < 1.0 and pd.notna(sma200.loc[idx]) and spy.loc[idx] > sma200.loc[idx]:
            state = 1.0
        exposure.append(state)
    weights["SPY"] = exposure
    return weights


def vol_target_qqq_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """Vol-managed leverage: QQQ exposure = 20% target / realized 20d vol,
    capped at 2x. Leverage only when markets are calm."""
    weights = _empty_weights(prices)
    if "QQQ" not in prices.columns:
        return weights
    vol = prices["QQQ"].pct_change().rolling(20).std() * (252 ** 0.5)
    weights["QQQ"] = (0.20 / vol).clip(0.0, 2.0).fillna(0.0)
    return weights


# ---- Batch 3: allocation / rotation ----

def permanent_portfolio(prices: pd.DataFrame) -> pd.DataFrame:
    """Browne's Permanent Portfolio: 25% each SPY/TLT/GLD, 25% cash."""
    weights = _empty_weights(prices)
    for t in ("SPY", "TLT", "GLD"):
        if t in prices.columns:
            weights[t] = 0.25
    return weights


def all_weather_lite(prices: pd.DataFrame) -> pd.DataFrame:
    """Dalio-inspired: 30 SPY / 40 TLT / 15 GLD / 7.5 XLE / 7.5 XLU."""
    weights = _empty_weights(prices)
    allocation = {"SPY": 0.30, "TLT": 0.40, "GLD": 0.15, "XLE": 0.075, "XLU": 0.075}
    for t, w in allocation.items():
        if t in prices.columns:
            weights[t] = w
    return weights


def gtaa_5_faber(prices: pd.DataFrame) -> pd.DataFrame:
    """Faber GTAA(5): 20% each in SPY/EWA/TLT/GLD/XLE, but a sleeve is held
    only while above its own 200d SMA at month-end (else cash)."""
    weights = _empty_weights(prices)
    assets = [t for t in ("SPY", "EWA", "TLT", "GLD", "XLE") if t in prices.columns]
    if not assets:
        return weights
    sma = prices[assets].rolling(200).mean()
    for t in assets:
        weights[t] = ((prices[t] > sma[t]) & sma[t].notna()).astype(float) * 0.20
    return _monthly(weights)


def sector_momentum_top3_filtered(prices: pd.DataFrame) -> pd.DataFrame:
    """Top-3 SPDR sectors by 6m momentum, each held only if above its own
    200d SMA (else that third stays in cash). Monthly."""
    weights = _empty_weights(prices)
    sectors = [t for t in ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY")
               if t in prices.columns]
    if len(sectors) < 3:
        return weights
    r6 = prices[sectors] / prices[sectors].shift(126) - 1.0
    sma = prices[sectors].rolling(200).mean()
    for idx in prices.index:
        scores = r6.loc[idx].dropna().sort_values(ascending=False)
        for t in scores.head(3).index:
            if pd.notna(sma.loc[idx, t]) and prices.loc[idx, t] > sma.loc[idx, t]:
                weights.loc[idx, t] = 1.0 / 3.0
    return _monthly(weights)


def spy_gld_switch(prices: pd.DataFrame) -> pd.DataFrame:
    """Hold SPY or GLD by 3m relative momentum, but only if the winner is
    above its own 200d SMA - else cash. Monthly."""
    weights = _empty_weights(prices)
    assets = [t for t in ("SPY", "GLD") if t in prices.columns]
    if len(assets) < 2:
        return weights
    r3 = prices[assets] / prices[assets].shift(63) - 1.0
    sma = prices[assets].rolling(200).mean()
    for idx in prices.index:
        scores = r3.loc[idx].dropna()
        if scores.empty:
            continue
        winner = scores.idxmax()
        if pd.notna(sma.loc[idx, winner]) and prices.loc[idx, winner] > sma.loc[idx, winner]:
            weights.loc[idx, winner] = 1.0
    return _monthly(weights)


def keller_vaa_lite(prices: pd.DataFrame) -> pd.DataFrame:
    """Keller VAA adapted to available data: offensive {SPY, EWA, VGK},
    defensive {TLT, GLD}. If ANY offensive 13612W momentum is negative,
    hold the best defensive asset; else hold the best offensive. Monthly."""
    weights = _empty_weights(prices)
    offense = [t for t in ("SPY", "EWA", "VGK") if t in prices.columns]
    defense = [t for t in ("TLT", "GLD") if t in prices.columns]
    if not offense or not defense:
        return weights
    mom = _mom_13612w(prices)
    for idx in prices.index:
        off_scores = mom.loc[idx, offense].dropna()
        def_scores = mom.loc[idx, defense].dropna()
        if len(off_scores) < len(offense) or def_scores.empty:
            continue
        if (off_scores < 0).any():
            weights.loc[idx, def_scores.idxmax()] = 1.0
        else:
            weights.loc[idx, off_scores.idxmax()] = 1.0
    return _monthly(weights)


def canary_daa_lite(prices: pd.DataFrame) -> pd.DataFrame:
    """Keller DAA-lite: canary basket {EWA, TLT} 13612W momentum decides the
    cash fraction (0/50/100%); the risky half goes to the top-2 of
    {SPY, QQQ, GLD, XLE} by momentum; the defensive fraction to TLT. Monthly."""
    weights = _empty_weights(prices)
    canary = [t for t in ("EWA", "TLT") if t in prices.columns]
    risky = [t for t in ("SPY", "QQQ", "GLD", "XLE") if t in prices.columns]
    if len(canary) < 2 or len(risky) < 2 or "TLT" not in prices.columns:
        return weights
    mom = _mom_13612w(prices)
    for idx in prices.index:
        canary_scores = mom.loc[idx, canary].dropna()
        risky_scores = mom.loc[idx, risky].dropna()
        if len(canary_scores) < 2 or len(risky_scores) < 2:
            continue
        cash_frac = (canary_scores < 0).sum() / 2.0
        risk_frac = 1.0 - cash_frac
        if risk_frac > 0:
            for t in risky_scores.sort_values(ascending=False).head(2).index:
                weights.loc[idx, t] = risk_frac / 2.0
        if cash_frac > 0:
            weights.loc[idx, "TLT"] += cash_frac
    return _monthly(weights)


# ---- Batch 4: overlays / hybrids (original combinations) ----

def composite_regime_spy(prices: pd.DataFrame) -> pd.DataFrame:
    """Graded exposure = score/3 of: SPY above 200d SMA, 3m momentum
    positive, 5d-median VIX below 25."""
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    spy = prices["SPY"]
    sma200 = spy.rolling(200).mean()
    r3 = spy / spy.shift(63) - 1.0
    vix = _vix_for(prices.index).rolling(5).median()
    score = (
        ((spy > sma200) & sma200.notna()).astype(float)
        + (r3 > 0).astype(float)
        + (vix < 25).astype(float)
    )
    weights["SPY"] = (score / 3.0).where(sma200.notna(), 0.0)
    return weights


def trinity_blend(prices: pd.DataFrame) -> pd.DataFrame:
    """50% buy-and-hold SPY core + 50% GTAA(5) tactical sleeve."""
    weights = gtaa_5_faber(prices) * 0.5
    if "SPY" in prices.columns:
        weights["SPY"] = weights["SPY"] + 0.5
    return weights


def tqqq_sma_vix_filter(prices: pd.DataFrame) -> pd.DataFrame:
    """Leverage laddering: 3x QQQ when above 200d SMA and 5d-median VIX < 30,
    1x when above SMA but VIX elevated, cash below the SMA."""
    weights = _empty_weights(prices)
    if "QQQ" not in prices.columns:
        return weights
    qqq = prices["QQQ"]
    sma200 = qqq.rolling(200).mean()
    vix = _vix_for(prices.index).rolling(5).median()
    above = (qqq > sma200) & sma200.notna()
    exposure = pd.Series(0.0, index=prices.index)
    exposure[above & (vix >= 30)] = 1.0
    exposure[above & (vix < 30)] = 3.0
    weights["QQQ"] = exposure
    return weights


def dd_guard_qqq_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """2x QQQ with a drawdown brake: de-lever to 1x beyond a 10% drawdown,
    cash beyond 20%; restore 2x when QQQ closes above its 200d SMA."""
    weights = _empty_weights(prices)
    if "QQQ" not in prices.columns:
        return weights
    qqq = prices["QQQ"]
    sma200 = qqq.rolling(200).mean()
    dd = qqq / qqq.cummax() - 1.0
    exposure = []
    state = 2.0
    for idx in prices.index:
        if state > 0.0:
            if dd.loc[idx] <= -0.20:
                state = 0.0
            elif dd.loc[idx] <= -0.10:
                state = min(state, 1.0)
        if state < 2.0 and pd.notna(sma200.loc[idx]) and qqq.loc[idx] > sma200.loc[idx]:
            state = 2.0
        exposure.append(state)
    weights["QQQ"] = exposure
    return weights


# ---- Round 4: strategies from the papers library ----

def dual_channel_cash_overlay(prices: pd.DataFrame) -> pd.DataFrame:
    """Xiong (2026, papers/cash_overlay_filters.md): a 50/50 growth/defensive
    sleeve with TWO continuous cash channels combined by max():

    - slow channel: scales to cash as the sleeve's trailing 12m Sharpe
      deteriorates below a threshold,
    - fast channel (crash brake): scales to cash proportionally to the
      sleeve's drawdown beyond -5%, releasing on recovery.

    Tested on 2004+ (through GFC) rather than the paper's 2017+ window.
    """
    weights = _empty_weights(prices)
    growth = [t for t in ("SPY", "QQQ") if t in prices.columns]
    defensive = [t for t in ("TLT", "GLD") if t in prices.columns]
    if not growth or not defensive:
        return weights

    base = _empty_weights(prices)
    for t in growth:
        base[t] = 0.5 / len(growth)
    for t in defensive:
        base[t] = 0.5 / len(defensive)

    sleeve_returns = (prices.pct_change().fillna(0.0) * base.shift(1)).sum(axis=1)

    # slow channel: trailing 252d Sharpe mapped to cash fraction
    mu = sleeve_returns.rolling(252).mean()
    sd = sleeve_returns.rolling(252).std()
    trailing_sharpe = (mu / sd * (252 ** 0.5)).fillna(1.0)
    slow_cash = ((0.5 - trailing_sharpe) / 1.0).clip(0.0, 1.0)

    # fast channel: sleeve drawdown beyond -5% scales linearly to full cash
    # at -20%
    equity = (1.0 + sleeve_returns).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    fast_cash = ((-drawdown - 0.05) / 0.15).clip(0.0, 1.0)

    invested = 1.0 - pd.concat([slow_cash, fast_cash], axis=1).max(axis=1)
    return base.mul(invested, axis=0)


def changepoint_gated_momentum(prices: pd.DataFrame) -> pd.DataFrame:
    """Wood/Roberts/Zohren (2021, papers/slow_momentum_fast_reversion.md),
    simplified without the deep-learning layer: follow the 200d SMA trend on
    SPY, but when a volatility changepoint fires (20d realized vol more than
    doubles its 100d median), cut exposure in half for the gate's duration.
    Targets trend's known weakness: fast regime turns.
    """
    weights = _empty_weights(prices)
    if "SPY" not in prices.columns:
        return weights
    spy = prices["SPY"]
    sma200 = spy.rolling(200).mean()
    trend = ((spy > sma200) & sma200.notna()).astype(float)

    vol_fast = spy.pct_change().rolling(20).std()
    vol_slow = vol_fast.rolling(100).median()
    changepoint = (vol_fast > 2.0 * vol_slow).fillna(False)

    exposure = trend.where(~changepoint, trend * 0.5)
    weights["SPY"] = exposure
    return weights


def low_vol_sector_basket(prices: pd.DataFrame) -> pd.DataFrame:
    """Blitz & van Vliet (2007, papers/volatility_effect_low_vol.md):
    inverse-volatility weighted basket of the 9 SPDR sectors, monthly -
    a retail-implementable low-vol equity tilt."""
    weights = _empty_weights(prices)
    sectors = [t for t in ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU",
                           "XLV", "XLY") if t in prices.columns]
    if len(sectors) < 3:
        return weights
    vol = prices[sectors].pct_change().rolling(63).std()
    inv = (1.0 / vol).replace([float("inf")], float("nan"))
    norm = inv.div(inv.sum(axis=1), axis=0).fillna(0.0)
    for t in sectors:
        weights[t] = norm[t]
    return _monthly(weights)


def canary_daa_low_vol_sleeve(prices: pd.DataFrame) -> pd.DataFrame:
    """Hybrid: canary DAA risk switching, but the risky sleeve is the
    inverse-vol sector basket instead of top-2 momentum assets."""
    weights = _empty_weights(prices)
    canary = [t for t in ("EWA", "TLT") if t in prices.columns]
    sectors = [t for t in ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU",
                           "XLV", "XLY") if t in prices.columns]
    defensive = [t for t in ("TLT", "GLD") if t in prices.columns]
    if len(canary) < 2 or len(sectors) < 3 or not defensive:
        return weights

    sleeve = low_vol_sector_basket(prices)
    mom = _mom_13612w(prices)
    canary_neg = (mom[canary] < 0).sum(axis=1)
    cash_frac = _monthly(pd.DataFrame({"x": canary_neg / 2.0},
                                      index=prices.index))["x"]
    risk_frac = 1.0 - cash_frac

    out = sleeve.mul(risk_frac, axis=0)
    def_scores = mom[defensive]
    for idx in prices.index:
        cf = cash_frac.loc[idx]
        if cf > 0:
            scores = def_scores.loc[idx].dropna()
            if not scores.empty and scores.max() > 0:
                out.loc[idx, scores.idxmax()] += cf
    return out


# ---- Round 2: hybrids of the round-1 winners ----

def canary_daa_2x(prices: pd.DataFrame) -> pd.DataFrame:
    """canary_daa_lite with a 1.5x levered risky sleeve when BOTH canary
    assets are positive (full risk-on confirmation), 1x otherwise."""
    base = canary_daa_lite(prices)
    canary = [t for t in ("EWA", "TLT") if t in prices.columns]
    if len(canary) < 2:
        return base
    mom = _mom_13612w(prices)
    both_positive = (mom[canary] > 0).all(axis=1)
    risky_cols = [t for t in ("SPY", "QQQ", "GLD", "XLE") if t in prices.columns]
    lever = _monthly(pd.DataFrame({"x": both_positive.astype(float)},
                                  index=prices.index))["x"]
    scale = 1.0 + 0.5 * lever
    out = base.copy()
    for t in risky_cols:
        out[t] = base[t] * scale
    return out


def canary_daa_vol_target(prices: pd.DataFrame) -> pd.DataFrame:
    """canary_daa_lite with the risky sleeve scaled by a 15% vol target
    (estimated from the sleeve's own 63d realized vol), capped at 1.25x."""
    base = canary_daa_lite(prices)
    risky_cols = [t for t in ("SPY", "QQQ", "GLD", "XLE") if t in prices.columns]
    if not risky_cols:
        return base
    sleeve_returns = (prices[risky_cols].pct_change() * base[risky_cols].shift(1)).sum(axis=1)
    vol = sleeve_returns.rolling(63).std() * (252 ** 0.5)
    scale = (0.15 / vol).clip(0.0, 1.25).fillna(1.0)
    out = base.copy()
    for t in risky_cols:
        out[t] = base[t] * scale
    return out


def canary_daa_smart_defense(prices: pd.DataFrame) -> pd.DataFrame:
    """canary_daa_lite, but the defensive fraction goes to the better of
    TLT/GLD by 13612W momentum - and to CASH if both are negative.
    Fixes the 2022 failure mode where the TLT 'safe' asset crashed too."""
    weights = _empty_weights(prices)
    canary = [t for t in ("EWA", "TLT") if t in prices.columns]
    risky = [t for t in ("SPY", "QQQ", "GLD", "XLE") if t in prices.columns]
    defensive = [t for t in ("TLT", "GLD") if t in prices.columns]
    if len(canary) < 2 or len(risky) < 2 or not defensive:
        return weights
    mom = _mom_13612w(prices)
    for idx in prices.index:
        canary_scores = mom.loc[idx, canary].dropna()
        risky_scores = mom.loc[idx, risky].dropna()
        if len(canary_scores) < 2 or len(risky_scores) < 2:
            continue
        cash_frac = (canary_scores < 0).sum() / 2.0
        risk_frac = 1.0 - cash_frac
        if risk_frac > 0:
            for t in risky_scores.sort_values(ascending=False).head(2).index:
                weights.loc[idx, t] = risk_frac / 2.0
        if cash_frac > 0:
            def_scores = mom.loc[idx, defensive].dropna()
            if not def_scores.empty and def_scores.max() > 0:
                weights.loc[idx, def_scores.idxmax()] += cash_frac
            # else: stay in actual cash for the defensive fraction
    return _monthly(weights)


def lab_winners_blend(prices: pd.DataFrame) -> pd.DataFrame:
    """40% canary DAA + 30% risk parity + 30% monthly SMA200 SPY.
    Three uncorrelated decision engines in one portfolio."""
    return (
        canary_daa_lite(prices) * 0.40
        + risk_parity_spy_tlt_gld(prices) * 0.30
        + sma200_monthly_spy(prices) * 0.30
    )


PORTFOLIO_STRATEGIES = {
    "top2_relative_strength_rotation": top2_relative_strength_rotation,
    "dual_momentum_rotation": dual_momentum_rotation,
    "regime_defensive_rotation": regime_defensive_rotation,
    "regime_defensive_rotation_2x": regime_defensive_rotation_2x,
    "regime_defensive_rotation_3x": regime_defensive_rotation_3x,
    "regime_defensive_rotation_with_bands": regime_defensive_rotation_with_bands,
    "regime_defensive_rotation_with_bands_2x": regime_defensive_rotation_with_bands_2x,
    "regime_defensive_rotation_with_bands_3x": regime_defensive_rotation_with_bands_3x,
    "dual_momentum_rotation_2x": dual_momentum_rotation_2x,
    "dual_momentum_rotation_3x": dual_momentum_rotation_3x,
    "top2_relative_strength_rotation_2x": top2_relative_strength_rotation_2x,
    "reddit_200sma_tqqq": reddit_200sma_tqqq,
    "reddit_200sma_spy": reddit_200sma_spy,
    "buy_hold_spy": buy_hold_spy,
    "buy_hold_spy_2x": buy_hold_spy_2x,
    "buy_hold_spy_3x": buy_hold_spy_3x,
    "buy_hold_qqq": buy_hold_qqq,
    "buy_hold_qqq_2x": buy_hold_qqq_2x,
    "buy_hold_qqq_3x": buy_hold_qqq_3x,
    "equal_weight_buy_hold": equal_weight_buy_hold,
    "spy_tlt_60_40": spy_tlt_60_40,
    "hfea_55_45": hfea_55_45,
    "hfea_lite_2x": hfea_lite_2x,
    # Strategy lab (2026-06)
    "golden_cross_spy": golden_cross_spy,
    "tsmom_12_1_spy": tsmom_12_1_spy,
    "sma200_monthly_spy": sma200_monthly_spy,
    "mom_ensemble_spy": mom_ensemble_spy,
    "donchian_55_20_spy": donchian_55_20_spy,
    "gem_dual_momentum": gem_dual_momentum,
    "vol_target_spy_15": vol_target_spy_15,
    "vix_regime_spy": vix_regime_spy,
    "vix_spike_buyer": vix_spike_buyer,
    "risk_parity_spy_tlt_gld": risk_parity_spy_tlt_gld,
    "target_dd_guard_spy": target_dd_guard_spy,
    "vol_target_qqq_2x": vol_target_qqq_2x,
    "permanent_portfolio": permanent_portfolio,
    "all_weather_lite": all_weather_lite,
    "gtaa_5_faber": gtaa_5_faber,
    "sector_momentum_top3_filtered": sector_momentum_top3_filtered,
    "spy_gld_switch": spy_gld_switch,
    "keller_vaa_lite": keller_vaa_lite,
    "canary_daa_lite": canary_daa_lite,
    "composite_regime_spy": composite_regime_spy,
    "trinity_blend": trinity_blend,
    "tqqq_sma_vix_filter": tqqq_sma_vix_filter,
    "dd_guard_qqq_2x": dd_guard_qqq_2x,
    "canary_daa_2x": canary_daa_2x,
    "canary_daa_vol_target": canary_daa_vol_target,
    "canary_daa_smart_defense": canary_daa_smart_defense,
    "lab_winners_blend": lab_winners_blend,
    # Round 4 (papers library)
    "dual_channel_cash_overlay": dual_channel_cash_overlay,
    "changepoint_gated_momentum": changepoint_gated_momentum,
    "low_vol_sector_basket": low_vol_sector_basket,
    "canary_daa_low_vol_sleeve": canary_daa_low_vol_sleeve,
}
