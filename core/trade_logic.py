from core.utils import calculate_pip_difference
from core.profit_guard import has_reached_daily_profit, set_reached_daily_profit
from core.symbol_guard import has_symbol_been_closed, mark_symbol_as_closed
from config.config import strategy_config
from core.trade_executor import place_hedge_trade, close_trade_by_symbol, place_trade


class TradeLogic:
    def __init__(self, symbol, start, current, latest_high, positions, deals, today_profit):
        self.symbol = symbol
        self.config = strategy_config.get(symbol, {})
        self.start = start
        self.current = current
        self.latest_high = latest_high
        self.positions = positions
        self.deals = deals
        self.today_profit = today_profit
        self.results = {}

    def get_details(self):
        data = calculate_pip_difference(
            self.start,
            self.current,
            self.latest_high,
            self.config.get("pip_size", 0.0001),
            threshold=self.config.get("threshold")
        )
        self.results = {
            "symbol": self.symbol,
            "start": self.start,
            "current": self.current,
            "latest_high": self.latest_high,
            "pip_diff": data["pip_diff"],
            "direction": data["direction"],
            "immediate_direction": data["immediate_direction"],
            "threshold": data["threshold"],
            "positions": self.positions
        }
        return self.results

    def has_hedge_pair(self):
        types = {p["type"] for p in self.positions}
        return "buy" in types and "sell" in types

    def should_place_hedge(self):
        if len(self.positions) != 1:
            return False
        solo = self.positions[0]
        if solo["type"] == "buy" and self.current < self.start:
            return True
        if solo["type"] == "sell" and self.current > self.start:
            return True
        return False

    def should_close_hedge(self):
        if self.has_hedge_pair():
            net_profit = sum([p.get("profit", 0) for p in self.positions])
            return net_profit >= 0
        return False

    def decide_trades(self):
        if has_reached_daily_profit():
            return "[🛑] Daily profit already reached. Skipping trades."

        if has_symbol_been_closed(self.symbol):
            return f"[⛔] {self.symbol} already closed due to threshold ≥ 2. No more trades."

        open_position_profit = sum([p.get("profit", 0) for p in self.positions])
        total_today_profit = round(self.today_profit + open_position_profit, 2)

        if total_today_profit >= 1000:
            set_reached_daily_profit()
            return f"[✅] Profit target reached (${total_today_profit}). Close all positions."

        threshold = self.results.get("threshold", 0)

        if self.positions:
            if self.should_close_hedge():
                mark_symbol_as_closed(self.symbol)
                close_trade_by_symbol(self.symbol)
                return f"[✅] Hedge neutralized. Closed all {self.symbol} positions."
            elif threshold >= 2:
                mark_symbol_as_closed(self.symbol)
                close_trade_by_symbol(self.symbol)
                return f"[📉] Threshold ≥ 2 reached. Closing positions for {self.symbol} and locking it."
            elif self.should_place_hedge():
                solo_type = self.positions[0]["type"]
                hedge_type = "sell" if solo_type == "buy" else "buy"
                place_hedge_trade(self.symbol, hedge_type)
                return f"[🔀] Hedge placed for {self.symbol} in {hedge_type.upper()} direction."
            return f"[ℹ️] {self.symbol}: Positions present — No close or hedge signal yet."

        if threshold >= 1 and not self.positions:
            direction = self.results.get("direction")  # use primary trade direction
            if direction in ["buy", "sell"]:
                success = place_trade(self.symbol, direction)
                if success:
                    return f"[✅] Entry trade placed for {self.symbol} in {direction.upper()} direction."
                else:
                    return f"[❌] Failed to place entry trade for {self.symbol}."

        return f"[🕒] {self.symbol}: Waiting — Thresholds not met."

    def execute_trades(self):
        decision = self.decide_trades()
        print(f"[{self.symbol}] Decision: {decision}")
        return decision


# # Test run with mock data for EURUSD
# if __name__ == "__main__":
#     # Mock values for testing
#     symbol = "EURUSD"
#     start_price = 1.0820
#     current_price = 1.0800  # simulate market reversal for hedge
#     latest_high = 1.0860
#     mock_positions = [{"type": "buy", "volume": 0.5, "profit": -15.0}]  # one losing trade
#     mock_deals = [{"type": "buy", "volume": 0.5, "profit": -15.0, "symbol": "EURUSD", "price": 1.0825}]
#     today_profit = 0.0
#
#     trade = TradeLogic(
#         symbol=symbol,
#         start=start_price,
#         current=current_price,
#         latest_high=latest_high,
#         positions=mock_positions,
#         deals=mock_deals,
#         today_profit=today_profit
#     )
#
#     results = trade.get_details()
#     decision = trade.execute_trades()
#
#     print("Trade details:", results)
#     print("Trade decision:", decision)