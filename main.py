import time
from pytz import timezone
from datetime import datetime
from mt5.price_fetcher import get_start_price, get_current_price, get_recent_high, get_server_datetime
from mt5.deals import get_current_open_positions, get_today_profit_from_history
from core.trade_logic import TradeLogic
from core.profit_guard import reset_daily_profit_flag
from utils.time_utils import wait_for_mt5_time

symbols = ["XAGUSD", "XAUUSD", "USDJPY", "EURUSD", "GBPUSD"]
IST = timezone("Asia/Kolkata")

def is_weekend_pause(server_time):
    ist_time = server_time.astimezone(IST)
    weekday = ist_time.weekday()  # Monday = 0, Saturday = 5
    hour = ist_time.hour
    return (weekday == 5 and hour >= 10) or weekday == 6

def print_time_banner(server_time):
    ist_time = server_time.astimezone(IST)
    print("\n📅 New Trading Day")
    print(f"🕒 MT5 Server Time: {server_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕒 IST Time       : {ist_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def main_loop():
    while True:
        server_time = get_server_datetime()

        # ⏸️ Check for weekend pause
        if is_weekend_pause(server_time):
            print("[🛌] Weekend pause. Market closed. Sleeping 5 minutes...")
            time.sleep(300)
            continue

        # 🕒 Wait for new trading day 12:05 MT5 server time
        wait_for_mt5_time("EURUSD", 12, 5)
        server_time = get_server_datetime()
        print_time_banner(server_time)

        # 🔄 Reset daily state
        reset_daily_profit_flag()

        # 🟢 Fetch start prices for today
        start_prices = {}
        for symbol in symbols:
            try:
                start_prices[symbol] = get_start_price(symbol)
                print(f"[✅] Start price for {symbol}: {start_prices[symbol]}")
            except Exception as e:
                print(f"[⚠️] Failed to fetch start price for {symbol}: {e}")
                start_prices[symbol] = None

        print("\n[🔁] Starting live price monitoring...\n")

        # 📡 Live price processing loop (until next day restart)
        while True:
            try:
                server_now = get_mt5_server_time("EURUSD")
                if server_now.hour == 0 and server_now.minute < 5:
                    print("[🔁] Preparing for new trading day soon...")
                    time.sleep(60)
                    break  # break inner loop to reset at 12:05

                if is_weekend_pause(server_now):
                    print("[🛌] Market paused. Rechecking in 5 minutes.")
                    time.sleep(300)
                    break

                all_positions, _ = get_current_open_positions()
                today_profit, all_deals, _ = get_today_profit_from_history()

                for symbol in symbols:
                    start = start_prices.get(symbol)
                    if start is None:
                        continue

                    try:
                        ask, bid = get_current_price(symbol)
                        current = ask
                        recent_high = get_recent_high(symbol)

                        symbol_positions = [p for p in all_positions if p["symbol"] == symbol]
                        symbol_deals = [d for d in all_deals if d["symbol"] == symbol]

                        print(f"[{symbol}] Start: {start:.5f}, Current: {current:.5f}")
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
                return


if __name__ == "__main__":
    main_loop()
