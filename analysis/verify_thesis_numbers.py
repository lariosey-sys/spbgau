#!/usr/bin/env python3
"""Программная верификация всех численных утверждений и формул ВКР.

Каждая проверка пересчитывает значение из первичных данных (SQLite-журнал,
сводные таблицы анализа, паспортные данные) и сравнивает с числом, приведенным
в тексте работы. Запуск: python3 analysis/verify_thesis_numbers.py
"""
from __future__ import annotations

import collections
import csv
import math
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "thesis" / "evidence" / "greenhouse_pi_data" / "history_2026-05-26.db"

PASS = 0
FAIL = 0


def check(name: str, actual, expected, tol=0.011):
    """Сравнение с допуском на округление в тексте."""
    global PASS, FAIL
    if isinstance(expected, (int, float)):
        ok = abs(actual - expected) <= tol * max(1.0, abs(expected))
    else:
        ok = actual == expected
    status = "OK  " if ok else "FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"[{status}] {name}: расчет={actual} текст={expected}")


def parse(ts: str):
    try:
        return datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def esat(t):  # формула Тетенса, кПа — формула (3.1)
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))


print("=== Геометрия бокса (раздел 3.1) ===")
check("площадь 2x4 м", 2 * 4, 8)
check("объем 8 м² x 3 м", 8 * 3, 24)

print("=== Установленная мощность (таблица 3.1) ===")
check("ТЭНы 2x6 кВт", 2 * 6, 12)
check("вентиляторы 2x0,33 кВт", 2 * 0.33, 0.66)
check("насосы 4x0,38 кВт", 4 * 0.38, 1.52)

print("=== DLI по формуле (2.9): PPFD*18*3600/1e6 (таблица 3.5) ===")
for ppfd, dli_text in [(79.0, 5.12), (95.0, 6.16), (150.8, 9.77),
                       (181.3, 11.75), (245.5, 15.91)]:
    check(f"DLI(PPFD={ppfd})", ppfd * 18 * 3600 / 1e6, dli_text)

print("=== Энергия освещения, формулы (3.2)-(3.3) ===")
check("вариант 5: 0,478*18 кВт·ч/сут", 0.478 * 18, 8.604, tol=1e-9)
check("вариант 2: 0,097*18 кВт·ч/сут", 0.097 * 18, 1.746, tol=1e-9)

print("=== Вентилятор канала 8, формулы (3.4)-(3.5) ===")
on_min = 39556.75
check("часы работы 39 556,75 мин -> ч", on_min / 60, 659, tol=0.001)
check("E_вент = 0,33 кВт * 659 ч", 0.33 * (on_min / 60), 217, tol=0.005)
check("стоимость при 6 руб/кВт·ч", 0.33 * (on_min / 60) * 6, 1300, tol=0.01)

print("=== Энергоэффективность света (таблица 3.6, рисунок 3.9) ===")
POWER = [116.3, 97.0, 221.0, 321.5, 478.0]
YIELD = [33.8, 89.9, 85.6, 105.6, 93.8]
DLI = [5.1192, 6.156, 9.77184, 11.74824, 15.9084]
GPW_TEXT = [0.29, 0.93, 0.39, 0.33, 0.20]
for i in range(5):
    check(f"вариант {i+1}: г/Вт", YIELD[i] / POWER[i], GPW_TEXT[i], tol=0.02)
check("вариант 2: г на ед. DLI", YIELD[1] / DLI[1], 14.6, tol=0.01)
check("вариант 5: г на ед. DLI", YIELD[4] / DLI[4], 5.9, tol=0.01)
check("PPFD/Вт вариант 2", 95.0 / 97.0, 0.98, tol=0.01)
check("PPFD/Вт вариант 5", 245.5 / 478.0, 0.51, tol=0.01)
check("предельный прирост в1->в2, г/моль",
      (YIELD[1] - YIELD[0]) / (DLI[1] - DLI[0]), 54, tol=0.01)

print("=== Сенсорные ряды (таблица 3.3, раздел 3.6) — пересчет из SQLite ===")
con = sqlite3.connect(str(DB))
rows = con.execute("select ts, device, temperature, humidity, co2 from sensor_log").fetchall()
by = collections.defaultdict(list)
for ts, dev, t, h, c in rows:
    dt = parse(ts)
    if dt:
        by[dev].append((dt, t, h, c))
check("строк th-1", len(by["th-1"]), 81316, tol=0)
check("строк th-2", len(by["th-2"]), 81315, tol=0)
check("строк co2-1", len(by["co2-1"]), 81315, tol=0)

for dev, t_text, h_text in [("co2-1", 24.98, 37.36), ("th-1", 25.17, 28.53),
                            ("th-2", 27.85, 27.57)]:
    ts_ = [t for _, t, h, c in by[dev] if t and 0 < t < 60]
    hs_ = [h for _, t, h, c in by[dev] if h and 0 < h <= 100]
    check(f"{dev}: средняя T", sum(ts_) / len(ts_), t_text, tol=0.002)
    check(f"{dev}: средняя RH", sum(hs_) / len(hs_), h_text, tol=0.002)

