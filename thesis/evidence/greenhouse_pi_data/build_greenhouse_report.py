#!/usr/bin/env python3
import json
import math
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "history_2026-05-26.db"
OUT_PATH = ROOT / "greenhouse_data_report_2026-05-26_extended_msk.pdf"
NAMES_PATH = ROOT / "names_2026-05-26.json"
PROFILES_PATH = ROOT / "profiles_2026-05-26.json"

MSK_LABEL = "МСК (UTC+3)"

PALETTE = {
    "co2-1": colors.HexColor("#0057d9"),
    "th-1": colors.HexColor("#c0392b"),
    "th-2": colors.HexColor("#2ca02c"),
    "relay": colors.HexColor("#5b5fc7"),
    "quality": colors.HexColor("#8e44ad"),
}


def register_font():
    for path in [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/Library/Fonts/Arial.ttf",
    ]:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont("ReportFont", path))
            return "ReportFont"
    return "Helvetica"


FONT = register_font()


def db_rows(sql, params=()):
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        return con.execute(sql, params).fetchall()


def db_one(sql, params=()):
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        return con.execute(sql, params).fetchone()


def dt(value):
    return datetime.fromisoformat(value)


def fmt(value, digits=1):
    if value is None:
        return "нет"
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.{digits}f}"


def fmt_dt(value):
    if value is None:
        return "нет"
    return str(value)


def load_json(path, fallback):
    if not path.exists():
        return fallback
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def relay_labels():
    names = load_json(NAMES_PATH, {"relays": {}}).get("relays", {})
    profiles = load_json(PROFILES_PATH, [])
    labels = {int(k): v for k, v in names.items()}
    usage = defaultdict(list)
    for profile in profiles:
        profile_name = profile.get("name", "профиль")
        for step in profile.get("pre", []):
            usage[int(step["relay"])].append(f"{profile_name}: подготовка")
        for step in profile.get("main", []):
            usage[int(step["relay"])].append(f"{profile_name}: основной канал")
    result = {}
    for relay_id in range(1, 16):
        parts = []
        if relay_id in labels:
            parts.append(labels[relay_id])
        if usage.get(relay_id):
            parts.extend(usage[relay_id][:2])
        result[relay_id] = "; ".join(parts) if parts else f"реле {relay_id}"
    return result, profiles


def styles():
    st = getSampleStyleSheet()
    for item in st.byName.values():
        item.fontName = FONT
    st.add(ParagraphStyle(name="Small", parent=st["BodyText"], fontName=FONT, fontSize=7.6, leading=9.2))
    st.add(
        ParagraphStyle(
            name="Note",
            parent=st["BodyText"],
            fontName=FONT,
            fontSize=8.8,
            leading=11.2,
            backColor=colors.HexColor("#f2f5f8"),
            borderPadding=6,
            textColor=colors.HexColor("#2f3944"),
        )
    )
    return st


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(colors.HexColor("#697386"))
    canvas.drawString(18 * mm, 10 * mm, f"Время на графиках: {MSK_LABEL}")
    canvas.drawRightString(192 * mm, 10 * mm, f"стр. {doc.page}")
    canvas.restoreState()


def p(text, style):
    return Paragraph(text, style)


def table(rows, widths=None, font_size=7.6):
    obj = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
    obj.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), FONT, font_size),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8edf3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2933")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c7d0d9")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfcfd")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    return obj


