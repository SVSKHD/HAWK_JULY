import MetaTrader5 as mt5
from datetime import datetime


def get_current_open_positions(symbol=None):
    """
    Returns:
    - Parsed position list with symbol, type, volume, price, profit, ticket
    - Raw MT5 positions object
    """
    if not mt5.initialize():
        raise RuntimeError("MT5 not initialized")

    raw_positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()

    result = []
    if raw_positions is None:
        print("[❌] No open positions found or error occurred.")
        return result, []

    for pos in raw_positions:
        result.append({
            "symbol": pos.symbol,
            "type": "buy" if pos.type == mt5.ORDER_TYPE_BUY else "sell",
            "volume": pos.volume,
            "price_open": pos.price_open,
            "profit": pos.profit,
            "ticket": pos.ticket
        })

    return result, raw_positions


def get_today_profit_from_history():
    """
    Returns:
    - Total profit for today
    - Parsed deals list with symbol, type, volume, profit, price
    - Raw MT5 deals list
    """
    if not mt5.initialize():
        raise RuntimeError("MT5 not initialized")

    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)

    raw_deals = mt5.history_deals_get(today_start, now)
    if raw_deals is None or len(raw_deals) == 0:
        print("[ℹ️] No history deals found for today.")
        return 0.0, [], []

    profit_sum = 0.0
    deals_list = []

    for deal in raw_deals:
        if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
            profit_sum += deal.profit
            deals_list.append({
                "symbol": deal.symbol,
                "type": "buy" if deal.type == mt5.DEAL_TYPE_BUY else "sell",
                "volume": deal.volume,
                "profit": deal.profit,
                "price": deal.price
            })

    return round(profit_sum, 2), deals_list, raw_deals
