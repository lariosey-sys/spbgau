#!/usr/bin/env python3
"""Reproducible ML baseline for greenhouse microclimate history.

The script intentionally uses only the Python standard library. It builds a
minute-scale dataset from SQLite, compares persistence and rolling-average
baselines with a small ridge regression model, and writes CSV/SVG artifacts.
"""

from __future__ import annotations

import csv
import math
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "thesis" / "evidence" / "greenhouse_pi_data" / "history_2026-05-26.db"
OUT = ROOT / "analysis"
TABLES = OUT / "tables"
FIGS = OUT / "figures"

MINUTE = timedelta(minutes=1)
MAX_FORWARD_FILL_MIN = 10
HORIZONS = [10, 30]
TARGETS = [
    ("th-1_temperature", "temperature"),
    ("th-1_humidity", "humidity"),
    ("co2-1_co2", "co2"),
]
BASE_VALUE_COLUMNS = [
    "th-1_temperature",
    "th-1_humidity",
    "th-2_temperature",
    "th-2_humidity",
    "co2-1_temperature",
    "co2-1_humidity",
    "co2-1_co2",
]
LAGS = [5, 10, 30, 60]
ROLLING_WINDOWS = [10, 30, 60]
RELAY_COLUMNS = [f"relay_{i}" for i in range(1, 16)]


@dataclass
class ModelResult:
    target: str
    horizon_min: int
    model: str
    n_train: int
    n_test: int
    mae: float
    rmse: float
    r2: float


def parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def minute_floor(ts: datetime) -> datetime:
    return ts.replace(second=0, microsecond=0)


def clean_value(metric: str, value: float | None) -> float | None:
    if value is None:
        return None
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        return None
    if value == 0 and metric in {"temperature", "humidity", "co2"}:
        return None
    if metric == "temperature" and not (-40 <= value <= 80):
        return None
    if metric == "humidity" and not (0 < value <= 100):
        return None
    if metric == "co2" and not (250 <= value <= 5000):
        return None
    return value


def fmt_dt(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def ensure_dirs() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)


def load_minute_values() -> tuple[list[datetime], dict[str, list[float | None]], dict[str, list[int]]]:
    con = sqlite3.connect(DB)
    sensor_rows = con.execute(
        "select ts, device, temperature, humidity, co2 from sensor_log order by ts, id"
    ).fetchall()
    relay_rows = con.execute(
        "select ts, relay_id, state from relay_log order by ts, id"
    ).fetchall()
    con.close()

    first_ts = min(parse_ts(row[0]) for row in sensor_rows)
    last_ts = max(parse_ts(row[0]) for row in sensor_rows)
    start = minute_floor(first_ts)
    end = minute_floor(last_ts)
    minutes: list[datetime] = []
    current = start
    while current <= end:
        minutes.append(current)
        current += MINUTE

    minute_index = {ts: i for i, ts in enumerate(minutes)}
    raw_values: dict[str, dict[datetime, list[float]]] = defaultdict(lambda: defaultdict(list))
    for ts_raw, device, temperature, humidity, co2 in sensor_rows:
        ts = minute_floor(parse_ts(ts_raw))
        for metric, value in [
            ("temperature", temperature),
            ("humidity", humidity),
            ("co2", co2),
        ]:
            value = clean_value(metric, value)
            if value is None:
                continue
            raw_values[f"{device}_{metric}"][ts].append(value)

    values: dict[str, list[float | None]] = {column: [None] * len(minutes) for column in BASE_VALUE_COLUMNS}
    for column in BASE_VALUE_COLUMNS:
        last_value: float | None = None
        last_seen: datetime | None = None
        by_minute = raw_values.get(column, {})
        for i, ts in enumerate(minutes):
            if ts in by_minute:
                xs = by_minute[ts]
                last_value = sum(xs) / len(xs)
                last_seen = ts
            if last_value is not None and last_seen is not None:
                if (ts - last_seen).total_seconds() <= MAX_FORWARD_FILL_MIN * 60:
                    values[column][i] = last_value

    relays: dict[str, list[int]] = {column: [0] * len(minutes) for column in RELAY_COLUMNS}
    states = {i: 0 for i in range(1, 16)}
    events_by_minute: dict[datetime, list[tuple[int, int]]] = defaultdict(list)
    for ts_raw, relay_id, state in relay_rows:
        state_value = 1 if str(state).upper() in {"ON", "1", "TRUE"} else 0
        events_by_minute[minute_floor(parse_ts(ts_raw))].append((int(relay_id), state_value))

    for ts in minutes:
        for relay_id, state_value in events_by_minute.get(ts, []):
            states[relay_id] = state_value
        idx = minute_index[ts]
        for relay_id in range(1, 16):
            relays[f"relay_{relay_id}"][idx] = states[relay_id]

    return minutes, values, relays


def rolling_mean(xs: list[float | None], idx: int, window: int) -> float | None:
    start = idx - window + 1
    if start < 0:
        return None
    vals = xs[start : idx + 1]
    if any(v is None for v in vals):
        return None
    return sum(v for v in vals if v is not None) / window


