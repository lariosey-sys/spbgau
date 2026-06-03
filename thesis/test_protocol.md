# Протокол испытаний системы

Документ описывает проверку работоспособности программно-аппаратной системы теплицы. Его можно использовать как основу для раздела 3.7 и для сбора фактических материалов перед защитой.

## Цель испытаний

Подтвердить, что система выполняет полный цикл:

1. датчики публикуют телеметрию в MQTT;
2. dashboard получает и отображает телеметрию;
3. пользовательская команда из dashboard публикуется в MQTT;
4. контроллер реле выполняет команду и возвращает подтвержденное состояние;
5. сервер сохраняет измерения и события реле в SQLite;
6. данные можно выгрузить для анализа и будущего ML-эксперимента.

## Предварительные условия

| Условие | Проверка |
|---|---|
| Контейнеры запускаются из `Greenhouse/` | в каталоге есть `docker-compose.yml` |
| MQTT-порт задан | если переменная не задана, использовать `MQTT_PORT=1883` |
| Dashboard доступен | контейнер публикует порт `80:8081` |
| Прошивки загружены на устройства | `sensor_th`, `sensor_co2`, `greenhouse_mega` |
| Устройства находятся в сети `Greenhouse` | SSID и пароль заданы в прошивках |
| MQTT_HOST в прошивках соответствует адресу брокера | сейчас в прошивках указан `192.168.1.112` |

## Запуск серверной части

Из каталога `Greenhouse/`:

```bash
MQTT_PORT=1883 docker compose up -d mosquitto dashboard
```

Проверка контейнеров:

```bash
docker compose ps
```

Ожидаемый результат: сервисы `mosquitto` и `dashboard` находятся в состоянии `running` или `healthy`.

Проверка логов dashboard:

```bash
docker compose logs --tail=100 dashboard
```

Ожидаемый результат: нет циклических ошибок подключения к MQTT или SQLite.

## Проверка MQTT-брокера

Подписка на все сообщения системы:

```bash
docker compose exec mosquitto mosquitto_sub -t 'greenhouse/#' -v
```

Ожидаемые сообщения после подключения устройств:

```text
greenhouse/th-1/status online
greenhouse/co2-1/status online
greenhouse/mega-1/status online
greenhouse/env/th-1/state {"ts":...,"device":"th-1","t":...,"h":...}
greenhouse/env/co2-1/state {"ts":...,"device":"co2-1","co2":...,"t":...,"h":...}
greenhouse/relay/summary {"ts":...,"device":"mega-1",...}
```

Если сообщения от датчиков не появляются, проверить питание, Wi-Fi, адрес `MQTT_HOST` в прошивке и доступность порта 1883.

## Проверка команд реле через MQTT

Команда включения одного реле:

```bash
docker compose exec mosquitto mosquitto_pub -t 'greenhouse/relay/1/set' -m 'ON'
```

Ожидаемое подтверждение в подписке:

```text
greenhouse/relay/1/state ON
```

Команда выключения:

```bash
docker compose exec mosquitto mosquitto_pub -t 'greenhouse/relay/1/set' -m 'OFF'
```

Ожидаемое подтверждение:

```text
greenhouse/relay/1/state OFF
```

Команда запроса состояния всех реле:

```bash
docker compose exec mosquitto mosquitto_pub -t 'greenhouse/relay/all/get' -m '1'
```

Ожидаемый результат: публикация состояний `greenhouse/relay/<n>/state` и сводки `greenhouse/relay/summary`.

## Проверка dashboard

Открыть веб-панель:

```text
http://localhost/
```

Если используется другой хост или порт, открыть адрес, соответствующий публикации контейнера `dashboard`.

Проверить:

1. вход по паролю из `DASHBOARD_PASSWORD`;
2. отображение статуса Mega;
3. отображение датчиков `th-1` и `co2-1`;
4. переключение одного реле с главной страницы;
5. включение и выключение группы;
6. создание правила на странице `/rules`;
7. создание профиля на странице `/profiles`;
8. отображение графика и таблицы на странице `/stats`.

Для ВКР нужно сохранить скриншоты главной страницы, правил, профилей и статистики.

## Проверка SQLite-журнала

