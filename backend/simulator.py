import requests
import time
import random

API_URL = "http://localhost:8000/api/v1/telemetry"
DEVICE_ID = "ESP32_RACK_SIMULATED"

def calculate_status(temp: float, hum: float, motion: bool) -> str:
    if temp >= 35.0 or hum >= 80.0 or motion:
        return "CRITICO"
    elif temp >= 30.0 or hum >= 70.0:
        return "ADVERTENCIA"
    else:
        return "NORMAL"

def run_simulation():
    print(f"🚀 Iniciando simulación de tráfico IoT para {DEVICE_ID}...")
    print(f"📡 Enviando datos a: {API_URL}")
    print("Presiona Ctrl + C para detener.\n")

    base_temp = 25.0
    base_hum = 50.0

    try:
        while True:
            temp = round(base_temp + random.uniform(-1.0, 1.5), 1)
            hum = round(base_hum + random.uniform(-2.0, 2.0), 1)
            motion = random.random() < 0.10

            if random.random() < 0.05:
                temp = round(random.uniform(35.5, 41.0), 1)

            status = calculate_status(temp, hum, motion)

            payload = {
                "device_id": DEVICE_ID,
                "temperature": temp,
                "humidity": hum,
                "motion": motion,
                "status": status
            }

            try:
                response = requests.post(API_URL, json=payload, timeout=2)
                if response.status_code == 200:
                    print(f"✅ [POST 200] Temp: {temp}°C | Hum: {hum}% | Mov: {motion} | Estado: {status}")
                else:
                    print(f"⚠️ [Error {response.status_code}] {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de conexión con la API: {e}")

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 Simulación detenida por el usuario.")

if __name__ == "__main__":
    run_simulation()