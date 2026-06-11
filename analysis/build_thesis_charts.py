#!/usr/bin/env python3
"""Генерация графиков и диаграмм для ВКР (matplotlib -> PDF).

Скрипт читает SQLite-журнал датчиков/реле и формирует векторные PDF-рисунки в
thesis/figures/. Агробиологические показатели берутся из подтвержденных сводок
по эксперименту со светом (см. analysis/tables и главу 3) во избежание повторного
хрупкого парсинга Excel; все значения соответствуют тексту работы.
"""
from __future__ import annotations

import collections
import math
import sqlite3
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "thesis" / "evidence" / "greenhouse_pi_data" / "history_2026-05-26.db"
OUT = ROOT / "thesis" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Liberation Serif", "Times New Roman"],
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
    }
)

BLUE, RED, GREEN, ORANGE = "#1f5fae", "#c0392b", "#1e8449", "#e08a00"


def parse(ts: str):
    try:
        return datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def load_sensor():
    con = sqlite3.connect(str(DB))
    rows = con.execute(
        "select ts, device, temperature, humidity, co2 from sensor_log"
    ).fetchall()
    con.close()
    data = collections.defaultdict(list)
    for ts, dev, t, h, co2 in rows:
        dt = parse(ts)
        if dt is None:
            continue
        data[dev].append((dt, t, h, co2))
    return data


def load_relay():
    con = sqlite3.connect(str(DB))
    rows = con.execute("select ts, relay_id, state from relay_log").fetchall()
    con.close()
    return [(parse(ts), rid, st) for ts, rid, st in rows if parse(ts)]


def esat(temp):  # давление насыщения по Тетенсу, кПа
    return 0.6108 * math.exp(17.27 * temp / (temp + 237.3))


def save(fig, name):
    path = OUT / name
    fig.savefig(path)
    plt.close(fig)
    print("written", path.relative_to(ROOT))


def chart_diurnal(data):
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for dev, color, label in (("th-1", BLUE, "th-1"), ("th-2", RED, "th-2")):
        hourly = collections.defaultdict(list)
        for dt, t, _, _ in data[dev]:
            if t and 0 < t < 60:
                hourly[dt.hour].append(t)
        hours = sorted(hourly)
        means = [sum(hourly[h]) / len(hourly[h]) for h in hours]
        ax.plot(hours, means, "-o", color=color, ms=3.5, label=label)
    ax.set_xlabel("Час суток")
    ax.set_ylabel("Средняя температура, °C")
    ax.set_xticks(range(0, 24, 2))
    ax.axvspan(8, 17, color=ORANGE, alpha=0.08)
    ax.legend()
    save(fig, "chart_diurnal_temp.pdf")


def chart_daily(data):
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    for dev, color in (("th-1", BLUE), ("th-2", RED), ("co2-1", GREEN)):
        daily = collections.defaultdict(list)
        for dt, t, _, _ in data[dev]:
            if t and 0 < t < 60:
                daily[dt.date()].append(t)
        days = sorted(daily)
        means = [sum(daily[d]) / len(daily[d]) for d in days]
        ax.plot(days, means, "-", color=color, lw=1.2, label=dev)
    ax.set_xlabel("Дата")
    ax.set_ylabel("Среднесуточная температура, °C")
    fig.autofmt_xdate(rotation=30)
    ax.legend()
    save(fig, "chart_daily_temp.pdf")


def chart_vpd(data):
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    for dev, color, label in (("th-1", BLUE, "th-1"), ("th-2", RED, "th-2")):
        vpd = []
        for dt, t, h, _ in data[dev]:
            if t and h and 0 < t < 60 and 0 < h <= 100:
                vpd.append(esat(t) * (1 - h / 100))
        ax.hist(vpd, bins=60, range=(0, 4), histtype="step", lw=1.6,
                color=color, label=f"{label} (среднее {sum(vpd)/len(vpd):.2f} кПа)")
    ax.axvspan(0.8, 1.2, color=GREEN, alpha=0.18, label="оптимум 0,8-1,2 кПа")
    ax.set_xlabel("Дефицит давления водяного пара VPD, кПа")
    ax.set_ylabel("Число измерений")
    ax.legend(fontsize=9)
    save(fig, "chart_vpd.pdf")