Внутри контейнера dashboard:

```bash
docker compose exec dashboard python - <<'PY'
import sqlite3
db = '/data/history.db'
conn = sqlite3.connect(db)
for table in ['sensor_log', 'relay_log']:
    (count,) = conn.execute(f'select count(*) from {table}').fetchone()
    print(table, count)
PY
```

Ожидаемый результат: после нескольких минут работы `sensor_log` содержит записи, а после переключения реле `relay_log` содержит события.

Проверка последних сенсорных записей:

```bash
docker compose exec dashboard python - <<'PY'
import sqlite3
conn = sqlite3.connect('/data/history.db')
for row in conn.execute('select ts, device, temperature, humidity, co2 from sensor_log order by id desc limit 5'):
    print(row)
PY
```

Проверка последних событий реле:

```bash
docker compose exec dashboard python - <<'PY'
import sqlite3
conn = sqlite3.connect('/data/history.db')
for row in conn.execute('select ts, relay_id, state from relay_log order by id desc limit 5'):
    print(row)
PY
```

Эти выводы можно использовать как фактическое доказательство журналирования в приложении Г.

## Проверка экспорта

CSV-экспорт датчиков:

```bash
curl -L 'http://localhost/api/export/sensors?format=csv&limit=100' -o greenhouse_sensors.csv
```

CSV-экспорт реле:

```bash
curl -L 'http://localhost/api/export/relays?format=csv&limit=100' -o greenhouse_relays.csv
```

Excel-экспорт:

```bash
curl -L 'http://localhost/api/export/sensors?format=excel&limit=100' -o greenhouse_sensors.xlsx
```

Если включена авторизация через сессию, экспорт удобнее выполнить из браузера после входа в dashboard.

## Проверка правил

Сценарий:

1. На странице `/rules` создать правило по датчику `th-1`.
2. Выбрать поле `t`, оператор `>`, порог ниже текущей температуры.
3. Выбрать одно безопасное реле или тестовую нагрузку.
4. Включить `reverse`, если нужно проверить обратное действие.
5. Дождаться периода проверки правил.

Ожидаемый результат: сервер публикует MQTT-команду, контроллер возвращает состояние реле, событие появляется в `relay_log`.

## Проверка профилей

Сценарий:

1. На странице `/profiles` создать профиль вентиляции.
2. В предварительные действия выбрать заслонки.
3. В основные действия выбрать вентиляторы.
4. Установить небольшую задержку, например 5-10 секунд.
5. Запустить профиль и наблюдать MQTT-сообщения.

Ожидаемый порядок:

```text
greenhouse/relay/<заслонка>/set ON
задержка
greenhouse/relay/<вентилятор>/set ON
```

При остановке профиля ожидается обратная последовательность: сначала основные устройства, затем после задержки предварительные.

## Фиксация результатов для ВКР

Для автоматического сбора большей части текстовых доказательств можно использовать:

```bash
bash thesis/collect_evidence.sh --start
```

Если контейнеры уже запущены, достаточно:

```bash
bash thesis/collect_evidence.sh
```

Скрипт создает папку `thesis/evidence/<timestamp>/` и сохраняет состояние контейнеров, логи, MQTT-сэмпл, SQL-выводы и CSV-экспорты. Скриншоты dashboard нужно сохранить вручную в ту же папку.

| Материал | Файл/место |
|---|---|
| Скриншоты dashboard | приложение Д |
| Вывод `mosquitto_sub` с датчиками | приложение В |
| Вывод `mosquitto_sub` с реле | приложение В |
| Вывод SQL по `sensor_log` | приложение Г |
| Вывод SQL по `relay_log` | приложение Г |
| CSV-фрагмент экспорта | глава 3 или приложение Г |
| Фото/схема щитка | приложение Е |

## Критерии успешного прохождения

Испытания считаются пройденными, если:

1. оба сенсорных узла публикуют телеметрию;
2. контроллер Mega публикует статус и сводку;
3. команда реле приводит к подтвержденному изменению состояния;
4. dashboard отображает датчики и реле;
5. `sensor_log` и `relay_log` пополняются;
6. экспорт формирует файл с историческими данными;
7. хотя бы один профиль выполняет последовательность с задержкой.
