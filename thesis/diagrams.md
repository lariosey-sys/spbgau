# Диаграммы для ВКР

Файл содержит исходники схем в формате Mermaid. Их можно вставить в Markdown-редактор с поддержкой Mermaid или экспортировать в PNG/SVG для финального документа.

## Рисунок 1. Общая архитектура системы

Назначение: использовать в главе 2 при описании распределенной архитектуры.

```mermaid
flowchart LR
    subgraph Sensors["Сенсорный слой"]
        TH["ESP8266 + DHT11\nsensor_th\nT, H"]
        CO2["ESP8266 + SCD30\nsensor_co2\nCO2, T, H"]
    end

    subgraph Actuators["Исполнительный слой"]
        MEGA["Arduino Mega 2560 + ESP8266 AT\ngreenhouse_mega\n15 реле"]
        RELAYS["Заслонки\nВентиляторы\nТЭНы\nНасосы\nФильтры"]
    end

    subgraph Server["Серверный слой"]
        MQTT["Mosquitto\nMQTT broker"]
        DASH["Flask dashboard\napp.py"]
        DB["SQLite\nhistory.db"]
        CFG["rules.json\nprofiles.json\nnames.json"]
    end

    OP["Оператор\nбраузер"]

    TH -->|"greenhouse/env/th-1/state"| MQTT
    CO2 -->|"greenhouse/env/co2-1/state"| MQTT
    MEGA -->|"relay state, summary, status"| MQTT
    MQTT -->|"telemetry and states"| DASH
    DASH -->|"relay set commands"| MQTT
    MQTT -->|"greenhouse/relay/<n>/set"| MEGA
    MEGA --> RELAYS
    DASH --> DB
    DASH --> CFG
    OP <-->|"HTTP UI"| DASH
```

## Рисунок 2. MQTT-обмен сообщениями

Назначение: использовать в разделе 2.3 или приложении В.

```mermaid
sequenceDiagram
    participant TH as sensor_th
    participant CO2 as sensor_co2
    participant Broker as Mosquitto
    participant Dash as Flask dashboard
    participant Mega as greenhouse_mega
    participant User as Оператор

    TH->>Broker: greenhouse/th-1/status = online
    CO2->>Broker: greenhouse/co2-1/status = online
    Mega->>Broker: greenhouse/mega-1/status = online
    Dash->>Broker: subscribe greenhouse/#

    loop Сенсорная телеметрия
        TH->>Broker: greenhouse/env/th-1/state {t,h}
        CO2->>Broker: greenhouse/env/co2-1/state {co2,t,h}
        Broker-->>Dash: MQTT messages
        Dash->>Dash: update state["sensors"]
    end

    User->>Dash: нажимает кнопку реле
    Dash->>Broker: greenhouse/relay/1/set ON
    Broker-->>Mega: command ON
    Mega->>Mega: applyRelay(1, true)
    Mega->>Broker: greenhouse/relay/1/state ON
    Broker-->>Dash: confirmed relay state
    Dash->>Dash: log relay event
```

## Рисунок 3. Контур правил и профилей

Назначение: использовать в разделе 2.7 или 3.6.

```mermaid
flowchart TD
    SENS["Текущие значения датчиков\nstate['sensors']"]
    RULES["Правила\nconditions + schedule + actions"]
    CHECK{"Условие истинно\nи расписание активно?"}
    ACTION["Действие\nреле или профиль"]
    PROFILE["Профиль\npre -> delay -> main"]
    MQTT["MQTT-команды\nrelay/<n>/set"]
    MEGA["Контроллер реле"]
    LOG["relay_log"]
    REV{"reverse включен\nи условие стало ложным?"}

    SENS --> RULES
    RULES --> CHECK
    CHECK -- да --> ACTION
    CHECK -- нет --> REV
    ACTION -->|реле| MQTT
    ACTION -->|profile_id| PROFILE
    PROFILE --> MQTT
    MQTT --> MEGA
    MEGA --> LOG
    REV -- да --> MQTT
    REV -- нет --> RULES
```

## Рисунок 4. Накопление данных и ML-пайплайн

Назначение: использовать в разделе 3.8 или приложении Ж.

```mermaid
flowchart LR
    MQTT["MQTT telemetry\nsensors + relay states"]
    STATE["Оперативное состояние\nFlask app state"]
    DB["SQLite\nsensor_log, relay_log"]
    EXPORT["CSV/XLSX export\n/api/export"]
    PREP["Подготовка датасета\nresampling, joins, lags"]
    FEATURES["Признаки\nlags, rolling stats,\nrelay states, time"]
    TARGETS["Targets\nT/H/CO2 +10/+30/+60 min"]
    BASE["Baseline\nlast value, moving average"]
    ML["ML-модель\nRF/GBM/LSTM/GRU"]
    EVAL["Оценка\nMAE, RMSE, R2"]

    MQTT --> STATE
    STATE --> DB
    DB --> EXPORT
    EXPORT --> PREP
    PREP --> FEATURES
    PREP --> TARGETS
    FEATURES --> BASE
    FEATURES --> ML
    TARGETS --> BASE
    TARGETS --> ML
    BASE --> EVAL
    ML --> EVAL
```

## Рисунок 5. SQLite-структура истории

Назначение: использовать в приложении Г.

```mermaid
erDiagram
    sensor_log {
        integer id PK
        text ts
        text device
        real temperature
        real humidity
        real co2
    }

    relay_log {
        integer id PK
        text ts
        integer relay_id
        integer state
    }
```

## Как экспортировать

Варианты:

1. Вставить Mermaid-блоки в Markdown-редактор с поддержкой Mermaid и экспортировать страницу.
2. Использовать Mermaid CLI, если он установлен локально.
3. Перерисовать схемы вручную в редакторе, сохранив структуру узлов и подписей из этого файла.
