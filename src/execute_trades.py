import os
import json
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def execute_trades():
    print("Initializing Alpaca client...")
    # Load API keys from environment variables
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("Error: ALPACA_API_KEY or ALPACA_SECRET_KEY not found in environment. Skipping execution.")
        write_execution_log([], "Missing Alpaca API keys.")
        return

    # Initialize the trading client. paper=True means we are using paper trading.
    trading_client = TradingClient(api_key, secret_key, paper=True)

    # Check if trades.json exists
    trades_file = "data/trades.json"
    if not os.path.exists(trades_file):
        print(f"No {trades_file} found. No trades to execute.")
        write_execution_log([], "No trades file found.")
        return

    with open(trades_file, "r") as f:
        try:
            trades = json.load(f)
        except json.JSONDecodeError:
            print(f"Error parsing {trades_file}. Invalid JSON.")
            write_execution_log([], "Invalid trades.json payload.")
            return

    if not trades:
        print("No actionable trades found in JSON array.")
        write_execution_log([], "")
        return

    execution_results = []
    account = trading_client.get_account()
    available_buying_power = float(account.buying_power)
    for trade in trades:
        ticker = trade.get("ticker")
        action = trade.get("action", "").lower()
        
        if not ticker or action not in ["buy", "sell"]:
            print(f"Invalid trade block: {trade}. Skipping.")
            execution_results.append({
                "trade": trade,
                "status": "skipped",
                "reason": "Invalid ticker/action."
            })
            continue
            
        side = OrderSide.BUY if action == "buy" else OrderSide.SELL

        print(f"Preparing to {action.upper()} {ticker}...")

        try:
            # Handle closing an entire position
            if action == "sell" and str(trade.get("qty")).lower() == "all":
                print(f"Closing entire position for {ticker}")
                trading_client.close_position(ticker)
                print(f"Successfully sent order to close {ticker}")
                execution_results.append({
                    "trade": trade,
                    "status": "submitted",
                    "order_type": "close_position"
                })
                continue

            # Prepare the order request
            order_data = {
                "symbol": ticker,
                "side": side,
                "time_in_force": TimeInForce.DAY
            }

            # Alpaca allows specifying EITHER fractional quantities OR notional dollar amounts
            if "notional_value" in trade:
                requested_notional = float(trade["notional_value"])
                if action == "buy":
                    if available_buying_power <= 0:
                        execution_results.append({
                            "trade": trade,
                            "status": "skipped",
                            "reason": "No available buying power."
                        })
                        continue
                    # Keep a small cushion to avoid rounding/rejection edge cases.
                    max_notional = max(0.0, available_buying_power * 0.98)
                    capped_notional = min(requested_notional, max_notional)
                    if capped_notional <= 0:
                        execution_results.append({
                            "trade": trade,
                            "status": "skipped",
                            "reason": "Capped notional is zero."
                        })
                        continue
                    if capped_notional < requested_notional:
                        print(
                            f"Capping {ticker} BUY notional from {requested_notional} to {capped_notional} "
                            "based on account buying power."
                        )
                    order_data["notional"] = round(capped_notional, 2)
                else:
                    order_data["notional"] = requested_notional
            elif "qty" in trade:
                order_data["qty"] = float(trade["qty"])
            else:
                print(f"Trade must specify 'qty' or 'notional_value': {trade}. Skipping.")
                execution_results.append({
                    "trade": trade,
                    "status": "skipped",
                    "reason": "Missing qty/notional_value."
                })
                continue
                
            market_order_data = MarketOrderRequest(**order_data)
            
            # Submit the order
            market_order = trading_client.submit_order(order_data=market_order_data)
            print(f"Order submitted successfully: {market_order.id}")
            execution_results.append({
                "trade": trade,
                "status": "submitted",
                "order_id": str(market_order.id)
            })
            if action == "buy" and "notional" in order_data:
                available_buying_power = max(0.0, available_buying_power - float(order_data["notional"]))

        except Exception as e:
            print(f"Failed to execute trade for {ticker}: {e}")
            execution_results.append({
                "trade": trade,
                "status": "failed",
                "reason": str(e)
            })

    write_execution_log(execution_results, "")


def write_execution_log(results, error):
    payload = {
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "error": error,
        "results": results
    }
    os.makedirs("data", exist_ok=True)
    with open("data/last_execution.json", "w") as f:
        json.dump(payload, f, indent=2)

if __name__ == "__main__":
    execute_trades()
