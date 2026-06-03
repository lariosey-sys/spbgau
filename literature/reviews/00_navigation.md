# Навигация по литературной базе

Дата актуализации: 26 мая 2026.

Эта папка используется как рабочая база для написания ВКР, а не только как архив PDF.

1. Для быстрого входа в тему читать `05_vkr_synthesized_review.md`.
2. Для подбора источников по конкретному разделу читать тематические обзоры.
3. Для финального цитирования сверять формулировки по PDF и, особенно для сборников, использовать указанные страницы.

## Тематические обзоры

| Файл | Что внутри |
|---|---|
| `01_forecasting_ml.md` | Прогнозирование роста, урожайности и микроклимата: LSTM, TCN, RNN, BiLSTM, GRU. |
| `02_control_rl_mpc.md` | MPC, RL-guided MPC, fuzzy/PID и ограничения управления теплицей. |
| `03_iot_system_architecture.md` | IoT, микроконтроллеры, MQTT, датчики, исполнительные механизмы и dashboards. |
| `04_russian_sources.md` | Русскоязычные статьи, ВКР и сборники с точными страницами. |
| `05_vkr_synthesized_review.md` | Синтез для главы 1 и мост к методике диплома. |
| `06_thermal_energy_greenhouse.md` | Теплотехническая рамка: тепловлажностный режим, вентиляция, тепло- и массообмен, энергопотребление. |

## Приоритет чтения

1. `agriculture-16-00761-v2.pdf` - главный свежий обзор smart greenhouse, IoT и AI.
2. `thermal_sources/sensors-2025-greenhouse-environment-control-review.pdf` - современный обзор стратегий управления и моделей теплиц.
3. `thermal_sources/agrojr-2025-temperature-humidity-greenhouse-model.pdf` - русскоязычная агроинженерная постановка температурно-влажностной модели.
4. `thermal_sources/agriculture-2021-heat-mass-distribution-greenhouse.pdf` и `thermal_sources/buildings-2023-heat-humidity-natural-ventilation.pdf` - тепло- и массообмен, неоднородность микроклимата, вентиляция.
5. `thermal_sources/energies-2023-heat-recovery-greenhouse-ventilation.pdf` - энергетическая рамка вентиляции, отопления и тепловых потерь.
6. `24_cyberleninka_sravnitelnyy_analiz.pdf` - русскоязычная рамка эволюции АСУ микроклимата.
7. `1-s2.0-S2772375524003551-main.pdf`, `14_arxiv_2303.06110_RL_vs_MPC_greenhouse.pdf` и `02_arxiv_2506.13278_RL_MPC_greenhouse.pdf` - современное управление RL/MPC.
8. `energies-18-05821-v2.pdf`, `04_arxiv_2507.21669_BiLSTM_GRU_predictive_control.pdf` и `12_agriengineering_2024_ml_microclimate_web_control.pdf` - forecast-driven climate control.
9. `08_agronomy_2024_transformer_rnn_greenhouse_prediction.pdf`, `agriculture-15-02461.pdf`, `07_pmc_sensors_2021_greenhouse_crop_yield_tcn_rnn.pdf` - прогноз микроклимата/урожайности.
10. `17_energies_2022_iot_smart_greenhouses_industry_4.pdf`, `MQTT_Protocol_based_Smart_Greenhouse_Environment_M.pdf`, `20_uspu_diploma_greenhouse_microcontrollers.pdf` - IoT, MQTT и инженерная реализация.
11. `22_irsau_maket_students_2025.pdf`, стр. 836-839 - модель микроклимата через уравнения баланса.
12. `23_altstu_conf_2020_greenhouse.pdf`, стр. 125-126 - базовые требования и структурная схема АСУ.

## Как раскладывать источники по главам

| Раздел ВКР | Основные источники |
|---|---|
| Глава 1. Аналитический обзор | El Ouaham et al.; Bersani et al.; CyberLeninka comparative analysis; Ahn et al.; Gong et al.; Mallick et al.; Choi and Yang; ВолГАУ; ИРСАУ |
| Глава 1. Теплотехническая рамка | Chen et al.; Ogunlowo et al.; Li et al.; Ghaderi et al.; Samarin et al.; ИРСАУ |
| Глава 2. Проектирование системы | Mallick et al.; Msaad et al.; Morcego et al.; Aborujilah et al.; Thwin et al.; Ghaderi et al.; Кельсин; АлтГТУ; ИРСАУ |
| Глава 3. Реализация/эксперимент | Кельсин; Thwin et al.; MQTT article; Manoharan et al.; CyberLeninka microgreens; собственные файлы `Greenhouse/firmware` и `Greenhouse/dashboard` |

## Служебные файлы

| Файл | Назначение |
|---|---|
| `../literature_matrix.md` | Табличная карта корпуса литературы. |
| `../source_cards.md` | Краткие карточки источников для быстрого написания текста. |
| `../duplicates.md` | Какие PDF являются дублями и какой файл считать основным. |
| `../download_log.md` | История скачивания и статусы ручной догрузки. |
| `../paywalled.md` | Что осталось скачать вручную. |