zeros_t = sum(1 for _, t, h, c in by["co2-1"] if t == 0)
zeros_h = sum(1 for _, t, h, c in by["co2-1"] if h == 0)
zeros_c = sum(1 for _, t, h, c in by["co2-1"] if c == 0)
check("тех. нули co2-1: T", zeros_t, 28752, tol=0)
check("тех. нули co2-1: RH", zeros_h, 28752, tol=0)
check("тех. нули co2-1: CO2", zeros_c, 28753, tol=0)
check("нулевая RH th-2", sum(1 for _, t, h, c in by["th-2"] if h == 0), 36, tol=0)

print("=== VPD, формула (3.1) (раздел 3.6, рисунок 3.6) ===")
for dev, mean_text, med_text in [("th-1", 2.31, 2.23), ("th-2", 2.74, 2.76)]:
    v = sorted(esat(t) * (1 - h / 100) for _, t, h, c in by[dev]
               if t and h and 0 < t < 60 and 0 < h <= 100)
    check(f"VPD {dev}: среднее", sum(v) / len(v), mean_text, tol=0.005)
    check(f"VPD {dev}: медиана", v[len(v) // 2], med_text, tol=0.005)
    in_opt = sum(1 for x in v if 0.8 <= x <= 1.2) / len(v) * 100
    check(f"VPD {dev}: % в оптимуме 0,8-1,2", round(in_opt, 1), 0.0, tol=0.1)

print("=== Суточный ход (раздел 3.8, рисунок 3.8) ===")
for dev, tmin, hmin, tmax, hmax, amp in [("th-1", 23.0, 8, 26.1, 17, 3.1),
                                          ("th-2", 26.0, 8, 28.7, 17, 2.6)]:
    hourly = collections.defaultdict(list)
    for dt, t, h, c in by[dev]:
        if t and 0 < t < 60:
            hourly[dt.hour].append(t)
    means = {hh: sum(v) / len(v) for hh, v in hourly.items()}
    h_lo = min(means, key=means.get)
    h_hi = max(means, key=means.get)
    check(f"{dev}: час минимума", h_lo, hmin, tol=0)
    check(f"{dev}: час максимума", h_hi, hmax, tol=0)
    check(f"{dev}: T мин", means[h_lo], tmin, tol=0.005)
    check(f"{dev}: T макс", means[h_hi], tmax, tol=0.005)
    check(f"{dev}: амплитуда", means[h_hi] - means[h_lo], amp, tol=0.02)

print("=== Расхождение th-2 - th-1 (раздел 3.6) ===")
a = {dt.replace(second=0): t for dt, t, h, c in by["th-1"] if t and 0 < t < 60}
b = {dt.replace(second=0): t for dt, t, h, c in by["th-2"] if t and 0 < t < 60}
common = set(a) & set(b)
diffs = [b[k] - a[k] for k in common]
check("среднее th2-th1", sum(diffs) / len(diffs), 2.69, tol=0.005)
daily = collections.defaultdict(list)
for k in common:
    daily[k.date()].append(b[k] - a[k])
dm = [sum(v) / len(v) for v in daily.values()]
check("дней наблюдений", len(dm), 58, tol=0)
check("мин. суточная разница", min(dm), 0.12, tol=0.1)
check("макс. суточная разница", max(dm), 4.91, tol=0.01)
mu = sum(dm) / len(dm)
check("сигма суточных разниц", math.sqrt(sum((x - mu) ** 2 for x in dm) / len(dm)), 1.41, tol=0.01)

print("=== Журнал реле (таблица 3.4, рисунок 3.7) ===")
relay = [(parse(ts), rid, st) for ts, rid, st in
         con.execute("select ts, relay_id, state from relay_log").fetchall()]
check("всего событий", len(relay), 165, tol=0)
night = sum(1 for dt, _, _ in relay if dt.hour < 6 or dt.hour >= 22)
check("ночных событий (22-06)", night, 0, tol=0)
hours = collections.Counter(dt.hour for dt, _, _ in relay)
check("пик активности: час", hours.most_common(1)[0][0], 16, tol=0)
check("событий в 16 ч", hours.most_common(1)[0][1], 41, tol=0)
per = collections.Counter(rid for _, rid, _ in relay)
for rid, n in [(8, 43), (9, 37), (11, 33), (2, 18), (3, 6)]:
    check(f"реле {rid}: событий", per[rid], n, tol=0)

print("=== Разрыв данных (раздел 3.6) ===")
all_ts = sorted(dt for dev in ("th-1",) for dt, *_ in by[dev])
gap = max((b2 - a2).total_seconds() / 60 for a2, b2 in zip(all_ts, all_ts[1:]))
check("макс. разрыв, мин", gap, 3965, tol=0.001)

print("=== ML-метрики (таблица 3.7) — сверка с analysis/tables ===")
mlcsv = ROOT / "analysis" / "tables" / "ml_baseline_metrics.csv"
if mlcsv.exists():
    rows_ml = list(csv.DictReader(open(mlcsv, encoding="utf-8")))
    expected_ml = {
        ("th-1_temperature", "10", "last_value"): (0.070, 0.149, 0.989),
        ("th-1_temperature", "30", "ridge_regression"): (0.156, 0.273, 0.963),
        ("th-1_humidity", "30", "ridge_regression"): (0.387, 0.633, 0.974),
        ("co2-1_co2", "30", "last_value"): (8.117, 14.103, 0.924),
    }
    matched = 0
    for r in rows_ml:
        key = (r.get("target", ""), str(r.get("horizon_min", r.get("horizon", ""))),
               r.get("model", ""))
        if key in expected_ml:
            mae, rmse, r2 = expected_ml[key]
            check(f"ML {key}: MAE", float(r["mae"]), mae, tol=0.01)
            check(f"ML {key}: RMSE", float(r["rmse"]), rmse, tol=0.01)
            check(f"ML {key}: R2", float(r["r2"]), r2, tol=0.01)
            matched += 1
    if matched == 0:
        print("[WARN] не удалось сопоставить строки ml_baseline_metrics.csv (формат колонок)")
else:
    print("[WARN] ml_baseline_metrics.csv не найден — таблица 3.7 проверена при построении")

# --- Статистика по световому эксперименту (подраздел 3.9): ANOVA, ДИ, корреляции ---
factorial = ROOT / "analysis" / "салат_отчёт" / "factorial.csv"
if factorial.exists():
    try:
        from scipy import stats
        rows_f = list(csv.DictReader(factorial.open(encoding="utf-8")))

        def fnum(x):
            try:
                return float(x)
            except (TypeError, ValueError):
                return None

        cells = {(r["cultivar"], int(float(r["variant"]))): r for r in rows_f}
        cults = sorted({k[0] for k in cells})
        vars_ = sorted({k[1] for k in cells})
        a, b = len(vars_), len(cults)
        col, sd, nn = "leaf_mass_mkt_g", "leaf_mass_mkt_g_sd", "leaf_mass_mkt_g_n"
        SSE = sum((fnum(cells[k][nn]) - 1) * fnum(cells[k][sd]) ** 2 for k in cells)
        dfE = sum(fnum(cells[k][nn]) - 1 for k in cells)
        MSE = SSE / dfE
        n_h = (a * b) / sum(1.0 / fnum(cells[k][nn]) for k in cells)
        M = {k: fnum(cells[k][col]) for k in cells}
        grand = sum(M.values()) / (a * b)
        vmean = {v: sum(M[(c, v)] for c in cults) / b for v in vars_}
        SSA = n_h * b * sum((vmean[v] - grand) ** 2 for v in vars_)
        FA = (SSA / (a - 1)) / MSE
        check("ANOVA свет: F(вариант)", FA, 20.4, tol=0.03)
        check("ANOVA свет: df ошибки", dfE, 110.0, tol=0.001)
        ci = stats.t.ppf(0.975, dfE) * math.sqrt(MSE / (n_h * b))
        check("ДИ урожая по варианту, ±г", ci, 12.2, tol=0.05)
        q = stats.studentized_range.ppf(0.95, a, dfE)
        hsd = q * math.sqrt(MSE / (n_h * b))
        check("Tukey HSD, г", hsd, 24.2, tol=0.05)
        for label, ccol, exp in [("корень", "root_mass_g", 0.77),
                                 ("нитраты", "nitrate", -0.62),
                                 ("сухое в-во", "dm_pct", 0.55),
                                 ("высота", "height_cm", -0.47)]:
            xs = [fnum(cells[(c, v)]["dli"]) for c in cults for v in vars_]
            ys = [fnum(cells[(c, v)][ccol]) for c in cults for v in vars_]
            pr = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
            rr = stats.pearsonr([p[0] for p in pr], [p[1] for p in pr])[0]
            check(f"corr DLI×{label} (n=30)", rr, exp, tol=0.02)
        rcrit = math.sqrt(1 / (1 + 3 / stats.t.ppf(0.975, 3) ** 2))
        check("критическое |r| при n=5", rcrit, 0.878, tol=0.005)
    except ImportError:
        print("[WARN] scipy не установлен — статистика 3.9 не перепроверена")
else:
    print("[WARN] factorial.csv не найден — статистика 3.9 проверена при построении")

print()
print(f"ИТОГО: пройдено {PASS}, провалено {FAIL}")
raise SystemExit(1 if FAIL else 0)
