import json
import os
import re
import sqlite3
import sys
from datetime import date, datetime, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
CLIENT_DIST_DIR = BASE_DIR / "client" / "dist"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "fitness-assistant.sqlite"


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def get_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def init_db():
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS weekly_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_index INTEGER NOT NULL UNIQUE,
                title TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                frequency TEXT NOT NULL,
                training_focus TEXT NOT NULL,
                diet_focus TEXT NOT NULL,
                expected_result TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS daily_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                trained INTEGER DEFAULT 0,
                water_liters REAL DEFAULT 0,
                steps INTEGER DEFAULT 0,
                sleep_hours REAL DEFAULT 0,
                weight_kg REAL,
                waist_cm REAL,
                thigh_cm REAL,
                snack_free INTEGER DEFAULT 0,
                dinner_controlled INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS custom_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'lifestyle',
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                UNIQUE(task_id, date)
            );

            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                calories REAL DEFAULT 0,
                protein_g REAL DEFAULT 0,
                carbs_g REAL DEFAULT 0,
                fat_g REAL DEFAULT 0,
                advice TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS food_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                aliases TEXT DEFAULT '[]',
                unit TEXT DEFAULT '份',
                default_amount_g REAL NOT NULL,
                calories_per_100g REAL NOT NULL,
                protein_per_100g REAL NOT NULL,
                carbs_per_100g REAL NOT NULL,
                fat_per_100g REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                body_part TEXT NOT NULL,
                exercise_name TEXT NOT NULL,
                sets INTEGER DEFAULT 0,
                reps INTEGER DEFAULT 0,
                duration_minutes INTEGER DEFAULT 0,
                rpe INTEGER DEFAULT 5,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            """
        )
        seed_weekly_plans(conn)
        seed_food_library(conn)
        seed_default_tasks(conn)


def seed_weekly_plans(conn):
    count = conn.execute("SELECT COUNT(*) FROM weekly_plans").fetchone()[0]
    if count:
        return
    plans = [
        (1, "恢复期", "2026-07-06", "2026-07-12", "3 次", "深蹲、俯卧撑、哑铃划船、推举、平板支撑", "控油，早餐补蛋白", "找回运动状态，不追求练到力竭"),
        (2, "适应期", "2026-07-13", "2026-07-19", "3-4 次", "肩、背、腹基础训练", "控制主食，减少零食", "建立训练习惯，提升出汗量"),
        (3, "正式减脂期", "2026-07-20", "2026-07-26", "4 次", "肩手臂、背腿、燃脂循环", "晚餐减少主食", "让心率上来，开始稳定减脂"),
        (4, "加量期", "2026-07-27", "2026-08-02", "4 次", "肩背强化、核心训练、有氧 25-30 分钟", "增加鱼肉、鸡蛋、蔬菜", "腰围开始变化，身体更紧实"),
        (5, "强化期", "2026-08-03", "2026-08-09", "4 次", "超级组、腹部强化、手臂训练", "保证蛋白质，控制夜宵", "肩背手臂线条增强"),
        (6, "推进期", "2026-08-10", "2026-08-16", "4 次", "力量训练加燃脂循环", "控制总热量，土豆和米饭二选一", "体重腰围继续下降"),
        (7, "冲刺期", "2026-08-17", "2026-08-23", "4 次", "腹部、肩背、长有氧", "严控零食和甜饮料", "腹部更紧，核心耐力提升"),
        (8, "整理测试期", "2026-08-24", "2026-08-26", "轻训练", "测体重、腰围、俯卧撑、平板支撑", "稳定饮食", "复盘成果并准备下一阶段"),
    ]
    conn.executemany(
        """
        INSERT INTO weekly_plans
        (week_index, title, start_date, end_date, frequency, training_focus, diet_focus, expected_result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        plans,
    )


