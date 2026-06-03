# Матрица трассировки задач ВКР

Матрица связывает задачи из введения с главами, исходными файлами и доказательствами. Она нужна для самопроверки перед финальной сборкой и защитой.

| Задача ВКР | Где раскрыта | Артефакты репозитория | Что еще нужно для финала |
|---|---|---|---|
| 1. Проанализировать подходы к автоматизации микроклимата, IoT, прогнозированию и интеллектуальному управлению | `chapter_01_literature_review.md`, `literature/reviews/*.md` | `literature/references.bib`, `literature/literature_matrix.md`, `literature/source_cards.md` | вычитать ГОСТ-список и заменить citation keys на финальный формат |
| 2. Определить требования к системе мониторинга и управления | `chapter_02_system_design.md`, `technical_spec.md` | MQTT-топики и env-параметры в `Greenhouse/dashboard/app.py`; прошивки датчиков и Mega | согласовать формулировку требований с шаблоном кафедры |
| 3. Спроектировать архитектуру на базе микроконтроллеров, MQTT, серверного приложения и базы истории | `chapter_02_system_design.md`, `draft_full.md` | `Greenhouse/docker-compose.yml`, `Greenhouse/firmware/*`, `Greenhouse/dashboard/app.py` | добавить архитектурную схему в рисунок |
| 4. Реализовать программно-аппаратный контур | `chapter_03_implementation_testing.md` | `sensor_th.ino`, `sensor_co2.ino`, `greenhouse_mega.ino`, `app.py` | добавить фото/скриншоты реального запуска |
| 5. Подготовить основу для интеллектуального слоя | `chapter_03_implementation_testing.md`, `ml_experiment_plan.md` | `sensor_log`, `relay_log`, `/api/export/<data_type>` | накопить датасет и при возможности выполнить baseline-прогноз |
| 6. Проверить работоспособность системы и оценить направления развития | `chapter_03_implementation_testing.md`, `test_protocol.md`, `conclusion.md` | MQTT-команды, SQLite-запросы, экспорт данных | выполнить протокол на оборудовании и сохранить доказательства |

## Трассировка компонентов

| Компонент | Реализация | Описание в тексте | Проверка |
|---|---|---|---|
| Датчик температуры/влажности | `Greenhouse/firmware/sensor_th/sensor_th.ino` | главы 2-3, `technical_spec.md` | MQTT `greenhouse/env/th-1/state` |
| Датчик CO2 | `Greenhouse/firmware/sensor_co2/sensor_co2.ino` | главы 2-3, `technical_spec.md` | MQTT `greenhouse/env/co2-1/state` |
| Контроллер реле | `Greenhouse/firmware/greenhouse_mega/greenhouse_mega.ino` | главы 2-3, `technical_spec.md` | MQTT `greenhouse/relay/<n>/state`, `greenhouse/relay/summary` |
| MQTT-брокер | `Greenhouse/docker-compose.yml` | главы 2-3 | `mosquitto_sub -t 'greenhouse/#' -v` |
| Dashboard | `Greenhouse/dashboard/app.py` | главы 2-3 | браузер, скриншоты страниц |
| Правила | `Greenhouse/dashboard/app.py`, `rules.json` | главы 2-3 | правило публикует MQTT-команду |
| Профили | `Greenhouse/dashboard/app.py`, `profiles.json` | главы 2-3 | профиль выполняет `pre -> delay -> main` |
| История датчиков | SQLite `sensor_log` | главы 2-3, `ml_experiment_plan.md` | SQL `select * from sensor_log` |
| История реле | SQLite `relay_log` | главы 2-3, `ml_experiment_plan.md` | SQL `select * from relay_log` |
| Экспорт | `/api/export/sensors`, `/api/export/relays` | глава 3, `ml_experiment_plan.md` | CSV/XLSX-файл |

## Риски неполной доказательной базы

| Риск | Как закрыть |
|---|---|
| Нет фактических MQTT-логов с оборудования | выполнить `test_protocol.md` и сохранить вывод |
| Нет скриншотов dashboard | запустить систему, открыть страницы, сохранить скриншоты |
| Нет данных для ML-результатов | оставить ML как подготовленный эксперимент или накопить минимум несколько дней истории |
| Схема щитка только в формате Obsidian-вставки | экспортировать изображение в PNG/JPG для приложения |
| Ссылки еще в формате citation keys | использовать `literature/citation_replacement_table.md` |
