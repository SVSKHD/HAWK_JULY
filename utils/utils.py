import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def get_log_file_path():
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(LOG_DIR, f"trades_{date_str}.log")


def log_trade(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    print(full_message)  # Optional: remove if logging only to file

    with open(get_log_file_path(), "a") as f:
        f.write(full_message + "\n")