def build_dataset(
    minutes: list[datetime],
    values: dict[str, list[float | None]],
    relays: dict[str, list[int]],
    target_col: str,
    horizon: int,
) -> tuple[list[datetime], list[list[float]], list[float], list[str], list[float], list[float]]:
    feature_names: list[str] = []
    for column in BASE_VALUE_COLUMNS:
        feature_names.append(column)
        for lag in LAGS:
            feature_names.append(f"{column}_lag_{lag}m")
        for window in ROLLING_WINDOWS:
            feature_names.append(f"{column}_mean_{window}m")
    feature_names.extend(["hour_sin", "hour_cos", "day_sin", "day_cos"])
    feature_names.extend(RELAY_COLUMNS)

    rows_ts: list[datetime] = []
    x_rows: list[list[float]] = []
    y_values: list[float] = []
    naive_values: list[float] = []
    moving_values: list[float] = []

    min_idx = max(max(LAGS), max(ROLLING_WINDOWS)) - 1
    max_idx = len(minutes) - horizon
    for idx in range(min_idx, max_idx):
        current_target = values[target_col][idx]
        future_target = values[target_col][idx + horizon]
        moving = rolling_mean(values[target_col], idx, 30)
        if current_target is None or future_target is None or moving is None:
            continue

        features: list[float] = []
        ok = True
        for column in BASE_VALUE_COLUMNS:
            value = values[column][idx]
            if value is None:
                ok = False
                break
            features.append(value)
            for lag in LAGS:
                lag_value = values[column][idx - lag]
                if lag_value is None:
                    ok = False
                    break
                features.append(lag_value)
            if not ok:
                break
            for window in ROLLING_WINDOWS:
                mean_value = rolling_mean(values[column], idx, window)
                if mean_value is None:
                    ok = False
                    break
                features.append(mean_value)
            if not ok:
                break
        if not ok:
            continue

        minute_of_day = minutes[idx].hour * 60 + minutes[idx].minute
        features.append(math.sin(2 * math.pi * minute_of_day / 1440))
        features.append(math.cos(2 * math.pi * minute_of_day / 1440))
        features.append(math.sin(2 * math.pi * minutes[idx].weekday() / 7))
        features.append(math.cos(2 * math.pi * minutes[idx].weekday() / 7))
        features.extend(float(relays[column][idx]) for column in RELAY_COLUMNS)

        rows_ts.append(minutes[idx])
        x_rows.append(features)
        y_values.append(future_target)
        naive_values.append(current_target)
        moving_values.append(moving)

    return rows_ts, x_rows, y_values, feature_names, naive_values, moving_values


def metric_values(y_true: list[float], y_pred: list[float]) -> tuple[float, float, float]:
    n = len(y_true)
    mae = sum(abs(a - b) for a, b in zip(y_true, y_pred)) / n
    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(y_true, y_pred)) / n)
    mean_y = sum(y_true) / n
    ss_res = sum((a - b) ** 2 for a, b in zip(y_true, y_pred))
    ss_tot = sum((a - mean_y) ** 2 for a in y_true)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return mae, rmse, r2


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    matrix = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(matrix[r][col]))
        if abs(matrix[pivot][col]) < 1e-12:
            continue
        if pivot != col:
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        scale = matrix[col][col]
        matrix[col] = [v / scale for v in matrix[col]]
        for row_idx in range(n):
            if row_idx == col:
                continue
            factor = matrix[row_idx][col]
            if factor == 0:
                continue
            matrix[row_idx] = [
                current - factor * pivot_value
                for current, pivot_value in zip(matrix[row_idx], matrix[col])
            ]
    return [matrix[i][-1] for i in range(n)]


