/*
  Mega2560 + ESP8266(AT) -> MQTT контроллер реле

  Зависимости: WiFiEspAT (by Arduino), PubSubClient (knolleary)
  DIP: режим 3 (ON ON OFF OFF) для загрузки скетча
       режим 5 (ON ON ON ON) для работы (ATmega2560 <-> ESP8266 + USB debug)

  Маппинг реле (щиток):
    1-4   Заслонки (отсчёт слева)
    5-6   Вентиляторы 1-2
    7-8   ТЭНы 1-2
    9-15  Резерв
*/

#include <WiFiEspAT.h>
#include <PubSubClient.h>
#include <avr/wdt.h>
#include <ctype.h>
#include <string.h>

// ---------- НАСТРОЙКИ ----------
const char* WIFI_SSID    = "Greenhouse";
const char* WIFI_PASS    = "77777777";

const char* MQTT_HOST    = "192.168.1.112";
const uint16_t MQTT_PORT = 1883;
const char* MQTT_USER    = "";
const char* MQTT_PASS    = "";

const char* DEVICE_ID    = "mega-1";
const char* BASE         = "greenhouse";

#define ESP_BAUD       115200
#define NUM_RELAYS     15
#define SUMMARY_MS     60000UL   // сводка каждые 60 сек
#define WIFI_RETRY_MS  5000UL    // пауза между попытками WiFi
#define MQTT_RETRY_MS  5000UL    // пауза между попытками MQTT
#define WIFI_TIMEOUT   15000UL   // таймаут подключения WiFi

uint8_t RELAY_PINS[NUM_RELAYS] = {
  22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50
};
const bool RELAY_ACTIVE_LOW = false;

// ---- Глобальные переменные ----
WiFiClient wifi;
PubSubClient mqtt(wifi);
bool relayState[NUM_RELAYS] = {0};
char TOPIC_LWT[64];

unsigned long tSummary    = 0;
unsigned long tWiFiRetry  = 0;
unsigned long tMqttRetry  = 0;
unsigned long tWdtPrint   = 0;

// Счётчики для отладки
uint32_t wifiReconnects = 0;
uint32_t mqttReconnects = 0;

// ---- Утилиты ----
inline uint8_t levelFor(bool on) {
  return ((RELAY_ACTIVE_LOW ? !on : on) ? HIGH : LOW);
}

void applyRelay(uint8_t idx, bool on) {
  if (idx >= NUM_RELAYS) return;
  relayState[idx] = on;
  digitalWrite(RELAY_PINS[idx], levelFor(on));
}

void publishRelayState(uint8_t idx) {
  if (!mqtt.connected() || idx >= NUM_RELAYS) return;
  char topic[64];
  snprintf(topic, sizeof(topic), "%s/relay/%u/state", BASE, idx + 1);
  mqtt.publish(topic, relayState[idx] ? "ON" : "OFF", /*retain=*/true);
}

void publishAllStates() {
  for (uint8_t i = 0; i < NUM_RELAYS; i++) publishRelayState(i);
}

void publishSummary() {
  if (!mqtt.connected()) return;
  static char buf[512];
  int n = snprintf(buf, sizeof(buf),
    "{\"ts\":%lu,\"device\":\"%s\",\"uptime\":%lu,\"wifi_rc\":%lu,\"mqtt_rc\":%lu,\"rssi\":%d,\"relays\":{",
    millis() / 1000UL, DEVICE_ID, millis() / 1000UL,
    (unsigned long)wifiReconnects, (unsigned long)mqttReconnects,
    WiFi.RSSI());
  for (uint8_t i = 0; i < NUM_RELAYS; i++) {
    n += snprintf(buf + n, sizeof(buf) - n, "\"%u\":%s%s",
      i + 1, relayState[i] ? "true" : "false",
      (i < NUM_RELAYS - 1) ? "," : "");
    if (n >= (int)sizeof(buf) - 16) break;
  }
  n += snprintf(buf + n, sizeof(buf) - n, "}}");
  mqtt.publish("greenhouse/relay/summary", buf, n, /*retain=*/false);
}

