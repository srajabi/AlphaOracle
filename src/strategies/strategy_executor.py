#!/usr/bin/env python3
"""
Strategy Executor - Automated trade execution for rule-based strategies.

Each strategy has clear entry/exit conditions. This script evaluates conditions
and executes trades via Alpaca API.

Strategies:
1. TQQQ Momentum: 200 SMA crossover on TQQQ
2. Dual Momentum: 12-month momentum rotation (SPY/QQQ/GLD)
3. Sector Rotation: Top 3 sectors by momentum
4. Mean Reversion: RSI oversold + 2 std dev below SMA
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from dotenv import load_dotenv

load_dotenv()


class StrategyExecutor:
    """Base class for strategy execution."""

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.client = TradingClient(api_key, secret_key, paper=paper)
        self.account = self.client.get_account()

    def get_current_positions(self) -> Dict[str, float]:
        """Get current positions as {symbol: quantity}."""
        positions = {}
        try:
            for position in self.client.get_all_positions():
                positions[position.symbol] = float(position.qty)
        except Exception as e:
            print(f"Error getting positions: {e}")
        return positions

    def get_buying_power(self) -> float:
        """Get available buying power."""
        return float(self.account.buying_power)

    def place_market_order(self, symbol: str, qty: float, side: OrderSide) -> bool:
        """Place a market order."""
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            order = self.client.submit_order(order_data)
            print(f"✓ Placed {side.value} order: {qty} shares of {symbol} (Order ID: {order.id})")
            return True
        except Exception as e:
            print(f"✗ Error placing {side.value} order for {symbol}: {e}")
            return False

    def close_position(self, symbol: str) -> bool:
        """Close an existing position."""
        try:
            self.client.close_position(symbol)
            print(f"✓ Closed position: {symbol}")
            return True
        except Exception as e:
            print(f"✗ Error closing position {symbol}: {e}")
            return False

    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical price data."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, auto_adjust=False)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()


class TQQQMomentumStrategy(StrategyExecutor):
    """
    TQQQ 200 SMA Strategy (Reddit LETF rotation)

    Entry Condition: TQQQ closes above 200-day SMA
    Exit Condition: TQQQ closes below 200-day SMA
    Position: 100% TQQQ when above, 100% cash when below
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        super().__init__(api_key, secret_key, paper)
        self.symbol = "TQQQ"
        self.sma_period = 200

    def evaluate(self) -> Tuple[str, str]:
        """
        Evaluate strategy and return (action, reason).

        Returns:
            ('buy', reason) - Go 100% TQQQ
            ('sell', reason) - Go 100% cash
            ('hold', reason) - No change
        """
        print(f"\n{'='*60}")
        print(f"TQQQ Momentum Strategy - {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*60}")

        # Get current position
        positions = self.get_current_positions()
        current_qty = positions.get(self.symbol, 0)
        print(f"Current position: {current_qty} shares of {self.symbol}")

        # Fetch historical data
        data = self.get_historical_data(self.symbol, period="1y")
        if data.empty or len(data) < self.sma_period:
            return ('hold', 'Insufficient data')

        # Calculate 200 SMA
        data['SMA200'] = data['Close'].rolling(window=self.sma_period).mean()
        latest = data.iloc[-1]
        close_price = latest['Close']
        sma_200 = latest['SMA200']

        print(f"Latest close: ${close_price:.2f}")
        print(f"200 SMA: ${sma_200:.2f}")
        print(f"Price vs SMA: {((close_price / sma_200 - 1) * 100):.2f}%")

        # Determine action
        above_sma = close_price > sma_200

        if above_sma and current_qty == 0:
            return ('buy', f'TQQQ (${close_price:.2f}) above 200 SMA (${sma_200:.2f}) - BULLISH')
        elif not above_sma and current_qty > 0:
            return ('sell', f'TQQQ (${close_price:.2f}) below 200 SMA (${sma_200:.2f}) - BEARISH')
        elif above_sma and current_qty > 0:
            return ('hold', f'Already long TQQQ, price above SMA')
        else:
            return ('hold', f'Already in cash, price below SMA')

    def execute(self, dry_run: bool = False):
        """Execute the strategy."""
        action, reason = self.evaluate()
        print(f"\nDecision: {action.upper()}")
        print(f"Reason: {reason}")

        if dry_run:
            print("\n[DRY RUN] No trades executed")
            return

        if action == 'buy':
            # Go 100% TQQQ
            buying_power = self.get_buying_power()
            data = self.get_historical_data(self.symbol, period="5d")
            if data.empty:
                print("Cannot get current price")
                return

            current_price = data['Close'].iloc[-1]
            qty = int(buying_power * 0.95 / current_price)  # Use 95% to account for slippage

            if qty > 0:
                print(f"\nExecuting: BUY {qty} shares of {self.symbol}")
                self.place_market_order(self.symbol, qty, OrderSide.BUY)
            else:
                print("Insufficient buying power")

        elif action == 'sell':
            # Go 100% cash
            print(f"\nExecuting: CLOSE {self.symbol} position")
            self.close_position(self.symbol)


