#!/usr/bin/env python3
"""
Multi-Account Execution Script

Manages multiple Alpaca accounts with different strategies.
Reads config/accounts.json and executes appropriate trades for each enabled account.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

# Import strategy generators
import sys
sys.path.append(str(Path(__file__).parent))
from strategies.momentum import generate_strategy_signals

load_dotenv()


class MultiAccountExecutor:
    """Execute trades across multiple configured Alpaca accounts."""

    def __init__(self, config_path: str = 'config/accounts.json'):
        self.config_path = Path(config_path)
        self.load_config()
        self.execution_log = []

    def load_config(self):
        """Load account configuration."""
        with open(self.config_path) as f:
            config = json.load(f)

        self.accounts = config.get('accounts', [])
        self.global_settings = config.get('global_settings', {})
        self.dry_run = self.global_settings.get('dry_run', False)

        print(f"Loaded {len(self.accounts)} accounts from config")

    def get_alpaca_client(self, env_prefix: str, paper: bool = True) -> Optional[TradingClient]:
        """Get Alpaca trading client for a specific account."""
        api_key = os.getenv(f"{env_prefix}_API_KEY")
        secret_key = os.getenv(f"{env_prefix}_SECRET_KEY")

        if not api_key or not secret_key:
            print(f"Missing API keys for {env_prefix}")
            return None

        return TradingClient(api_key, secret_key, paper=paper)

    def get_account_positions(self, client: TradingClient) -> List[Dict]:
        """Get current positions for an account."""
        try:
            positions = client.get_all_positions()
            return [
                {
                    "symbol": p.symbol,
                    "qty": float(p.qty),
                    "market_value": float(p.market_value),
                    "current_price": float(p.current_price),
                    "avg_entry_price": float(p.avg_entry_price),
                    "unrealized_pl": float(p.unrealized_pl),
                }
                for p in positions
            ]
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []

    def generate_llm_signals(self, config: Dict) -> List[Dict]:
        """Generate signals from LLM recommendations (data/trades.json)."""
        trades_file = Path(config.get('trades_source', 'data/trades.json'))

        if not trades_file.exists():
            print(f"No trades file found at {trades_file}")
            return []

        try:
            with open(trades_file) as f:
                trades = json.load(f)

            # LLM recommendations are already in the right format
            return trades

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading LLM trades: {e}")
            return []

    def scale_signals_to_buying_power(self, signals: List[Dict], buying_power: float, config: Dict) -> List[Dict]:
        """Scale buy signals to fit available buying power."""
        auto_scale = config.get('auto_scale_to_buying_power', True)
        max_usage = config.get('max_buying_power_usage', 0.98)

        if not auto_scale:
            return signals

        # Calculate total notional for buy signals
        buy_signals = [s for s in signals if s.get('action') == 'buy']
        total_notional = sum(s.get('notional_value', 0) for s in buy_signals if s.get('notional_value'))

        if total_notional == 0:
            # Use all buying power if no notional specified
            if buy_signals:
                equal_allocation = (buying_power * max_usage) / len(buy_signals)
                for signal in buy_signals:
                    if 'notional_value' not in signal or signal['notional_value'] is None:
                        signal['notional_value'] = equal_allocation
            return signals

        available_capital = buying_power * max_usage
        scale_factor = min(1.0, available_capital / total_notional)

        if scale_factor < 1.0:
            print(f"Scaling signals: ${total_notional:,.0f} -> ${available_capital:,.0f} ({scale_factor:.1%})")

        # Apply scaling
        scaled_signals = []
        for signal in signals:
            if signal.get('action') == 'buy' and signal.get('notional_value'):
                signal = signal.copy()
                signal['notional_value'] = signal['notional_value'] * scale_factor
                signal['rationale'] = f"{signal.get('rationale', '')} (scaled {scale_factor:.1%})".strip()
            scaled_signals.append(signal)

        return scaled_signals

    def execute_signal(self, client: TradingClient, signal: Dict, buying_power: float) -> Dict:
        """Execute a single trade signal."""
        ticker = signal.get('ticker')
        action = signal.get('action', '').lower()

        if not ticker or action not in ['buy', 'sell']:
            return {
                "signal": signal,
                "status": "skipped",
                "reason": "Invalid ticker/action"
            }

        try:
            # Handle sell all
            if action == 'sell' and str(signal.get('qty', '')).lower() == 'all':
                if self.dry_run:
                    print(f"[DRY RUN] Would close position {ticker}")
                    return {"signal": signal, "status": "dry_run", "order_type": "close_position"}

                client.close_position(ticker)
                print(f"Closed position {ticker}")
                return {"signal": signal, "status": "submitted", "order_type": "close_position"}

            # Prepare order
            side = OrderSide.BUY if action == 'buy' else OrderSide.SELL
            order_data = {
                "symbol": ticker,
                "side": side,
                "time_in_force": TimeInForce.DAY
            }

            # Handle notional or qty
            if 'notional_value' in signal and signal['notional_value']:
                notional = float(signal['notional_value'])
                if action == 'buy' and notional > buying_power * 0.98:
                    notional = buying_power * 0.98
                order_data['notional'] = round(notional, 2)
            elif 'qty' in signal:
                order_data['qty'] = float(signal['qty'])
            else:
                return {
                    "signal": signal,
                    "status": "skipped",
                    "reason": "Missing qty/notional_value"
                }

            if self.dry_run:
                print(f"[DRY RUN] Would {action} {ticker}: {order_data}")
                return {"signal": signal, "status": "dry_run", "order_data": order_data}

            # Submit order
            market_order = client.submit_order(order_data=MarketOrderRequest(**order_data))
            print(f"Order submitted: {market_order.id}")

            return {
                "signal": signal,
                "status": "submitted",
                "order_id": str(market_order.id)
            }

        except Exception as e:
            print(f"Error executing {action} {ticker}: {e}")
            return {
                "signal": signal,
                "status": "failed",
                "reason": str(e)
            }

    def process_account(self, account_config: Dict):
        """Process a single account: generate signals and execute trades."""
        account_id = account_config['id']
        account_name = account_config['name']
        strategy = account_config.get('strategy')

        print(f"\n{'='*60}")
        print(f"Processing: {account_name} ({account_id})")
        print(f"Strategy: {strategy}")
        print(f"{'='*60}")

        if not account_config.get('enabled', False):
            print(f"Account {account_id} is disabled. Skipping.")
            return

        if not strategy:
            print(f"No strategy configured for {account_id}. Skipping.")
            return

        # Get Alpaca client
        client = self.get_alpaca_client(
            account_config['env_prefix'],
            paper=account_config.get('paper_trading', True)
        )

        if not client:
            print(f"Could not initialize client for {account_id}")
            return

        # Get account info
        try:
            account = client.get_account()
            buying_power = float(account.buying_power)
            cash = float(account.cash)
            equity = float(account.equity)

            print(f"Account Status:")
            print(f"  Cash: ${cash:,.2f}")
            print(f"  Equity: ${equity:,.2f}")
            print(f"  Buying Power: ${buying_power:,.2f}")

        except Exception as e:
            print(f"Error getting account info: {e}")
            return

        # Get current positions
        positions = self.get_account_positions(client)
        print(f"Current Positions: {len(positions)}")
        for p in positions:
            print(f"  {p['symbol']}: {p['qty']} shares @ ${p['current_price']:.2f}")

        # Generate signals based on strategy
        strategy_config = account_config.get('config', {})

        if strategy == 'llm_recommendations':
            signals = self.generate_llm_signals(strategy_config)
            signals = self.scale_signals_to_buying_power(signals, buying_power, strategy_config)
        else:
            signals = generate_strategy_signals(strategy, strategy_config, positions)
            signals = self.scale_signals_to_buying_power(signals, buying_power, strategy_config)

        print(f"\nGenerated {len(signals)} signals:")
        for sig in signals:
            action = sig.get('action', '').upper()
            ticker = sig.get('ticker')
            rationale = sig.get('rationale', '')
            print(f"  {action} {ticker}: {rationale}")

        # Execute signals
        results = []
        for signal in signals:
            result = self.execute_signal(client, signal, buying_power)
            results.append(result)

            # Update buying power if buy was successful
            if result['status'] in ['submitted', 'dry_run'] and signal.get('action') == 'buy':
                notional = signal.get('notional_value', 0)
                if notional:
                    buying_power = max(0, buying_power - notional)

        # Log results
        self.execution_log.append({
            "account_id": account_id,
            "account_name": account_name,
            "strategy": strategy,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signals": signals,
            "results": results
        })

        print(f"\nExecution complete for {account_name}")

    def run(self):
        """Execute trades for all enabled accounts."""
        print(f"\n{'='*60}")
        print(f"Multi-Account Execution - {datetime.now()}")
        print(f"Dry Run: {self.dry_run}")
        print(f"{'='*60}\n")

        for account_config in self.accounts:
            try:
                self.process_account(account_config)
            except Exception as e:
                print(f"Error processing account {account_config['id']}: {e}")
                import traceback
                traceback.print_exc()

        # Save execution log
        self.save_execution_log()

        print(f"\n{'='*60}")
        print("Multi-Account Execution Complete")
        print(f"{'='*60}\n")

    def save_execution_log(self):
        """Save execution log to file."""
        log_dir = Path('data/multi_account_logs')
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(log_file, 'w') as f:
            json.dump(self.execution_log, f, indent=2)

        # Also save as latest.json
        with open(log_dir / 'latest.json', 'w') as f:
            json.dump(self.execution_log, f, indent=2)

        print(f"\nExecution log saved to {log_file}")


def main():
    """Entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Execute trades across multiple Alpaca accounts')
    parser.add_argument('--config', default='config/accounts.json', help='Path to accounts config file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual trades)')
    parser.add_argument('--account', help='Execute only for specific account ID')
    parser.add_argument('--env', choices=['dev', 'prod', 'all'], default='all',
                       help='Environment filter: dev (testing), prod (production), or all')

    args = parser.parse_args()

    # Can also be controlled via environment variable
    env_filter = os.getenv('ALPACA_ENVIRONMENT', args.env)

    executor = MultiAccountExecutor(config_path=args.config)

    if args.dry_run:
        executor.dry_run = True

    if args.account:
        # Filter to specific account
        executor.accounts = [a for a in executor.accounts if a['id'] == args.account]
        if not executor.accounts:
            print(f"Account {args.account} not found in config")
            return
    elif env_filter != 'all':
        # Filter by environment
        executor.accounts = [a for a in executor.accounts if a.get('environment') == env_filter]
        print(f"Filtered to {env_filter} environment: {len(executor.accounts)} accounts")

    executor.run()


if __name__ == '__main__':
    main()
