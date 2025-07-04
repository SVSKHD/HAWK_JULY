import json
import os

PROFIT_STATE_FILE = "daily_profit_state.json"

def has_reached_daily_profit():
    if not os.path.exists(PROFIT_STATE_FILE):
        return False
    with open(PROFIT_STATE_FILE, "r") as f:
        data = json.load(f)
        return data.get("reached", False)

def set_reached_daily_profit():
    with open(PROFIT_STATE_FILE, "w") as f:
        json.dump({"reached": True}, f)