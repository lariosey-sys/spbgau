# Ручная догрузка и проблемные источники

Дата проверки: 26 мая 2026.

Ниже не пиратский список, а очередь ручной догрузки из официальных страниц издателей или репозиториев. После скачивания PDF лучше класть в `literature/` с номером, который не конфликтует с текущими файлами, и затем обновлять `download_log.md`, `literature_matrix.md` и `references.bib`.

## Уже закрыто ручной догрузкой

| Источник | Локальный файл |
|---|---|
| Smart Greenhouses in the Era of IoT and AI | `agriculture-16-00761-v2.pdf` |
| Forecast-Driven Climate Control for Smart Greenhouses | `energies-18-05821-v2.pdf` |
| Probabilistic Deep Learning Framework for Greenhouse Microclimate Prediction | `agriculture-15-02461.pdf` |
| Smart Farming Experiment: IoT-Enhanced Greenhouse Design for Rice Cultivation | `agriengineering-07-00380.pdf` |
| Clean and Smart Energy Technologies for Agricultural Energy Internet Systems | `applsci-16-04859.pdf` |
| Reinforcement learning-based model predictive control for greenhouse climate control | `1-s2.0-S2772375524003551-main.pdf` |
| MQTT Protocol based Smart Greenhouse Environment Monitoring System using Machine Learning | `MQTT_Protocol_based_Smart_Greenhouse_Environment_M.pdf` |

## Высокий приоритет

| Источник | Ссылка | Причина включения | Что произошло при автозагрузке |
|---|---|---|---|
| Predictive Modeling for Enhanced Plant Cultivation in Greenhouse Environment | https://www.e3s-conferences.org/articles/e3sconf/abs/2024/37/e3sconf_icftest2024_01066/e3sconf_icftest2024_01066.html | Прикладной LSTM-пример для прогнозного управления выращиванием. | PDF-URL найден, но поток обрывается/зависает. |
| Елесин: математическая модель управления температурно-влажностным режимом | http://www.ivdon.ru/uploads/article/pdf/IVD_18_elesin.pdf_1506.pdf | Русскоязычная математическая модель температуры/влажности полезна для главы с моделью объекта. | CLI получил HTML вместо PDF. |

## Средний приоритет

| Источник | Ссылка | Причина включения | Что произошло при автозагрузке |
|---|---|---|---|
| Can AI predict the impact of its implementation in greenhouse farming? | https://www.sciencedirect.com/science/article/pii/S1364032124001461 | Обзор последствий внедрения AI в тепличное хозяйство; пригоден для актуальности и экономического эффекта. | Авторский PDF по ссылке `iris.uniroma1.it` вернул 403. |
| Комп'ютерно-інтегрована система віддаленого керування мікрокліматом смарт теплиці | https://ela.kpi.ua/bitstreams/a60478b3-bc74-4ecf-8acb-b98e4a2de311/download | Инженерная ВКР по удаленному управлению микроклиматом. | DNS `ela.kpi.ua` не разрешился. |

## Низкий приоритет / кандидаты

| Источник | Ссылка | Комментарий |
|---|---|---|
| IoT Based Greenhouse Monitoring System Using Raspberry Pi | https://www.academia.edu/51351077 | Может быть полезен как инженерный пример, но Academia часто требует интерактивного скачивания. |
| Диплом ТНУ по компьютерно-интегрированной системе теплицы | https://etnuir.tnu.edu.ua/bitstream/handle/123456789/388/Срібний%20Максим%20Мколайович.pdf | Полезен как дополнительный ВКР-аналог, но источник не критичен, пока есть УрГПУ/УрФУ/КПИ-кандидат. |
