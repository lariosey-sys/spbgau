# -*- coding: utf-8 -*-
"""Разбор микроклимата по датчикам (history_2026-05-26.db) для отчёта по салату.

Датчики: th-1, th-2 (температура/влажность), co2-1 (CO2 + темп/влаж).
Лог: 2026-03-28 .. 2026-05-26 — покрывает вторую половину цикла салата и хранение.
Выходы: climate_daily.csv, climate_hourly.csv, climate_summary.json
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "thesis" / "evidence" / "greenhouse_pi_data" / "history_2026-05-26.db"
OUT = Path(__file__).resolve().parent

# агрономические ориентиры для салата
T_OPT = (16, 22)        # оптимум воздуха, °C
T_STRESS = 24           # выше — риск стрелкования/горечи
T_HEAT = 28             # выраженный тепловой стресс
RH_OPT = (50, 70)       # оптимум влажности, %
VPD_OPT = (0.8, 1.2)    # оптимум VPD, кПа
VPD_STRESS = 1.6        # выше — повышенная транспирация/риск краевого ожога

# фазы опыта (то, что попало в лог)
WIN = {
    "growth": ("2026-03-28", "2026-04-16", "Финал вегетации (захвачено датчиками)"),
    "storage": ("2026-04-17", "2026-04-27", "Период хранения (17–27.04)"),
}


def vpd(T, RH):
    es = 0.6108 * np.exp(17.27 * T / (T + 237.3))
    return es * (1 - RH / 100.0)


def load():
    import sqlite3
    c = sqlite3.connect(DB)
    df = pd.read_sql("select ts,device,temperature,humidity,co2 from sensor_log",
                     c, parse_dates=["ts"])
    c.close()
    df.loc[df.temperature <= 0, "temperature"] = np.nan
    df.loc[(df.humidity <= 0) | (df.humidity > 100), "humidity"] = np.nan
    df.loc[(df.co2 <= 0) | (df.co2 > 5000), "co2"] = np.nan
    return df


def window_stats(th):
    out = {}
    for key, (a, b, label) in WIN.items():
        w = th[(th.ts >= a) & (th.ts <= b)]
        if not len(w):
            continue
        out[key] = {
            "label": label, "from": a, "to": b, "n": int(len(w)),
            "t_med": float(w.temperature.median()),
            "t_min": float(w.temperature.min()),
            "t_max": float(w.temperature.max()),
            "share_t_gt24": float((w.temperature > T_STRESS).mean()),
            "share_t_gt28": float((w.temperature > T_HEAT).mean()),
            "rh_med": float(w.humidity.median()),
            "share_rh_lt40": float((w.humidity < 40).mean()),
            "vpd_med": float(w.vpd.median()),
            "vpd_max": float(w.vpd.max()),
            "share_vpd_gt16": float((w.vpd > VPD_STRESS).mean()),
        }
    return out


def main():
    df = load()
    th = df[df.device.isin(["th-1", "th-2"])].copy()
    th["vpd"] = vpd(th.temperature, th.humidity)

    # суточные ряды (по всем th-датчикам)
    daily = (th.set_index("ts")
             .resample("1D")
             .agg(t_min=("temperature", "min"), t_mean=("temperature", "mean"),
                  t_max=("temperature", "max"), rh_mean=("humidity", "mean"),
                  vpd_mean=("vpd", "mean"))
             .dropna(how="all").reset_index())
    daily["date"] = daily.ts.dt.strftime("%Y-%m-%d")
    daily.drop(columns="ts").to_csv(OUT / "climate_daily.csv", index=False)

    # суточный ход
    h = th.set_index("ts")
    hourly = pd.DataFrame({
        "hour": range(24),
        "t_mean": h.groupby(h.index.hour)["temperature"].mean().reindex(range(24)).values,
        "rh_mean": h.groupby(h.index.hour)["humidity"].mean().reindex(range(24)).values,
        "vpd_mean": h.groupby(h.index.hour)["vpd"].mean().reindex(range(24)).values,
    })
    co2 = df[df.device == "co2-1"].dropna(subset=["co2"]).set_index("ts")
    hourly["co2_med"] = co2.groupby(co2.index.hour)["co2"].median().reindex(range(24)).values
    hourly.to_csv(OUT / "climate_hourly.csv", index=False)

    # сводка
    summary = {
        "ts_from": str(df.ts.min()), "ts_to": str(df.ts.max()),
        "n_total": int(len(df)),
        "devices": sorted(df.device.unique().tolist()),
        "overall": {
            "t_med": float(th.temperature.median()),
            "t_max": float(th.temperature.max()),
            "share_t_gt24": float((th.temperature > T_STRESS).mean()),
            "share_t_gt28": float((th.temperature > T_HEAT).mean()),
            "rh_med": float(th.humidity.median()),
            "share_rh_lt40": float((th.humidity < 40).mean()),
            "vpd_med": float(th.vpd.median()),
            "vpd_max": float(th.vpd.max()),
            "share_vpd_gt16": float((th.vpd > VPD_STRESS).mean()),
            "diurnal_amp": float(hourly.t_mean.max() - hourly.t_mean.min()),
        },
        "gradient": {
            d: {"t_med": float(th[th.device == d].temperature.median()),
                "rh_med": float(th[th.device == d].humidity.median()),
                "vpd_med": float(th[th.device == d].vpd.median())}
            for d in ["th-1", "th-2"]
        },
        "co2": {
            "n_valid": int(co2.shape[0]),
            "med": float(co2.co2.median()),
            "min": float(co2.co2.min()),
            "max": float(co2.co2.max()),
            "share_valid": float(df[df.device == "co2-1"].co2.notna().mean()),
        },
        "windows": window_stats(th),
        "refs": {"T_OPT": T_OPT, "T_STRESS": T_STRESS, "T_HEAT": T_HEAT,
                 "RH_OPT": RH_OPT, "VPD_OPT": VPD_OPT, "VPD_STRESS": VPD_STRESS},
    }
    (OUT / "climate_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("daily:", daily.shape, "hourly:", hourly.shape)
    print(json.dumps(summary["overall"], ensure_ascii=False, indent=1))
    print("gradient:", summary["gradient"])
    print("co2:", summary["co2"])


if __name__ == "__main__":
    main()
