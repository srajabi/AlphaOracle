import math
from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestResult:
    strategy: str
    ticker: str
    period: str
    observations: int
    trades: int
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe: float
    max_drawdown: float
    win_rate: float
    tax_adjusted_return: float = None  # Total return after taxes
    tax_adjusted_annualized: float = None  # Annualized return after taxes
    tax_adjusted_sharpe: float = None  # Sharpe ratio after taxes
    total_taxes_paid: float = None  # Total taxes paid as % of gains

    def to_dict(self):
        result = {
            "strategy": self.strategy,
            "ticker": self.ticker,
            "period": self.period,
            "observations": self.observations,
            "trades": self.trades,
            "total_return": round(self.total_return, 6),
            "annualized_return": round(self.annualized_return, 6),
            "annualized_volatility": round(self.annualized_volatility, 6),
            "sharpe": round(self.sharpe, 6),
            "max_drawdown": round(self.max_drawdown, 6),
            "win_rate": round(self.win_rate, 6),
        }
        if self.tax_adjusted_return is not None:
            result["tax_adjusted_return"] = round(self.tax_adjusted_return, 6)
            result["tax_adjusted_annualized"] = round(self.tax_adjusted_annualized, 6)
            result["tax_adjusted_sharpe"] = round(self.tax_adjusted_sharpe, 6)
            result["total_taxes_paid"] = round(self.total_taxes_paid, 6)
        return result


def run_backtest(
    df: pd.DataFrame,
    strategy_name: str,
    signal: pd.Series,
    transaction_cost_bps: float,
    period_name: str,
) -> BacktestResult:
    prices = df["close"].astype(float)
    asset_returns = prices.pct_change().fillna(0.0)

    position = signal.fillna(0.0).clip(-1.0, 1.0)
    applied_position = position.shift(1).fillna(0.0)
    turnover = position.diff().abs().fillna(position.abs())
    transaction_cost = turnover * (transaction_cost_bps / 10000.0)

    strategy_returns = (applied_position * asset_returns) - transaction_cost
    equity_curve = (1.0 + strategy_returns).cumprod()
    running_max = equity_curve.cummax()
    drawdown = (equity_curve / running_max) - 1.0

    observations = max(len(strategy_returns), 1)
    total_return = equity_curve.iloc[-1] - 1.0
    annualized_return = (equity_curve.iloc[-1] ** (252 / observations)) - 1.0 if equity_curve.iloc[-1] > 0 else -1.0
    annualized_volatility = strategy_returns.std(ddof=0) * math.sqrt(252)
    sharpe = annualized_return / annualized_volatility if annualized_volatility > 0 else 0.0

    active_days = strategy_returns[applied_position != 0]
    win_rate = float((active_days > 0).mean()) if len(active_days) > 0 else 0.0

    return BacktestResult(
        strategy=strategy_name,
        ticker=str(df.attrs.get("ticker", "UNKNOWN")),
        period=period_name,
        observations=observations,
        trades=int((turnover > 0).sum()),
        total_return=float(total_return),
        annualized_return=float(annualized_return),
        annualized_volatility=float(annualized_volatility),
        sharpe=float(sharpe),
        max_drawdown=float(drawdown.min()),
        win_rate=win_rate,
    )