def chart_relay_hourly(relay):
    counts = collections.Counter(dt.hour for dt, _, _ in relay)
    hours = list(range(24))
    vals = [counts.get(h, 0) for h in hours]
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    colors = [ORANGE if 6 <= h < 22 else "#7f8c8d" for h in hours]
    ax.bar(hours, vals, color=colors)
    ax.set_xlabel("Час суток")
    ax.set_ylabel("Число переключений реле")
    ax.set_xticks(range(0, 24, 2))
    ax.axvspan(22, 24, color="#7f8c8d", alpha=0.12)
    ax.axvspan(0, 6, color="#7f8c8d", alpha=0.12)
    ax.text(2.8, max(vals) * 0.7, "ночь:\n0 событий", ha="center", fontsize=9,
            color="#555")
    save(fig, "chart_relay_hourly.pdf")


def chart_thermal_inertia(data):
    """Кривая ночного остывания th-1 и экспоненциальный фит (тепловая инерция).

    Ночью (22:00-06:00) реле не переключаются и нагрев не работает, поэтому
    остывание бокса описывается первым порядком T(t)=T_inf+(T0-T_inf)exp(-t/tau).
    По наклону логарифма идентифицируется постоянная времени tau, на порядки
    превышающая воздушную, что отражает эффективную теплоемкость массивных
    элементов (гидропонные баки, субстрат, конструкции).
    """
    series = {dt: t for dt, t, _, _ in data["th-1"] if t and 0 < t < 60}
    times = sorted(series)
    t0, t1 = datetime(2026, 4, 22, 21, 30), datetime(2026, 4, 23, 6, 0)
    seg = [dt for dt in times if t0 <= dt <= t1]
    xs = [(dt - seg[0]).total_seconds() / 3600 for dt in seg]  # часы
    ys = [series[dt] for dt in seg]
    t_end = ys[-1]
    best = None
    off = 0.2
    while off <= 3.01:
        t_inf = t_end - off
        lx, ly, ok = [], [], True
        for x, y in zip(xs, ys):
            v = y - t_inf
            if v <= 0:
                ok = False
                break
            lx.append(x)
            ly.append(math.log(v))
        off += 0.2
        if not ok or len(lx) < 30:
            continue
        n = len(lx)
        mx, my = sum(lx) / n, sum(ly) / n
        sxx = sum((x - mx) ** 2 for x in lx)
        sxy = sum((x - mx) * (y - my) for x, y in zip(lx, ly))
        slope = sxy / sxx
        if slope >= 0:
            continue
        b = my - slope * mx
        ssr = sum((y - (slope * x + b)) ** 2 for x, y in zip(lx, ly))
        sst = sum((y - my) ** 2 for y in ly)
        r2 = 1 - ssr / sst if sst > 0 else 0
        if best is None or r2 > best[-1]:
            best = (t_inf, slope, b, r2)
    t_inf, slope, b, r2 = best
    tau = -1 / slope  # часы
    fit = [t_inf + math.exp(b) * math.exp(slope * x) for x in xs]
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    ax.plot(xs, ys, color=BLUE, lw=1.5, label="th-1, ночь 22–23.04.2026")
    ax.plot(xs, fit, "--", color=RED, lw=1.8,
            label=f"экспонента, τ≈{tau:.1f} ч (R²={r2:.2f})")
    ax.set_xlabel("Время от начала ночного остывания, ч")
    ax.set_ylabel("Температура воздуха, °C")
    ax.legend(fontsize=9)
    save(fig, "chart_thermal_inertia.pdf")


