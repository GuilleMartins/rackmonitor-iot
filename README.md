# RackMonitor IoT 2.0 

Sistema integral de monitoreo ambiental, seguridad física y analítica predictiva diseñado para gabinetes y racks de servidores en centros de datos.

## Características Principales

* **Monitoreo en Tiempo Real:** Lectura continua de temperatura, humedad (sensor DHT22) y detección de intrusión (sensor PIR) a través de un microcontrolador ESP32.
* **Analítica Predictiva (Forecasting):** Algoritmos de regresión sobre series temporales para proyectar tendencias a corto plazo y prevenir sobrecalentamientos.
* **Alertas Multicanal:** Notificaciones automáticas de estados críticos vía correo electrónico (SMTP) y Telegram Bot.
* **Dashboard Interactivo:** Panel web dinámico para visualización de métricas en tiempo real y gráficos de proyección.
* **Exportación de Historial:** Generación de reportes de telemetría en formato CSV.

## Stack Tecnológico

* **Hardware & Firmware:** ESP32, Sensores DHT22/PIR, C++, PlatformIO.
* **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy (SQLite/PostgreSQL).
* **Data Science & Analítica:** NumPy, Scikit-Learn, Pandas.
* **Frontend:** HTML5, Tailwind CSS, Chart.js.

## Equipo del Proyecto

Proyecto Integrador desarrollado en la Universidad del Norte:
* **Guillermo Martins** - Backend & Forecasting
* **Helen Duré** - Frontend & Dashboard
* **Gabriela Vasso** - Integración de Hardware y Firmware ESP32
* **Tutor:** Ing. Richard Nuñez
