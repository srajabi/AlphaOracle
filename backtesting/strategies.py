import pandas as pd


def buy_and_hold(df: pd.DataFrame) -> pd.Series:
    return pd.Series(1.0, index=df.index, name="buy_and_hold")


def sma_trend_following(df: pd.DataFrame) -> pd.Series:
    fast = df["close"].rolling(20).mean()
    slow = df["close"].rolling(50).mean()
    return (fast > slow).astype(float).rename("sma_trend_following")


def rsi_mean_reversion(df: pd.DataFrame) -> pd.Series:
    delta = df["close"].diff()
    gains = delta.clip(lower=0).rolling(14).mean()
    losses = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gains / losses.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))

    signal = pd.Series(0.0, index=df.index)
    signal[rsi < 35] = 1.0
    signal[rsi > 65] = 0.0
    return signal.ffill().fillna(0.0).rename("rsi_mean_reversion")


def breakout_20d(df: pd.DataFrame) -> pd.Series:
    rolling_high = df["close"].rolling(20).max().shift(1)
    rolling_low = df["close"].rolling(10).min().shift(1)

    signal = pd.Series(0.0, index=df.index)
    signal[df["close"] > rolling_high] = 1.0
    signal[df["close"] < rolling_low] = 0.0
    return signal.ffill().fillna(0.0).rename("breakout_20d")


def sma_200_trend(df: pd.DataFrame) -> pd.Series:
    """Long when price closes above the 200-day SMA, cash below.

    Same rule the Account 2 forward test (TQQQ momentum) executes.
    """
    sma200 = df["close"].rolling(200).mean()
    return (df["close"] > sma200).astype(float).rename("sma_200_trend")


def sma_200_trend_bands(
    df: pd.DataFrame, upper_band: float = 0.05, lower_band: float = 0.03
) -> pd.Series:
    """200 SMA trend with asymmetric tolerance bands (Reddit LETF style).

    Enter when price > SMA200 * 1.05, exit when price < SMA200 * 0.97,
    hold otherwise. Cuts whipsaw trades versus the plain crossover.
    """
    close = df["close"]
    sma200 = close.rolling(200).mean()

    signal = pd.Series(float("nan"), index=df.index)
    signal[close > sma200 * (1 + upper_band)] = 1.0
    signal[close < sma200 * (1 - lower_band)] = 0.0
    signal[sma200.isna()] = 0.0
    return signal.ffill().fillna(0.0).rename("sma_200_trend_bands")


STRATEGIES = {
    "buy_and_hold": buy_and_hold,
    "sma_trend_following": sma_trend_following,
    "rsi_mean_reversion": rsi_mean_reversion,
    "breakout_20d": breakout_20d,
    "sma_200_trend": sma_200_trend,
    "sma_200_trend_bands": sma_200_trend_bands,
}