# Подтвержденные значения эксперимента со светом (среднее по 6 сортам).
VAR = [1, 2, 3, 4, 5]
DLI = [5.12, 6.16, 9.77, 11.75, 15.91]
POWER = [116.3, 97.0, 221.0, 321.5, 478.0]
YIELD = [33.8, 89.9, 85.6, 105.6, 93.8]
YIELD_CI = [12.2, 12.2, 12.2, 12.2, 12.2]
GPERW = [0.29, 0.93, 0.39, 0.33, 0.20]
NITRATE = [6.96, 3.22, 1.86, 1.86, 1.79]
DRYMATTER = [5.24, 5.41, 7.24, 7.21, 7.90]


def chart_light_yield():
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    # 95% ДИ средней товарной массы по вариантам (двухфакторный ANOVA, MSE=1026,
    # n_h*b плодов за вариантом): половина интервала ≈ 12,2 г для всех вариантов.
    ax.errorbar(DLI, YIELD, yerr=YIELD_CI, fmt="-o", color=GREEN, capsize=4,
                ecolor=GREEN, elinewidth=1, label="Урожай товарного листа (95% ДИ)")
    ax.set_xlabel("Световая доза DLI, моль/(м²·сут)")
    ax.set_ylabel("Урожай, г/растение", color=GREEN)
    ax.tick_params(axis="y", labelcolor=GREEN)
    for x, y, v in zip(DLI, YIELD, VAR):
        ax.annotate(f"в{v}", (x, y), textcoords="offset points", xytext=(4, 6),
                    fontsize=9)
    ax2 = ax.twinx()
    ax2.bar(DLI, GPERW, width=0.5, color=BLUE, alpha=0.35)
    ax2.set_ylabel("Энергоэффективность, г/Вт", color=BLUE)
    ax2.tick_params(axis="y", labelcolor=BLUE)
    ax2.grid(False)
    save(fig, "chart_light_yield.pdf")


def chart_light_quality():
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    x = range(len(VAR))
    ax.bar([i - 0.2 for i in x], NITRATE, width=0.4, color=RED,
           label="Нитраты, отн. ед.")
    ax2 = ax.twinx()
    ax2.bar([i + 0.2 for i in x], DRYMATTER, width=0.4, color=GREEN,
            label="Сухое вещество, %")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"в{v}\nDLI {d:.1f}" for v, d in zip(VAR, DLI)])
    ax.set_ylabel("Нитраты, отн. ед.", color=RED)
    ax2.set_ylabel("Сухое вещество, %", color=GREEN)
    ax.tick_params(axis="y", labelcolor=RED)
    ax2.tick_params(axis="y", labelcolor=GREEN)
    ax2.grid(False)
    lines = [plt.Rectangle((0, 0), 1, 1, color=RED),
             plt.Rectangle((0, 0), 1, 1, color=GREEN)]
    ax.legend(lines, ["Нитраты, отн. ед.", "Сухое вещество, %"], fontsize=9,
              loc="upper center")
    save(fig, "chart_light_quality.pdf")


def chart_ml_metrics():
    # RMSE: persistence (last value) vs ridge на горизонте 30 мин.
    targets = ["Темп. th-1", "Влажн. th-1", "CO2 co2-1"]
    last = [0.331, 0.674, 14.103]
    ridge = [0.273, 0.633, 14.486]
    x = range(len(targets))
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    ax.bar([i - 0.2 for i in x], last, width=0.4, color="#7f8c8d",
           label="last value (persistence)")
    ax.bar([i + 0.2 for i in x], ridge, width=0.4, color=BLUE,
           label="ridge regression")
    ax.set_xticks(list(x))
    ax.set_xticklabels(targets)
    ax.set_ylabel("RMSE (горизонт 30 мин)")
    ax.set_yscale("log")
    ax.legend(fontsize=9)
    save(fig, "chart_ml_metrics.pdf")


