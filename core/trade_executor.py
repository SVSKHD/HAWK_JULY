import MetaTrader5 as mt5
from time import sleep
from datetime import datetime
import zlib
from config.config import strategy_config
from utils.utils import log_trade


def generate_trade_identifiers(symbol, trade_type, is_hedge=False):
    date_str = datetime.now().strftime("%Y%m%d")
    tag_type = "HEDGE" if is_hedge else "TRADE"
    readable_id = f"HAWK-TRADE-{tag_type}-{symbol}-{trade_type.upper()}-{date_str}"
    # Generate a reproducible integer magic from the readable_id
    magic = zlib.crc32(readable_id.encode()) & 0xFFFFFFFF
    return readable_id, magic


def place_trade(symbol, trade_type, volume=None):
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")

    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"[❌] No tick data for {symbol}")
        return False

    volume = volume or strategy_config.get(symbol, {}).get("volume", 0.5)
    readable_id, magic = generate_trade_identifiers(symbol, trade_type, is_hedge=False)

    price = tick.ask if trade_type == "buy" else tick.bid
    order_type = mt5.ORDER_TYPE_BUY if trade_type == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": magic,
        "type_filling": mt5.ORDER_FILLING_FOK,
        "type_time": mt5.ORDER_TIME_GTC
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        msg = f"❌ Trade failed for {readable_id} ({symbol}): {result.retcode}"
        log_trade(msg)
        return False

    msg = f"✅ Trade placed: {readable_id} @ {price} | Vol: {volume} | Magic: {magic}"
    log_trade(msg)
    return True


def place_hedge_trade(symbol, trade_type, volume=None):
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")

    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print(f"[❌] No tick data for {symbol}")
        return False

    volume = volume or strategy_config.get(symbol, {}).get("volume", 0.5)
    readable_id, magic = generate_trade_identifiers(symbol, trade_type, is_hedge=True)

    price = tick.ask if trade_type == "buy" else tick.bid
    order_type = mt5.ORDER_TYPE_BUY if trade_type == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": magic,
        "type_filling": mt5.ORDER_FILLING_FOK,
        "type_time": mt5.ORDER_TIME_GTC
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        msg = f"❌ Trade failed for {readable_id} ({symbol}): {result.retcode}"
        log_trade(msg)
        return False

    msg = f"✅ Trade placed: {readable_id} @ {price} | Vol: {volume} | Magic: {magic}"
    log_trade(msg)
    return True


def close_trade_by_symbol(symbol):
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")

    positions = mt5.positions_get(symbol=symbol)
    if positions is None or len(positions) == 0:
        msg = f"[ℹ️] No positions to close for {symbol}"
        log_trade(msg)
        return

    for pos in positions:
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            msg = f"[❌] No tick data for {symbol} during close"
            log_trade(msg)
            continue

        trade_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = tick.bid if trade_type == mt5.ORDER_TYPE_SELL else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": trade_type,
            "position": pos.ticket,
            "price": price,
            "deviation": 10,
            "magic": 202500,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_GTC
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            msg = f"[❌] Failed to close position {pos.ticket} on {symbol}: {result.retcode}"
            log_trade(msg)
        else:
            msg = f"[✅] Closed position {pos.ticket} on {symbol} @ {price} | Vol: {pos.volume}"
            log_trade(msg)
def close_all_trades():
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")

    positions = mt5.positions_get()
    if not positions:
        log_trade("[ℹ️] No open positions to close.")
        return

    for pos in positions:
        symbol = pos.symbol
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            msg = f"[❌] No tick data for {symbol} during global close"
            log_trade(msg)
            continue

        trade_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = tick.bid if trade_type == mt5.ORDER_TYPE_SELL else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": trade_type,
            "position": pos.ticket,
            "price": price,
            "deviation": 10,
            "magic": 202500,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_GTC
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            msg = f"[❌] Failed to close position {pos.ticket} on {symbol}: {result.retcode}"
            log_trade(msg)
        else:
            msg = f"[✅] Closed position {pos.ticket} on {symbol} @ {price} | Vol: {pos.volume}"
            log_trade(msg)

        sleep(0.5)  # optional delay