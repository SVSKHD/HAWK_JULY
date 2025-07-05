import time
from mt5.price_fetcher import get_start_price, get_current_price, get_recent_high
from mt5.deals import get_current_open_positions, get_today_profit_from_history
from core.trade_logic import TradeLogic
from core.profit_guard import reset_daily_profit_flag, has_reached_daily_profit

# Symbols to monitor
symbols = ["XAGUSD", "XAUUSD", "USDJPY", "EURUSD", "GBPUSD"]

# 🔄 Reset daily profit status at startup
reset_daily_profit_flag()

# ⏳ Fetch start prices once at boot
start_prices = {}
for symbol in symbols:
    try:
        start_prices[symbol] = get_start_price(symbol)
        print(f"[✅] Start price for {symbol}: {start_prices[symbol]}")
    except Exception as e:
        print(f"[⚠️] Failed to fetch start price for {symbol}: {e}")
        start_prices[symbol] = None

print("\n[🔁] Starting live price monitoring...\n")

# 🔁 Continuous monitoring loop
while True:
    try:
        # 🔄 Get updated open positions and today's profit every second
        all_positions, _ = get_current_open_positions()
        today_profit, all_deals, _ = get_today_profit_from_history()

        for symbol in symbols:
            start = start_prices.get(symbol)
            if start is None:
                continue  # skip symbol if no start price available

            try:
                ask, bid = get_current_price(symbol)
                current = ask  # use ask as "current" execution price
                recent_high = get_recent_high(symbol)

                # Filter today's symbol-specific data
                symbol_positions = [p for p in all_positions if p["symbol"] == symbol]
                symbol_deals = [d for d in all_deals if d["symbol"] == symbol]

                # 🧠 Apply trading logic
                logic = TradeLogic(
                    symbol=symbol,
                    start=start,
                    current=current,
                    latest_high=recent_high,
                    positions=symbol_positions,
                    deals=symbol_deals,
                    today_profit=today_profit
                )

                logic.get_details()
                logic.execute_trades()

            except Exception as e:
                print(f"[⚠️] Failed to process {symbol}: {e}")

        time.sleep(1)

    except KeyboardInterrupt:
        print("\n[🛑] Monitoring stopped by user.")
        break
