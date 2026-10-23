#include <Arduino.h>
#include <Wire.h>
#include <DHT.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// =====================================================
// RACKMONITOR IoT 2.0
// Firmware base para ESP32
// =====================================================


// =====================================================
// CONFIGURACIÓN DE PINES
// =====================================================

#define DHT_PIN       4
#define DHT_TYPE      DHT11

#define PIR_PIN       27

#define LED_GREEN     18
#define LED_YELLOW    19
#define LED_RED       23

#define BUZZER_PIN    25

#define OLED_SDA      21
#define OLED_SCL      22


// =====================================================
// OLED
// =====================================================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    &Wire,
    -1
);
const char* WIFI_SSID = "TIC-SSD";
const char* WIFI_PASSWORD = "L3gion935!!";
const char* API_URL =
  "http://192.168.40.94:8000/api/v1/telemetry";

// =====================================================
// SENSOR DHT
// =====================================================

DHT dht(
    DHT_PIN,
    DHT_TYPE
);


// =====================================================
// VARIABLES
// =====================================================

float temperature = 0.0;
float humidity = 0.0;

bool motion = false;

String systemStatus = "INICIANDO";


// =====================================================
// TEMPORIZADOR
// =====================================================

unsigned long lastReading = 0;

const unsigned long readingInterval = 2000;


// =====================================================
// FUNCIÓN: LEER SENSORES
// =====================================================

void readSensors()
{
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (!isnan(temp))
    {
        temperature = temp;
    }

    if (!isnan(hum))
    {
        humidity = hum;
    }

    motion = digitalRead(PIR_PIN);
}


// =====================================================
// FUNCIÓN: DETERMINAR ESTADO
// =====================================================

void calculateStatus()
{
    if (
        temperature >= 35.0 ||
        humidity >= 80.0 ||
        motion
    )
    {
        systemStatus = "CRITICO";
    }

    else if (
        temperature >= 30.0 ||
        humidity >= 70.0
    )
    {
        systemStatus = "ADVERTENCIA";
    }

    else
    {
        systemStatus = "NORMAL";
    }
}


// =====================================================
// FUNCIÓN: CONTROL DE ALERTAS
// =====================================================

void updateIndicators()
{
    // Apagar todo primero

    digitalWrite(
        LED_GREEN,
        LOW
    );

    digitalWrite(
        LED_YELLOW,
        LOW
    );

    digitalWrite(
        LED_RED,
        LOW
    );

    noTone(BUZZER_PIN);


    // NORMAL

    if (systemStatus == "NORMAL")
    {
        digitalWrite(
            LED_GREEN,
            HIGH
        );
    }


    // ADVERTENCIA

    else if (
        systemStatus == "ADVERTENCIA"
    )
    {
        digitalWrite(
            LED_YELLOW,
            HIGH
        );
    }


    // CRITICO

    else if (
        systemStatus == "CRITICO"
    )
    {
        digitalWrite(
            LED_RED,
            HIGH
        );

        tone(
            BUZZER_PIN,
            1000
        );
    }
}


// =====================================================
// FUNCIÓN: OLED
// =====================================================

void updateDisplay()
{
    display.clearDisplay();

    display.setTextColor(
        SSD1306_WHITE
    );


    // Título

    display.setTextSize(1);

    display.setCursor(
        0,
        0
    );

    display.println(
        "RACKMONITOR IoT"
    );


    display.drawLine(
        0,
        10,
        127,
        10,
        SSD1306_WHITE
    );


    // Temperatura

    display.setCursor(
        0,
        17
    );

    display.print(
        "TEMP: "
    );

    display.print(
        temperature,
        1
    );

    display.println(
        " C"
    );


    // Humedad

    display.setCursor(
        0,
        29
    );

    display.print(
        "HUM : "
    );

    display.print(
        humidity,
        1
    );

    display.println(
        " %"
    );


    // Movimiento

    display.setCursor(
        0,
        41
    );

    display.print(
        "MOV : "
    );

    if (motion)
    {
        display.println(
            "DETECTADO"
        );
    }
    else
    {
        display.println(
            "NORMAL"
        );
    }


    // Estado

    display.setCursor(
        0,
        53
    );

    display.print(
        "STATUS: "
    );

    display.println(
        systemStatus
    );


    display.display();
}


// =====================================================
// FUNCIÓN: MONITOR SERIAL
// =====================================================

void printSerial()
{
    Serial.println();
    Serial.println(
        "================================"
    );

    Serial.println(
        "       RACKMONITOR IoT"
    );

    Serial.println(
        "================================"
    );

    Serial.print(
        "Temperatura: "
    );

    Serial.print(
        temperature,
        1
    );

    Serial.println(
        " C"
    );


    Serial.print(
        "Humedad: "
    );

    Serial.print(
        humidity,
        1
    );

    Serial.println(
        " %"
    );


    Serial.print(
        "Movimiento: "
    );

    if (motion)
    {
        Serial.println(
            "DETECTADO"
        );
    }
    else
    {
        Serial.println(
            "NORMAL"
        );
    }


    Serial.print(
        "Estado: "
    );

    Serial.println(
        systemStatus
    );

    Serial.println(
        "================================"
    );
}


// =====================================================
// SETUP
// =====================================================

void setup()
{
    Serial.begin(
        115200
    );

    delay(1000);


    // Configurar pines

    pinMode(
        PIR_PIN,
        INPUT
    );

    pinMode(
        LED_GREEN,
        OUTPUT
    );

    pinMode(
        LED_YELLOW,
        OUTPUT
    );

    pinMode(
        LED_RED,
        OUTPUT
    );

    pinMode(
        BUZZER_PIN,
        OUTPUT
    );


    // Inicializar DHT

    dht.begin();


    // Inicializar I2C

    Wire.begin(
        OLED_SDA,
        OLED_SCL
    );


    // Inicializar OLED

    if (
        !display.begin(
            SSD1306_SWITCHCAPVCC,
            0x3C
        )
    )
    {
        Serial.println(
            "ERROR: OLED no encontrado"
        );
    }
    else
    {
        display.clearDisplay();

        display.setTextColor(
            SSD1306_WHITE
        );

        display.setTextSize(2);

        display.setCursor(
            10,
            20
        );

        display.println(
            "RackMonitor"
        );

        display.display();

        delay(2000);
    }


    // Mensaje inicial

    Serial.println();
    Serial.println(
        "================================"
    );

    Serial.println(
        "     RACKMONITOR IoT 2.0"
    );

    Serial.println(
        "================================"
    );

    Serial.println(
        "ESP32 iniciado correctamente"
    );

    Serial.println(
        "Sistema listo"
    );
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
    if (
        millis() - lastReading
        >= readingInterval
    )
    {
        lastReading =
            millis();


        // 1. Leer sensores

        readSensors();


        // 2. Calcular estado

        calculateStatus();


        // 3. Actualizar LEDs y buzzer

        updateIndicators();


        // 4. Actualizar OLED

        updateDisplay();


        // 5. Mostrar información

        printSerial();
    }
}