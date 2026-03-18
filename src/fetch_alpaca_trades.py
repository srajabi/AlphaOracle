#!/usr/bin/env python3
"""
Fetch trade history from Alpaca API.

Fetches recent trade activity (fills) from Alpaca and saves to JSON for display
on the dashboard. This provides real trade history instead of simulated data.
"""

import os
import json
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()


def fetch_trades(days_back=30):
    """
    Fetch trade history from Alpaca for the last N days.

    Args:
        days_back: Number of days of history to fetch (default: 30)

    Returns:
        dict: Trade history data
    """
    result = {
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "ok": False,
        "error": "",
        "trades": []
    }

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        print("ALPACA_API_KEY or ALPACA_SECRET_KEY not found. Skipping trade fetch.")
        result["error"] = "ALPACA_API_KEY or ALPACA_SECRET_KEY not found."
        write_trades_output(result)
        return result

    try:
        trading_client = TradingClient(api_key, secret_key, paper=True)

        # Fetch filled orders from the last N days
        # These represent executed trades
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        order_request = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED,
            limit=500,  # Max orders to fetch
            after=cutoff_date
        )

        orders = trading_client.get_orders(filter=order_request)

        # Convert filled orders to trade format
        trades = []

        for order in orders:
            # Only include filled orders
            if order.status.value != 'filled':
                continue

            # Use filled_at if available, otherwise created_at
            trade_time = order.filled_at if hasattr(order, 'filled_at') and order.filled_at else order.created_at

            trade_data = {
                "id": order.id,
                "timestamp": trade_time.isoformat() if hasattr(trade_time, 'isoformat') else str(trade_time),
                "side": order.side.value if hasattr(order, 'side') else None,
                "symbol": order.symbol,
                "qty": float(order.filled_qty) if hasattr(order, 'filled_qty') else float(order.qty),
                "price": float(order.filled_avg_price) if hasattr(order, 'filled_avg_price') else 0.0,
                "notional": float(order.filled_qty) * float(order.filled_avg_price) if hasattr(order, 'filled_qty') and hasattr(order, 'filled_avg_price') else 0.0,
                "type": order.type.value if hasattr(order, 'type') else None,
            }
            trades.append(trade_data)

        # Sort by timestamp, most recent first
        trades.sort(key=lambda x: x['timestamp'], reverse=True)

        result["ok"] = True
        result["trades"] = trades
        result["total_trades"] = len(trades)
        result["period_days"] = days_back

        write_trades_output(result)
        print(f"Successfully fetched {len(trades)} trades from last {days_back} days")

    except Exception as e:
        print(f"Error fetching Alpaca trades: {e}")
        result["error"] = str(e)
        write_trades_output(result)

    return result


def write_trades_output(result):
    """Write trade data to JSON files."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("frontend/public/data", exist_ok=True)

    # Write to backend data directory
    with open("data/alpaca_trades.json", "w") as f:
        json.dump(result, f, indent=2)

    # Copy to frontend
    with open("frontend/public/data/alpaca_trades.json", "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    fetch_trades(days_back=30)
