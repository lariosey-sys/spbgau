# Greenhouse - Умная теплица

## Обзор проекта
Система автоматизации теплицы на базе Raspberry Pi 4 и Arduino Mega 2560. Arduino управляет 15 реле через MQTT, Raspberry Pi выступает сервером с Docker-контейнерами для автоматизации, базы данных и MQTT-брокера.

## Архитектура

### Железо
- **Raspberry Pi 4 Model B** (8GB RAM, Debian 12 Bookworm, 64GB SD)
- **Arduino Mega 2560** + **ESP8266** (AT-прошивка) — контроллер реле
- **15 реле** на пинах: 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50
- Реле с инвертированными входами (active low), при старте всё выключено

### Сеть
- WiFi SSID: `Greenhouse`
- Raspberry Pi: `192.168.1.112` (eth0), `192.168.1.105` (wlan0)
- Tailscale: `100.74.177.121`
- Docker bridge: `172.18.0.0/16`

### SSH подключение
```
ssh greenhouse
```
- Host: 100.74.177.121 (Tailscale)
- User: sergei
- Key: ~/.ssh/sergeikey

## Docker-сервисы (~/greenhouse/)

| Сервис | Образ | Порт | Назначение |
|--------|-------|------|------------|
| **PostgreSQL** | postgres:16-alpine | 5432 (внутренний) | БД для n8n и NocoDB |
| **n8n** | n8nio/n8n:latest | 5678 | Автоматизация (workflow) |
| **NocoDB** | nocodb/nocodb:latest | 8080 | UI для данных (Airtable-like) |
| **Mosquitto** | eclipse-mosquitto:2 | 1883 | MQTT-брокер |

Все контейнеры с `restart: unless-stopped`. Конфиги и данные в bind-mount томах в `~/greenhouse/`.

## MQTT-протокол

Брокер: Mosquitto на `192.168.1.112:1883`, анонимный доступ.

### Топики

| Топик | Направление | Описание |
|-------|-------------|----------|
| `greenhouse/relay/<N>/set` | -> Arduino | Команда: `ON`, `OFF`, `TOGGLE` |
| `greenhouse/relay/all/set` | -> Arduino | Команда на все реле |
| `greenhouse/relay/<N>/get` | -> Arduino | Запрос состояния |
| `greenhouse/relay/all/get` | -> Arduino | Запрос всех состояний |
| `greenhouse/relay/<N>/state` | Arduino -> | Текущее состояние (retain) |
| `greenhouse/relay/summary` | Arduino -> | JSON-сводка каждые 60 сек |
| `greenhouse/mega-1/status` | Arduino -> | LWT: `online`/`offline` (retain) |
| `greenhouse/env/<dev>/state` | Sensor -> | JSON: `{"ts":N,"device":"<dev>","t":32.5,"h":17.0}` |
| `greenhouse/<dev>/status` | Sensor -> | LWT: `online`/`offline` (retain) |

N = 1..15, MQTT-клиент Arduino: `mega-1`.

### Датчики окружающей среды
- **th-1** — датчик температуры/влажности #1 (ESP + DHT20), оффлайн
- **th-2** — датчик температуры/влажности #2 (ESP + DHT20), онлайн
- **co2-1** — датчик CO2, оффлайн

### Формат сводки (summary)
```json
{"ts":241,"device":"mega-1","uptime":241,"wifi_rc":1,"mqtt_rc":1,"rssi":199,"relays":{"1":false,...,"15":false}}
```

## Arduino Mega — прошивка

- **Библиотеки**: WiFiEspAT, PubSubClient
- **Режим DIP**: 5 (ATmega2560 <-> ESP8266), джампер TXD3/RXD3
- **ESP baud**: 115200
- WiFi реконнект каждые 2 сек, MQTT реконнект каждые 2 сек
- При подключении к MQTT публикует `online` в LWT и рассылает состояния всех реле

## n8n Workflows
- **States** (ID: o6MCe5YSf3nb2G5G) — активный workflow для управления состояниями

## Файловая структура на Pi

```
~/greenhouse/
├── docker-compose.yml
├── .env
├── local-files/          # монтируется в n8n как /files
├── mosquitto/
│   ├── config/mosquitto.conf
│   ├── data/mosquitto.db
│   └── log/mosquitto.log
├── n8n/                  # данные n8n
├── nocodb/               # данные NocoDB
└── postgres/
    ├── data/             # данные PostgreSQL
    └── init/00-init.sql  # инициализация БД (n8n, nocodb)
```

## Известные проблемы
- Healthcheck Mosquitto показывает `unhealthy` (но брокер работает — pub/sub функционирует)
- n8n пишет `EAI_AGAIN` для telemetry.n8n.io — нет доступа к интернету для телеметрии (не критично)
- В `00-init.sql` GRANT ссылается на `pguser`, а реальный пользователь `sergei` — гранты не применились (БД работают, т.к. `sergei` — владелец)

## План работ
1. Настроить автозапуск контейнеров при перезагрузке (уже решено через `restart: unless-stopped`)
