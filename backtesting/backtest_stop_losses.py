#!/usr/bin/env python3
"""
Backtest Stop Loss Parameters for Each Strategy

Goal: Find optimal stop loss levels that provide crash protection
without destroying profits through premature exits.

Test ranges:
- TQQQ Momentum: 3%, 5%, 7%, 10%, None (200 SMA only)
- Dual Momentum: 5%, 8%, 10%, 12%, None (monthly rotation only)
- Sector Rotation: 5%, 7%, 10%, None
- Mean Reversion: 8%, 10%, 15%, None

Metrics tracked:
- Total Return
- CAGR
- Max Drawdown
- Sharpe Ratio
- Win Rate
- Number of stop triggers
- Average time in position
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json


class StopLossBacktester:
    """Backtest various stop loss levels for a strategy."""

    def __init__(self, start_date='2020-01-01', end_date='2024-12-31'):
        self.start_date = start_date
        self.end_date = end_date
        self.results = []

    def download_data(self, symbol: str) -> pd.DataFrame:
        """Download historical data."""
        try:
            data = yf.download(symbol, start=self.start_date, end=self.end_date, progress=False)
            return data
        except Exception as e:
            print(f"Error downloading {symbol}: {e}")
            return pd.DataFrame()

    def backtest_tqqq_momentum(self, stop_loss_pct: float = None) -> Dict:
        """
        Backtest TQQQ 200 SMA strategy with optional stop loss.

        Args:
            stop_loss_pct: Stop loss as decimal (e.g., 0.05 for 5%). None = no stop.
        """
        print(f"\n{'='*60}")
        print(f"TQQQ Momentum - Stop Loss: {stop_loss_pct*100 if stop_loss_pct else 'None (200 SMA only)'}%")
        print(f"{'='*60}")

        data = self.download_data('TQQQ')
        if data.empty:
            return None

        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Calculate 200 SMA
        data['SMA200'] = data['Close'].rolling(window=200).mean()
        data = data.dropna().copy()  # Make a copy to avoid fragmentation

        # Backtest
        cash = 10000
        position = 0
        entry_price = 0
        peak_price = 0
        trades = []

        equity_curve = []
        stop_triggers = 0
        sma_exits = 0

        for i in range(len(data)):
            date = data.index[i]
            price = float(data['Close'].iloc[i])
            sma = float(data['SMA200'].iloc[i])

            # Update peak if in position
            if position > 0:
                peak_price = max(peak_price, price)

            # Check stop loss first (if active)
            if position > 0 and stop_loss_pct:
                stop_price = peak_price * (1 - stop_loss_pct)
                if price <= stop_price:
                    # Stop triggered
                    pnl = (price - entry_price) * position
                    cash += price * position
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': date,
                        'entry_price': entry_price,
                        'exit_price': price,
                        'pnl': pnl,
                        'pnl_pct': (price / entry_price - 1) * 100,
                        'exit_reason': 'stop_loss'
                    })
                    position = 0
                    stop_triggers += 1
                    peak_price = 0

            # Check 200 SMA signal
            if position == 0 and price > sma:
                # Buy signal
                position = cash / price
                entry_price = price
                entry_date = date
                peak_price = price
                cash = 0

            elif position > 0 and price < sma:
                # Sell signal
                pnl = (price - entry_price) * position
                cash = price * position
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': date,
                    'entry_price': entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'pnl_pct': (price / entry_price - 1) * 100,
                    'exit_reason': 'sma_cross'
                })
                position = 0
                sma_exits += 1
                peak_price = 0

            # Record equity
            portfolio_value = cash + (position * price if position > 0 else 0)
            equity_curve.append({'date': date, 'equity': portfolio_value})

        # Calculate metrics
        final_equity = equity_curve[-1]['equity']
        total_return = (final_equity - 10000) / 10000

        # Max drawdown
        equity_series = pd.Series([e['equity'] for e in equity_curve])
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()

        # Sharpe ratio (simplified - daily returns)
        returns = equity_series.pct_change().dropna()
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        # Win rate
        winning_trades = [t for t in trades if t['pnl'] > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0

        # CAGR
        years = (data.index[-1] - data.index[0]).days / 365.25
        cagr = (final_equity / 10000) ** (1 / years) - 1

        result = {
            'strategy': 'TQQQ_Momentum',
            'stop_loss_pct': stop_loss_pct * 100 if stop_loss_pct else None,
            'total_return': total_return * 100,
            'cagr': cagr * 100,
            'max_drawdown': max_drawdown * 100,
            'sharpe_ratio': sharpe,
            'total_trades': len(trades),
            'win_rate': win_rate * 100,
            'stop_triggers': stop_triggers,
            'sma_exits': sma_exits,
            'final_equity': final_equity
        }

        print(f"Total Return: {result['total_return']:.2f}%")
        print(f"CAGR: {result['cagr']:.2f}%")
        print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"Total Trades: {result['total_trades']}")
        print(f"Win Rate: {result['win_rate']:.2f}%")
        print(f"Stop Triggers: {stop_triggers} | SMA Exits: {sma_exits}")

        return result

    def backtest_dual_momentum(self, stop_loss_pct: float = None) -> Dict:
        """
        Backtest Dual Momentum with optional trailing stop.

        Simplified: Just tests SPY vs QQQ rotation (no GLD for now).
        """
        print(f"\n{'='*60}")
        print(f"Dual Momentum - Stop Loss: {stop_loss_pct*100 if stop_loss_pct else 'None (monthly only)'}%")
        print(f"{'='*60}")

        # Download data
        spy = self.download_data('SPY')
        qqq = self.download_data('QQQ')

        if spy.empty or qqq.empty:
            return None

        # Flatten multi-index columns if present
        if isinstance(spy.columns, pd.MultiIndex):
            spy.columns = spy.columns.get_level_values(0)
        if isinstance(qqq.columns, pd.MultiIndex):
            qqq.columns = qqq.columns.get_level_values(0)

        # Align dates
        data = pd.DataFrame({
            'SPY': spy['Close'],
            'QQQ': qqq['Close']
        }).dropna().copy()

        # Backtest
        cash = 10000
        position_symbol = None
        position_qty = 0
        entry_price = 0
        peak_price = 0
        trades = []

        equity_curve = []
        stop_triggers = 0
        rotation_exits = 0

        # Monthly rebalancing
        last_rebalance = None

        for i in range(252, len(data)):  # Start after 1 year for momentum calc
            date = data.index[i]

            # Current prices
            spy_price = float(data['SPY'].iloc[i])
            qqq_price = float(data['QQQ'].iloc[i])

            current_price = spy_price if position_symbol == 'SPY' else qqq_price if position_symbol == 'QQQ' else 0

            # Update peak if in position
            if position_qty > 0:
                peak_price = max(peak_price, current_price)

            # Check stop loss (daily)
            if position_qty > 0 and stop_loss_pct:
                stop_price = peak_price * (1 - stop_loss_pct)
                if current_price <= stop_price:
                    # Stop triggered - go to cash
                    pnl = (current_price - entry_price) * position_qty
                    cash = current_price * position_qty
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': date,
                        'symbol': position_symbol,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'pnl': pnl,
                        'pnl_pct': (current_price / entry_price - 1) * 100,
                        'exit_reason': 'stop_loss'
                    })
                    position_qty = 0
                    position_symbol = None
                    stop_triggers += 1
                    peak_price = 0

            # Monthly rebalancing check
            if last_rebalance is None or (date - last_rebalance).days >= 28:
                # Calculate 12-month momentum
                spy_momentum = (float(data['SPY'].iloc[i]) / float(data['SPY'].iloc[i-252]) - 1)
                qqq_momentum = (float(data['QQQ'].iloc[i]) / float(data['QQQ'].iloc[i-252]) - 1)

                best_symbol = 'SPY' if spy_momentum > qqq_momentum else 'QQQ'
                best_price = spy_price if best_symbol == 'SPY' else qqq_price

                # If holding different asset, rotate
                if position_symbol and position_symbol != best_symbol:
                    # Exit current position
                    pnl = (current_price - entry_price) * position_qty
                    cash = current_price * position_qty
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': date,
                        'symbol': position_symbol,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'pnl': pnl,
                        'pnl_pct': (current_price / entry_price - 1) * 100,
                        'exit_reason': 'rotation'
                    })
                    position_qty = 0
                    rotation_exits += 1

                # Enter best asset (if not already holding it)
                if position_symbol != best_symbol:
                    position_symbol = best_symbol
                    position_qty = cash / best_price
                    entry_price = best_price
                    entry_date = date
                    peak_price = best_price
                    cash = 0

                last_rebalance = date

            # Record equity
            if position_qty > 0:
                current_price = float(data[position_symbol].iloc[i])
                portfolio_value = position_qty * current_price
            else:
                portfolio_value = cash

            equity_curve.append({'date': date, 'equity': portfolio_value})

        # Calculate metrics
        final_equity = equity_curve[-1]['equity']
        total_return = (final_equity - 10000) / 10000

        equity_series = pd.Series([e['equity'] for e in equity_curve])
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()

        returns = equity_series.pct_change().dropna()
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0

        winning_trades = [t for t in trades if t['pnl'] > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0

        years = (data.index[-1] - data.index[252]).days / 365.25
        cagr = (final_equity / 10000) ** (1 / years) - 1

        result = {
            'strategy': 'Dual_Momentum',
            'stop_loss_pct': stop_loss_pct * 100 if stop_loss_pct else None,
            'total_return': total_return * 100,
            'cagr': cagr * 100,
            'max_drawdown': max_drawdown * 100,
            'sharpe_ratio': sharpe,
            'total_trades': len(trades),
            'win_rate': win_rate * 100,
            'stop_triggers': stop_triggers,
            'rotation_exits': rotation_exits,
            'final_equity': final_equity
        }

        print(f"Total Return: {result['total_return']:.2f}%")
        print(f"CAGR: {result['cagr']:.2f}%")
        print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"Total Trades: {result['total_trades']}")
        print(f"Win Rate: {result['win_rate']:.2f}%")
        print(f"Stop Triggers: {stop_triggers} | Rotation Exits: {rotation_exits}")

        return result


def main():
    """Run stop loss parameter sweep."""

    print("\n" + "="*70)
    print("STOP LOSS HYPERPARAMETER OPTIMIZATION")
    print("Testing multiple stop loss levels to find optimal crash protection")
    print("="*70)

    backtester = StopLossBacktester(start_date='2020-01-01', end_date='2024-12-31')

    all_results = []

    # Test TQQQ Momentum with various stops
    print("\n" + "="*70)
    print("STRATEGY 1: TQQQ MOMENTUM (200 SMA)")
    print("="*70)

    for stop_pct in [None, 0.03, 0.05, 0.07, 0.10]:
        result = backtester.backtest_tqqq_momentum(stop_pct)
        if result:
            all_results.append(result)

    # Test Dual Momentum with various stops
    print("\n" + "="*70)
    print("STRATEGY 2: DUAL MOMENTUM")
    print("="*70)

    for stop_pct in [None, 0.05, 0.08, 0.10, 0.12]:
        result = backtester.backtest_dual_momentum(stop_pct)
        if result:
            all_results.append(result)

    # Save results
    results_df = pd.DataFrame(all_results)
    results_df.to_csv('data/stop_loss_backtest_results.csv', index=False)

    with open('data/stop_loss_backtest_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY - BEST PARAMETERS")
    print("="*70)

    for strategy in ['TQQQ_Momentum', 'Dual_Momentum']:
        strategy_results = results_df[results_df['strategy'] == strategy]

        print(f"\n{strategy}:")
        print(f"{'Stop %':<10} {'Return %':<12} {'Max DD %':<12} {'Sharpe':<10} {'Stops':<8}")
        print("-" * 60)

        for _, row in strategy_results.iterrows():
            stop_label = f"{row['stop_loss_pct']:.0f}%" if row['stop_loss_pct'] else "None"
            print(f"{stop_label:<10} {row['total_return']:>10.2f}% {row['max_drawdown']:>10.2f}% "
                  f"{row['sharpe_ratio']:>8.2f} {row['stop_triggers']:>6}")

        # Best by Sharpe ratio
        best = strategy_results.loc[strategy_results['sharpe_ratio'].idxmax()]
        best_stop = f"{best['stop_loss_pct']:.0f}%" if best['stop_loss_pct'] else "None"
        print(f"\n✓ OPTIMAL: {best_stop} stop (Best Sharpe: {best['sharpe_ratio']:.2f})")

    print("\nResults saved to data/stop_loss_backtest_results.csv")


if __name__ == '__main__':
    main()
