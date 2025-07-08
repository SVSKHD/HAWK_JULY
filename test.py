from datetime import datetime
import MetaTrader5 as mt5

mt5.initialize()
tick = mt5.symbol_info_tick("EURUSD")
server_time = datetime.fromtimestamp(tick.time)

print("MT5 server raw timestamp:", tick.time)
print("Python converted time     :", server_time)
