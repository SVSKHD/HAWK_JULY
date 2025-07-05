# core/notifier.py
import requests

# === Define your webhooks ===
DISCORD_HOOKS = {
    "critical": "https://discord.com/api/webhooks/xxx/critical",
    "update": "https://discord.com/api/webhooks/xxx/update",
    "daily": "https://discord.com/api/webhooks/xxx/daily"
}

# Cache for throttling repeat messages (only for "update")
_last_sent_update = {}

def send_discord_notification(message, type="update", symbol=None):
    url = DISCORD_HOOKS.get(type)
    if not url:
        print(f"[❌] No webhook defined for type '{type}'")
        return

    # Limit repeated 'update' messages per symbol
    if type == "update":
        key = symbol or "global"
        if _last_sent_update.get(key) == message:
            return  # Skip repeated message
        _last_sent_update[key] = message  # Update only if new

    data = {
        "username": f"HawkBot | {type.upper()}",
        "content": f"**{symbol}** - {message}" if symbol else message
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code != 204:
            print(f"[⚠️] Discord error [{type}]: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[❌] Discord webhook error [{type}]: {e}")
