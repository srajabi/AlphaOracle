import json
import math
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

MAX_EXPIRATIONS_PER_TICKER = 2
MIN_DTE = 14
MAX_DTE = 60
MIN_OPEN_INTEREST = 100
MAX_BID_ASK_SPREAD_PCT = 0.15
LONG_OPTION_UNDERLYINGS = {"SPY", "QQQ", "GLD", "TLT", "XLE"}


def load_portfolio():
    """Load current portfolio holdings."""
    if not os.path.exists("portfolio.csv"):
        return pd.DataFrame(columns=["Ticker", "Quantity", "CostBasis", "Type"])
    return pd.read_csv("portfolio.csv")


def load_watchlist():
    if not os.path.exists("watchlist.csv"):
        return pd.DataFrame(columns=["Ticker", "Sector", "Notes"])
    return pd.read_csv("watchlist.csv")


def safe_float(value, default=0.0):
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_mid_price(contract):
    bid = safe_float(contract.get("bid"))
    ask = safe_float(contract.get("ask"))
    last_price = safe_float(contract.get("lastPrice"))
    if bid > 0 and ask > 0:
        return round((bid + ask) / 2, 4)
    return round(last_price, 4)


def compute_spread_pct(contract):
    bid = safe_float(contract.get("bid"))
    ask = safe_float(contract.get("ask"))
    mid = compute_mid_price(contract)
    if bid <= 0 or ask <= 0 or mid <= 0:
        return None
    return round((ask - bid) / mid, 4)


def select_contract(contracts_df, option_type, current_price, target_moneyness, contract_bias):
    if contracts_df is None or contracts_df.empty:
        return None

    filtered = contracts_df.copy()
    filtered["openInterest"] = filtered["openInterest"].fillna(0)
    filtered["volume"] = filtered["volume"].fillna(0)
    filtered["bid"] = filtered["bid"].fillna(0)
    filtered["ask"] = filtered["ask"].fillna(0)
    filtered["mid_price"] = filtered.apply(compute_mid_price, axis=1)
    filtered["spread_pct"] = filtered.apply(compute_spread_pct, axis=1)
    filtered["moneyness_pct"] = (
        (filtered["strike"] - current_price) / current_price
        if option_type == "call"
        else (current_price - filtered["strike"]) / current_price
    )

    filtered = filtered[filtered["openInterest"] >= MIN_OPEN_INTEREST]
    filtered = filtered[filtered["mid_price"] > 0]
    filtered = filtered[
        filtered["spread_pct"].isna() | (filtered["spread_pct"] <= MAX_BID_ASK_SPREAD_PCT)
    ]

    if contract_bias == "otm":
        filtered = filtered[filtered["moneyness_pct"] >= 0]
    elif contract_bias == "protective_put":
        filtered = filtered[(filtered["moneyness_pct"] >= 0.02) & (filtered["moneyness_pct"] <= 0.12)]

    if filtered.empty:
        return None

    filtered["target_distance"] = (filtered["moneyness_pct"] - target_moneyness).abs()
    filtered = filtered.sort_values(
        by=["target_distance", "spread_pct", "openInterest", "volume"],
        ascending=[True, True, False, False],
    )

    best = filtered.iloc[0].to_dict()
    return {
        "contract_symbol": best.get("contractSymbol"),
        "strike": round(safe_float(best.get("strike")), 2),
        "last_price": round(safe_float(best.get("lastPrice")), 4),
        "bid": round(safe_float(best.get("bid")), 4),
        "ask": round(safe_float(best.get("ask")), 4),
        "mid_price": safe_float(best.get("mid_price")),
        "implied_volatility": round(safe_float(best.get("impliedVolatility")), 4),
        "open_interest": int(safe_float(best.get("openInterest"))),
        "volume": int(safe_float(best.get("volume"))),
        "spread_pct": best.get("spread_pct"),
        "moneyness_pct": round(safe_float(best.get("moneyness_pct")), 4),
    }


def get_candidate_expirations(ticker):
    try:
        expirations = yf.Ticker(ticker).options
    except Exception as exc:
        print(f"Failed to fetch expirations for {ticker}: {exc}", file=sys.stderr)
        return []

    today = datetime.now(timezone.utc).date()
    candidates = []
    for expiration in expirations:
        try:
            expiry_date = datetime.strptime(expiration, "%Y-%m-%d").date()
        except ValueError:
            continue
        dte = (expiry_date - today).days
        if MIN_DTE <= dte <= MAX_DTE:
            candidates.append({"expiration": expiration, "dte": dte})
    return candidates[:MAX_EXPIRATIONS_PER_TICKER]


def build_option_idea(ticker, strategy, current_price, expiration_meta, contract, rationale, contracts=1):
    if not contract:
        return None
    return {
        "ticker": ticker,
        "strategy": strategy,
        "expiration": expiration_meta["expiration"],
        "dte": expiration_meta["dte"],
        "current_price": round(current_price, 2),
        "contracts": contracts,
        "option_type": "call" if "call" in strategy else "put",
        "contract": contract,
        "rationale": rationale,
    }