bool equalsNoCase(const char* a, const char* b) {
  while (*a && *b) { if (tolower(*a++) != tolower(*b++)) return false; }
  return *a == *b;
}

bool parseBoolCmd(const char* s, bool &val, bool &toggle) {
  toggle = false;
  if (equalsNoCase(s, "ON")  || !strcmp(s, "1")) { val = true;  return true; }
  if (equalsNoCase(s, "OFF") || !strcmp(s, "0")) { val = false; return true; }
  if (equalsNoCase(s, "TOGGLE"))                 { toggle = true; return true; }
  return false;
}

void setAllCmd(const char* cmd) {
  bool v = false, tog = false;
  if (!parseBoolCmd(cmd, v, tog)) return;
  for (uint8_t i = 0; i < NUM_RELAYS; i++) {
    bool on = tog ? !relayState[i] : v;
    applyRelay(i, on);
    publishRelayState(i);
  }
}

// ---- MQTT callback ----
// Топики: greenhouse/relay/<N|all>/<set|get>
void onMqtt(char* topic, byte* payload, unsigned int len) {
  wdt_reset();

  char cmd[16];
  len = (len >= sizeof(cmd)) ? sizeof(cmd) - 1 : len;
  memcpy(cmd, payload, len);
  cmd[len] = 0;

  char expect[32];
  snprintf(expect, sizeof(expect), "%s/relay/", BASE);
  size_t prefixLen = strlen(expect);
  if (strncmp(topic, expect, prefixLen) != 0) return;
  const char* p = topic + prefixLen;

  char token[12] = {0};
  const char* slash = strchr(p, '/');
  if (!slash) return;
  size_t tokLen = (size_t)(slash - p);
  if (tokLen >= sizeof(token)) tokLen = sizeof(token) - 1;
  memcpy(token, p, tokLen);
  token[tokLen] = 0;

  const char* action = slash + 1;

  if (equalsNoCase(action, "set")) {
    if (equalsNoCase(token, "all")) {
      setAllCmd(cmd);
      return;
    }
    int n = atoi(token);
    if (n >= 1 && n <= (int)NUM_RELAYS) {
      bool v = false, tog = false;
      if (!parseBoolCmd(cmd, v, tog)) return;
      bool newVal = tog ? !relayState[n - 1] : v;
      applyRelay(n - 1, newVal);
      publishRelayState(n - 1);
    }
  } else if (equalsNoCase(action, "get")) {
    if (equalsNoCase(token, "all")) {
      publishAllStates();
      publishSummary();
      return;
    }
    int n = atoi(token);
    if (n >= 1 && n <= (int)NUM_RELAYS) {
      publishRelayState(n - 1);
    }
  }
}

// ---- WiFi ----
void ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  unsigned long now = millis();
  if (now - tWiFiRetry < WIFI_RETRY_MS) return;
  tWiFiRetry = now;

  Serial.println(F("[WiFi] Connecting..."));
  wifiReconnects++;

  WiFi.disconnect();
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < WIFI_TIMEOUT) {
    wdt_reset();
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print(F("[WiFi] Connected, IP: "));
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(F("[WiFi] Failed, will retry"));
  }
}

// ---- MQTT ----
void ensureMQTT() {
  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;

  unsigned long now = millis();
  if (now - tMqttRetry < MQTT_RETRY_MS) return;
  tMqttRetry = now;

  Serial.println(F("[MQTT] Connecting..."));
  mqttReconnects++;

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqtt);
  mqtt.setBufferSize(768);
  mqtt.setKeepAlive(60);
  mqtt.setSocketTimeout(15);

  snprintf(TOPIC_LWT, sizeof(TOPIC_LWT), "%s/%s/status", BASE, DEVICE_ID);

  bool ok;
  if (MQTT_USER[0]) {
    ok = mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASS, TOPIC_LWT, 1, true, "offline");
  } else {
    ok = mqtt.connect(DEVICE_ID, TOPIC_LWT, 1, true, "offline");
  }

  if (ok) {
    Serial.println(F("[MQTT] Connected!"));
    mqtt.publish(TOPIC_LWT, "online", true);
    mqtt.subscribe("greenhouse/relay/+/set");
    mqtt.subscribe("greenhouse/relay/+/get");
    publishAllStates();
    publishSummary();
  } else {
    Serial.print(F("[MQTT] Failed, rc="));
    Serial.println(mqtt.state());
  }
}

