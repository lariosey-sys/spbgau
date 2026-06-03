/*
  ESP8266 + DHT11 — датчик температуры/влажности для теплицы
  Публикует данные по MQTT каждые 10 секунд.

  Подключение DHT11:
    DATA -> GPIO2 (D4 на NodeMCU / пин 2 на ESP-01)
    VCC  -> 3.3V
    GND  -> GND

  Зависимости: ESP8266WiFi, PubSubClient, DHT sensor library
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ---------- НАСТРОЙКИ ----------
const char* WIFI_SSID = "Greenhouse";
const char* WIFI_PASS = "77777777";

const char* MQTT_HOST = "192.168.1.112";
const uint16_t MQTT_PORT = 1883;

// Идентификатор устройства: th-1, th-2, th-3...
const char* DEVICE_ID = "th-1";

// DHT11
#define DHT_PIN   2        // GPIO2 — DATA на модуле TB:IOTMCU
#define DHT_TYPE  DHT11

// Интервалы
#define READ_INTERVAL_MS   10000UL  // чтение датчика каждые 10 сек
#define WIFI_RETRY_MS      5000UL
#define MQTT_RETRY_MS      5000UL
// --------------------------------

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);

char topicState[64];
char topicLWT[64];

unsigned long tLastRead = 0;
unsigned long tWiFiRetry = 0;
unsigned long tMqttRetry = 0;

float lastTemp = NAN;
float lastHum = NAN;

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println(F("=== Greenhouse Sensor ==="));
  Serial.print(F("Device: "));
  Serial.println(DEVICE_ID);

  // Формируем топики
  snprintf(topicState, sizeof(topicState), "greenhouse/env/%s/state", DEVICE_ID);
  snprintf(topicLWT, sizeof(topicLWT), "greenhouse/%s/status", DEVICE_ID);

  dht.begin();

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

    // Сразу отправить текущие показания если есть
    if (!isnan(lastTemp)) {
      publishData(lastTemp, lastHum);
    }
  } else {
    Serial.print(F("[MQTT] Failed, rc="));
    Serial.println(mqtt.state());
  }
}

void readAndPublish() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println(F("[DHT] Read error"));
    return;
  }

  lastTemp = t;
  lastHum = h;

  Serial.print(F("[DHT] T="));
  Serial.print(t, 1);
  Serial.print(F("°C  H="));
  Serial.print(h, 1);
  Serial.println(F("%"));

  publishData(t, h);
}

void publishData(float t, float h) {
  if (!mqtt.connected()) return;

  char buf[128];
  int n = snprintf(buf, sizeof(buf),
    "{\"ts\":%lu,\"device\":\"%s\",\"t\":%.1f,\"h\":%.1f}",
    millis() / 1000UL, DEVICE_ID, t, h);

  mqtt.publish(topicState, (const uint8_t*)buf, (unsigned int)n, false);
  Serial.print(F("[MQTT] Published: "));
  Serial.println(buf);
}
