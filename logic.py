from config import strategy_config


def calculate_pip_difference(start, current, latest_high, pip_size):
    pip_diff = (current - start) / pip_size
    direction = "neutral"
    immediate_direction = "neutral"
    latest_high_difference = (latest_high - current) / pip_size

    if latest_high_difference > 0:
        immediate_direction = "down"
    elif latest_high_difference < 0:
        immediate_direction = "up"

    if pip_diff > 0:
        direction = "up"
    elif pip_diff < 0:
        direction = "down"

    return {
        "pip_diff": round(pip_diff, 5),
        "direction": direction,
        "immediate_direction": immediate_direction
    }


class TradeLogic:
    def __init__(self, symbol, start, current, latest_high, positions, deals):
        self.symbol = symbol
        self.config = strategy_config.get(symbol, {})
        self.start = start
        self.current = current
        self.latest_high = latest_high
        self.positions = positions
        self.results = {}

    def get_details(self):
        data = calculate_pip_difference(
            self.start,
            self.current,
            self.latest_high,
            self.config.get("pip_size", 0.0001)
        )
        self.results = {
            "symbol": self.symbol,
            "start": self.start,
            "current": self.current,
            "latest_high": self.latest_high,
            "pip_diff": data["pip_diff"],
            "direction": data["direction"],
            "immediate_direction": data["immediate_direction"],
            "positions": self.positions
        }
        return self.results

    def decide_trades(self):
        if len(self.positions) > 0:
            return "Positions present — Hedging enabled"
        else:
            return "No positions — Trading enabled"

    def execute_trades(self):
        decision = self.decide_trades()
        print(decision)
        return decision


# Example usage
trade = TradeLogic("XAGUSD", 31.000, 31.500, 32.000, [{"type": "buy", "volume": 1.0}, {"type": "sell", "volume": 0.5}], [{"type": "buy", "volume": 1.0}, {"type": "sell", "volume": 0.5}])
results = trade.get_details()
trade_decision = trade.execute_trades()
print(results)
print("Trade decision:", trade_decision)
