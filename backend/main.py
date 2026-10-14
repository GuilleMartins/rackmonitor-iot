from forecasting import predict_future_trends
from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import deque
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import io

# Módulos de Base de Datos
import models
from database import engine, get_db

# Crear tablas en la BD automáticamente al arrancar
models.Base.metadata.create_all(bind=engine)

# =====================================================
# CONFIGURACIÓN DE CORREO SMTP
# =====================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "alertasdashboard050@gmail.com"
SENDER_PASSWORD = "xhwomxhbdregrurl"  # Contraseña de aplicación de 16 caracteres
RECIPIENT_EMAIL = "guilleaugustomartins@gmail.com"

LAST_EMAIL_SENT = None
EMAIL_COOLDOWN_MINUTES = 5

app = FastAPI(title="RackMonitor IoT API", version="2.0")

MAX_HISTORY = 15
history_telemetry = deque(maxlen=MAX_HISTORY)

latest_telemetry = {
    "device_id": "N/A",
    "temperature": 0.0,
    "humidity": 0.0,
    "motion": False,
    "status": "SIN DATOS",
    "timestamp": "--"
}

class SensorData(BaseModel):
    device_id: str
    temperature: float
    humidity: float
    motion: bool
    status: str
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RackMonitor IoT 2.0 - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-slate-900 text-white min-h-screen p-8 font-sans">
    <div class="max-w-5xl mx-auto space-y-6">
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-700 pb-4 gap-4">
            <div>
                <h1 class="text-3xl font-bold tracking-tight text-blue-400">RackMonitor IoT 2.0</h1>
                <p class="text-slate-400 text-sm">Monitoreo Ambiental e Intrusión en Tiempo Real</p>
            </div>
            <div class="flex items-center gap-3">
                <a href="/api/v1/telemetry/export-csv" 
                   class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-600 rounded-lg text-sm font-semibold transition flex items-center gap-2 shadow">
                    📥 Exportar CSV
                </a>
                <div id="status-badge" class="px-4 py-2 rounded-full text-sm font-bold bg-slate-800 text-slate-300">
                    ESPERANDO DATOS...
                </div>
            </div>
        </header>

        <main class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg">
                <p class="text-slate-400 text-sm font-medium">Temperatura</p>
                <div class="flex items-baseline mt-2">
                    <span id="temp-val" class="text-4xl font-extrabold text-amber-400">--</span>
                    <span class="text-xl text-slate-400 ml-1">°C</span>
                </div>
            </div>

            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg">
                <p class="text-slate-400 text-sm font-medium">Humedad</p>
                <div class="flex items-baseline mt-2">
                    <span id="hum-val" class="text-4xl font-extrabold text-blue-400">--</span>
                    <span class="text-xl text-slate-400 ml-1">%</span>
                </div>
            </div>

            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg">
                <p class="text-slate-400 text-sm font-medium">Sensor PIR (Movimiento)</p>
                <div class="mt-2">
                    <span id="motion-val" class="text-2xl font-bold text-slate-300">--</span>
                </div>
            </div>
        </main>

        <section class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-bold text-slate-300">Tendencia Ambiental y Proyección (Forecasting)</h2>
                <span class="text-xs text-amber-400 bg-amber-900/40 px-3 py-1 rounded-full border border-amber-700/50">
                    -- Línea punteada = Predicción
                </span>
            </div>
            <div class="relative h-72 w-full">
                <canvas id="telemetryChart"></canvas>
            </div>
        </section>
<!-- Nueva Sección: Tabla de Historial -->
        <section class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg">
            <h2 class="text-lg font-bold text-slate-300 mb-4">Registro de Eventos Recientes</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-600 text-slate-400 text-sm">
                            <th class="py-3 px-4">Hora</th>
                            <th class="py-3 px-4">Dispositivo</th>
                            <th class="py-3 px-4">Temp (°C)</th>
                            <th class="py-3 px-4">Humedad (%)</th>
                            <th class="py-3 px-4">Estado</th>
                        </tr>
                    </thead>
                    <tbody id="history-table-body" class="text-sm text-slate-300">
                        <!-- Las filas se inyectarán dinámicamente aquí -->
                    </tbody>
                </table>
            </div>
        </section>
        <footer class="text-center text-xs text-slate-500">
            Última actualización: <span id="last-update">Nunca</span>
        </footer>
    </div>

    <script>
        const ctx = document.getElementById('telemetryChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Temperatura (°C)',
                        data: [],
                        borderColor: '#fbbf24',
                        backgroundColor: 'rgba(251, 191, 36, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: 'Predicción Temp (°C)',
                        data: [],
                        borderColor: '#f59e0b',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: 'Humedad (%)',
                        data: [],
                        borderColor: '#60a5fa',
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                },
                plugins: { legend: { labels: { color: '#f8fafc' } } }
            }
        });

