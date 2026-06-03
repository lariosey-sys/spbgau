# Раскладка источников по разделам ВКР

Этот файл нужен для дальнейшей сборки текста: он показывает, где какой источник использовать и какие источники являются основными.

## Введение

| Тезис | Источники | Приоритет |
|---|---|---|
| Рост актуальности smart greenhouse и защищенного грунта | El Ouaham et al.; Ван, Харисов; Bersani et al. | Высокий |
| Энергоэффективность и устойчивость как мотивация | Aborujilah et al.; Wu and Fu; Jawad et al. | Высокий |
| Необходимость IoT и сбора телеметрии | Bersani et al.; MQTT article; Кельсин | Высокий |
| Переход от реактивного управления к прогнозному | Aborujilah et al.; Thwin et al.; Tарков, Сукьясов | Высокий |

## Глава 1

| Раздел | Основные источники | Дополнительные источники |
|---|---|---|
| 1.1. Теплица как киберфизическая система | El Ouaham et al.; Ван, Харисов; Халина, Цыбанюк | Гречиха; Тарков, Сукьясов |
| 1.2. IoT-архитектура | Bersani et al.; MQTT article; Кельсин | Joni et al.; Manoharan et al.; Thwin et al. |
| 1.3. Прогнозирование | Alhnaity et al.; Gong et al.; Ahn et al.; Aborujilah et al.; Thwin et al. | Huang et al.; Choi and Yang; Soumo et al. |
| 1.4. Методы управления | Воробьева и др.; Mallick et al.; Msaad et al.; Morcego et al. | Xiao et al.; Platero-Horcajadas et al.; Jawad et al. |
| 1.5. Энергоэффективность | Aborujilah et al.; Wu and Fu; Jawad et al. | Hindi et al.; Platero-Horcajadas et al. |
| 1.6. Выводы | Thwin et al.; Mallick et al.; Кельсин; El Ouaham et al. | Choi and Yang; Bersani et al. |

## Глава 2

| Раздел | Источники | Связь с проектом |
|---|---|---|
| Требования к системе | Ван, Харисов; Халина, Цыбанюк; Гречиха | Определить параметры: температура, влажность, CO2, освещение, полив/вентиляция. |
| Сенсорный слой | Bersani et al.; MQTT article; Кельсин | `sensor_th.ino`, `sensor_co2.ino`, MQTT topics `greenhouse/env/.../state`. |
| Управляющий слой | Халина, Цыбанюк; Кельсин; Воробьева и др. | `greenhouse_mega.ino`, 15 реле, группы заслонок/вентиляторов/ТЭНов/насосов/фильтров. |
| MQTT и сервер | MQTT article; Bersani et al.; Thwin et al. | Mosquitto, Flask MQTT client, relay commands and states. |
| История и данные для ML | Ahn et al.; Aborujilah et al.; Thwin et al.; Choi and Yang | SQLite `sensor_log`, `relay_log`, будущие признаки и target-переменные. |
| Профили управления | Thwin et al.; Mallick et al.; Воробьева и др. | `profiles.json`, pre-actions, delay, main-actions, reverse actions. |

## Глава 3

Файл черновика: `thesis/chapter_03_implementation_testing.md`.

| Раздел | Источники | Что доказать |
|---|---|---|
| Аппаратная реализация | Кельсин; MQTT article; Bersani et al. | Система имеет датчики, контроллер, исполнительные устройства и связь. |
| Прошивки | Кельсин; MQTT article | Узлы публикуют данные, релейный контроллер принимает команды. |
| Dashboard | Thwin et al.; Bersani et al. | Web integration, отображение состояния, управление реле, история. |
| Проверка работоспособности | Халина, Цыбанюк; Кельсин | Замыкание контура: датчик -> MQTT -> dashboard -> команда -> реле -> состояние. |
| Подготовка ML-эксперимента | Ahn et al.; Aborujilah et al.; Choi and Yang; Thwin et al. | Экспорт и накопление временных рядов для будущей модели прогноза. |

Детальный план ML-эксперимента: `thesis/ml_experiment_plan.md`.

## Что не перегружать в основном тексте

| Источник/тема | Как использовать |
|---|---|
| Agricultural Energy Internet | Упомянуть в актуальности и перспективах, не делать центральной темой. |
| Grower-in-the-loop RL | Упомянуть как перспективу развития интерфейса оператора. |
| Attention CNN-LSTM для грибной теплицы | Использовать как дополнительный пример ML, но не как основной метод. |
| Artificial bee colony | Упомянуть как альтернативную оптимизацию, не смешивать с ML-прогнозом. |
| ВКР по температуре помещения | Использовать только как аналог fuzzy/temperature control. |
