"""
Advanced LLM Trading Agent for Dev Account (2x Daily Execution)

This agent uses a more sophisticated approach than the standard LLM strategy:
- Analyzes real-time market context, news, options flow, and technical indicators
- Makes dynamic position sizing decisions based on confidence and risk
- Can enter/exit positions more actively throughout the day
- Uses ensemble reasoning across multiple data sources
- Implements risk management with position limits and stop considerations

Runs: 10 AM ET and 3:30 PM ET daily
Account: Alpaca Dev (paper trading)
"""

import os
import json
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Dict, List, Any

load_dotenv()


class AdvancedLLMAgent:
    """Advanced LLM agent with multi-source analysis and dynamic trading"""

    def __init__(self, api_key: str, secret_key: str):
        self.trading_client = TradingClient(api_key, secret_key, paper=True)
        self.account = None
        self.positions = []
        self.market_context = {}
        self.options_context = {}
        self.strategy_ratings = {}
        self.ticker_indicators = {}
        self.indicators = {}

    def load_market_data(self):
        """Load all available market data sources"""
        try:
            with open("data/market_context.json", "r") as f:
                self.market_context = json.load(f)
        except:
            print("Warning: Could not load market_context.json")

        try:
            with open("data/options_context.json", "r") as f:
                self.options_context = json.load(f)
        except:
            print("Warning: Could not load options_context.json")

        try:
            with open("data/strategy_ratings.json", "r") as f:
                self.strategy_ratings = json.load(f)
        except:
            print("Warning: Could not load strategy_ratings.json")

        try:
            with open("data/ticker_indicators.json", "r") as f:
                self.ticker_indicators = json.load(f)
        except:
            print("Warning: Could not load ticker_indicators.json")

        try:
            with open("data/indicators.json", "r") as f:
                self.indicators = json.load(f)
        except:
            print("Warning: Could not load indicators.json")

    def get_account_state(self):
        """Fetch current account and position state"""
        self.account = self.trading_client.get_account()
        self.positions = self.trading_client.get_all_positions()

        print(f"\n=== Account State ===")
        print(f"Buying Power: ${float(self.account.buying_power):,.2f}")
        print(f"Portfolio Value: ${float(self.account.portfolio_value):,.2f}")
        print(f"Current Positions: {len(self.positions)}")
        for pos in self.positions:
            pl_pct = (float(pos.unrealized_pl) / float(pos.cost_basis)) * 100 if float(pos.cost_basis) > 0 else 0
            print(f"  {pos.symbol}: {float(pos.qty):.2f} shares, P/L: {pl_pct:+.2f}%")

    def analyze_regime(self) -> Dict[str, Any]:
        """Analyze current market regime and risk level"""
        regime = self.market_context.get("regime", "Unknown")

        # Map regime to risk level
        risk_map = {
            "Bull Stable": {"risk_on": True, "volatility": "low", "max_position_size": 0.25},
            "Bull Volatile": {"risk_on": True, "volatility": "high", "max_position_size": 0.15},
            "Bear": {"risk_on": False, "volatility": "high", "max_position_size": 0.10},
            "Sideways": {"risk_on": False, "volatility": "medium", "max_position_size": 0.12}
        }

        regime_data = risk_map.get(regime, {"risk_on": False, "volatility": "unknown", "max_position_size": 0.10})

        print(f"\n=== Market Regime Analysis ===")
        print(f"Regime: {regime}")
        print(f"Risk-On: {regime_data['risk_on']}")
        print(f"Volatility: {regime_data['volatility']}")
        print(f"Max Position Size: {regime_data['max_position_size']*100:.0f}%")

        return regime_data

    def analyze_top_opportunities(self, regime_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify top trading opportunities from strategy ratings and technical indicators"""
        opportunities = []

        # Get top-rated tickers from strategy ratings
        if self.strategy_ratings:
            for strategy_name, strategy_data in self.strategy_ratings.items():
                if "target_positions" in strategy_data:
                    for ticker, weight in strategy_data["target_positions"].items():
                        if weight > 0:
                            opportunities.append({
                                "ticker": ticker,
                                "strategy": strategy_name,
                                "weight": weight,
                                "source": "strategy_rating"
                            })

        # Get tickers with strong momentum from technical indicators
        if self.ticker_indicators:
            for ticker, indicators in self.ticker_indicators.items():
                if indicators.get("rsi_14", 50) < 35:  # Oversold
                    opportunities.append({
                        "ticker": ticker,
                        "signal": "oversold",
                        "rsi": indicators.get("rsi_14"),
                        "source": "technical"
                    })
                elif indicators.get("sma_20_50_bullish", False):  # Golden cross
                    opportunities.append({
                        "ticker": ticker,
                        "signal": "momentum",
                        "source": "technical"
                    })

        # Analyze options flow for institutional activity
        if self.options_context:
            options_data = self.options_context.get("options_data", {})
            for ticker, opt_data in options_data.items():
                iv_percentile = opt_data.get("iv_percentile", 50)
                put_call_ratio = opt_data.get("put_call_ratio", 1.0)

                # High call activity + low IV = bullish setup
                if put_call_ratio < 0.7 and iv_percentile < 40:
                    opportunities.append({
                        "ticker": ticker,
                        "signal": "bullish_options_flow",
                        "put_call_ratio": put_call_ratio,
                        "iv_percentile": iv_percentile,
                        "source": "options"
                    })

        # Score and rank opportunities
        scored_opportunities = self._score_opportunities(opportunities, regime_data)

        print(f"\n=== Top Opportunities (Scored) ===")
        for i, opp in enumerate(scored_opportunities[:10], 1):
            print(f"{i}. {opp['ticker']}: Score={opp['score']:.2f}, Sources={opp.get('source', 'multiple')}")

        return scored_opportunities

    def _score_opportunities(self, opportunities: List[Dict], regime_data: Dict) -> List[Dict]:
        """Score and rank opportunities based on multiple factors"""
        ticker_scores = {}

        for opp in opportunities:
            ticker = opp.get("ticker")
            if not ticker:
                continue

            if ticker not in ticker_scores:
                ticker_scores[ticker] = {"ticker": ticker, "score": 0, "signals": []}

            # Score based on source and signal strength
            if opp.get("source") == "strategy_rating":
                ticker_scores[ticker]["score"] += opp.get("weight", 0) * 10
                ticker_scores[ticker]["signals"].append(f"strategy_{opp.get('strategy')}")
            elif opp.get("source") == "technical":
                ticker_scores[ticker]["score"] += 5
                ticker_scores[ticker]["signals"].append(opp.get("signal", "technical"))
            elif opp.get("source") == "options":
                ticker_scores[ticker]["score"] += 7
                ticker_scores[ticker]["signals"].append("options_flow")

        # Adjust scores based on regime
        if not regime_data.get("risk_on"):
            # In risk-off regime, favor defensive sectors
            for ticker, data in ticker_scores.items():
                if ticker in ["TLT", "GLD", "XLU", "XLP"]:
                    data["score"] *= 1.5
                elif ticker in ["QQQ", "TQQQ"]:
                    data["score"] *= 0.5

        # Sort by score descending
        sorted_opportunities = sorted(ticker_scores.values(), key=lambda x: x["score"], reverse=True)
        return sorted_opportunities

    def generate_trade_plan(self, opportunities: List[Dict], regime_data: Dict) -> List[Dict]:
        """Generate executable trade plan based on opportunities and current positions"""
        trades = []
        buying_power = float(self.account.buying_power)
        portfolio_value = float(self.account.portfolio_value)
        max_position_size = regime_data["max_position_size"]

        # Current position tickers
        current_tickers = {pos.symbol for pos in self.positions}

        # Exit logic: Sell positions that are no longer in top opportunities or have losses
        for pos in self.positions:
            ticker = pos.symbol
            unrealized_pl_pct = (float(pos.unrealized_pl) / float(pos.cost_basis)) * 100 if float(pos.cost_basis) > 0 else 0

            # Check if ticker is still in top 5 opportunities
            top_tickers = {opp["ticker"] for opp in opportunities[:5]}

            # Sell if: not in top opportunities OR down >5%
            if ticker not in top_tickers or unrealized_pl_pct < -5:
                reason = "not in top opportunities" if ticker not in top_tickers else f"stop loss triggered ({unrealized_pl_pct:.1f}%)"
                trades.append({
                    "ticker": ticker,
                    "action": "sell",
                    "qty": "all",
                    "reason": reason
                })
                print(f"  SELL {ticker}: {reason}")

        # Entry logic: Buy top opportunities we don't already hold
        available_capital = buying_power * 0.95  # Use 95% of buying power
        positions_to_add = min(5 - len(current_tickers), 3)  # Max 5 total positions, add up to 3 new

        for opp in opportunities[:positions_to_add]:
            ticker = opp["ticker"]
            if ticker in current_tickers:
                continue

            # Position size based on score and regime
            position_size = min(
                max_position_size * portfolio_value,  # Regime-based max
                available_capital / max(1, positions_to_add),  # Split available capital
                opp["score"] / 10 * portfolio_value * 0.10  # Score-based sizing
            )

            if position_size > 100:  # Minimum $100 position
                trades.append({
                    "ticker": ticker,
                    "action": "buy",
                    "notional_value": round(position_size, 2),
                    "reason": f"score={opp['score']:.1f}, signals={','.join(opp['signals'][:2])}"
                })
                print(f"  BUY {ticker}: ${position_size:.0f} - {trades[-1]['reason']}")
                available_capital -= position_size

        print(f"\n=== Trade Plan Summary ===")
        print(f"Total Trades: {len(trades)}")
        print(f"Buys: {sum(1 for t in trades if t['action'] == 'buy')}")
        print(f"Sells: {sum(1 for t in trades if t['action'] == 'sell')}")

        return trades

    def execute_trades(self, trades: List[Dict]) -> List[Dict]:
        """Execute the generated trade plan"""
        results = []

        for trade in trades:
            ticker = trade["ticker"]
            action = trade["action"]
            side = OrderSide.BUY if action == "buy" else OrderSide.SELL

            try:
                # Handle sell all
                if action == "sell" and str(trade.get("qty")).lower() == "all":
                    self.trading_client.close_position(ticker)
                    results.append({
                        "trade": trade,
                        "status": "submitted",
                        "order_type": "close_position"
                    })
                    print(f"✓ Closed position: {ticker}")
                    continue

                # Handle buy with notional value
                order_data = {
                    "symbol": ticker,
                    "side": side,
                    "time_in_force": TimeInForce.DAY
                }

                if "notional_value" in trade:
                    order_data["notional"] = round(float(trade["notional_value"]), 2)
                elif "qty" in trade:
                    order_data["qty"] = float(trade["qty"])
                else:
                    results.append({
                        "trade": trade,
                        "status": "skipped",
                        "reason": "Missing qty/notional_value"
                    })
                    continue

                market_order_data = MarketOrderRequest(**order_data)
                market_order = self.trading_client.submit_order(order_data=market_order_data)

                results.append({
                    "trade": trade,
                    "status": "submitted",
                    "order_id": str(market_order.id)
                })
                print(f"✓ Order submitted: {action.upper()} {ticker}")

            except Exception as e:
                results.append({
                    "trade": trade,
                    "status": "failed",
                    "reason": str(e)
                })
                print(f"✗ Failed: {action.upper()} {ticker} - {e}")

        return results

    def run(self):
        """Main execution flow"""
        print("\n" + "="*60)
        print("ADVANCED LLM AGENT - Dev Account")
        print(f"Execution Time: {datetime.now(timezone.utc).isoformat()}")
        print("="*60)

        # Load all market data
        print("\n[1/6] Loading market data...")
        self.load_market_data()

        # Get account state
        print("\n[2/6] Fetching account state...")
        self.get_account_state()

        # Analyze regime
        print("\n[3/6] Analyzing market regime...")
        regime_data = self.analyze_regime()

        # Find opportunities
        print("\n[4/6] Analyzing opportunities...")
        opportunities = self.analyze_top_opportunities(regime_data)

        # Generate trade plan
        print("\n[5/6] Generating trade plan...")
        trades = self.generate_trade_plan(opportunities, regime_data)

        # Execute trades
        print("\n[6/6] Executing trades...")
        if not trades:
            print("No trades to execute - portfolio is optimal")
            results = []
        else:
            results = self.execute_trades(trades)

        # Write execution log
        self._write_log(results)

        print("\n" + "="*60)
        print("EXECUTION COMPLETE")
        print("="*60 + "\n")

    def _write_log(self, results: List[Dict]):
        """Write execution log"""
        payload = {
            "last_updated_utc": datetime.now(timezone.utc).isoformat(),
            "account": "dev",
            "strategy": "advanced_llm",
            "results": results
        }
        os.makedirs("data", exist_ok=True)
        with open("data/advanced_llm_execution.json", "w") as f:
            json.dump(payload, f, indent=2)


def main():
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        print("Error: ALPACA_API_KEY or ALPACA_SECRET_KEY not found in environment.")
        return

    agent = AdvancedLLMAgent(api_key, secret_key)
    agent.run()


if __name__ == "__main__":
    main()
