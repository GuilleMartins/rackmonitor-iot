# RackMonitor IoT 2.0

**Sistema de monitoreo ambiental y detección de movimiento en tiempo real para racks de servidores.**

Proyecto académico desarrollado en la Universidad del Norte, carrera de Ingeniería Informática, décimo semestre, asignatura Robótica.

## Integrantes

- Gabriela Vasso
- Helen Dure
- Guillermo Martins

**Docente:** Ing. Richard Núñez
**Año:** 2026

## Prototipo físico implementado

El sistema utiliza un microcontrolador ESP32 DevKit V1, un sensor DHT11 para medir temperatura y humedad, y un sensor PIR HC-SR501 para detectar movimiento.

Los datos se transmiten mediante Wi-Fi a un backend desarrollado en Python con FastAPI.

## Funcionalidades implementadas

- Lectura de temperatura y humedad.
- Detección de movimiento.
- Transmisión de telemetría mediante HTTP.
- Visualización de datos en un dashboard web.
- Clasificación de estados NORMAL, ADVERTENCIA y CRÍTICO.
- Gráficos históricos y proyección de temperatura.
- Registro de eventos.
- Opción de exportación de datos en CSV.

## Funcionalidades adicionales y pendientes de validación

El proyecto contiene código relacionado con alertas por correo electrónico, pantalla OLED, indicadores LED y buzzer. Estas funciones requieren validación o instalación física según corresponda.

La integración con Telegram no se considera una funcionalidad demostrada en esta versión.

## Conexiones principales

| Componente | Conexión ESP32 |
|---|---|
| DHT11 DATA | GPIO4 |
| PIR OUT | GPIO27 |
| DHT11 VCC | 3V3 |
| PIR VCC | VIN (5 V USB) |
| GND | GND común |

## Evidencia de funcionamiento

Se verificó la recepción exitosa de telemetría mediante respuestas HTTP 200 y la visualización de mediciones y estados de alerta en el dashboard.

## Repositorio

https://github.com/GuilleMartins/rackmonitor-iot