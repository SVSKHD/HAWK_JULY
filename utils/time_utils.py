import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time


def ensure_mt5_initialized():
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")


from datetime import datetime, timedelta

def get_server_datetime(symbol="EURUSD"):
    ensure_mt5_initialized()
    tick = mt5.symbol_info_tick(symbol)
    if not tick or not tick.time:
        print("[⚠️] No valid server tick time. Falling back to system UTC time.")
        return datetime.utcnow() + timedelta(hours=3)  # fallback to UTC+3
    # Convert tick time from UTC to UTC+3
    return datetime.utcfromtimestamp(tick.time) + timedelta(hours=3)



def wait_for_mt5_time(symbol="EURUSD", target_hour=12, target_minute=5):
    """
    Waits until the server time reaches the given hour and minute.
    """
    print(f"[⏳] Waiting for MT5 server time to reach {target_hour:02d}:{target_minute:02d}...")
    while True:
        now = get_server_datetime(symbol)
        print(f"[🕒] Current server time: {now.strftime('%H:%M:%S')}")
        if now.hour > target_hour or (now.hour == target_hour and now.minute >= target_minute):
            print(f"[✅] Server time reached: {now.strftime('%H:%M:%S')}")
            return now
        time.sleep(10)
