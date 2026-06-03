# Таблица замены групп цитирования

Этот файл фиксирует все уникальные группы служебных цитат, которые сейчас встречаются в `thesis/*.md`. Правая колонка показывает нумерованный вариант по `literature/references_numbered.md`.

## Правило замены

При финальной сборке текста заменить левую колонку на правую. Если кафедра требует другой стиль, использовать эту таблицу как промежуточную карту.

| Служебная цитата | Нумерованная ссылка | Вхождений |
|---|---:|---:|
| `[elouaham2026smartgreenhouses; bersani2022iotsmartgreenhouse]` | `[1; 2]` | 1 |
| `[aborujilah2025forecastlstm; wu2026agriculturalenergyinternet]` | `[14; 25]` | 1 |
| `[alhnaity2019plantgrowth; gong2021tcnrnnyield; ahn2024transformerrnngreenhouse; choi2025probabilisticmicroclimate]` | `[9; 10; 11; 13]` | 1 |
| `[elouaham2026smartgreenhouses]` | `[1]` | 1 |
| `[vanharisov_cyberleninka]` | `[3]` | 1 |
| `[khalina2020greenhousecontrol]` | `[4]` | 1 |
| `[tarkov2025microclimatemodel]` | `[5]` | 1 |
| `[bersani2022iotsmartgreenhouse]` | `[2]` | 1 |
| `[kelsin2021greenhousemicrocontrollers]` | `[7]` | 1 |
| `[mqtt2020greenhouse]` | `[23]` | 1 |
| `[joni2025iotricegreenhouse]` | `[24]` | 1 |
| `[thwin2024microclimateweb]` | `[16]` | 2 |
| `[alhnaity2019plantgrowth]` | `[9]` | 1 |
| `[gong2021tcnrnnyield]` | `[10]` | 1 |
| `[ahn2024transformerrnngreenhouse]` | `[11]` | 1 |
| `[huang2024attentioncnnlstm]` | `[12]` | 1 |
| `[aborujilah2025forecastlstm]` | `[14]` | 2 |
| `[soumo2026bilstmgrugreenhouse]` | `[15]` | 1 |
| `[choi2025probabilisticmicroclimate]` | `[13]` | 1 |
| `[vorobyeva2026greenhousetemperature]` | `[6]` | 1 |
| `[mallick2025rlbasedmpcgreenhouse]` | `[17]` | 1 |
| `[msaad2025rlmpcgreenhouse]` | `[18]` | 1 |
| `[morcego2023rlversusmpc]` | `[19]` | 1 |
| `[xiao2025growerlooprl]` | `[20]` | 1 |
| `[jawad2025abcgreenhouse]` | `[22]` | 1 |
| `[wu2026agriculturalenergyinternet]` | `[25]` | 1 |
| `[chen2025environmentcontrolreview]` | `[28]` | 1 |
| `[ogunlowo2021heatmassgreenhouse]` | `[29]` | 1 |
| `[li2023heathumidityventilation]` | `[30]` | 1 |
| `[ghaderi2023heatrecoverygreenhouse]` | `[31]` | 1 |
| `[samarin2025simulationmicroclimate]` | `[32]` | 1 |
| `[platero2024iotrlgreenhouse]` | `[21]` | 1 |
| `[bersani2022iotsmartgreenhouse; mqtt2020greenhouse]` | `[2; 23]` | 2 |
| `[mqtt2020greenhouse; joni2025iotricegreenhouse]` | `[23; 24]` | 1 |
| `[ahn2024transformerrnngreenhouse; aborujilah2025forecastlstm; choi2025probabilisticmicroclimate]` | `[11; 14; 13]` | 1 |
| `[mallick2025rlbasedmpcgreenhouse; tarkov2025microclimatemodel; khalina2020greenhousecontrol]` | `[17; 5; 4]` | 1 |
| `[alhnaity2019plantgrowth; ahn2024transformerrnngreenhouse; aborujilah2025forecastlstm]` | `[9; 11; 14]` | 1 |
| `[khalina2020greenhousecontrol; mallick2025rlbasedmpcgreenhouse]` | `[4; 17]` | 1 |
| `[ahn2024transformerrnngreenhouse; aborujilah2025forecastlstm; thwin2024microclimateweb; choi2025probabilisticmicroclimate]` | `[11; 14; 16; 13]` | 1 |
| `[chen2025environmentcontrolreview; ghaderi2023heatrecoverygreenhouse]` | `[28; 31]` | 1 |
| `[samarin2025simulationmicroclimate; ogunlowo2021heatmassgreenhouse]` | `[32; 29]` | 1 |

## Проверка после замены

После замены в копии финального текста выполнить проверку:

```bash
rg -n '\[[A-Za-z0-9_; -]+\]' thesis
```

Команда не должна находить служебные citation keys в финальной версии. В рабочих файлах `thesis/*.md` их можно оставить до окончательного выбора формата ссылок.