// ---- Setup ----
void setup() {
  // Watchdog 8 секунд
  wdt_disable();

  Serial.begin(115200);
  Serial.println(F("\n=== Greenhouse Mega Controller ==="));
  Serial.println(F("Initializing..."));

  // Инициализация реле — сначала подтяжка LOW (OFF для active-high),
  // потом переключаем в OUTPUT. Это предотвращает кратковременное включение.
  for (uint8_t i = 0; i < NUM_RELAYS; i++) {
    digitalWrite(RELAY_PINS[i], LOW);   // LOW = OFF для active-high
    pinMode(RELAY_PINS[i], OUTPUT);
    relayState[i] = false;
  }
  Serial.println(F("[Relay] All OFF"));

  // ESP8266 init — автоопределение baudrate
  {
    const long bauds[] = {115200, 9600, 57600, 38400, 19200, 74880};
    const int numBauds = 6;
    bool espFound = false;

    for (int b = 0; b < numBauds && !espFound; b++) {
      Serial.print(F("[ESP] Trying "));
      Serial.print(bauds[b]);
      Serial.print(F("..."));

      Serial3.begin(bauds[b]);
      delay(100);
      while (Serial3.available()) Serial3.read(); // flush

      Serial3.println(F("AT"));
      delay(1000);

      String resp = "";
      while (Serial3.available()) resp += (char)Serial3.read();

      if (resp.indexOf("OK") >= 0) {
        Serial.println(F(" OK!"));
        espFound = true;

        // Если не 115200, переключим ESP на 115200 для стабильности
        if (bauds[b] != 115200) {
          Serial.println(F("[ESP] Switching to 115200..."));
          Serial3.println(F("AT+UART_DEF=115200,8,1,0,0"));
          delay(1000);
          Serial3.end();
          Serial3.begin(115200);
          delay(500);
        }
      } else {
        Serial.println(F(" no"));
        Serial3.end();
      }
    }

    if (!espFound) {
      Serial.println(F("[ESP] Not found on any baudrate! Starting Serial3 at 115200 anyway."));
      Serial3.begin(115200);
    }
  }

  WiFi.init(Serial3);

  // Ждём ESP8266
  for (int i = 0; i < 10 && WiFi.status() == WL_NO_SHIELD; i++) {
    Serial.print(F("."));
    delay(500);
  }
  Serial.println();

  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println(F("[ESP] ERROR: ESP8266 not found after init!"));
  } else {
    Serial.println(F("[ESP] ESP8266 ready"));
  }

  // Включаем watchdog после инициализации
  wdt_enable(WDTO_8S);

  ensureWiFi();
  ensureMQTT();

  tSummary = millis();
  Serial.println(F("[Boot] Ready"));
}

// ---- Loop ----
void loop() {
  wdt_reset();

  ensureWiFi();
  ensureMQTT();
  mqtt.loop();

  // Периодическая сводка
  if (millis() - tSummary >= SUMMARY_MS) {
    tSummary = millis();
    publishSummary();
  }

  // Debug вывод каждые 30 сек
  if (millis() - tWdtPrint >= 30000UL) {
    tWdtPrint = millis();
    Serial.print(F("[Status] WiFi="));
    Serial.print(WiFi.status() == WL_CONNECTED ? "OK" : "DISCONNECTED");
    Serial.print(F(" MQTT="));
    Serial.print(mqtt.connected() ? "OK" : "DISCONNECTED");
    Serial.print(F(" Uptime="));
    Serial.print(millis() / 1000UL);
    Serial.println(F("s"));
  }
}
