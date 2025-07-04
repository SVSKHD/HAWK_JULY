import MetaTrader5 as mt5
from datetime import datetime


def ensure_mt5_initialized():
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")


def get_server_datetime():
    ensure_mt5_initialized()
    timestamp = mt5.time()
    if timestamp is None:
        raise RuntimeError("Failed to fetch MT5 server time.")
    return datetime.fromtimestamp(timestamp)


def get_start_price(symbol):
    ensure_mt5_initialized()

    now_server = get_server_datetime()
    candle_time = datetime(now_server.year, now_server.month, now_server.day, 12, 5)

    rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, candle_time, 1)
    if not rates or len(rates) == 0:
        raise ValueError(f"No rates found for {symbol} at 12:05")

    return rates[0]["open"]


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
    if not rates or len(rates) == 0:
        raise ValueError(f"No recent candles for {symbol}")

    return max(r["high"] for r in rates)