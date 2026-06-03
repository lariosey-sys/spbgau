# Промежуточные заметки исследовательского анализа

## Проверенные источники

- `Данные салат мощность.xlsx`: все 11 листов.
- `history_2026-05-26.db`: таблицы `sensor_log` и `relay_log`.
- CSV-экспорты sensor/relay summary и raw log.
- JSON `names`, `profiles`, `rules`.

## Главные наблюдения

1. Датчики температуры не взаимозаменяемы: расхождения между узлами систематические и достаточно большие для учета в модели.
2. CO2-канал содержит много нулевых значений; анализ CO2 требует фильтрации технических нулей.
3. Релейный журнал полезен для разведочного event-study, но мал для строгого вывода об эффективности оборудования.
4. Для световых вариантов добавлен слой PPFD и DLI: фотопериод 18 ч свет / 6 ч ночь, PPFD 79,0-245,5 мкмоль/(м2·с), DLI 5,12-15,91 моль/(м2·сут).
5. Электрические измерения в Вт из Excel сохранены отдельно и не смешиваются с PPFD: это разные физические показатели.
6. Гипотеза о близости ручной температуры раствора к co2-1 не подтвердилась устойчиво; чаще ближе th-1, а точное сравнение ограничено отсутствием времени измерения внутри дня.

## Таблицы

- `analysis/tables/anomalies_and_quality_flags.csv`
- `analysis/tables/bolting_notes.csv`
- `analysis/tables/excel_numeric_column_summary.csv`
- `analysis/tables/excel_sheet_inventory.csv`
- `analysis/tables/lag_correlations.csv`
- `analysis/tables/light_treatments_ppfd_dli.csv`
- `analysis/tables/nutrient_solution_summary.csv`
- `analysis/tables/organoleptic_mentions.csv`
- `analysis/tables/phenology.csv`
- `analysis/tables/power_measurements.csv`
- `analysis/tables/reference_temperature_comparison.csv`
- `analysis/tables/reference_temperature_measurements.csv`
- `analysis/tables/relay_intervals.csv`
- `analysis/tables/relay_response_windows.csv`
- `analysis/tables/relay_summary_enriched.csv`
- `analysis/tables/sensor_daily_summary.csv`
- `analysis/tables/sensor_device_summary.csv`
- `analysis/tables/sensor_gap_analysis.csv`
- `analysis/tables/sensor_hourly_cycles.csv`
- `analysis/tables/sensor_pairwise_comparison.csv`
- `analysis/tables/source_inventory.csv`
- `analysis/tables/storage_losses.csv`
- `analysis/tables/top_temperature_divergence_periods.csv`

## Графики

- `analysis/figures/daily_co2.svg`
- `analysis/figures/daily_humidity.svg`
- `analysis/figures/daily_temperature.svg`
- `analysis/figures/electric_power_measurements.svg`
- `analysis/figures/hourly_co2.svg`
- `analysis/figures/hourly_humidity.svg`
- `analysis/figures/hourly_temperature.svg`
- `analysis/figures/light_treatments_dli.svg`
- `analysis/figures/relay_event_counts.svg`
- `analysis/figures/storage_loss_top15.svg`
- `analysis/figures/temperature_pairwise_mean_abs_diff.svg`
