import MetaTrader5 as mt5
from datetime import datetime, timedelta


def ensure_mt5_initialized():
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")


def get_server_datetime():
    ensure_mt5_initialized()
    last_tick = mt5.symbol_info_tick("EURUSD")  # Use a valid symbol
    if last_tick is None or last_tick.time is None:
        raise RuntimeError("Failed to fetch MT5 server time.")
    return datetime.fromtimestamp(last_tick.time)



def get_start_price(symbol):
    ensure_mt5_initialized()

    now_server = get_server_datetime()
    attempt_day = now_server

    while True:
        candle_time = datetime(attempt_day.year, attempt_day.month, attempt_day.day, 12, 5)

        rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, candle_time, 1)
        if rates is not None and len(rates) > 0:
            return rates[0]["open"]

        # Go back one day
        attempt_day -= timedelta(days=1)


def get_current_price(symbol):
    ensure_mt5_initialized()

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError(f"No tick data for {symbol}")
    return tick.ask, tick.bid


def get_recent_high(symbol, candles=5):
    ensure_mt5_initialized()
    now_server = get_server_datetime()

    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, now_server, candles)
    if rates is None or len(rates) == 0:
        raise ValueError(f"No recent candles for {symbol}")

    return max(r["high"] for r in rates)