def build_options_context():
    portfolio = load_portfolio()
    watchlist = load_watchlist()

    owned_rows = portfolio[
        (portfolio["Type"] == "Equity") & (portfolio["Quantity"].fillna(0) > 0)
    ].copy()
    watchlist_tickers = set(watchlist["Ticker"].dropna().astype(str).tolist())
    analysis_tickers = set(owned_rows["Ticker"].astype(str).tolist()) | watchlist_tickers | LONG_OPTION_UNDERLYINGS

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "covered_calls": [],
        "cash_secured_puts": [],
        "protective_puts": [],
        "long_option_ideas": [],
        "errors": [],
    }

    for ticker in sorted(analysis_tickers):
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="5d", auto_adjust=False)
            if history.empty:
                continue

            current_price = safe_float(history["Close"].dropna().iloc[-1])
            if current_price <= 0:
                continue

            expirations = get_candidate_expirations(ticker)
            if not expirations:
                continue

            owned_position = owned_rows[owned_rows["Ticker"] == ticker]
            owned_qty = safe_float(owned_position["Quantity"].iloc[0]) if not owned_position.empty else 0.0
            whole_contracts = int(owned_qty // 100)

            for expiration_meta in expirations:
                option_chain = stock.option_chain(expiration_meta["expiration"])

                if whole_contracts > 0:
                    covered_call = select_contract(
                        option_chain.calls,
                        "call",
                        current_price,
                        target_moneyness=0.06,
                        contract_bias="otm",
                    )
                    payload["covered_calls"].append(
                        build_option_idea(
                            ticker,
                            "covered_call",
                            current_price,
                            expiration_meta,
                            covered_call,
                            "Generate premium against an existing equity position using a moderately OTM call.",
                            contracts=whole_contracts,
                        )
                    )

                    protective_put = select_contract(
                        option_chain.puts,
                        "put",
                        current_price,
                        target_moneyness=0.06,
                        contract_bias="protective_put",
                    )
                    payload["protective_puts"].append(
                        build_option_idea(
                            ticker,
                            "protective_put",
                            current_price,
                            expiration_meta,
                            protective_put,
                            "Add downside protection to an existing equity holding with a moderately OTM put.",
                            contracts=max(1, whole_contracts),
                        )
                    )

                if ticker in watchlist_tickers:
                    csp = select_contract(
                        option_chain.puts,
                        "put",
                        current_price,
                        target_moneyness=0.06,
                        contract_bias="otm",
                    )
                    payload["cash_secured_puts"].append(
                        build_option_idea(
                            ticker,
                            "cash_secured_put",
                            current_price,
                            expiration_meta,
                            csp,
                            "Get paid to enter a desired position below spot using a moderately OTM put.",
                        )
                    )

                if ticker in LONG_OPTION_UNDERLYINGS:
                    long_call = select_contract(
                        option_chain.calls,
                        "call",
                        current_price,
                        target_moneyness=0.03,
                        contract_bias="otm",
                    )
                    payload["long_option_ideas"].append(
                        build_option_idea(
                            ticker,
                            "long_call",
                            current_price,
                            expiration_meta,
                            long_call,
                            "Directional upside expression on a liquid ETF/underlying using a slightly OTM call.",
                        )
                    )

                    long_put = select_contract(
                        option_chain.puts,
                        "put",
                        current_price,
                        target_moneyness=0.03,
                        contract_bias="otm",
                    )
                    payload["long_option_ideas"].append(
                        build_option_idea(
                            ticker,
                            "long_put",
                            current_price,
                            expiration_meta,
                            long_put,
                            "Directional downside hedge or bearish expression on a liquid ETF/underlying using a slightly OTM put.",
                        )
                    )

        except Exception as exc:
            payload["errors"].append({"ticker": ticker, "error": str(exc)})

    for key in ["covered_calls", "cash_secured_puts", "protective_puts", "long_option_ideas"]:
        payload[key] = [item for item in payload[key] if item is not None][:12]

    return payload


def main():
    payload = build_options_context()
    os.makedirs("data", exist_ok=True)
    with open("data/options_context.json", "w") as f:
        json.dump(payload, f, indent=2)

    os.makedirs("frontend/public/data", exist_ok=True)
    with open("frontend/public/data/options_context.json", "w") as f:
        json.dump(payload, f, indent=2)

    print(
        "Options ideas saved:",
        f"covered_calls={len(payload['covered_calls'])}",
        f"cash_secured_puts={len(payload['cash_secured_puts'])}",
        f"protective_puts={len(payload['protective_puts'])}",
        f"long_option_ideas={len(payload['long_option_ideas'])}",
        f"errors={len(payload['errors'])}",
    )


if __name__ == "__main__":
    main()
