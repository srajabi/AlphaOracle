import os
import json
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def fetch_portfolio():
    status_payload = {
        "paper_trading": True,
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "ok": False,
        "error": "",
        "account": None,
        "positions": []
    }

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("ALPACA_API_KEY or ALPACA_SECRET_KEY not found. Skipping portfolio fetch.")
        status_payload["error"] = "ALPACA_API_KEY or ALPACA_SECRET_KEY not found."
        write_portfolio_outputs(status_payload)
        return

    try:
        trading_client = TradingClient(api_key, secret_key, paper=True)
        account = trading_client.get_account()
        positions = trading_client.get_all_positions()

        status_payload["ok"] = True
        status_payload["account"] = {
            "status": account.status.value,
            "cash": float(account.cash),
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
        }
        status_payload["positions"] = [
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
        write_portfolio_outputs(status_payload)
        print("Successfully fetched and saved Alpaca portfolio status.")

    except Exception as e:
        print(f"Error fetching Alpaca portfolio: {e}")
        status_payload["error"] = str(e)
        write_portfolio_outputs(status_payload)


def write_portfolio_outputs(status_payload):
    os.makedirs("data", exist_ok=True)
    with open("data/portfolio_status.json", "w") as f:
        json.dump(status_payload, f, indent=2)

if __name__ == "__main__":
    fetch_portfolio()
