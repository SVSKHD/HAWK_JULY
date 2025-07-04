from utils import calculate_pip_difference
from core.profit_guard import has_reached_daily_profit, set_reached_daily_profit
from core.symbol_guard import has_symbol_been_closed, mark_symbol_as_closed
from config.config import strategy_config


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
            threshold = self.config.get("threshold")
        )
        self.results = {
            "symbol": self.symbol,
            "start": self.start,
            "current": self.current,
            "latest_high": self.latest_high,
            "pip_diff": data["pip_diff"],
            "direction": data["direction"],
            "immediate_direction": data["immediate_direction"],
            "threshold":data["threshold"],
            "positions": self.positions
        }
        return self.results

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
            if threshold >= 2:
                mark_symbol_as_closed(self.symbol)
                return f"[📉] Threshold ≥ 2 reached. Closing positions for {self.symbol} and locking it."
            return f"[ℹ️] {self.symbol}: Positions present — No close signal yet."

        if threshold >= 1:
            return f"[📈] Threshold ≥ 1 reached. Place trade for {self.symbol}."

        return f"[🕒] {self.symbol}: Waiting — Thresholds not met."

    def execute_trades(self):
        decision = self.decide_trades()
        print(f"[{self.symbol}] Decision: {decision}")
        return decision


# Test run with mock data for EURUSD
if __name__ == "__main__":
    # Mock values for testing
    symbol = "EURUSD"
    start_price = 1.0820
    current_price = 1.0850
    latest_high = 1.0860
    mock_positions = [{"type": "buy", "volume": 1.0, "profit": 500.0}, {"type": "sell", "volume": 1.0, "profit": 300.0}]
    mock_deals = [{"type": "buy", "volume": 1.0, "profit": 200.0, "symbol": "EURUSD", "price": 1.0830}]
    today_profit = 250.0  # From history_deals

    trade = TradeLogic(
        symbol=symbol,
        start=start_price,
        current=current_price,
        latest_high=latest_high,
        positions=mock_positions,
        deals=mock_deals,
        today_profit=today_profit
    )

    results = trade.get_details()
    decision = trade.execute_trades()

    print("Trade details:", results)
    print("Trade decision:", decision)
