# Литература для ВКР
## «Разработка и внедрение интеллектуальной системы управления микроклиматом в теплице на основе машинного обучения»

Папка создана: 2026-05-23  
Актуализация рабочей базы: 2026-05-26
Некоторые файлы скачаны автоматически, некоторые требуют ручного скачивания (сайты блокируют автоматические запросы).

---

## Рабочие файлы обработки

По аналогии с соседней папкой `../vkr/thesis/literature` эта папка теперь используется как база для написания ВКР:

- `literature_matrix.md` - матрица источников: год, блок ВКР, назначение и ограничения.
- `download_log.md` - что скачано, что догружено сейчас и что не удалось скачать автоматически.
- `paywalled.md` - очередь ручной догрузки с приоритетами.
- `references.bib` - черновой BibTeX для основных источников.
- `source_cards.md` - карточки источников: метод, польза для ВКР, ограничения.
- `duplicates.md` - учет дублей и вариантов PDF.
- `reviews/` - тематические обзоры и синтезированный обзор для главы 1.
- `extracted/` - автоматически извлеченные первые страницы и инвентаризация PDF через `pypdf`.

---

## ✅ Уже скачано (в этой папке)

### Обзорные статьи (IoT + ИИ в теплицах)
| Файл | Авторы | Описание |
|------|--------|----------|
| `01_arxiv_1907.00624_DL_plant_growth.pdf` | Alhnaity B. et al. | LSTM для прогнозирования роста растений и урожайности в теплице (томат, фикус). Сравнение LSTM vs SVR vs RF. |
| `02_arxiv_2506.13278_RL_MPC_greenhouse.pdf` | Msaad S. et al. | RL-Guided MPC для автономного управления теплицей. Интеграция RL и MPC. |
| `03_arxiv_2409.12789_RL_based_MPC.pdf` | Mallick S. et al. | Reinforcement learning-based MPC для управления климатом теплицы. Уменьшение нарушений ограничений. |
| `04_arxiv_2507.21669_BiLSTM_GRU_predictive_control.pdf` | Soumo E.A. et al. | Data-driven climate regulation: BiLSTM/GRU predictive control для выращивания салата. |
| `05_sensors_2024_iot_rl_greenhouse_climate_control.pdf` | Platero-Horcajadas M. et al. | IoT + reinforcement learning для оптимизированного управления климатом. |
| `06_scirep_2025_energy_optimization_plant_comfort_abc.pdf` | Jawad M. et al. | Energy optimization and plant comfort management через artificial bee colony. |
| `07_pmc_sensors_2021_greenhouse_crop_yield_tcn_rnn.pdf` | Gong L. et al. | Прогноз урожайности тепличных культур: TCN + RNN, сравнение с классическими ML baseline. |
| `08_agronomy_2024_transformer_rnn_greenhouse_prediction.pdf` | Ahn J.Y. et al. | Transformer/RNN прогноз температуры, влажности и CO2 в теплице. |
| `09_hal_RL_Enhanced_MPC_Sustainable_Greenhouse.pdf` | (HAL) | RL-Enhanced MPC для устойчивого управления климатом теплицы. Soft Actor-Critic + MPC. |
| `11_semanticscholar_hybrid_RL_IoT_MPC.pdf` | (Semantic Scholar) | Гибридные подходы RL + IoT + MPC + Digital Twins для автономных теплиц. |
| `10_semanticscholar_iot_greenhouse_systems.pdf` | (Semantic Scholar) | IoT-enabled Greenhouse Systems: Optimizing Plant Cultivation. Node-RED, MQTT, Raspberry Pi. |
| `12_agriengineering_2024_ml_microclimate_web_control.pdf` | Thwin K.M.M. et al. | ML microclimate forecasting + web integration + adaptive equipment control. |
| `13_agronomy_2024_attention_cnn_lstm_mushroom_greenhouse.pdf` | Huang S. et al. | Attention CNN-LSTM для прогноза среды грибной теплицы. |
| `14_arxiv_2303.06110_RL_vs_MPC_greenhouse.pdf` | Morcego B. et al. | Сравнение RL и MPC для greenhouse climate control. |
| `15_arxiv_2505.23355_grower_in_loop_RL_greenhouse.pdf` | Xiao M. et al. | Grower-in-the-loop interactive RL для управления климатом. |
| `17_energies_2022_iot_smart_greenhouses_industry_4.pdf` | Bersani C. et al. | IoT approaches for monitoring and control of smart greenhouses in Industry 4.0. |
| `1-s2.0-S2772375524003551-main.pdf` | Mallick S. et al. | Опубликованная версия RL-based MPC for greenhouse climate control. |
| `agriculture-16-00761-v2.pdf` | El Ouaham W. et al. | Большой обзор smart greenhouse в эпоху IoT и AI. |
| `agriculture-15-02461.pdf` | Choi W.-J., Yang M. | Probabilistic deep learning для прогноза микроклимата с неопределенностью. |
| `energies-18-05821-v2.pdf` | Aborujilah A. et al. | Forecast-driven climate control и energy optimization через LSTM. |
| `agriengineering-07-00380.pdf` | Joni I.M. et al. | IoT-enhanced greenhouse design для smart farming experiment. |
| `applsci-16-04859.pdf` | Wu Y., Fu X. | Agricultural Energy Internet и energy-aware greenhouse control. |
| `MQTT_Protocol_based_Smart_Greenhouse_Environment_M.pdf` | (IJITEE) | MQTT protocol based smart greenhouse environment monitoring. |