def seed_food_library(conn):
    count = conn.execute("SELECT COUNT(*) FROM food_library").fetchone()[0]
    if count:
        return
    foods = [
        ("米饭", ["大米", "白米饭", "饭"], "碗", 150, 116, 2.6, 25.9, 0.3),
        ("小米粥", ["小米", "粥"], "碗", 250, 46, 1.4, 8.4, 0.7),
        ("八宝粥", ["八宝"], "碗", 250, 85, 2.4, 17, 0.8),
        ("馒头", ["花卷"], "个", 100, 223, 7, 47, 1.1),
        ("面包", ["吐司"], "片", 35, 265, 9, 49, 3.2),
        ("鸡蛋", ["蛋"], "个", 55, 143, 12.6, 0.7, 9.5),
        ("鱼肉", ["鱼", "炖鱼"], "份", 150, 120, 20, 0, 4),
        ("猪瘦肉", ["瘦肉", "猪肉", "炖肉"], "份", 120, 143, 20.3, 1.5, 6.2),
        ("土豆", ["马铃薯"], "个", 150, 81, 2.6, 17.8, 0.2),
        ("茄子", ["炖茄子"], "份", 200, 25, 1.1, 5.7, 0.2),
        ("辣椒", ["青椒", "尖椒"], "份", 100, 29, 1, 6, 0.3),
        ("青菜", ["蔬菜", "白菜", "生菜", "菠菜"], "份", 200, 25, 2, 4, 0.3),
        ("西瓜", ["瓜"], "块", 300, 31, 0.6, 7.8, 0.2),
        ("豆腐", ["豆干"], "份", 150, 82, 8.1, 3.7, 3.7),
        ("牛奶", ["奶"], "杯", 250, 54, 3.3, 5, 3.2),
        ("辣条", ["零食"], "包", 60, 450, 8, 55, 22),
    ]
    conn.executemany(
        """
        INSERT INTO food_library
        (name, aliases, unit, default_amount_g, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [(name, json.dumps(aliases, ensure_ascii=False), unit, amount, cal, protein, carbs, fat) for name, aliases, unit, amount, cal, protein, carbs, fat in foods],
    )


def seed_default_tasks(conn):
    count = conn.execute("SELECT COUNT(*) FROM custom_tasks").fetchone()[0]
    if count:
        return
    tasks = [
        ("饮水达到 2L", "lifestyle"),
        ("不吃辣条/零食", "diet"),
        ("晚餐控制主食", "diet"),
        ("完成今日训练或快走", "training"),
        ("睡眠达到 7 小时", "lifestyle"),
    ]
    conn.executemany(
        "INSERT INTO custom_tasks (title, category, active, created_at) VALUES (?, ?, 1, ?)",
        [(title, category, now_iso()) for title, category in tasks],
    )


def current_stage(conn, target_date):
    row = conn.execute(
        """
        SELECT * FROM weekly_plans
        WHERE date(?) BETWEEN date(start_date) AND date(end_date)
        ORDER BY week_index
        LIMIT 1
        """,
        (target_date,),
    ).fetchone()
    return dict(row) if row else None


def get_latest_metric(conn, field):
    row = conn.execute(
        f"SELECT {field} AS value FROM daily_checkins WHERE {field} IS NOT NULL ORDER BY date DESC LIMIT 1"
    ).fetchone()
    return row["value"] if row else None


def week_bounds(target_date):
    d = date.fromisoformat(target_date)
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


def calculate_streak(conn, target_date):
    streak = 0
    d = date.fromisoformat(target_date)
    while True:
        row = conn.execute(
            """
            SELECT trained, snack_free, dinner_controlled
            FROM daily_checkins
            WHERE date = ?
            """,
            (d.isoformat(),),
        ).fetchone()
        if not row or not (row["trained"] or row["snack_free"] or row["dinner_controlled"]):
            break
        streak += 1
        d -= timedelta(days=1)
    return streak


def amount_multiplier(text, food_name, aliases):
    keys = [food_name] + aliases
    matches = [(text.find(k), k) for k in keys if k in text]
    if not matches:
        return 1.0
    pos, key = min(matches, key=lambda item: item[0])
    before = text[max(0, pos - 3): pos]
    after = text[pos + len(key): pos + len(key) + 4]
    if re.search(r"(半|0\.5)", after) or re.search(r"(半|0\.5)$", before):
        return 0.5
    if re.search(r"^(两|二|2)\s*(个|碗|片|份|块)?", after) or re.search(r"(两|二|2)\s*$", before):
        return 2.0
    if re.search(r"^(三|3)\s*(个|碗|片|份|块)?", after) or re.search(r"(三|3)\s*$", before):
        return 3.0
    if re.search(r"^(四|4)\s*(个|碗|片|份|块)?", after) or re.search(r"(四|4)\s*$", before):
        return 4.0
    return 1.0


def analyze_meal_text(conn, raw_text):
    foods = rows_to_dicts(conn.execute("SELECT * FROM food_library").fetchall())
    matched = []
    total = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    normalized = raw_text.replace(" ", "")
    for food in foods:
        aliases = json.loads(food["aliases"] or "[]")
        keys = [food["name"]] + aliases
        if any(key and key in normalized for key in keys):
            multiplier = amount_multiplier(normalized, food["name"], aliases)
            amount = food["default_amount_g"] * multiplier
            item = {
                "name": food["name"],
                "amount_g": round(amount, 1),
                "calories": round(amount * food["calories_per_100g"] / 100, 1),
                "protein_g": round(amount * food["protein_per_100g"] / 100, 1),
                "carbs_g": round(amount * food["carbs_per_100g"] / 100, 1),
                "fat_g": round(amount * food["fat_per_100g"] / 100, 1),
            }
            matched.append(item)
            for key in total:
                total[key] += item[key]
    advice_parts = []
    if not matched:
        advice_parts.append("没有匹配到食物库，建议补充具体食物和份量。")
    if total["protein_g"] < 20 and matched:
        advice_parts.append("蛋白质偏少，可以加鸡蛋、鱼肉、豆腐或牛奶。")
    if total["carbs_g"] > 90:
        advice_parts.append("碳水偏高，土豆、米饭、馒头尽量不要同餐叠加。")
    if total["fat_g"] > 30:
        advice_parts.append("脂肪偏高，注意少油，辣条和重油茄子要控制。")
    if matched and not advice_parts:
        advice_parts.append("这一餐结构可以，注意蔬菜和饮水。")
    return {
        "matched_items": matched,
        "calories": round(total["calories"], 1),
        "protein_g": round(total["protein_g"], 1),
        "carbs_g": round(total["carbs_g"], 1),
        "fat_g": round(total["fat_g"], 1),
        "advice": " ".join(advice_parts),
    }


def get_stats(conn, target_date):
    week_start, week_end = week_bounds(target_date)
    workout_days = conn.execute(
        "SELECT COUNT(DISTINCT date) AS count FROM workout_logs WHERE date BETWEEN ? AND ?",
        (week_start, week_end),
    ).fetchone()["count"]
    checkin_count = conn.execute(
        "SELECT COUNT(*) AS count FROM daily_checkins WHERE date BETWEEN ? AND ?",
        (week_start, week_end),
    ).fetchone()["count"]
    meal_rows = rows_to_dicts(
        conn.execute(
            """
            SELECT date, ROUND(SUM(calories), 1) AS calories, ROUND(SUM(protein_g), 1) AS protein_g
            FROM meals
            GROUP BY date
            ORDER BY date
            """
        ).fetchall()
    )
    body_rows = rows_to_dicts(
        conn.execute(
            """
            SELECT date, weight_kg, waist_cm, thigh_cm
            FROM daily_checkins
            WHERE weight_kg IS NOT NULL OR waist_cm IS NOT NULL OR thigh_cm IS NOT NULL
            ORDER BY date
            """
        ).fetchall()
    )
    snack_count = conn.execute(
        "SELECT COUNT(*) AS count FROM daily_checkins WHERE snack_free = 0 AND date BETWEEN ? AND ?",
        (week_start, week_end),
    ).fetchone()["count"]
    completion_rate = min(100, round((workout_days / 4) * 100)) if workout_days else 0
    return {
        "week_start": week_start,
        "week_end": week_end,
        "workout_days": workout_days,
        "checkin_count": checkin_count,
        "completion_rate": completion_rate,
        "streak": calculate_streak(conn, target_date),
        "snack_risk_days": snack_count,
        "meal_trend": meal_rows,
        "body_trend": body_rows,
        "summary": build_summary(workout_days, completion_rate, meal_rows, body_rows),
    }


def get_recovery(conn, target_date):
    end = date.fromisoformat(target_date)
    start = end - timedelta(days=6)
    start_text = start.isoformat()
    end_text = end.isoformat()
    summary = conn.execute(
        """
        SELECT
            COALESCE(SUM(duration_minutes), 0) AS total_minutes,
            AVG(rpe) AS average_rpe
        FROM workout_logs
        WHERE date BETWEEN ? AND ?
        """,
        (start_text, end_text),
    ).fetchone()
    high_rpe_days = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM (
            SELECT date
            FROM workout_logs
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            HAVING MAX(rpe) >= 8
        )
        """,
        (start_text, end_text),
    ).fetchone()["count"]

    total_minutes = int(summary["total_minutes"] or 0)
    average_rpe = round(float(summary["average_rpe"] or 0), 1)

    if total_minutes >= 360 or average_rpe >= 8 or high_rpe_days >= 3:
        risk_level = "high"
        advice = "过去 7 天训练负荷偏高，建议今天安排休息、拉伸或低强度有氧，并优先保证睡眠和补水。"
    elif total_minutes >= 180 or average_rpe >= 6.5 or high_rpe_days >= 1:
        risk_level = "medium"
        advice = "过去 7 天训练负荷中等，建议保留训练但降低强度，避免连续高 RPE 训练。"
    else:
        risk_level = "low"
        advice = "过去 7 天训练负荷较低，恢复风险不高，可以按计划训练，并逐步增加训练量。"

    return {
        "date": end_text,
        "window_start": start_text,
        "window_end": end_text,
        "total_minutes": total_minutes,
        "average_rpe": average_rpe,
        "high_rpe_days": high_rpe_days,
        "risk_level": risk_level,
        "advice": advice,
    }


