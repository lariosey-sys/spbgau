/*
  ESP8266 + SCD30 — датчик CO2 / температуры / влажности для теплицы
  Публикует данные по MQTT каждые 5 секунд.

  Подключение SCD30 (I2C):
    SCL -> D1 (GPIO5)
    SDA -> D2 (GPIO4)
    VCC -> 3.3V
    GND -> GND

  Зависимости: ESP8266WiFi, PubSubClient, SparkFun SCD30 Arduino Library
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <SparkFun_SCD30_Arduino_Library.h>

// ---------- НАСТРОЙКИ ----------
const char* WIFI_SSID = "Greenhouse";
const char* WIFI_PASS = "77777777";

const char* MQTT_HOST = "192.168.1.112";
const uint16_t MQTT_PORT = 1883;

const char* DEVICE_ID = "co2-1";

#define SDA_PIN   4   // D2
#define SCL_PIN   5   // D1

#define READ_INTERVAL_MS   5000UL
#define WIFI_RETRY_MS      5000UL
#define MQTT_RETRY_MS      5000UL
// --------------------------------

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
SCD30 scd30;

char topicState[64];
char topicLWT[64];

unsigned long tLastRead = 0;
unsigned long tWiFiRetry = 0;
unsigned long tMqttRetry = 0;

float lastCO2 = NAN;
float lastTemp = NAN;
float lastHum = NAN;
bool sensorOk = false;

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println(F("=== Greenhouse CO2 Sensor ==="));
  Serial.print(F("Device: "));
  Serial.println(DEVICE_ID);

  snprintf(topicState, sizeof(topicState), "greenhouse/env/%s/state", DEVICE_ID);
  snprintf(topicLWT, sizeof(topicLWT), "greenhouse/%s/status", DEVICE_ID);

  // I2C init
  Wire.begin(SDA_PIN, SCL_PIN);

  // SCD30 init
  if (scd30.begin(Wire)) {
    Serial.println(F("[SCD30] Found!"));
    scd30.setMeasurementInterval(5);  // каждые 5 сек
    sensorOk = true;
  } else {
    Serial.println(F("[SCD30] NOT found! Check wiring."));
  }

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);

  ensureWiFi();
  ensureMQTT();
}

void loop() {
  ensureWiFi();
  ensureMQTT();
  mqtt.loop();

  if (millis() - tLastRead >= READ_INTERVAL_MS) {
    tLastRead = millis();
    readAndPublish();
  }
}

void ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  unsigned long now = millis();
  if (now - tWiFiRetry < WIFI_RETRY_MS) return;
  tWiFiRetry = now;

  Serial.print(F("[WiFi] Connecting to "));
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASS);

  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 15000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print(F("[WiFi] Connected, IP: "));
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(F("[WiFi] Failed, will retry"));
  }
}

void ensureMQTT() {
  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;

  unsigned long now = millis();
  if (now - tMqttRetry < MQTT_RETRY_MS) return;
  tMqttRetry = now;

  Serial.println(F("[MQTT] Connecting..."));

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);
  mqtt.setKeepAlive(60);

  if (mqtt.connect(DEVICE_ID, topicLWT, 1, true, "offline")) {
    Serial.println(F("[MQTT] Connected!"));
    mqtt.publish(topicLWT, "online", true);

    if (!isnan(lastCO2)) {
      publishData(lastCO2, lastTemp, lastHum);
    }
  } else {
    Serial.print(F("[MQTT] Failed, rc="));
    Serial.println(mqtt.state());
  }
}

void readAndPublish() {
  if (!sensorOk) {
    // Попробуем переинициализировать
    if (scd30.begin(Wire)) {
      Serial.println(F("[SCD30] Reconnected!"));
      scd30.setMeasurementInterval(5);
      sensorOk = true;
    }
    return;
  }

  if (!scd30.dataAvailable()) return;

  float co2 = scd30.getCO2();
  float t = scd30.getTemperature();
  float h = scd30.getHumidity();

  // Фильтр мусорных значений
  if (co2 < 0 || co2 > 10000) return;

  lastCO2 = co2;
  lastTemp = t;
  lastHum = h;

  Serial.print(F("[SCD30] CO2="));
  Serial.print(co2, 0);
  Serial.print(F("ppm  T="));
  Serial.print(t, 1);
  Serial.print(F("°C  H="));
  Serial.print(h, 1);
  Serial.println(F("%"));

  publishData(co2, t, h);
}

void publishData(float co2, float t, float h) {
  if (!mqtt.connected()) return;

  char buf[160];
  int n = snprintf(buf, sizeof(buf),
    "{\"ts\":%lu,\"device\":\"%s\",\"co2\":%.0f,\"t\":%.1f,\"h\":%.1f}",
    millis() / 1000UL, DEVICE_ID, co2, t, h);

  mqtt.publish(topicState, (const uint8_t*)buf, (unsigned int)n, false);
  Serial.print(F("[MQTT] Published: "));
  Serial.println(buf);
}