### Русскоязычные источники
| Файл | Авторы | Описание |
|------|--------|----------|
| `16_volgau_2026_intelligent_temperature_control.pdf` | Воробьева Н.С. и др. | Интеллектуальная система контроля температуры в теплице. Прогнозирующий алгоритм, тестовый стенд. |
| `19_urfu_diploma_intelligent_control_2021.pdf` | Тюхтий Ю.А. | Диплом УрФУ: интеллектуальная система управления температурным режимом. Нечёткая логика, термостаты. |
| `20_uspu_diploma_greenhouse_microcontrollers.pdf` | Кельсин А.А. | Диплом УрГПУ: АСУ тепличным хозяйством на микроконтроллерах. Raspberry Pi + Arduino + MQTT + Flask. |
| `21_robotics_nw_ru_greenhouse_models.pdf` | (Робототехника СЗФО) | Модели, методы и архитектуры автоматизации теплиц. Нейросети + нечёткая логика. |
| `22_irsau_maket_students_2025.pdf` | (ИРСАУ) | Макет студентов: уравнения баланса для параметров микроклимата. |
| `23_altstu_conf_2020_greenhouse.pdf` | (АлтГТУ) | Требования к АСУ микроклиматом тепличного комплекса. Структурная схема, алгоритмы. |
| `24_cyberleninka_sravnitelnyy_analiz.pdf` | (CyberLeninka) | Сравнительный анализ современных систем АСУ микроклиматом. Переход к предиктивному контролю. |
| `25_cyberleninka_obzor_mikrozelen.pdf` | (CyberLeninka) | Обзор систем управления микроклиматом для микрозелени. ОВЕН, WirenBoard. |

### Прочие
| Файл | Авторы | Описание |
|------|--------|----------|
| `26_agriarticles_iot_local_forecasting.pdf` | (AgriArticles) | IoT sensor networks, data fusion, AI/ML methods for local forecasting in agriculture. |

---

## ⬇️ Требуется скачать вручную

Ниже ссылки на источники, которые заблокированы для автоматического скачивания (403/таймаут).  
Откройте ссылку в браузере и сохраните PDF через кнопку «Download» / «Скачать» / «PDF». Подробные статусы и причины см. в `paywalled.md`.

### Preprints (дополнительно)
1. **Explainable Deep Learning for Greenhouse Horticulture** (Preprints, 2026)  
   https://www.preprints.org/manuscript/202602.1268

### ScienceDirect / PMC / E3S
2. **Predictive Modeling for Enhanced Plant Cultivation in Greenhouse Environment** (E3S, 2024)  
   https://www.e3s-conferences.org/articles/e3sconf/abs/2024/37/e3sconf_icftest2024_01066/e3sconf_icftest2024_01066.html

### ResearchGate / Academia / Прочие
3. **IoT Based Greenhouse Monitoring System Using Raspberry Pi**  
    https://www.academia.edu/51351077

4. **Hoseinzadeh — Can AI predict...** (Renewable and Sustainable Energy Reviews, 2024)  
    https://iris.uniroma1.it/retrieve/b1c7a735-278e-4dc0-9a81-e90c58891740/Hoseinzadeh_Can%20AI%20predict_2024.pdf

### Русскоязычные (недоступные автоматически)
5. **Елесин — математическая модель управления температурно-влажностным режимом** (ИВДОН)  
    http://www.ivdon.ru/uploads/article/pdf/IVD_18_elesin.pdf_1506.pdf

6. **Диплом КПИ** — «Комп'ютерно-інтегрована система віддаленого керування мікрокліматом смарт теплиці»  
    https://ela.kpi.ua/bitstreams/a60478b3-bc74-4ecf-8acb-b98e4a2de311/download

7. **Диплом ТНУ** — «Розробка комп'ютерно-інтегрованої системи...»  
    https://etnuir.tnu.edu.ua/bitstream/handle/123456789/388/Срібний%20Максим%20Мколайович.pdf

---

## 📋 Дополнительные ссылки для обзора (без PDF)

- **Сравнительный анализ на CyberLeninka**  
  https://cyberleninka.ru/article/n/sravnitelnyy-analiz-sovremennyh-sistem-avtomatizirovannogo-upravleniya-mikroklimatom-v-teplitse

- **Обзор системы управления микроклиматом для микрозелени**  
  https://cyberleninka.ru/article/n/obzor-sistemy-upravleniya-mikroklimatom-avtomatizirovannoy-teplitsy-dlya-vyraschivaniya-mikrozeleni

- **Кульмамиров С.А. — Результаты анализа ИСУМ «умной теплицы»**  
  https://elibrary.ru/item.asp?id=46320055  
  http://synergy-journal.ru/archive/article6036

- **Макет студентов ИРСАУ** (альтернативная ссылка)  
  https://irsau.ru/structure/science/materialy/2025/Макет_студентов.pdf

---

## 💡 Совет по использованию

Для оформления списка литературы в дипломе рекомендуется:
- **60–70% англоязычных источников** (желательно из Scopus / WoS: MDPI, Elsevier, IEEE, arXiv)
- **30–40% русскоязычных** (CyberLeninka, elibrary.ru, диссертации, ВКР)
- Обязательно включить источники не старше 2020–2021 гг. (показать актуальность)
- Классические работы по LSTM/MPC/RL можно брать 2015–2020 гг.
