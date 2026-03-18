#!/usr/bin/env python3
"""
Paper Trading Engine - Mode 3 of AlphaOracle

Tracks forward performance of strategies and LLM recommendations without risking capital.
"""

import json
import shutil
from datetime import datetime, date
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, List, Optional


class PaperTradingEngine:
    """
    Execute paper trades and track performance for multiple strategies.
    """

    def __init__(self, starting_capital: float = 100000.0):
        self.starting_capital = starting_capital
        self.data_dir = Path('data/paper_trading')
        self.positions_file = self.data_dir / 'positions.json'
        self.trades_file = self.data_dir / 'trades_history.json'
        self.performance_file = self.data_dir / 'performance.json'

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / 'daily_snapshots').mkdir(exist_ok=True)

        self.load_state()

    def load_state(self):
        """Load current positions and trade history"""
        if self.positions_file.exists():
            with open(self.positions_file) as f:
                self.positions = json.load(f)
        else:
            self.positions = self.initialize_positions()

        if self.trades_file.exists():
            with open(self.trades_file) as f:
                self.trades_history = json.load(f)
        else:
            self.trades_history = {"trades": []}

    def initialize_positions(self):
        """Initialize starting positions for all strategies"""
        # Strategies from Mode 2 (generate_strategy_ratings.py)
        strategies = [
            'dual_momentum',
            'sma_200_trend',
            'sma_trend_20_50',
            'rsi_mean_reversion',
            'breakout_20d',
            'leveraged_etf_timing',
            'llm_recommendations'
        ]

        return {
            "initialized_at": datetime.utcnow().isoformat() + 'Z',
            "updated_at": datetime.utcnow().isoformat() + 'Z',
            "strategies": {
                strategy: {
                    "starting_capital": self.starting_capital,
                    "current_cash": self.starting_capital,
                    "current_positions": {},
                    "total_portfolio_value": self.starting_capital,
                    "total_return": 0.0,
                    "total_return_pct": 0.0
                }
                for strategy in strategies
            }
        }

    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current EOD price for ticker"""
        try:
            history_file = Path(f'data/history/{ticker}.json')
            with open(history_file) as f:
                data = json.load(f)

            # Get most recent price (data is an array of price records)
            if isinstance(data, list) and len(data) > 0:
                return data[-1]['close']
            return None
        except (FileNotFoundError, KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Warning: Could not get price for {ticker}: {e}")
            return None

    def update_portfolio_value(self, strategy_name: str):
        """Recalculate total portfolio value with current prices"""
        strategy = self.positions['strategies'][strategy_name]

        total_value = strategy['current_cash']
        for ticker, position in list(strategy['current_positions'].items()):
            current_price = self.get_current_price(ticker)

            if current_price is None:
                print(f"Warning: No price for {ticker} in {strategy_name}, removing position")
                strategy['current_positions'].pop(ticker)
                continue

            position['current_price'] = current_price
            position['market_value'] = position['shares'] * current_price
            position['unrealized_pnl'] = (current_price - position['avg_entry_price']) * position['shares']
            position['unrealized_pnl_pct'] = (current_price / position['avg_entry_price']) - 1.0
            total_value += position['market_value']

        strategy['total_portfolio_value'] = total_value
        strategy['total_return'] = total_value - strategy['starting_capital']
        strategy['total_return_pct'] = strategy['total_return'] / strategy['starting_capital']

    def execute_trade(
        self,
        strategy_name: str,
        ticker: str,
        action: str,
        shares: Optional[float] = None,
        target_weight: Optional[float] = None,
        rationale: str = "",
        signal_data: Optional[Dict] = None
    ):
        """
        Execute a single paper trade.

        Args:
            strategy_name: Name of strategy
            ticker: Stock ticker
            action: 'buy' or 'sell'
            shares: Number of shares (if None, calculated from target_weight)
            target_weight: Target portfolio weight (0.0 to 1.0)
            rationale: Explanation for trade
            signal_data: Additional signal metadata
        """
        current_price = self.get_current_price(ticker)
        if current_price is None:
            print(f"Skipping trade: No price data for {ticker}")
            return

        strategy = self.positions['strategies'][strategy_name]

        # Calculate shares from target weight if needed
        if shares is None and target_weight is not None:
            portfolio_value = strategy['total_portfolio_value']
            target_value = portfolio_value * target_weight
            shares = target_value / current_price

        if shares is None or shares <= 0:
            return

        # Round shares to avoid floating point precision issues
        shares = round(shares, 6)
        notional = shares * current_price

        if action == 'sell':
            # Check if position exists
            if ticker not in strategy['current_positions']:
                print(f"Warning: Trying to sell {ticker} but no position exists in {strategy_name}")
                return

            position = strategy['current_positions'].pop(ticker)
            proceeds = shares * current_price
            strategy['current_cash'] += proceeds

        elif action == 'buy':
            # Check if enough cash
            cost = shares * current_price
            if cost > strategy['current_cash']:
                print(f"Warning: Not enough cash in {strategy_name} to buy {shares} shares of {ticker} (${cost:,.2f} needed, ${strategy['current_cash']:,.2f} available)")
                return

            strategy['current_cash'] -= cost

            # Update or create position
            if ticker in strategy['current_positions']:
                # Average in if already holding
                existing = strategy['current_positions'][ticker]
                total_shares = existing['shares'] + shares
                total_cost = (existing['shares'] * existing['avg_entry_price']) + cost
                avg_price = total_cost / total_shares

                strategy['current_positions'][ticker] = {
                    'shares': total_shares,
                    'avg_entry_price': avg_price,
                    'current_price': current_price,
                    'market_value': total_shares * current_price,
                    'unrealized_pnl': (current_price - avg_price) * total_shares,
                    'unrealized_pnl_pct': (current_price / avg_price) - 1.0,
                    'entry_date': existing['entry_date']  # Keep original entry date
                }
            else:
                # New position
                strategy['current_positions'][ticker] = {
                    'shares': shares,
                    'avg_entry_price': current_price,
                    'current_price': current_price,
                    'market_value': shares * current_price,
                    'unrealized_pnl': 0.0,
                    'unrealized_pnl_pct': 0.0,
                    'entry_date': date.today().isoformat()
                }

        # Log trade
        trade_id = f"trade_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{ticker}"
        trade = {
            'id': trade_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'strategy': strategy_name,
            'ticker': ticker,
            'action': action,
            'shares': float(shares),
            'price': float(current_price),
            'notional': float(notional),
            'commission': 0.0,
            'rationale': rationale,
            'signal_data': signal_data or {}
        }

        self.trades_history['trades'].append(trade)
        print(f"[{strategy_name}] {action.upper()} {shares:.2f} shares of {ticker} @ ${current_price:.2f} = ${notional:,.2f}")

        # Update portfolio value after trade
        self.update_portfolio_value(strategy_name)

    def execute_strategy_signals(self, strategy_name: str, target_positions: Dict[str, float]):
        """
        Execute trades to align current positions with target positions.

        Args:
            strategy_name: Name of strategy
            target_positions: Dict of {ticker: target_weight}
        """
        strategy = self.positions['strategies'][strategy_name]
        current_holdings = set(strategy['current_positions'].keys())
        target_holdings = set(target_positions.keys())

        # Sell positions no longer in target
        to_sell = current_holdings - target_holdings
        for ticker in to_sell:
            shares = strategy['current_positions'][ticker]['shares']
            self.execute_trade(
                strategy_name,
                ticker,
                'sell',
                shares=shares,
                rationale=f"{strategy_name}: Exiting position (no longer in target)"
            )

        # Buy or adjust positions in target
        for ticker, target_weight in target_positions.items():
            self.execute_trade(
                strategy_name,
                ticker,
                'buy',
                target_weight=target_weight,
                rationale=f"{strategy_name}: Target weight {target_weight:.1%}"
            )

    def execute_llm_trades(self, llm_trades: List[Dict]):
        """
        Execute trades from LLM recommendations (data/trades.json).
        Auto-scales buy recommendations to fit available capital.

        Args:
            llm_trades: List of trade dictionaries from LLM
        """
        strategy_name = 'llm_recommendations'
        strategy = self.positions['strategies'][strategy_name]

        # Separate buys and sells
        buy_trades = [t for t in llm_trades if t.get('action', '').lower() == 'buy']
        sell_trades = [t for t in llm_trades if t.get('action', '').lower() == 'sell']

        # Get tickers we want to buy
        buy_tickers = set(t.get('ticker', '') for t in buy_trades if t.get('ticker', ''))

        # Sell positions not in buy list (unless explicitly in sell list)
        current_holdings = set(strategy['current_positions'].keys())
        for ticker in current_holdings:
            if ticker not in buy_tickers:
                shares = strategy['current_positions'][ticker]['shares']
                self.execute_trade(
                    strategy_name,
                    ticker,
                    'sell',
                    shares=shares,
                    rationale=f"LLM recommendation: Exit {ticker} (not in new portfolio)",
                    signal_data={'source': 'llm'}
                )

        # Execute explicit sells
        for trade in sell_trades:
            ticker = trade.get('ticker', '')
            rationale = trade.get('rationale', 'LLM recommendation: Sell')

            if not ticker:
                continue

            # Sell all shares if we have a position
            if ticker in strategy['current_positions']:
                shares = strategy['current_positions'][ticker]['shares']
                self.execute_trade(
                    strategy_name,
                    ticker,
                    'sell',
                    shares=shares,
                    rationale=rationale,
                    signal_data={'source': 'llm'}
                )

        # Calculate total notional for buys
        total_notional = sum(t.get('notional_value', 0) for t in buy_trades)
        available_capital = strategy['current_cash']

        if total_notional == 0:
            return

        # Calculate scaling factor
        scale_factor = available_capital / total_notional if total_notional > available_capital else 1.0

        if scale_factor < 1.0:
            print(f"\nScaling LLM recommendations: ${total_notional:,.0f} -> ${available_capital:,.0f} (factor: {scale_factor:.2%})")

        # Execute scaled buys
        for trade in buy_trades:
            ticker = trade.get('ticker', '')
            notional = trade.get('notional_value', 0)
            rationale = trade.get('rationale', 'LLM recommendation')

            if not ticker:
                continue

            current_price = self.get_current_price(ticker)
            if current_price is None:
                continue

            # Apply scaling factor
            scaled_notional = notional * scale_factor
            shares = scaled_notional / current_price if scaled_notional > 0 else 0

            if shares > 0:
                self.execute_trade(
                    strategy_name,
                    ticker,
                    'buy',
                    shares=shares,
                    rationale=f"{rationale} (scaled {scale_factor:.1%})",
                    signal_data={
                        'source': 'llm',
                        'notional_requested': notional,
                        'notional_scaled': scaled_notional,
                        'scale_factor': scale_factor
                    }
                )

    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics for all strategies"""
        performance = {
            "updated_at": datetime.utcnow().isoformat() + 'Z',
            "period_start": self.positions.get('initialized_at', ''),
            "period_end": date.today().isoformat(),
            "strategies": {},
            "rankings": {}
        }

        strategy_returns = []
        strategy_sharpes = []

        for strategy_name, strategy in self.positions['strategies'].items():
            metrics = {
                "starting_capital": strategy['starting_capital'],
                "current_value": strategy['total_portfolio_value'],
                "total_return": strategy['total_return'],
                "total_return_pct": strategy['total_return_pct'],
                "current_positions": len(strategy['current_positions']),
                "cash_pct": strategy['current_cash'] / strategy['total_portfolio_value'] if strategy['total_portfolio_value'] > 0 else 1.0,
                "equity_pct": 1.0 - (strategy['current_cash'] / strategy['total_portfolio_value']) if strategy['total_portfolio_value'] > 0 else 0.0
            }

            # Count trades for this strategy
            strategy_trades = [t for t in self.trades_history['trades'] if t['strategy'] == strategy_name]
            metrics['trades_total'] = len(strategy_trades)

            # Calculate win rate (closed trades only - for now just count buys vs sells)
            buys = [t for t in strategy_trades if t['action'] == 'buy']
            sells = [t for t in strategy_trades if t['action'] == 'sell']
            metrics['trades_executed'] = len(buys) + len(sells)

            performance['strategies'][strategy_name] = metrics

            strategy_returns.append({
                "strategy": strategy_name,
                "return_pct": strategy['total_return_pct']
            })

            # Placeholder Sharpe (would need daily returns history)
            strategy_sharpes.append({
                "strategy": strategy_name,
                "sharpe": 0.0  # TODO: Calculate from daily returns
            })

        # Rankings
        performance['rankings'] = {
            "by_total_return": sorted(strategy_returns, key=lambda x: x['return_pct'], reverse=True),
            "by_sharpe": sorted(strategy_sharpes, key=lambda x: x['sharpe'], reverse=True)
        }

        return performance

    def save_state(self):
        """Save positions, trades, and performance"""
        self.positions['updated_at'] = datetime.utcnow().isoformat() + 'Z'

        # Save positions
        with open(self.positions_file, 'w') as f:
            json.dump(self.positions, f, indent=2)

        # Save trades
        with open(self.trades_file, 'w') as f:
            json.dump(self.trades_history, f, indent=2)

        # Save daily snapshot
        snapshot_file = self.data_dir / 'daily_snapshots' / f"{date.today().isoformat()}.json"
        with open(snapshot_file, 'w') as f:
            json.dump({
                "date": date.today().isoformat(),
                "positions": self.positions,
                "trades_today": [t for t in self.trades_history['trades'] if t['timestamp'].startswith(date.today().isoformat())]
            }, f, indent=2)

    def copy_to_frontend(self):
        """Copy paper trading data to frontend/public/data/"""
        frontend_data = Path('frontend/public/data')
        frontend_data.mkdir(parents=True, exist_ok=True)

        # Copy positions
        shutil.copy(self.positions_file, frontend_data / 'paper_positions.json')

        # Copy trades
        shutil.copy(self.trades_file, frontend_data / 'paper_trades.json')

        # Copy performance
        shutil.copy(self.performance_file, frontend_data / 'paper_performance.json')

        print(f"Copied paper trading data to {frontend_data}")

    def run_daily_update(self):
        """Main daily execution - update all strategies"""
        print(f"\n{'='*60}")
        print(f"Paper Trading Daily Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # 1. Update all portfolio values with latest prices
        print("Updating portfolio values...")
        for strategy_name in self.positions['strategies'].keys():
            self.update_portfolio_value(strategy_name)

        # 2. Execute LLM recommendations
        print("\nExecuting LLM recommendations...")
        try:
            with open('data/trades.json') as f:
                llm_trades = json.load(f)
            self.execute_llm_trades(llm_trades)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load LLM trades: {e}")

        # 3. TODO: Execute rule-based strategy signals
        # This would integrate with src/generate_strategy_ratings.py output
        # For now, strategies other than LLM remain at their current positions

        # 4. Save state
        print("\nSaving state...")
        self.save_state()

        # 5. Calculate and save performance metrics
        print("Calculating performance metrics...")
        performance = self.calculate_performance_metrics()
        with open(self.performance_file, 'w') as f:
            json.dump(performance, f, indent=2)

        # 6. Copy to frontend
        self.copy_to_frontend()

        # 7. Print summary
        print(f"\n{'='*60}")
        print("Portfolio Summary:")
        print(f"{'='*60}")
        for strategy_name, strategy in self.positions['strategies'].items():
            print(f"\n{strategy_name}:")
            print(f"  Portfolio Value: ${strategy['total_portfolio_value']:,.2f}")
            print(f"  Return: ${strategy['total_return']:,.2f} ({strategy['total_return_pct']:.2%})")
            print(f"  Cash: ${strategy['current_cash']:,.2f}")
            print(f"  Positions: {len(strategy['current_positions'])}")

            if strategy['current_positions']:
                print("  Holdings:")
                for ticker, pos in strategy['current_positions'].items():
                    print(f"    {ticker}: {pos['shares']:.2f} shares @ ${pos['current_price']:.2f} = ${pos['market_value']:,.2f} ({pos['unrealized_pnl_pct']:+.2%})")

        print(f"\n{'='*60}")
        print("Update complete!")
        print(f"{'='*60}\n")


def main():
    """Entry point for paper trading execution"""
    engine = PaperTradingEngine(starting_capital=100000.0)
    engine.run_daily_update()


if __name__ == '__main__':
    main()