def line_chart(title, series, y_label="", width=172 * mm, height=62 * mm):
    drawing = Drawing(width, height)
    drawing.add(String(0, height - 10, title, fontName=FONT, fontSize=9.5, fillColor=colors.HexColor("#1f2933")))
    plot_x = 30
    plot_y = 22
    plot_w = width - 50
    plot_h = height - 44
    labels = []
    all_y = []
    visible_series = []
    for name, points, color in series:
        valid = []
        for idx, (label, value) in enumerate(points):
            if len(labels) < len(points):
                labels.append(label)
            if value is None:
                continue
            valid.append((idx, label, float(value)))
            all_y.append(float(value))
        if len(valid) >= 2:
            visible_series.append((name, valid, color))
    if not visible_series:
        drawing.add(String(34, height / 2, "Нет двух и более валидных точек для линии", fontName=FONT, fontSize=8, fillColor=colors.HexColor("#697386")))
        return drawing
    ymin, ymax = min(all_y), max(all_y)
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    pad = (ymax - ymin) * 0.08
    ymin -= pad
    ymax += pad

    def sx(idx):
        return plot_x + (idx / max(1, len(labels) - 1)) * plot_w

    def sy(value):
        return plot_y + ((value - ymin) / (ymax - ymin)) * plot_h

    drawing.add(Line(plot_x, plot_y, plot_x + plot_w, plot_y, strokeColor=colors.HexColor("#9aa6b2"), strokeWidth=0.6))
    drawing.add(Line(plot_x, plot_y, plot_x, plot_y + plot_h, strokeColor=colors.HexColor("#9aa6b2"), strokeWidth=0.6))

    for i in range(5):
        value = ymin + (ymax - ymin) * i / 4
        y = sy(value)
        drawing.add(Line(plot_x - 3, y, plot_x + plot_w, y, strokeColor=colors.HexColor("#e5e9ef"), strokeWidth=0.35))
        drawing.add(String(0, y - 3, fmt(value, 1), fontName=FONT, fontSize=6.5, fillColor=colors.HexColor("#697386")))

    if labels:
        step = max(1, math.ceil(len(labels) / 6))
        for idx in range(0, len(labels), step):
            label = labels[idx]
            label = label[5:] if "-" in label else label
            x_tick = sx(idx)
            drawing.add(Line(x_tick, plot_y, x_tick, plot_y - 3, strokeColor=colors.HexColor("#9aa6b2"), strokeWidth=0.5))
            drawing.add(String(x_tick - 8, plot_y - 12, label, fontName=FONT, fontSize=6.5, fillColor=colors.HexColor("#697386")))

    # Draw co2-1 last and with markers so it cannot disappear behind another sensor line.
    visible_series.sort(key=lambda item: 1 if item[0] == "co2-1" else 0)
    for name, valid, color in visible_series:
        stroke_width = 2.8 if name == "co2-1" else 1.7
        point_radius = 1.7 if name == "co2-1" else 1.1
        for left, right in zip(valid, valid[1:]):
            drawing.add(Line(sx(left[0]), sy(left[2]), sx(right[0]), sy(right[2]), strokeColor=color, strokeWidth=stroke_width))
        for idx, _label, value in valid:
            drawing.add(Circle(sx(idx), sy(value), point_radius, fillColor=color, strokeColor=color))

    if y_label:
        drawing.add(String(0, 18, y_label, fontName=FONT, fontSize=7, fillColor=colors.HexColor("#697386")))
    x = 34
    y = height - 24
    for name, _points, color in visible_series:
        drawing.add(Rect(x, y - 5, 7, 7, fillColor=color, strokeColor=color))
        drawing.add(String(x + 10, y - 4, name, fontName=FONT, fontSize=7.2, fillColor=colors.HexColor("#333333")))
        x += 42
    return drawing


def bar_chart(title, labels, values, width=172 * mm, height=56 * mm, color=PALETTE["relay"]):
    drawing = Drawing(width, height)
    drawing.add(String(0, height - 10, title, fontName=FONT, fontSize=9.5, fillColor=colors.HexColor("#1f2933")))
    chart = VerticalBarChart()
    chart.x = 26
    chart.y = 21
    chart.width = width - 44
    chart.height = height - 42
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = FONT
    chart.categoryAxis.labels.fontSize = 6.6
    chart.valueAxis.labels.fontName = FONT
    chart.valueAxis.labels.fontSize = 6.6
    chart.bars[0].fillColor = color
    chart.barWidth = max(4, min(14, chart.width / max(1, len(labels)) * 0.46))
    drawing.add(chart)
    return drawing