class DualMomentumStrategy(StrategyExecutor):
    """
    Dual Momentum Strategy

    Entry Condition: Hold asset with highest 12-month momentum
    Exit Condition: Rotate when another asset has higher momentum
    Assets: SPY (US stocks), QQQ (Tech), GLD (Gold)
    Rebalance: Monthly
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        super().__init__(api_key, secret_key, paper)
        self.assets = ['SPY', 'QQQ', 'GLD']
        self.lookback_days = 252  # ~12 months

    def calculate_momentum(self, symbol: str) -> float:
        """Calculate 12-month momentum (total return)."""
        data = self.get_historical_data(symbol, period="2y")  # Get 2 years to ensure we have enough
        if data.empty or len(data) < 20:  # Need at least some data
            return -999.0  # Invalid signal

        # Use last 252 trading days (1 year) if available, otherwise use what we have
        lookback = min(len(data), self.lookback_days)
        start_price = data['Close'].iloc[-lookback]
        end_price = data['Close'].iloc[-1]
        momentum = (end_price - start_price) / start_price
        return momentum

    def evaluate(self) -> Tuple[str, str, Optional[str]]:
        """
        Evaluate which asset to hold.

        Returns:
            (action, reason, target_symbol)
        """
        print(f"\n{'='*60}")
        print(f"Dual Momentum Strategy - {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*60}")

        # Calculate momentum for each asset
        momentums = {}
        for symbol in self.assets:
            mom = self.calculate_momentum(symbol)
            momentums[symbol] = mom
            print(f"{symbol}: {mom*100:.2f}% (12-month return)")

        # Find best asset
        best_asset = max(momentums, key=momentums.get)
        best_momentum = momentums[best_asset]

        print(f"\nBest asset: {best_asset} ({best_momentum*100:.2f}%)")

        # Get current position
        positions = self.get_current_positions()
        current_holdings = [sym for sym in self.assets if positions.get(sym, 0) > 0]

        if len(current_holdings) == 0:
            return ('buy', f'{best_asset} has best momentum', best_asset)
        elif current_holdings[0] == best_asset:
            return ('hold', f'Already holding {best_asset}', None)
        else:
            return ('rotate', f'Rotate from {current_holdings[0]} to {best_asset}', best_asset)

    def execute(self, dry_run: bool = False):
        """Execute the strategy."""
        action, reason, target_symbol = self.evaluate()
        print(f"\nDecision: {action.upper()}")
        print(f"Reason: {reason}")

        if dry_run:
            print("\n[DRY RUN] No trades executed")
            return

        if action == 'buy':
            # Buy target asset
            buying_power = self.get_buying_power()
            data = self.get_historical_data(target_symbol, period="5d")
            if data.empty:
                print("Cannot get current price")
                return

            current_price = data['Close'].iloc[-1]
            qty = int(buying_power * 0.95 / current_price)

            if qty > 0:
                print(f"\nExecuting: BUY {qty} shares of {target_symbol}")
                self.place_market_order(target_symbol, qty, OrderSide.BUY)

        elif action == 'rotate':
            # Close current position and buy new asset
            positions = self.get_current_positions()
            for symbol in self.assets:
                if positions.get(symbol, 0) > 0:
                    print(f"\nExecuting: CLOSE {symbol}")
                    self.close_position(symbol)

            # Wait a moment for order to fill, then buy new asset
            import time
            time.sleep(2)

            # Buy new asset
            account = self.client.get_account()
            buying_power = float(account.buying_power)
            data = self.get_historical_data(target_symbol, period="5d")
            if data.empty:
                print("Cannot get current price")
                return

            current_price = data['Close'].iloc[-1]
            qty = int(buying_power * 0.95 / current_price)

            if qty > 0:
                print(f"\nExecuting: BUY {qty} shares of {target_symbol}")
                self.place_market_order(target_symbol, qty, OrderSide.BUY)


class SectorRotationStrategy(StrategyExecutor):
    """
    Sector Rotation Strategy

    Entry Condition: Hold top 3 sectors by 3-month momentum
    Exit Condition: Rebalance when rankings change
    Sectors: XLE, XLF, XLV, XLI, XLK, XLU, XLP, XLY, XLB
    Rebalance: Monthly
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        super().__init__(api_key, secret_key, paper)
        self.sectors = ['XLE', 'XLF', 'XLV', 'XLI', 'XLK', 'XLU', 'XLP', 'XLY', 'XLB']
        self.top_n = 3
        self.lookback_days = 63  # ~3 months

    def calculate_momentum(self, symbol: str) -> float:
        """Calculate 3-month momentum."""
        data = self.get_historical_data(symbol, period="1y")  # Get more data
        if data.empty or len(data) < 20:
            return -999.0

        # Use 63 days (3 months) if available
        lookback = min(len(data), self.lookback_days)
        start_price = data['Close'].iloc[-lookback]
        end_price = data['Close'].iloc[-1]
        momentum = (end_price - start_price) / start_price
        return momentum

    def evaluate(self) -> Tuple[str, str, List[str]]:
        """Determine which sectors to hold."""
        print(f"\n{'='*60}")
        print(f"Sector Rotation Strategy - {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*60}")

        # Calculate momentum for each sector
        momentums = {}
        for sector in self.sectors:
            mom = self.calculate_momentum(sector)
            momentums[sector] = mom
            print(f"{sector}: {mom*100:.2f}% (3-month return)")

        # Sort by momentum and take top N
        sorted_sectors = sorted(momentums.items(), key=lambda x: x[1], reverse=True)
        top_sectors = [s[0] for s in sorted_sectors[:self.top_n]]

        print(f"\nTop {self.top_n} sectors: {', '.join(top_sectors)}")

        # Get current positions
        positions = self.get_current_positions()
        current_sectors = [sym for sym in self.sectors if positions.get(sym, 0) > 0]

        if set(current_sectors) == set(top_sectors):
            return ('hold', f'Already holding top {self.top_n} sectors', [])
        else:
            return ('rebalance', f'Rebalance to: {", ".join(top_sectors)}', top_sectors)

    def execute(self, dry_run: bool = False):
        """Execute the strategy."""
        action, reason, target_sectors = self.evaluate()
        print(f"\nDecision: {action.upper()}")
        print(f"Reason: {reason}")

        if dry_run:
            print("\n[DRY RUN] No trades executed")
            return

        if action == 'rebalance':
            # Close all current sector positions
            positions = self.get_current_positions()
            for sector in self.sectors:
                if positions.get(sector, 0) > 0:
                    print(f"\nClosing: {sector}")
                    self.close_position(sector)

            # Wait for orders to fill
            import time
            time.sleep(2)

            # Buy top N sectors equally weighted
            account = self.client.get_account()
            buying_power = float(account.buying_power)
            allocation_per_sector = buying_power * 0.95 / len(target_sectors)

            for sector in target_sectors:
                data = self.get_historical_data(sector, period="5d")
                if data.empty:
                    continue

                current_price = data['Close'].iloc[-1]
                qty = int(allocation_per_sector / current_price)

                if qty > 0:
                    print(f"\nBuying: {qty} shares of {sector}")
                    self.place_market_order(sector, qty, OrderSide.BUY)