def calculate_tax_adjusted_returns(
    weights: pd.DataFrame,
    prices: pd.DataFrame,
    asset_returns: pd.DataFrame,
    transaction_cost: pd.Series,
    stcg_rate: float = 0.20,  # Short-term capital gains rate
    ltcg_rate: float = 0.15,  # Long-term capital gains rate
    holding_period_days: int = 252,  # 1 year = 252 trading days
) -> tuple:
    """
    Calculate tax-adjusted returns for a portfolio strategy.

    Tracks each position's holding period and applies:
    - Short-term capital gains tax (default 20%) for holdings < 1 year
    - Long-term capital gains tax (default 15%) for holdings >= 1 year

    Returns:
        (tax_adjusted_returns, total_taxes_paid_pct)
    """
    # Track positions and their entry dates
    position_entries = {}  # ticker -> (entry_date, entry_price, shares)
    tax_adjusted_returns = pd.Series(0.0, index=prices.index)
    total_taxes = 0.0
    total_gains = 0.0

    applied_weights = weights.shift(1).fillna(0.0)

    for i, date in enumerate(prices.index):
        # Calculate raw returns before taxes
        raw_return = (applied_weights.loc[date] * asset_returns.loc[date]).sum() - transaction_cost.loc[date]

        # Check for position changes (trades that trigger tax events)
        if i > 0:
            prev_date = prices.index[i - 1]
            prev_weights = weights.loc[prev_date]
            curr_weights = weights.loc[date]

            for ticker in weights.columns:
                prev_w = prev_weights[ticker] if ticker in prev_weights.index else 0.0
                curr_w = curr_weights[ticker] if ticker in curr_weights.index else 0.0

                # Position closed or reduced
                if prev_w > curr_w + 0.001:  # Threshold for numerical stability
                    if ticker in position_entries:
                        entry_date, entry_price, shares = position_entries[ticker]
                        exit_price = prices.loc[date, ticker]

                        # Calculate gain/loss
                        gain_per_share = exit_price - entry_price
                        total_gain = gain_per_share * shares * (prev_w - curr_w) / prev_w

                        if total_gain > 0:
                            # Calculate holding period
                            holding_days = (date - entry_date).days

                            # Apply appropriate tax rate
                            if holding_days < holding_period_days:
                                tax = total_gain * stcg_rate
                            else:
                                tax = total_gain * ltcg_rate

                            total_taxes += tax
                            total_gains += total_gain

                        # Remove or reduce position entry
                        if curr_w < 0.001:
                            del position_entries[ticker]
                        else:
                            # Partial exit - keep proportional entry
                            position_entries[ticker] = (entry_date, entry_price, shares * curr_w / prev_w)

                # Position opened or increased
                elif curr_w > prev_w + 0.001:
                    # Record entry
                    entry_price = prices.loc[date, ticker]
                    position_entries[ticker] = (date, entry_price, curr_w)

        # Record return (taxes will be subtracted at realization)
        tax_adjusted_returns.loc[date] = raw_return

    # Apply tax drag - spread proportionally across all returns
    if total_gains > 0:
        tax_drag_per_period = total_taxes / len(tax_adjusted_returns)
        tax_adjusted_returns = tax_adjusted_returns - tax_drag_per_period

    taxes_as_pct_of_gains = total_taxes / total_gains if total_gains > 0 else 0.0

    return tax_adjusted_returns, taxes_as_pct_of_gains


def run_weighted_backtest(
    prices: pd.DataFrame,
    strategy_name: str,
    weights: pd.DataFrame,
    transaction_cost_bps: float,
    period_name: str,
    ticker_name: str = "PORTFOLIO",
    calculate_taxes: bool = False,
) -> BacktestResult:
    asset_returns = prices.pct_change().fillna(0.0)
    weights = weights.reindex(prices.index).fillna(0.0)
    applied_weights = weights.shift(1).fillna(0.0)
    turnover = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1))
    transaction_cost = turnover * (transaction_cost_bps / 10000.0)

    strategy_returns = (applied_weights * asset_returns).sum(axis=1) - transaction_cost
    equity_curve = (1.0 + strategy_returns).cumprod()
    running_max = equity_curve.cummax()
    drawdown = (equity_curve / running_max) - 1.0

    observations = max(len(strategy_returns), 1)
    total_return = equity_curve.iloc[-1] - 1.0
    annualized_return = (equity_curve.iloc[-1] ** (252 / observations)) - 1.0 if equity_curve.iloc[-1] > 0 else -1.0
    annualized_volatility = strategy_returns.std(ddof=0) * math.sqrt(252)
    sharpe = annualized_return / annualized_volatility if annualized_volatility > 0 else 0.0

    active_days = strategy_returns[applied_weights.abs().sum(axis=1) > 0]
    win_rate = float((active_days > 0).mean()) if len(active_days) > 0 else 0.0

    # Calculate tax-adjusted metrics if requested
    tax_adjusted_return = None
    tax_adjusted_annualized = None
    tax_adjusted_sharpe = None
    total_taxes_paid = None

    if calculate_taxes:
        tax_adj_returns, taxes_pct = calculate_tax_adjusted_returns(
            weights, prices, asset_returns, transaction_cost
        )
        tax_adj_equity = (1.0 + tax_adj_returns).cumprod()
        tax_adjusted_return = float(tax_adj_equity.iloc[-1] - 1.0)
        tax_adjusted_annualized = float((tax_adj_equity.iloc[-1] ** (252 / observations)) - 1.0 if tax_adj_equity.iloc[-1] > 0 else -1.0)
        tax_adj_vol = tax_adj_returns.std(ddof=0) * math.sqrt(252)
        tax_adjusted_sharpe = float(tax_adjusted_annualized / tax_adj_vol if tax_adj_vol > 0 else 0.0)
        total_taxes_paid = float(taxes_pct)

    return BacktestResult(
        strategy=strategy_name,
        ticker=ticker_name,
        period=period_name,
        observations=observations,
        trades=int((turnover > 0).sum()),
        total_return=float(total_return),
        annualized_return=float(annualized_return),
        annualized_volatility=float(annualized_volatility),
        sharpe=float(sharpe),
        max_drawdown=float(drawdown.min()),
        win_rate=win_rate,
        tax_adjusted_return=tax_adjusted_return,
        tax_adjusted_annualized=tax_adjusted_annualized,
        tax_adjusted_sharpe=tax_adjusted_sharpe,
        total_taxes_paid=total_taxes_paid,
    )
