import os
import json
import csv
import shutil
from pathlib import Path
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

        # Calculate total market value of positions (equities only, excluding cash)
        total_positions_value = sum(float(p.market_value) for p in positions)

        status_payload["ok"] = True
        status_payload["account"] = {
            "status": account.status.value,
            "cash": float(account.cash),
            "equity": total_positions_value,  # Equities only (excluding cash)
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
    portfolio_status_file = "data/portfolio_status.json"
    with open(portfolio_status_file, "w") as f:
        json.dump(status_payload, f, indent=2)
    if status_payload.get("ok") and status_payload.get("account") is not None:
        write_portfolio_csv(status_payload)

    # Copy to frontend
    frontend_data = Path('frontend/public/data')
    frontend_data.mkdir(parents=True, exist_ok=True)
    shutil.copy(portfolio_status_file, frontend_data / 'portfolio_status.json')


def write_portfolio_csv(status_payload):
    rows = [["Ticker", "Quantity", "CostBasis", "Type"]]

    account = status_payload.get("account") or {}
    cash = float(account.get("cash") or 0.0)
    rows.append(["CASH", "1", f"{cash:.2f}", "Currency"])

    for position in status_payload.get("positions", []):
        qty = float(position.get("qty") or 0.0)
        avg_entry_price = float(position.get("avg_entry_price") or 0.0)
        cost_basis = qty * avg_entry_price
        rows.append([
            position.get("symbol", ""),
            f"{qty:.12f}".rstrip("0").rstrip("."),
            f"{cost_basis:.2f}",
            "Equity",
        ])

    with open("portfolio.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

if __name__ == "__main__":
    fetch_portfolio()
