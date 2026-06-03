# Карта цитирования для главы 1

Дата актуализации: 26 мая 2026.

Этот файл связывает тезисы будущей главы с источниками из корпуса. Он нужен, чтобы при написании текста быстро подбирать 2-3 источника на каждый важный аргумент.

| Тезис | Основные источники | Как использовать |
|---|---|---|
| Теплица является киберфизической системой, а не просто объектом ручного контроля. | `agriculture-16-00761-v2.pdf`; `17_energies_2022_iot_smart_greenhouses_industry_4.pdf`; `24_cyberleninka_sravnitelnyy_analiz.pdf` | Вводная постановка и актуальность smart greenhouse. |
| Базовая АСУ строится вокруг датчиков, блока управления и исполнительных механизмов. | `23_altstu_conf_2020_greenhouse.pdf`, стр. 125-126; `25_cyberleninka_obzor_mikrozelen.pdf`; `20_uspu_diploma_greenhouse_microcontrollers.pdf` | Описать классическую архитектуру и переход к собственной системе. |
| Микроклимат теплицы инерционен и многосвязен, поэтому реактивного управления недостаточно. | `22_irsau_maket_students_2025.pdf`, стр. 836-839; `energies-18-05821-v2.pdf`; `1-s2.0-S2772375524003551-main.pdf` | Обосновать прогнозный слой и ограничения пороговой логики. |
| IoT нужен для непрерывной телеметрии, удаленного мониторинга и связи компонентов. | `17_energies_2022_iot_smart_greenhouses_industry_4.pdf`; `10_semanticscholar_iot_greenhouse_systems.pdf`; `MQTT_Protocol_based_Smart_Greenhouse_Environment_M.pdf` | Подраздел про архитектуру: датчики, MQTT, сервер, dashboard. |
| MQTT является подходящим легким протоколом для smart greenhouse monitoring. | `MQTT_Protocol_based_Smart_Greenhouse_Environment_M.pdf`; `20_uspu_diploma_greenhouse_microcontrollers.pdf` | Обосновать коммуникационный слой проекта. |
| ML применим для прогнозирования роста и урожайности растений. | `01_arxiv_1907.00624_DL_plant_growth.pdf`; `07_pmc_sensors_2021_greenhouse_crop_yield_tcn_rnn.pdf`; `sensors-21-04537.pdf` | Показать исторический переход от данных к прогнозной аналитике. |
| Температуру, влажность и CO2 можно прогнозировать как временные ряды. | `08_agronomy_2024_transformer_rnn_greenhouse_prediction.pdf`; `13_agronomy_2024_attention_cnn_lstm_mushroom_greenhouse.pdf`; `12_agriengineering_2024_ml_microclimate_web_control.pdf` | Подраздел про прогноз микроклимата. |
| LSTM/BiLSTM/GRU могут быть частью forecast-driven climate control. | `energies-18-05821-v2.pdf`; `04_arxiv_2507.21669_BiLSTM_GRU_predictive_control.pdf`; `12_agriengineering_2024_ml_microclimate_web_control.pdf` | Мост от прогноза к управляющим воздействиям. |
| Прогнозы имеют неопределенность, которую нельзя игнорировать в управлении. | `agriculture-15-02461.pdf`; `1-s2.0-S2772375524003551-main.pdf` | Ограничения ML и необходимость защитного нижнего контура. |
| PID/fuzzy остаются полезными как надежный нижний уровень управления. | `16_volgau_2026_intelligent_temperature_control.pdf`, стр. 517-522; `19_urfu_diploma_intelligent_control_2021.pdf`; `24_cyberleninka_sravnitelnyy_analiz.pdf` | Сбалансировать обзор, не утверждать, что ML заменяет все. |
| MPC подходит для теплицы благодаря учету модели, ограничений и горизонта прогноза. | `1-s2.0-S2772375524003551-main.pdf`; `14_arxiv_2303.06110_RL_vs_MPC_greenhouse.pdf`; `03_arxiv_2409.12789_RL_based_MPC.pdf` | Раздел про продвинутые методы управления. |
| RL может улучшать управление по данным, но требует осторожности. | `1-s2.0-S2772375524003551-main.pdf`; `02_arxiv_2506.13278_RL_MPC_greenhouse.pdf`; `05_sensors_2024_iot_rl_greenhouse_climate_control.pdf` | Описать RL как перспективный верхний слой, а не как обязательную полную реализацию. |
| Опыт оператора/агронома можно включать в интеллектуальную систему. | `15_arxiv_2505.23355_grower_in_loop_RL_greenhouse.pdf`; `24_cyberleninka_sravnitelnyy_analiz.pdf` | Раздел про человеко-ориентированное управление и перспективы. |
| Энергоэффективность является ключевым мотивом интеллектуального управления. | `energies-18-05821-v2.pdf`; `06_scirep_2025_energy_optimization_plant_comfort_abc.pdf`; `applsci-16-04859.pdf` | Актуальность, экономическая и экологическая мотивация. |
| Собственная ВКР должна занять промежуточную позицию между инженерной АСУ и ML/MPC/RL-исследованиями. | `20_uspu_diploma_greenhouse_microcontrollers.pdf`; `12_agriengineering_2024_ml_microclimate_web_control.pdf`; `1-s2.0-S2772375524003551-main.pdf`; `agriculture-16-00761-v2.pdf` | Финальный вывод обзора и постановка задачи диплома. |

## Источники, которые лучше не ставить центральными

| Источник | Почему второстепенный |
|---|---|
| `26_agriarticles_iot_local_forecasting.pdf` | Полезен для аграрного IoT и локального прогноза погоды, но не про тепличный контур напрямую. |
| `13_agronomy_2024_attention_cnn_lstm_mushroom_greenhouse.pdf` | Сильный ML-пример, но объект - грибная теплица. |
| `agriengineering-07-00380.pdf` | Хороший IoT-эксперимент, но культура риса и агрономическая постановка отличаются от основной темы. |
| `applsci-16-04859.pdf` | Важен для энергетического контекста, но слишком широкий для основной методики. |
| `19_urfu_diploma_intelligent_control_2021.pdf` | Температурное управление помещением, а не теплицей; использовать как аналог по fuzzy/temperature control. |