def period_ranges():
    row = db_one("select min(ts) as min_ts, max(ts) as max_ts from sensor_log")
    end = dt(row["max_ts"])
    start_all = dt(row["min_ts"])
    return [
        {"key": "14d", "title": "Последние 14 дней", "start": end - timedelta(days=14), "end": end},
        {"key": "30d", "title": "Последние 30 дней", "start": end - timedelta(days=30), "end": end},
        {"key": "all", "title": "Весь период", "start": start_all, "end": end},
    ]


def period_stats(start, end):
    return db_one(
        """
        select count(*) as rows,
               count(distinct date(ts)) as days,
               min(ts) as first_ts,
               max(ts) as last_ts,
               avg(case when temperature > 0 then temperature end) as avg_t,
               min(case when temperature > 0 then temperature end) as min_t,
               max(case when temperature > 0 then temperature end) as max_t,
               avg(case when humidity > 0 and humidity < 100 then humidity end) as avg_h,
               min(case when humidity > 0 and humidity < 100 then humidity end) as min_h,
               max(case when humidity > 0 and humidity < 100 then humidity end) as max_h,
               avg(case when co2 >= 250 and co2 <= 3000 then co2 end) as avg_co2,
               min(case when co2 >= 250 and co2 <= 3000 then co2 end) as min_co2,
               max(case when co2 >= 250 and co2 <= 3000 then co2 end) as max_co2,
               sum(case when temperature is null or temperature <= 0 then 1 else 0 end) as bad_t,
               sum(case when humidity is null or humidity <= 0 or humidity >= 100 then 1 else 0 end) as bad_h,
               sum(case when co2 is not null and co2 < 250 then 1 else 0 end) as bad_co2
        from sensor_log
        where ts between ? and ?
        """,
        (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
    )


def device_stats(start, end):
    return db_rows(
        """
        select device, count(*) as rows,
               avg(case when temperature > 0 then temperature end) as avg_t,
               min(case when temperature > 0 then temperature end) as min_t,
               max(case when temperature > 0 then temperature end) as max_t,
               avg(case when humidity > 0 and humidity < 100 then humidity end) as avg_h,
               min(case when humidity > 0 and humidity < 100 then humidity end) as min_h,
               max(case when humidity > 0 and humidity < 100 then humidity end) as max_h,
               avg(case when co2 >= 250 and co2 <= 3000 then co2 end) as avg_co2,
               min(case when co2 >= 250 and co2 <= 3000 then co2 end) as min_co2,
               max(case when co2 >= 250 and co2 <= 3000 then co2 end) as max_co2
        from sensor_log
        where ts between ? and ?
        group by device
        order by device
        """,
        (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
    )


def daily_points(start, end, metric, devices=None):
    rows = db_rows(
        f"""
        select date(ts) as day, device,
               avg(case
                   when ? = 'avg_t' and temperature > 0 then temperature
                   when ? = 'avg_h' and humidity > 0 and humidity < 100 then humidity
                   when ? = 'avg_co2' and co2 >= 250 and co2 <= 3000 then co2
               end) as value
        from sensor_log
        where ts between ? and ?
        group by day, device
        order by day, device
        """,
        (metric, metric, metric, start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
    )
    days = sorted({r["day"] for r in rows})
    values = defaultdict(dict)
    for row in rows:
        values[row["device"]][row["day"]] = row["value"]
    series = []
    for device in (devices or ["th-1", "th-2", "co2-1"]):
        if device in values:
            series.append((device, [(day, values[device].get(day)) for day in days], PALETTE[device]))
    return series


def hourly_profile(start, end, metric, devices=None):
    rows = db_rows(
        """
        select cast(strftime('%H', ts) as integer) as hour, device,
               avg(case
                   when ? = 'avg_t' and temperature > 0 then temperature
                   when ? = 'avg_h' and humidity > 0 and humidity < 100 then humidity
                   when ? = 'avg_co2' and co2 >= 250 and co2 <= 3000 then co2
               end) as value
        from sensor_log
        where ts between ? and ?
        group by hour, device
        order by hour, device
        """,
        (metric, metric, metric, start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
    )
    values = defaultdict(dict)
    for row in rows:
        values[row["device"]][row["hour"]] = row["value"]
    series = []
    for device in (devices or ["th-1", "th-2", "co2-1"]):
        if device in values:
            series.append((device, [(f"{hour:02d}", values[device].get(hour)) for hour in range(24)], PALETTE[device]))
    return series


def relay_events(start, end):
    return db_rows(
        """
        select relay_id,
               count(*) as events,
               sum(state = 'ON') as on_events,
               sum(state = 'OFF') as off_events,
               min(ts) as first_ts,
               max(ts) as last_ts
        from relay_log
        where ts between ? and ?
        group by relay_id
        order by events desc, relay_id
        """,
        (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
    )


def relay_state_at(cur, relay_id, start):
    row = cur.execute(
        "select state from relay_log where relay_id = ? and ts < ? order by ts desc limit 1",
        (relay_id, start.strftime("%Y-%m-%d %H:%M:%S")),
    ).fetchone()
    return row[0] if row else "OFF"


def relay_on_durations(start, end):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        relay_ids = [row[0] for row in cur.execute("select distinct relay_id from relay_log order by relay_id")]
        result = []
        for relay_id in relay_ids:
            state = relay_state_at(cur, relay_id, start)
            last_ts = start
            on_seconds = 0.0
            events = cur.execute(
                "select ts, state from relay_log where relay_id = ? and ts between ? and ? order by ts",
                (relay_id, start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
            ).fetchall()
            for ts_text, new_state in events:
                ts = dt(ts_text)
                if state == "ON":
                    on_seconds += (ts - last_ts).total_seconds()
                state = new_state
                last_ts = ts
            if state == "ON":
                on_seconds += (end - last_ts).total_seconds()
            result.append({"relay_id": relay_id, "on_hours": max(0, on_seconds / 3600), "final_state": state, "events": len(events)})
    return sorted(result, key=lambda x: (-x["on_hours"], x["relay_id"]))


def avg_window(cur, ts_text, device, column, start_min, end_min):
    row = cur.execute(
        f"""
        select avg({column}) from sensor_log
        where device = ?
          and ts >= datetime(?, ?)
          and ts < datetime(?, ?)
          and {column} is not null
          and {column} > 0
        """,
        (device, ts_text, f"{start_min} minutes", ts_text, f"{end_min} minutes"),
    ).fetchone()
    return row[0] if row else None


def relay_impact(start, end):
    active = [row["relay_id"] for row in relay_events(start, end)[:6]]
    if not active:
        return []
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        buckets = defaultdict(list)
        q_marks = ",".join("?" for _ in active)
        params = active + [start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")]
        rows = cur.execute(
            f"select ts, relay_id, state from relay_log where relay_id in ({q_marks}) and ts between ? and ? order by ts",
            params,
        ).fetchall()
        for event in rows:
            for device, column in [("th-1", "temperature"), ("th-2", "temperature"), ("th-1", "humidity")]:
                before = avg_window(cur, event["ts"], device, column, -10, 0)
                after = avg_window(cur, event["ts"], device, column, 10, 40)
                if before is not None and after is not None:
                    buckets[(event["relay_id"], event["state"], device, column)].append(after - before)
        out = []
        for relay_id in active:
            for state in ["ON", "OFF"]:
                def mean(device, column):
                    vals = buckets.get((relay_id, state, device, column), [])
                    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)

                th1_t, n = mean("th-1", "temperature")
                th2_t, _ = mean("th-2", "temperature")
                th1_h, _ = mean("th-1", "humidity")
                if n:
                    out.append({"relay_id": relay_id, "state": state, "n": n, "th1_t": th1_t, "th2_t": th2_t, "th1_h": th1_h})
        return out


def sensor_offsets(start, end):
    return db_one(
        """
        select avg(b.temperature - a.temperature) as th2_minus_th1_t,
               avg(c.temperature - a.temperature) as co2_minus_th1_t,
               avg(b.humidity - a.humidity) as th2_minus_th1_h,
               avg(c.humidity - a.humidity) as co2_minus_th1_h
        from sensor_log a
        join sensor_log b on b.ts = a.ts and b.device = 'th-2'
        join sensor_log c on c.ts = a.ts and c.device = 'co2-1'
        where a.device = 'th-1'
          and a.ts between ? and ?
          and a.temperature > 0 and b.temperature > 0 and c.temperature > 0
          and a.humidity > 0 and a.humidity < 100
          and b.humidity > 0 and b.humidity < 100
          and c.humidity > 0 and c.humidity < 100
        """,
        (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
    )


def day_night_stats(start, end):
    return db_rows(
        """
        select device,
               case when cast(strftime('%H', ts) as integer) between 8 and 19 then 'день 08-19' else 'ночь 20-07' end as period,
               avg(case when temperature > 0 then temperature end) as avg_t,
               avg(case when humidity > 0 and humidity < 100 then humidity end) as avg_h,
               avg(case when co2 >= 250 and co2 <= 3000 then co2 end) as avg_co2
        from sensor_log
        where ts between ? and ?
        group by device, period
        order by device, period
        """,
        (start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")),
    )


def build_report():
    st = styles()
    labels, profiles = relay_labels()
    ranges = period_ranges()
    overall = db_one(
        """
        select
          (select count(*) from sensor_log) as sensor_rows,
          (select min(ts) from sensor_log) as sensor_from,
          (select max(ts) from sensor_log) as sensor_to,
          (select count(*) from relay_log) as relay_rows,
          (select min(ts) from relay_log) as relay_from,
          (select max(ts) from relay_log) as relay_to
        """
    )
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=15 * mm,
        title="Расширенный отчет по данным теплицы",
    )
    story = []
    story.append(p("Расширенный аналитический отчет по данным теплицы", st["Title"]))
    story.append(p(f"Источник: Raspberry Pi `green`, база dashboard. Все timestamps и оси времени приведены как {MSK_LABEL}.", st["BodyText"]))
    story.append(Spacer(1, 4 * mm))
    story.append(
        table(
            [
                ["Блок", "Строк", "Начало, МСК", "Окончание, МСК"],
                ["Датчики", overall["sensor_rows"], overall["sensor_from"], overall["sensor_to"]],
                ["Реле", overall["relay_rows"], overall["relay_from"], overall["relay_to"]],
            ],
            [26 * mm, 28 * mm, 58 * mm, 58 * mm],
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(p("<b>Ключевые наблюдения.</b>", st["Heading2"]))
    story.append(
        p(
            "В истории есть регулярные минутные данные от `th-1`, `th-2` и `co2-1`, а также журнал управляющих воздействий. "
            "Это позволяет смотреть систему не только как мониторинг, но и как опытное внедрение с зарегистрированными реакциями объекта.",
            st["BodyText"],
        )
    )
    story.append(
        p(
            "Самые информативные управляющие каналы в текущей истории: реле 8, 9 и 11. По профилям dashboard они связаны с режимом "
            "`Приток с улицы (Бокс 2)`: реле 8 — основной канал профиля, реле 9 и 11 — подготовительные каналы. "
            "Реле 2 и 3 подписаны как ультразвуковые увлажнители.",
            st["Note"],
        )
    )
    profile_rows = [["Профиль", "Описание", "Подготовка", "Основной канал"]]
    for profile in profiles:
        pre = ", ".join(f"{x['relay']}={x['state']}" for x in profile.get("pre", [])) or "-"
        main = ", ".join(f"{x['relay']}={x['state']}" for x in profile.get("main", [])) or "-"
        profile_rows.append([profile.get("name", "-"), profile.get("description", "-"), pre, main])
    story.append(table(profile_rows, [38 * mm, 58 * mm, 35 * mm, 35 * mm], font_size=6.8))
    story.append(PageBreak())

    overview_rows = [["Диапазон", "Строк датчиков", "Дней", "T сред.", "H сред.", "CO2 сред.", "Проблемные значения"]]
    for item in ranges:
        stat = period_stats(item["start"], item["end"])
        bad = f"T:{stat['bad_t']} H:{stat['bad_h']} CO2:{stat['bad_co2']}"
        overview_rows.append([item["title"], stat["rows"], stat["days"], fmt(stat["avg_t"]), fmt(stat["avg_h"]), fmt(stat["avg_co2"]), bad])
    story.append(p("Сравнение диапазонов", st["Heading1"]))
    story.append(table(overview_rows, [32 * mm, 25 * mm, 16 * mm, 20 * mm, 20 * mm, 22 * mm, 38 * mm], font_size=7))
    story.append(Spacer(1, 4 * mm))
    story.append(
        p(
            "Нули и граничные значения не удалялись из базы, но в средних значениях графиков они фильтруются: T > 0, 0 < H < 100, 250 <= CO2 <= 3000. "
            "Так отчет показывает рабочую динамику и одновременно фиксирует проблему качества данных для ML-подготовки.",
            st["Note"],
        )
    )

    for idx, item in enumerate(ranges):
        if idx > 0:
            story.append(PageBreak())
        start, end = item["start"], item["end"]
        story.append(p(item["title"], st["Heading1"]))
        story.append(p(f"Диапазон: {start:%Y-%m-%d %H:%M:%S} — {end:%Y-%m-%d %H:%M:%S} {MSK_LABEL}.", st["BodyText"]))
        stats = device_stats(start, end)
        rows = [["Датчик", "Строк", "T ср/мин/макс", "H ср/мин/макс", "CO2 ср/мин/макс"]]
        for row in stats:
            rows.append(
                [
                    row["device"],
                    row["rows"],
                    f"{fmt(row['avg_t'])}/{fmt(row['min_t'])}/{fmt(row['max_t'])}",
                    f"{fmt(row['avg_h'])}/{fmt(row['min_h'])}/{fmt(row['max_h'])}",
                    f"{fmt(row['avg_co2'])}/{fmt(row['min_co2'])}/{fmt(row['max_co2'])}",
                ]
            )
        story.append(table(rows, [18 * mm, 22 * mm, 43 * mm, 43 * mm, 43 * mm], font_size=7))
        off = sensor_offsets(start, end)
        story.append(
            p(
                f"Среднее расхождение датчиков: th-2 относительно th-1 по температуре {fmt(off['th2_minus_th1_t'])} °C, "
                f"co2-1 относительно th-1 {fmt(off['co2_minus_th1_t'])} °C. "
                f"По влажности: th-2 - th-1 = {fmt(off['th2_minus_th1_h'])} п.п., co2-1 - th-1 = {fmt(off['co2_minus_th1_h'])} п.п.",
                st["Small"],
            )
        )
        story.append(line_chart(f"{item['title']}: среднесуточная температура, °C", daily_points(start, end, "avg_t"), "дата / °C"))
        story.append(line_chart(f"{item['title']}: среднесуточная влажность, %", daily_points(start, end, "avg_h"), "дата / %"))
        story.append(line_chart(f"{item['title']}: среднесуточный CO2, ppm", daily_points(start, end, "avg_co2", devices=["co2-1"]), "дата / ppm"))
        story.append(Spacer(1, 2 * mm))
        story.append(p("Суточный профиль по часам", st["Heading2"]))
        story.append(line_chart(f"{item['title']}: средняя температура по часу суток", hourly_profile(start, end, "avg_t"), f"час {MSK_LABEL} / °C"))
        story.append(line_chart(f"{item['title']}: средняя влажность по часу суток", hourly_profile(start, end, "avg_h"), f"час {MSK_LABEL} / %"))
        story.append(line_chart(f"{item['title']}: средний CO2 по часу суток", hourly_profile(start, end, "avg_co2", devices=["co2-1"]), f"час {MSK_LABEL} / ppm"))
        dn = day_night_stats(start, end)
        dn_rows = [["Датчик", "Период, МСК", "T сред.", "H сред.", "CO2 сред."]]
        for row in dn:
            dn_rows.append([row["device"], row["period"], fmt(row["avg_t"]), fmt(row["avg_h"]), fmt(row["avg_co2"])])
        story.append(table(dn_rows, [24 * mm, 30 * mm, 24 * mm, 24 * mm, 24 * mm], font_size=7))

        story.append(PageBreak())
        story.append(p(f"{item['title']}: реле и управляющие воздействия", st["Heading1"]))
        events = relay_events(start, end)
        if events:
            story.append(bar_chart("Количество событий реле в диапазоне", [str(r["relay_id"]) for r in events], [r["events"] for r in events]))
        ev_rows = [["Реле", "Назначение/связь с профилем", "Событий", "ON", "OFF", "Последнее событие"]]
        for row in events[:12]:
            ev_rows.append([row["relay_id"], labels.get(row["relay_id"], ""), row["events"], row["on_events"], row["off_events"], row["last_ts"]])
        story.append(table(ev_rows, [12 * mm, 72 * mm, 17 * mm, 13 * mm, 13 * mm, 42 * mm], font_size=6.6))
        dur_rows = [["Реле", "Назначение", "ON часов", "Событий", "Состояние на конец"]]
        for row in relay_on_durations(start, end)[:10]:
            if row["on_hours"] > 0 or row["events"] > 0:
                dur_rows.append([row["relay_id"], labels.get(row["relay_id"], ""), fmt(row["on_hours"], 2), row["events"], row["final_state"]])
        story.append(Spacer(1, 3 * mm))
        story.append(table(dur_rows, [12 * mm, 84 * mm, 24 * mm, 20 * mm, 28 * mm], font_size=6.8))
        impact = relay_impact(start, end)
        imp_rows = [["Реле", "Событие", "N", "ΔT th-1", "ΔT th-2", "ΔH th-1"]]
        for row in impact:
            imp_rows.append([row["relay_id"], row["state"], row["n"], fmt(row["th1_t"], 2), fmt(row["th2_t"], 2), fmt(row["th1_h"], 2)])
        story.append(Spacer(1, 3 * mm))
        story.append(p("Грубая реакция после переключений: среднее изменение через 10-40 минут относительно 10 минут до события.", st["Small"]))
        story.append(table(imp_rows, [14 * mm, 22 * mm, 14 * mm, 26 * mm, 26 * mm, 26 * mm], font_size=7))
        story.append(
            p(
                "Эта оценка не доказывает причинность: на микроклимат одновременно влияют погода, солнечная радиация, открытие теплицы и соседние реле. "
                "Но таблица помогает выбрать признаки для ML и понять, какие каналы управления стоит анализировать глубже.",
                st["Note"],
            )
        )

    story.append(PageBreak())
    story.append(p("Что из этого брать в ВКР и ML", st["Heading1"]))
    story.append(
        p(
            "1. Для текста ВКР можно уверенно писать об опытном внедрении: есть реальная история датчиков с 28 марта по 26 мая 2026 года и журнал переключений реле. "
            "2. Для ML нужно строить датасет с шагом 1-5 минут: текущие значения, лаги 5/10/30/60 минут, час суток, день недели, состояния реле 8/9/11 и флаги качества. "
            "3. Целевые переменные: температура и влажность `th-1`/`th-2` на горизонте 10-30 минут; CO2 — после дополнительной фильтрации и проверки калибровки. "
            "4. Отдельно стоит описать spatial variability: `th-2` систематически теплее `th-1`, значит платформа полезна именно как многоточечный мониторинг, а не один датчик.",
            st["BodyText"],
        )
    )
    story.append(
        p(
            "Ограничения: в истории есть выбросы и нулевые значения; часть реле не подписана явно в `names.json`, поэтому их назначение восстановлено по профилям dashboard. "
            "Для строгого вывода о влиянии реле потребуется экспериментальный протокол: включение одного исполнительного устройства при фиксированном состоянии остальных.",
            st["Note"],
        )
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUT_PATH)


if __name__ == "__main__":
    build_report()
