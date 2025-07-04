import MetaTrader5 as mt5
from datetime import datetime
import time


def ensure_mt5_initialized():
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")


def get_mt5_server_time(symbol):
    ensure_mt5_initialized()
    tick = mt5.symbol_info_tick(symbol)
    if tick is None or not hasattr(tick, "time"):
        raise RuntimeError(f"Unable to fetch server tick time for {symbol}")
    return datetime.fromtimestamp(tick.time)


def wait_for_mt5_time(symbol, target_hour=12, target_minute=5):
    print(f"[⏳] Waiting for server time {target_hour:02d}:{target_minute:02d}…")
    while True:
        now = get_mt5_server_time(symbol)
        if now.hour > target_hour or (now.hour == target_hour and now.minute >= target_minute):
            print(f"[✅] Server time reached: {now.strftime('%H:%M:%S')}")
            return now
        time.sleep(10)