def box(ax, x, y, w, h, title, body, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015",
                                fc=fc, ec="#2b2b2b", lw=1.3))
    cx = x + w / 2
    ax.text(cx, y + h - 0.30, title, ha="center", va="center",
            fontsize=10, fontweight="bold")
    ax.text(cx, y + (h - 0.55) / 2, body, ha="center", va="center",
            fontsize=8.6, linespacing=1.35)


def arrow(ax, p1, p2, label=None, lpos=0.5, ldx=0.0, ldy=0.0, rad=0.0, color="#2b2b2b"):
    style = f"arc3,rad={rad}" if rad else "arc3"
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14,
                                 color=color, lw=1.4, shrinkA=2, shrinkB=2,
                                 connectionstyle=style))
    if label:
        mx = p1[0] + (p2[0] - p1[0]) * lpos + ldx
        my = p1[1] + (p2[1] - p1[1]) * lpos + ldy
        ax.text(mx, my, label, ha="center", va="center", fontsize=7.8,
                color="#333", bbox=dict(boxstyle="round,pad=0.12", fc="white",
                                        ec="none", alpha=0.85))


def chart_architecture():
    fig, ax = plt.subplots(figsize=(6.9, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    EDGE_S, EDGE_A, BROK, SRV = "#d6eaf8", "#fdebd0", "#e8daef", "#d5f5e3"
    # верхний уровень: датчики и исполнительные устройства
    box(ax, 0.2, 7.55, 4.4, 1.95,
        "Сенсорный уровень",
        "ESP8266 + DHT11 (th-1, th-2),\nSCD30 (co2-1)", EDGE_S)
    box(ax, 5.4, 7.55, 4.4, 1.95,
        "Исполнительный уровень",
        "Arduino Mega 2560 + ESP8266,\n15 силовых реле", EDGE_A)
    # средний уровень: брокер
    box(ax, 2.95, 4.45, 4.1, 1.55,
        "MQTT-брокер (Mosquitto)",
        "единая шина обмена,\nretained-сообщения", BROK)
    # нижний уровень: сервер и хранилище
    box(ax, 0.2, 0.9, 4.4, 2.05,
        "Серверный уровень",
        "Flask-dashboard,\nправила и профили", SRV)
    box(ax, 5.4, 0.9, 4.4, 2.05,
        "Хранение и анализ",
        "SQLite-журнал,\nML и экспорт данных", SRV)

    # потоки данных
    arrow(ax, (2.4, 7.55), (3.9, 6.0), "телеметрия", lpos=0.5, ldx=-0.55)
    arrow(ax, (6.1, 6.0), (6.9, 7.55), "команды", lpos=0.45, ldx=-0.5, rad=0.18)
    arrow(ax, (7.7, 7.55), (6.9, 6.0), "состояния", lpos=0.55, ldx=0.7, rad=0.18)
    arrow(ax, (3.9, 4.45), (2.4, 2.95), "подписка", lpos=0.5, ldx=-0.55)
    arrow(ax, (6.1, 4.45), (7.6, 2.95), "журнал", lpos=0.5, ldx=0.5)
    arrow(ax, (4.6, 1.92), (5.4, 1.92), rad=0.0)
    arrow(ax, (5.4, 1.55), (4.6, 1.55), rad=0.0)
    ax.text(5.0, 2.35, "обмен\nданными", ha="center", va="center", fontsize=7.6,
            color="#333")
    save(fig, "chart_architecture.pdf")


def main():
    data = load_sensor()
    relay = load_relay()
    chart_diurnal(data)
    chart_daily(data)
    chart_vpd(data)
    chart_relay_hourly(relay)
    chart_thermal_inertia(data)
    chart_light_yield()
    chart_light_quality()
    chart_ml_metrics()
    chart_architecture()


if __name__ == "__main__":
    main()
