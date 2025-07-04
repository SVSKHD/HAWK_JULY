from mt5.deals import get_current_open_positions, get_today_profit_from_history
from core.trade_logic import TradeLogic
from config.config import strategy_config
from collections import defaultdict

# Fetch data
positions, _ = get_current_open_positions()
today_profit, deals_list, _ = get_today_profit_from_history()

# Group by symbol
symbol_positions = defaultdict(list)
for pos in positions:
    symbol_positions[pos["symbol"]].append(pos)

# Replace these with live price data fetching if needed
mock_price_data = {
    "XAGUSD": {"start": 31.000, "current": 31.500, "latest_high": 32.000},
    "EURUSD": {"start": 1.0820, "current": 1.0850, "latest_high": 1.0860},
}

# Loop through configured symbols
for symbol in strategy_config.keys():
    price_info = mock_price_data.get(symbol)
    if not price_info:
        continue

    trade = TradeLogic(
        symbol=symbol,
        start=price_info["start"],
        current=price_info["current"],
        latest_high=price_info["latest_high"],
        positions=symbol_positions.get(symbol, []),
        deals=deals_list,
        today_profit=today_profit
    )
    trade.get_details()
    trade.execute_trades()