class MeanReversionStrategy(StrategyExecutor):
    """
    Mean Reversion Strategy

    Entry Condition: RSI < 30 AND price > 2 std dev below 20-day SMA
    Exit Condition: Price returns to 20-day SMA OR RSI > 70
    Asset: SPY (for safety)
    Check: Daily
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        super().__init__(api_key, secret_key, paper)
        self.symbol = "SPY"
        self.sma_period = 20
        self.rsi_period = 14
        self.entry_std_dev = 2.0
        self.rsi_oversold = 30
        self.rsi_overbought = 70

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI."""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def evaluate(self) -> Tuple[str, str]:
        """Evaluate entry/exit conditions."""
        print(f"\n{'='*60}")
        print(f"Mean Reversion Strategy - {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*60}")

        # Get current position
        positions = self.get_current_positions()
        current_qty = positions.get(self.symbol, 0)
        print(f"Current position: {current_qty} shares of {self.symbol}")

        # Fetch data
        data = self.get_historical_data(self.symbol, period="3mo")
        if data.empty or len(data) < max(self.sma_period, self.rsi_period):
            return ('hold', 'Insufficient data')

        # Calculate indicators
        data['SMA20'] = data['Close'].rolling(window=self.sma_period).mean()
        data['StdDev'] = data['Close'].rolling(window=self.sma_period).std()
        data['Lower_Band'] = data['SMA20'] - (self.entry_std_dev * data['StdDev'])
        data['RSI'] = self.calculate_rsi(data, self.rsi_period)

        latest = data.iloc[-1]
        close_price = latest['Close']
        sma_20 = latest['SMA20']
        lower_band = latest['Lower_Band']
        rsi = latest['RSI']

        print(f"Close: ${close_price:.2f}")
        print(f"20 SMA: ${sma_20:.2f}")
        print(f"Lower Band (-2σ): ${lower_band:.2f}")
        print(f"RSI: {rsi:.2f}")

        # Entry: Oversold
        oversold = rsi < self.rsi_oversold and close_price < lower_band

        # Exit: Price recovered or overbought
        recovered = close_price >= sma_20 or rsi > self.rsi_overbought

        if oversold and current_qty == 0:
            return ('buy', f'OVERSOLD: RSI={rsi:.1f} < 30, Price ${close_price:.2f} < Lower Band ${lower_band:.2f}')
        elif recovered and current_qty > 0:
            return ('sell', f'EXIT: Price recovered to ${close_price:.2f} (SMA=${sma_20:.2f}) or RSI={rsi:.1f} overbought')
        elif current_qty > 0:
            return ('hold', f'Holding position, waiting for recovery')
        else:
            return ('hold', f'No entry signal')

    def execute(self, dry_run: bool = False):
        """Execute the strategy."""
        action, reason = self.evaluate()
        print(f"\nDecision: {action.upper()}")
        print(f"Reason: {reason}")

        if dry_run:
            print("\n[DRY RUN] No trades executed")
            return

        if action == 'buy':
            # Use 50% of capital for mean reversion (conservative)
            buying_power = self.get_buying_power()
            data = self.get_historical_data(self.symbol, period="5d")
            if data.empty:
                print("Cannot get current price")
                return

            current_price = data['Close'].iloc[-1]
            qty = int((buying_power * 0.50) / current_price)  # Only 50% allocation

            if qty > 0:
                print(f"\nExecuting: BUY {qty} shares of {self.symbol}")
                self.place_market_order(self.symbol, qty, OrderSide.BUY)

        elif action == 'sell':
            print(f"\nExecuting: CLOSE {self.symbol} position")
            self.close_position(self.symbol)


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Execute trading strategies')
    parser.add_argument('--strategy', choices=['tqqq', 'dual', 'sector', 'mean'], required=True,
                        help='Strategy to execute')
    parser.add_argument('--dry-run', action='store_true', help='Evaluate only, do not execute trades')
    parser.add_argument('--account', type=int, default=2, help='Account number (2-5)')
    args = parser.parse_args()

    # Get API keys from environment
    if args.account == 2:
        api_key = os.getenv('ALPACA_PROD_2_API_KEY')
        secret_key = os.getenv('ALPACA_PROD_2_SECRET_KEY')
        expected_strategy = 'tqqq'
    elif args.account == 3:
        api_key = os.getenv('ALPACA_PROD_3_API_KEY')
        secret_key = os.getenv('ALPACA_PROD_3_SECRET_KEY')
        expected_strategy = 'dual'
    elif args.account == 4:
        api_key = os.getenv('ALPACA_PROD_4_API_KEY')
        secret_key = os.getenv('ALPACA_PROD_4_SECRET_KEY')
        expected_strategy = 'sector'
    elif args.account == 5:
        api_key = os.getenv('ALPACA_PROD_5_API_KEY')
        secret_key = os.getenv('ALPACA_PROD_5_SECRET_KEY')
        expected_strategy = 'mean'
    else:
        print(f"Invalid account number: {args.account}")
        sys.exit(1)

    if not api_key or not secret_key:
        print(f"Missing API keys for account {args.account}")
        sys.exit(1)

    # Validate strategy matches account
    if args.strategy != expected_strategy:
        print(f"WARNING: Account {args.account} is configured for '{expected_strategy}' strategy, but you requested '{args.strategy}'")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            sys.exit(0)

    # Execute strategy
    if args.strategy == 'tqqq':
        strategy = TQQQMomentumStrategy(api_key, secret_key, paper=True)
    elif args.strategy == 'dual':
        strategy = DualMomentumStrategy(api_key, secret_key, paper=True)
    elif args.strategy == 'sector':
        strategy = SectorRotationStrategy(api_key, secret_key, paper=True)
    elif args.strategy == 'mean':
        strategy = MeanReversionStrategy(api_key, secret_key, paper=True)

    strategy.execute(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
