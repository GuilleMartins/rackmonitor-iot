import numpy as np
from datetime import datetime, timedelta

def predict_future_trends(history: list, steps_ahead: int = 5) -> list:
    if len(history) < 5:
        return []

    temps = [item['temperature'] for item in history]
    hums = [item['humidity'] for item in history]
    n = len(temps)
    x = np.arange(n)

    slope_temp, intercept_temp = np.polyfit(x, temps, 1)
    slope_hum, intercept_hum = np.polyfit(x, hums, 1)

    last_ts_str = history[-1]['timestamp']
    try:
        last_time = datetime.strptime(last_ts_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        last_time = datetime.now()

    forecasts = []
    for i in range(1, steps_ahead + 1):
        future_x = n - 1 + i
        pred_temp = round(float(slope_temp * future_x + intercept_temp), 1)
        pred_hum = round(float(slope_hum * future_x + intercept_hum), 1)
        future_time = (last_time + timedelta(seconds=i * 2)).strftime("%H:%M:%S")

        forecasts.append({
            "timestamp": future_time,
            "pred_temperature": max(0.0, pred_temp),
            "pred_humidity": min(100.0, max(0.0, pred_hum))
        })

    return forecasts