def build_summary(workout_days, completion_rate, meal_rows, body_rows):
    parts = []
    if completion_rate >= 75:
        parts.append("本周训练频率达标，继续保持 3-4 次节奏。")
    elif workout_days:
        parts.append("本周已经开始训练，建议补足到 3 次以上。")
    else:
        parts.append("本周暂无训练记录，先从快走和基础力量恢复。")
    if meal_rows:
        latest = meal_rows[-1]
        if latest["calories"] and latest["calories"] > 2200:
            parts.append("最近一天热量偏高，晚餐主食和零食需要收紧。")
        elif latest["protein_g"] and latest["protein_g"] < 70:
            parts.append("蛋白质可能不足，优先加鸡蛋、鱼肉、豆腐。")
        else:
            parts.append("饮食记录已有基础数据，可以继续观察热量趋势。")
    if len(body_rows) >= 2:
        first, last = body_rows[0], body_rows[-1]
        if first.get("waist_cm") and last.get("waist_cm") and last["waist_cm"] < first["waist_cm"]:
            parts.append("腰围趋势在下降，减脂方向正确。")
    return " ".join(parts)


class FitnessHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        parsed = urlparse(path)
        clean_path = parsed.path
        if clean_path == "/":
            return str(CLIENT_DIST_DIR / "index.html")
        target = CLIENT_DIST_DIR / clean_path.lstrip("/")
        if not target.exists() and CLIENT_DIST_DIR.exists():
            return str(CLIENT_DIST_DIR / "index.html")
        return str(target)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        if not path.startswith("/api/"):
            return super().do_GET()
        try:
            with get_db() as conn:
                if path == "/api/health":
                    return self.send_json({"ok": True, "database": str(DB_PATH), "time": now_iso()})
                if path == "/api/plans":
                    rows = conn.execute("SELECT * FROM weekly_plans ORDER BY week_index").fetchall()
                    return self.send_json(rows_to_dicts(rows))
                if path == "/api/food-library":
                    rows = conn.execute(
                        """
                        SELECT name, unit, default_amount_g, calories_per_100g,
                               protein_per_100g, carbs_per_100g, fat_per_100g
                        FROM food_library
                        ORDER BY id
                        """
                    ).fetchall()
                    return self.send_json(rows_to_dicts(rows))
                if path == "/api/tasks":
                    rows = conn.execute("SELECT * FROM custom_tasks WHERE active = 1 ORDER BY id").fetchall()
                    return self.send_json(rows_to_dicts(rows))
                if path.startswith("/api/checkins/"):
                    target = path.rsplit("/", 1)[-1]
                    row = conn.execute("SELECT * FROM daily_checkins WHERE date = ?", (target,)).fetchone()
                    task_rows = conn.execute(
                        """
                        SELECT t.id, t.title, t.category, COALESCE(l.completed, 0) AS completed
                        FROM custom_tasks t
                        LEFT JOIN task_logs l ON l.task_id = t.id AND l.date = ?
                        WHERE t.active = 1
                        ORDER BY t.id
                        """,
                        (target,),
                    ).fetchall()
                    return self.send_json({"checkin": dict(row) if row else None, "tasks": rows_to_dicts(task_rows)})
                if path == "/api/meals":
                    target = query.get("date", [date.today().isoformat()])[0]
                    rows = conn.execute("SELECT * FROM meals WHERE date = ? ORDER BY id DESC", (target,)).fetchall()
                    return self.send_json(rows_to_dicts(rows))
                if path == "/api/workouts":
                    target = query.get("date", [date.today().isoformat()])[0]
                    rows = conn.execute("SELECT * FROM workout_logs WHERE date = ? ORDER BY id DESC", (target,)).fetchall()
                    return self.send_json(rows_to_dicts(rows))
                if path == "/api/stats":
                    target = query.get("date", [date.today().isoformat()])[0]
                    return self.send_json(get_stats(conn, target))
                if path == "/api/recovery":
                    target = query.get("date", [date.today().isoformat()])[0]
                    return self.send_json(get_recovery(conn, target))
                if path == "/api/dashboard":
                    target = query.get("date", [date.today().isoformat()])[0]
                    week_start, week_end = week_bounds(target)
                    workouts = conn.execute(
                        "SELECT COUNT(DISTINCT date) AS count FROM workout_logs WHERE date BETWEEN ? AND ?",
                        (week_start, week_end),
                    ).fetchone()["count"]
                    calories = conn.execute(
                        "SELECT COALESCE(SUM(calories), 0) AS total FROM meals WHERE date = ?",
                        (target,),
                    ).fetchone()["total"]
                    checkin = conn.execute("SELECT * FROM daily_checkins WHERE date = ?", (target,)).fetchone()
                    return self.send_json(
                        {
                            "date": target,
                            "stage": current_stage(conn, target),
                            "checkin": dict(checkin) if checkin else None,
                            "weight_kg": get_latest_metric(conn, "weight_kg"),
                            "waist_cm": get_latest_metric(conn, "waist_cm"),
                            "week_workouts": workouts,
                            "today_calories": round(calories or 0, 1),
                            "streak": calculate_streak(conn, target),
                            "stats": get_stats(conn, target),
                        }
                    )
        except Exception as exc:
            return self.send_json({"error": str(exc)}, status=500)
        return self.send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if not path.startswith("/api/"):
            return self.send_json({"error": "Not found"}, status=404)
        try:
            payload = self.read_json()
            with get_db() as conn:
                if path == "/api/checkins":
                    target = payload.get("date") or date.today().isoformat()
                    values = {
                        "trained": int(bool(payload.get("trained"))),
                        "water_liters": float(payload.get("water_liters") or 0),
                        "steps": int(payload.get("steps") or 0),
                        "sleep_hours": float(payload.get("sleep_hours") or 0),
                        "weight_kg": payload.get("weight_kg") or None,
                        "waist_cm": payload.get("waist_cm") or None,
                        "thigh_cm": payload.get("thigh_cm") or None,
                        "snack_free": int(bool(payload.get("snack_free"))),
                        "dinner_controlled": int(bool(payload.get("dinner_controlled"))),
                        "notes": payload.get("notes") or "",
                    }
                    existing = conn.execute("SELECT id FROM daily_checkins WHERE date = ?", (target,)).fetchone()
                    if existing:
                        conn.execute(
                            """
                            UPDATE daily_checkins
                            SET trained=:trained, water_liters=:water_liters, steps=:steps, sleep_hours=:sleep_hours,
                                weight_kg=:weight_kg, waist_cm=:waist_cm, thigh_cm=:thigh_cm,
                                snack_free=:snack_free, dinner_controlled=:dinner_controlled,
                                notes=:notes, updated_at=:updated_at
                            WHERE date=:date
                            """,
                            {**values, "date": target, "updated_at": now_iso()},
                        )
                    else:
                        conn.execute(
                            """
                            INSERT INTO daily_checkins
                            (date, trained, water_liters, steps, sleep_hours, weight_kg, waist_cm, thigh_cm,
                             snack_free, dinner_controlled, notes, created_at, updated_at)
                            VALUES (:date, :trained, :water_liters, :steps, :sleep_hours, :weight_kg, :waist_cm,
                                    :thigh_cm, :snack_free, :dinner_controlled, :notes, :created_at, :updated_at)
                            """,
                            {**values, "date": target, "created_at": now_iso(), "updated_at": now_iso()},
                        )
                    return self.send_json({"ok": True})
                if path == "/api/tasks":
                    cur = conn.execute(
                        "INSERT INTO custom_tasks (title, category, active, created_at) VALUES (?, ?, 1, ?)",
                        (payload.get("title", "").strip(), payload.get("category", "lifestyle"), now_iso()),
                    )
                    return self.send_json({"ok": True, "id": cur.lastrowid})
                if path == "/api/task-logs":
                    target = payload.get("date") or date.today().isoformat()
                    for item in payload.get("tasks", []):
                        conn.execute(
                            """
                            INSERT INTO task_logs (task_id, date, completed)
                            VALUES (?, ?, ?)
                            ON CONFLICT(task_id, date) DO UPDATE SET completed = excluded.completed
                            """,
                            (int(item["id"]), target, int(bool(item.get("completed")))),
                        )
                    return self.send_json({"ok": True})
                if path == "/api/meals/analyze":
                    target = payload.get("date") or date.today().isoformat()
                    meal_type = payload.get("meal_type") or "breakfast"
                    raw_text = payload.get("raw_text", "").strip()
                    analysis = analyze_meal_text(conn, raw_text)
                    cur = conn.execute(
                        """
                        INSERT INTO meals
                        (date, meal_type, raw_text, calories, protein_g, carbs_g, fat_g, advice, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            target,
                            meal_type,
                            raw_text,
                            analysis["calories"],
                            analysis["protein_g"],
                            analysis["carbs_g"],
                            analysis["fat_g"],
                            analysis["advice"],
                            now_iso(),
                        ),
                    )
                    return self.send_json({"ok": True, "id": cur.lastrowid, **analysis})
                if path == "/api/workouts":
                    cur = conn.execute(
                        """
                        INSERT INTO workout_logs
                        (date, body_part, exercise_name, sets, reps, duration_minutes, rpe, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            payload.get("date") or date.today().isoformat(),
                            payload.get("body_part") or "全身",
                            payload.get("exercise_name") or "",
                            int(payload.get("sets") or 0),
                            int(payload.get("reps") or 0),
                            int(payload.get("duration_minutes") or 0),
                            int(payload.get("rpe") or 5),
                            payload.get("notes") or "",
                            now_iso(),
                        ),
                    )
                    return self.send_json({"ok": True, "id": cur.lastrowid})
        except Exception as exc:
            return self.send_json({"error": str(exc)}, status=500)
        return self.send_json({"error": "Not found"}, status=404)

    def do_PATCH(self):
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
            with get_db() as conn:
                if path.startswith("/api/tasks/"):
                    task_id = int(path.rsplit("/", 1)[-1])
                    conn.execute(
                        "UPDATE custom_tasks SET title = ?, category = ? WHERE id = ?",
                        (payload.get("title"), payload.get("category", "lifestyle"), task_id),
                    )
                    return self.send_json({"ok": True})
        except Exception as exc:
            return self.send_json({"error": str(exc)}, status=500)
        return self.send_json({"error": "Not found"}, status=404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        try:
            with get_db() as conn:
                if path.startswith("/api/tasks/"):
                    task_id = int(path.rsplit("/", 1)[-1])
                    conn.execute("UPDATE custom_tasks SET active = 0 WHERE id = ?", (task_id,))
                    return self.send_json({"ok": True})
                if path.startswith("/api/workouts/"):
                    workout_id = int(path.rsplit("/", 1)[-1])
                    conn.execute("DELETE FROM workout_logs WHERE id = ?", (workout_id,))
                    return self.send_json({"ok": True})
        except Exception as exc:
            return self.send_json({"error": str(exc)}, status=500)
        return self.send_json({"error": "Not found"}, status=404)


def run():
    init_db()
    port = int(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), FitnessHandler)
    print(f"健身助手 MVP 已启动: http://127.0.0.1:{port}")
    print(f"SQLite 数据库: {DB_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    run()
