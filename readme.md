# HAWK_JULY — Intelligent MT5 Trading Bot

## 🚀 Overview
This project is a robust, real-time MetaTrader 5 trading bot that:
- Trades multiple symbols using configurable pip/threshold logic
- Syncs with broker server time (not local system)
- Locks trading once profit is hit (global or symbol-specific)
- Supports hedging, FOK orders, logging, and Telegram notifications

---

## 🧩 Folder Structure & Responsibilities

| File / Module                | Purpose                                                                 |
|-----------------------------|-------------------------------------------------------------------------|
| `main.py`                   | Entry point, waits for 12:05, loops symbols, runs trade logic           |
| `config/config.py`          | `strategy_config`: pip size, thresholds, volume per symbol              |
| `core/trade_logic.py`       | Threshold checks, profit validation, decides trade action               |
| `core/trade_executor.py`    | Executes FOK trades (buy/sell/hedge/close) with readable magic          |
| `core/profit_guard.py`      | Tracks global daily $1000 profit and disables further trades            |
| `core/symbol_guard.py`      | Tracks per-symbol threshold-2 closures and prevents re-entry            |
| `mt5/deals.py`              | Gets open positions and today's profit via MT5 history                  |
| `mt5/price_fetcher.py`      | Fetches MT5 server-aligned prices: `start_price`, `latest_high`, `tick`|
| `utils/time_utils.py`       | Waits until MT5 server reaches 12:05 to fetch daily start candle        |
| `utils/logger.py`           | Logs trade activity to `logs/trades_YYYYMMDD.log`                       |
| `utils/notifier.py`         | (Optional) Sends Telegram alerts for trades or failures                 |

---

## 🛠️ How It Works

1. **Bot starts at any time**
2. It waits until **12:05 MT5 server time** to fetch daily `start_price`
3. For each symbol:
   - Calculates pip difference, current vs. start vs. high
   - If `threshold >= 1` → entry (if no positions)
   - If `threshold >= 2` → exit (if positions) and locks symbol
   - If `profit ≥ $1000` (total) → closes everything and stops
4. All trades are **FOK orders** with **unique HAWK IDs** and **logged**

---

## ⚙️ Setup Instructions

1. ✅ Install MetaTrader5 Python module:
   ```bash
   pip install MetaTrader5