async function fetchHistoryAndForecast() {
            try {
                const resHist = await fetch('/api/v1/telemetry/history');
                const resFore = await fetch('/api/v1/telemetry/forecast');
                if (!resHist.ok) return;

                const history = await resHist.json();
                const forecast = resFore.ok ? await resFore.json() : [];

                if (history.length > 0) {
                    const latest = history[history.length - 1];
                    updateUI(latest);
                    updateChart(history, forecast);
                    updateTable(history); // <--- AGREGAR ESTA LÍNEA
                }
            } catch (err) {
                console.error("Error al obtener datos:", err);
            }
        }

        function updateUI(data) {
            document.getElementById('temp-val').innerText = Number(data.temperature).toFixed(1);
            document.getElementById('hum-val').innerText = Number(data.humidity).toFixed(1);
            
            const motionElem = document.getElementById('motion-val');
            motionElem.innerText = data.motion ? "DETECTADO" : "NORMAL";
            motionElem.className = data.motion ? "text-2xl font-bold text-red-500 animate-pulse" : "text-2xl font-bold text-emerald-400";

            const badge = document.getElementById('status-badge');
            badge.innerText = data.status;

            if (data.status === 'CRITICO') {
                badge.className = "px-4 py-2 rounded-full text-sm font-bold bg-red-600 text-white animate-bounce";
            } else if (data.status === 'ADVERTENCIA') {
                badge.className = "px-4 py-2 rounded-full text-sm font-bold bg-amber-500 text-black";
            } else {
                badge.className = "px-4 py-2 rounded-full text-sm font-bold bg-emerald-500 text-slate-950";
            }

            document.getElementById('last-update').innerText = data.timestamp;
        }
            function updateTable(history) {
            const tbody = document.getElementById('history-table-body');
            tbody.innerHTML = ''; // Limpiar contenido previo
            
            // Tomar las últimas 10 lecturas e invertir el array (más recientes arriba)
            const recent = history.slice(-10).reverse();
            
            recent.forEach(item => {
                const tr = document.createElement('tr');
                tr.className = "border-b border-slate-700/50 hover:bg-slate-700/30 transition";
                
                // Determinar colores del badge según el estado
                let badgeClass = "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"; // NORMAL
                if (item.status === "ADVERTENCIA") badgeClass = "bg-amber-500/20 text-amber-400 border border-amber-500/30";
                if (item.status === "CRITICO") badgeClass = "bg-red-500/20 text-red-400 font-bold border border-red-500/30 animate-pulse";

                // Formatear la hora
                const timeOnly = item.timestamp.split(' ')[1] || item.timestamp;

                tr.innerHTML = `
                    <td class="py-3 px-4 text-slate-400">${timeOnly}</td>
                    <td class="py-3 px-4 font-mono text-xs text-slate-500">${item.device_id}</td>
                    <td class="py-3 px-4 font-semibold">${Number(item.temperature).toFixed(1)}</td>
                    <td class="py-3 px-4 font-semibold">${Number(item.humidity).toFixed(1)}</td>
                    <td class="py-3 px-4">
                        <span class="px-2 py-1 rounded text-xs ${badgeClass}">${item.status}</span>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
        function updateChart(history, forecast) {
            const histLabels = history.map(i => i.timestamp.split(' ')[1]);
            const foreLabels = forecast.map(i => i.timestamp);
            
            chart.data.labels = [...histLabels, ...foreLabels];

            const histTemps = history.map(i => i.temperature);
            const histHums = history.map(i => i.humidity);

            const predTemps = new Array(history.length - 1).fill(null);
            if (history.length > 0) {
                predTemps.push(history[history.length - 1].temperature);
            }
            forecast.forEach(i => predTemps.push(i.pred_temperature));

            chart.data.datasets[0].data = histTemps;
            chart.data.datasets[1].data = predTemps;
            chart.data.datasets[2].data = histHums;

            chart.update();
        }

        setInterval(fetchHistoryAndForecast, 1500);
        fetchHistoryAndForecast();
    </script>
</body>
</html>
"""
# =====================================================
# FUNCIÓN ENVÍO DE CORREO (SEGUNDO PLANO)
# =====================================================
def send_email_alert(data: SensorData, timestamp: str):
    global LAST_EMAIL_SENT
    now = datetime.now()
    if LAST_EMAIL_SENT and (now - LAST_EMAIL_SENT) < timedelta(minutes=EMAIL_COOLDOWN_MINUTES):
        print("⏳ Alerta crítica detectada, pero el envío de correo está en periodo de cooldown.")
        return

    subject = f"🚨 ALERTA CRÍTICA: RackMonitor IoT [{data.device_id}]"
    body = f"""
    <h2>🚨 Alerta Crítica Detectada en el Rack</h2>
    <p>Se ha registrado un estado crítico en el monitoreo ambiental:</p>
    <ul>
        <li><b>Dispositivo:</b> {data.device_id}</li>
        <li><b>Fecha/Hora:</b> {timestamp}</li>
        <li><b>Temperatura:</b> {data.temperature} °C</li>
        <li><b>Humedad:</b> {data.humidity} %</li>
        <li><b>Movimiento PIR:</b> {'DETECTADO' if data.motion else 'NORMAL'}</li>
        <li><b>Estado:</b> <span style="color:red; font-weight:bold;">{data.status}</span></li>
    </ul>
    <p>Por favor, revisa el Rack de inmediato.</p>
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        LAST_EMAIL_SENT = now
        print(f"📧 Correo de alerta enviado exitosamente a {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"❌ Error al enviar el correo de alerta: {e}")


# =====================================================
# ENDPOINTS API
# =====================================================
@app.get("/", response_class=HTMLResponse)
def read_dashboard():
    return HTML_CONTENT

@app.post("/api/v1/telemetry")
def receive_telemetry(data: SensorData, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    global latest_telemetry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save to Database
    db_log = models.TelemetryLog(
        device_id=data.device_id,
        temperature=data.temperature,
        humidity=data.humidity,
        motion=data.motion,
        status=data.status
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    payload = {
        "device_id": data.device_id,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "motion": data.motion,
        "status": data.status,
        "timestamp": timestamp
    }
    
    latest_telemetry = payload
    history_telemetry.append(payload)
    
    if data.status == "CRITICO":
        background_tasks.add_task(send_email_alert, data, timestamp)
    
    print(f"[{timestamp}] [DB ID: {db_log.id}] [{data.device_id}] Temp: {data.temperature}°C | Hum: {data.humidity}% | Mov: {data.motion} | Estado: {data.status}")
    return {"status": "success", "record_id": db_log.id, "timestamp": timestamp}

@app.get("/api/v1/telemetry/latest")
def get_latest_telemetry():
    return latest_telemetry

@app.get("/api/v1/telemetry/history")
def get_history():
    return list(history_telemetry)

@app.get("/api/v1/telemetry/db-history")
def get_db_history(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(models.TelemetryLog).order_by(models.TelemetryLog.id.desc()).limit(limit).all()
    return logs
@app.get("/api/v1/telemetry/forecast")
def get_forecast():
    return predict_future_trends(list(history_telemetry), steps_ahead=5)

@app.get("/api/v1/telemetry/export-csv")
def export_telemetry_csv(db: Session = Depends(get_db)):
    logs = db.query(models.TelemetryLog).order_by(models.TelemetryLog.id.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Dispositivo", "Temperatura (°C)", "Humedad (%)", "Movimiento PIR", "Estado", "Fecha/Hora"])

    for log in logs:
        writer.writerow([
            log.id,
            log.device_id,
            log.temperature,
            log.humidity,
            "DETECTADO" if log.motion else "NORMAL",
            log.status,
            log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "--"
        ])

    output.seek(0)

    filename = f"RackMonitor_Historial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers=headers
    )