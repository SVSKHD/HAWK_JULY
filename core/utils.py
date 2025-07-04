def calculate_pip_difference(start, current, latest_high, pip_size, threshold):
    pip_diff = (current - start) / pip_size
    direction = "neutral"
    immediate_direction = "neutral"
    latest_high_difference = (latest_high - current) / pip_size

    calculated_threshold = pip_diff/threshold

    if latest_high_difference > 0:
        immediate_direction = "down"
    elif latest_high_difference < 0:
        immediate_direction = "up"

    if pip_diff > 0:
        direction = "up"
    elif pip_diff < 0:
        direction = "down"

    return {
        "pip_diff": round(pip_diff, 5),
        "direction": direction,
        "immediate_direction": immediate_direction,
        "threshold":calculated_threshold
    }