def ridge_fit_predict(
    x_train: list[list[float]],
    y_train: list[float],
    x_test: list[list[float]],
    alpha: float = 10.0,
) -> list[float]:
    n_features = len(x_train[0])
    means = [0.0] * n_features
    stds = [0.0] * n_features
    for j in range(n_features):
        col = [row[j] for row in x_train]
        means[j] = sum(col) / len(col)
        var = sum((v - means[j]) ** 2 for v in col) / len(col)
        stds[j] = math.sqrt(var) or 1.0

    def transform(rows: list[list[float]]) -> list[list[float]]:
        return [[1.0] + [(row[j] - means[j]) / stds[j] for j in range(n_features)] for row in rows]

    xt = transform(x_train)
    xtest = transform(x_test)
    p = n_features + 1
    gram = [[0.0] * p for _ in range(p)]
    rhs = [0.0] * p
    for row, target in zip(xt, y_train):
        for i in range(p):
            rhs[i] += row[i] * target
            for j in range(p):
                gram[i][j] += row[i] * row[j]
    for i in range(1, p):
        gram[i][i] += alpha
    coeffs = solve_linear_system(gram, rhs)
    return [sum(c * v for c, v in zip(coeffs, row)) for row in xtest]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_prediction_svg(path: Path, rows: list[dict], title: str, y_label: str) -> None:
    if not rows:
        return
    width, height = 900, 360
    margin_left, margin_right, margin_top, margin_bottom = 70, 25, 35, 45
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    y_values = [float(row["actual"]) for row in rows] + [float(row["ridge"]) for row in rows]
    y_min, y_max = min(y_values), max(y_values)
    if y_min == y_max:
        y_min -= 1
        y_max += 1

    def x_pos(i: int) -> float:
        return margin_left + i * plot_w / max(1, len(rows) - 1)

    def y_pos(v: float) -> float:
        return margin_top + (y_max - v) * plot_h / (y_max - y_min)

    def polyline(key: str, color: str) -> str:
        points = " ".join(f"{x_pos(i):.1f},{y_pos(float(row[key])):.1f}" for i, row in enumerate(rows))
        return f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}" />'

    y_ticks = []
    for k in range(5):
        value = y_min + (y_max - y_min) * k / 4
        y = y_pos(value)
        y_ticks.append(
            f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width-margin_right}" y2="{y:.1f}" stroke="#e0e0e0" />'
            f'<text x="{margin_left-8}" y="{y+4:.1f}" text-anchor="end" font-size="11">{value:.1f}</text>'
        )

    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="white" />',
            f'<text x="{margin_left}" y="22" font-size="16" font-family="Arial">{title}</text>',
            *y_ticks,
            f'<line x1="{margin_left}" y1="{height-margin_bottom}" x2="{width-margin_right}" y2="{height-margin_bottom}" stroke="#333" />',
            f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height-margin_bottom}" stroke="#333" />',
            f'<text x="18" y="{height/2}" transform="rotate(-90 18,{height/2})" font-size="12" font-family="Arial">{y_label}</text>',
            polyline("actual", "#1b4f72"),
            polyline("ridge", "#d35400"),
            f'<text x="{width-230}" y="24" font-size="12" fill="#1b4f72">факт</text>',
            f'<text x="{width-170}" y="24" font-size="12" fill="#d35400">ridge</text>',
            "</svg>",
        ]
    )
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    minutes, values, relays = load_minute_values()
    metrics_rows: list[dict] = []
    prediction_rows_all: list[dict] = []
    best_plot_rows: list[dict] = []

    for target_col, target_kind in TARGETS:
        for horizon in HORIZONS:
            ts_rows, x_rows, y_values, feature_names, naive_values, moving_values = build_dataset(
                minutes, values, relays, target_col, horizon
            )
            if len(y_values) < 1000:
                continue
            split = int(len(y_values) * 0.7)
            x_train, x_test = x_rows[:split], x_rows[split:]
            y_train, y_test = y_values[:split], y_values[split:]
            ts_test = ts_rows[split:]
            naive_test = naive_values[split:]
            moving_test = moving_values[split:]
            ridge_test = ridge_fit_predict(x_train, y_train, x_test)

            for model_name, preds in [
                ("last_value", naive_test),
                ("moving_mean_30m", moving_test),
                ("ridge_regression", ridge_test),
            ]:
                mae, rmse, r2 = metric_values(y_test, preds)
                metrics_rows.append(
                    {
                        "target": target_col,
                        "target_kind": target_kind,
                        "horizon_min": horizon,
                        "model": model_name,
                        "n_train": split,
                        "n_test": len(y_test),
                        "mae": f"{mae:.6f}",
                        "rmse": f"{rmse:.6f}",
                        "r2": f"{r2:.6f}",
                    }
                )

            sample_step = max(1, len(y_test) // 500)
            for ts, actual, naive, moving, ridge in zip(ts_test[::sample_step], y_test[::sample_step], naive_test[::sample_step], moving_test[::sample_step], ridge_test[::sample_step]):
                prediction_rows_all.append(
                    {
                        "target": target_col,
                        "horizon_min": horizon,
                        "ts": fmt_dt(ts),
                        "actual": f"{actual:.6f}",
                        "last_value": f"{naive:.6f}",
                        "moving_mean_30m": f"{moving:.6f}",
                        "ridge_regression": f"{ridge:.6f}",
                    }
                )

            if target_col == "th-1_temperature" and horizon == 30:
                best_plot_rows = [
                    {
                        "ts": fmt_dt(ts),
                        "actual": actual,
                        "ridge": ridge,
                    }
                    for ts, actual, ridge in zip(ts_test[-240:], y_test[-240:], ridge_test[-240:])
                ]

    write_csv(
        TABLES / "ml_baseline_metrics.csv",
        metrics_rows,
        ["target", "target_kind", "horizon_min", "model", "n_train", "n_test", "mae", "rmse", "r2"],
    )
    write_csv(
        TABLES / "ml_baseline_predictions_sample.csv",
        prediction_rows_all,
        ["target", "horizon_min", "ts", "actual", "last_value", "moving_mean_30m", "ridge_regression"],
    )
    write_prediction_svg(
        FIGS / "ml_temperature_30m_prediction.svg",
        best_plot_rows,
        "Прогноз температуры th-1 на 30 минут",
        "Температура, °C",
    )
    print(f"Wrote {TABLES / 'ml_baseline_metrics.csv'}")
    print(f"Wrote {TABLES / 'ml_baseline_predictions_sample.csv'}")
    print(f"Wrote {FIGS / 'ml_temperature_30m_prediction.svg'}")


if __name__ == "__main__":
    main()
