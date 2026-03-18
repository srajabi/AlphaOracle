import pandas as pd


DEFAULT_RISK_ON = ["SPY", "QQQ", "XLE"]  # SPY is S&P 500 (33 years of history)
DEFAULT_DEFENSIVE = ["GLD", "TLT", "XLU"]


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
}
