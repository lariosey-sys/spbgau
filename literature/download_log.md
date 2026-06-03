# Лог сбора PDF

Дата актуализации: 26 мая 2026.

Статусы:

- `downloaded` - PDF есть локально и читается через `pypdf`.
- `downloaded_now` - PDF был догружен в ходе текущей обработки.
- `manual` - источник открыт/найден, но автоматическая загрузка не дала корректный PDF.
- `blocked_or_unstable` - сервер вернул HTML/403, DNS-ошибку или обрывал поток.
- `candidate` - источник полезен для обзора, но пока не включен в основной корпус.

| Статус | URL | Локальный путь | Комментарий |
|---|---|---|---|
| downloaded | https://arxiv.org/abs/1907.00624 | `01_arxiv_1907.00624_DL_plant_growth.pdf` | LSTM для роста и урожайности растений в теплице. |
| downloaded | https://arxiv.org/abs/2506.13278 | `02_arxiv_2506.13278_RL_MPC_greenhouse.pdf` | RL-guided MPC для автономного управления теплицей. |
| downloaded | https://arxiv.org/abs/2409.12789 | `03_arxiv_2409.12789_RL_based_MPC.pdf` | RL-based MPC для климат-контроля теплицы. |
| downloaded_now | https://arxiv.org/abs/2507.21669 | `04_arxiv_2507.21669_BiLSTM_GRU_predictive_control.pdf` | Догружено автоматически; 38 страниц. |
| downloaded | https://doi.org/10.3390/s24248109 | `05_sensors_2024_iot_rl_greenhouse_climate_control.pdf` | IoT + reinforcement learning для climate control. |
| downloaded | https://doi.org/10.1038/s41598-024-84141-5 | `06_scirep_2025_energy_optimization_plant_comfort_abc.pdf` | Energy optimization + plant comfort через artificial bee colony. |
| downloaded_now | https://mdpi-res.com/d_attachment/sensors/sensors-21-04537/article_deploy/sensors-21-04537-with-cover.pdf | `07_pmc_sensors_2021_greenhouse_crop_yield_tcn_rnn.pdf` | Догружено автоматически через MDPI CDN; 17 страниц. |
| downloaded | https://doi.org/10.3390/agronomy14030417 | `08_agronomy_2024_transformer_rnn_greenhouse_prediction.pdf` | Transformer/RNN прогноз температуры, влажности и CO2. |
| downloaded | https://hal.science/hal-05401361 | `09_hal_RL_Enhanced_MPC_Sustainable_Greenhouse.pdf` | RL-enhanced MPC, препринт HAL. |
| downloaded | local/semantic-scholar-export | `10_semanticscholar_iot_greenhouse_systems.pdf` | IoT-enabled greenhouse systems. |
| downloaded | https://doi.org/10.1371/journal.pone.0344946 | `11_semanticscholar_hybrid_RL_IoT_MPC.pdf` | PLOS One 2026, autonomous agriculture control systems. |
| downloaded | https://doi.org/10.3390/agriengineering6030165 | `12_agriengineering_2024_ml_microclimate_web_control.pdf` | ML-прогноз микроклимата + web integration + equipment control. |
| downloaded | https://doi.org/10.3390/agronomy14030473 | `13_agronomy_2024_attention_cnn_lstm_mushroom_greenhouse.pdf` | Attention CNN-LSTM для прогнозирования среды грибной теплицы. |
| downloaded | https://arxiv.org/abs/2303.06110 | `14_arxiv_2303.06110_RL_vs_MPC_greenhouse.pdf` | Сравнение RL и MPC для тепличного климата. |
| downloaded | https://arxiv.org/abs/2505.23355 | `15_arxiv_2505.23355_grower_in_loop_RL_greenhouse.pdf` | Grower-in-the-loop interactive RL. |
| downloaded | local/volgau-issue | `16_volgau_2026_intelligent_temperature_control.pdf` | Нужная статья внутри сборника: стр. 517-522. |
| downloaded | https://doi.org/10.3390/en15103834 | `17_energies_2022_iot_smart_greenhouses_industry_4.pdf` | IoT approaches for monitoring and control of smart greenhouses. |
| downloaded | local/urfu-thesis | `19_urfu_diploma_intelligent_control_2021.pdf` | Магистерская ВКР по интеллектуальному температурному управлению. |
| downloaded | local/uspu-thesis | `20_uspu_diploma_greenhouse_microcontrollers.pdf` | ВКР по микроконтроллерам, Raspberry Pi/Arduino/MQTT/Flask. |
| downloaded | local/robotics-nw | `21_robotics_nw_ru_greenhouse_models.pdf` | Автоматизация вертикальных ферм и тепличных процессов. |
| downloaded | local/irsau-issue | `22_irsau_maket_students_2025.pdf` | Нужная статья внутри сборника: стр. 836-839. |
| downloaded | local/altstu-conf | `23_altstu_conf_2020_greenhouse.pdf` | Нужная статья внутри сборника: стр. 125-126. |
| downloaded | https://cyberleninka.ru/article/n/sravnitelnyy-analiz-sovremennyh-sistem-avtomatizirovannogo-upravleniya-mikroklimatom-v-teplitse | `24_cyberleninka_sravnitelnyy_analiz.pdf` | Сравнительный анализ АСУ микроклимата. |
| downloaded | https://cyberleninka.ru/article/n/obzor-sistemy-upravleniya-mikroklimatom-avtomatizirovannoy-teplitsy-dlya-vyraschivaniya-mikrozeleni | `25_cyberleninka_obzor_mikrozelen.pdf` | Обзор систем для микрозелени. |
| downloaded | http://www.agriarticles.com | `26_agriarticles_iot_local_forecasting.pdf` | IoT + AI local weather forecasting in extension services. |
| downloaded_manual | https://www.mdpi.com/2077-0472/16/7/761 | `agriculture-16-00761-v2.pdf` | Добавлено вручную; ранее MDPI отдавал 403 через CLI. |
| downloaded_manual | https://www.mdpi.com/1996-1073/18/21/5821 | `energies-18-05821-v2.pdf` | Добавлено вручную; ранее MDPI отдавал 403 через CLI. |
| downloaded_manual | https://www.mdpi.com/2077-0472/15/23/2461 | `agriculture-15-02461.pdf` | Добавлено вручную; ранее MDPI отдавал 403 через CLI. |
| downloaded_manual | https://www.mdpi.com/2624-7402/7/11/380 | `agriengineering-07-00380.pdf` | Добавлено вручную; ранее MDPI отдавал 403 через CLI. |
| downloaded_manual | https://www.mdpi.com/2076-3417/16/10/4859 | `applsci-16-04859.pdf` | Добавлено вручную; ссылка подтверждена. |
| downloaded_manual | https://www.sciencedirect.com/science/article/pii/S2772375524003551 | `1-s2.0-S2772375524003551-main.pdf` | Добавлена опубликованная версия Mallick et al. |
| downloaded_manual | https://www.researchgate.net/publication/363700078 | `MQTT_Protocol_based_Smart_Greenhouse_Environment_M.pdf` | Добавлен PDF статьи по MQTT. |
| duplicate | https://arxiv.org/abs/2506.13278 | `2506.13278v1.pdf` | Дубль `02_arxiv_2506.13278_RL_MPC_greenhouse.pdf`. |
| duplicate | https://arxiv.org/abs/2507.21669 | `2507.21669v2.pdf` | Дубль `04_arxiv_2507.21669_BiLSTM_GRU_predictive_control.pdf`. |
| duplicate_variant | https://doi.org/10.3390/s21134537 | `sensors-21-04537.pdf` | Та же статья, что `07_pmc_sensors_2021_greenhouse_crop_yield_tcn_rnn.pdf`, но другая PDF-сборка. |
| blocked_or_unstable | https://www.e3s-conferences.org/articles/e3sconf/pdf/2024/37/e3sconf_icftest2024_01066.pdf | нет | Сервер зависает и отдает неполный PDF; нужен ручной скачанный файл. |
| blocked_or_unstable | http://www.ivdon.ru/uploads/article/pdf/IVD_18_elesin.pdf_1506.pdf | нет | CLI получил HTML вместо PDF. |
| blocked_or_unstable | https://ela.kpi.ua/bitstreams/a60478b3-bc74-4ecf-8acb-b98e4a2de311/download | нет | DNS `ela.kpi.ua` не разрешился из текущей среды. |
| blocked_or_unstable | https://iris.uniroma1.it/retrieve/b1c7a735-278e-4dc0-9a81-e90c58891740/Hoseinzadeh_Can%20AI%20predict_2024.pdf | нет | Сервер вернул 403. |
| blocked_or_unstable | https://www.ijitee.org/wp-content/uploads/papers/v9i9/I7149079920.pdf | нет | Поток зависал и оборвался по таймауту. |
