import json
import os

SYMBOL_STATE_FILE = "symbol_trade_state.json"

def load_symbol_state():
    if not os.path.exists(SYMBOL_STATE_FILE):
        return {}
    with open(SYMBOL_STATE_FILE, "r") as f:
        return json.load(f)

def save_symbol_state(state):
    with open(SYMBOL_STATE_FILE, "w") as f:
        json.dump(state, f)

def has_symbol_been_closed(symbol):
    state = load_symbol_state()
    return state.get(symbol, False)

def mark_symbol_as_closed(symbol):
    state = load_symbol_state()
    state[symbol] = True
    save_symbol_state(state)