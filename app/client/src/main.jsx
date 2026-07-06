import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const initialDate = "2026-07-06";
const views = [
  ["dashboard", "总览"],
  ["plans", "分周计划"],
  ["checkin", "每日打卡"],
  ["meals", "饮食分析"],
  ["workouts", "训练记录"],
  ["stats", "后台统计"]
];

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  const data = await response.json();
  if (!response.ok || data.error) throw new Error(data.error || "请求失败");
  return data;
}

function metric(value, suffix) {
  return value === null || value === undefined || value === "" ? `-- ${suffix}` : `${value} ${suffix}`;
}

function mealLabel(type) {
  return { breakfast: "早餐", lunch: "午餐", dinner: "晚餐", snack: "加餐" }[type] || type;
}

function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [currentDate, setCurrentDate] = useState(initialDate);
  const [dashboard, setDashboard] = useState(null);
  const [plans, setPlans] = useState([]);
  const [checkinData, setCheckinData] = useState({ checkin: null, tasks: [] });
  const [meals, setMeals] = useState([]);
  const [workouts, setWorkouts] = useState([]);
  const [stats, setStats] = useState(null);
  const [toast, setToast] = useState("");

  async function loadAll(date = currentDate) {
    const [dashboardData, planData, checkin, mealData, workoutData, statData] = await Promise.all([
      api(`/api/dashboard?date=${date}`),
      api("/api/plans"),
      api(`/api/checkins/${date}`),
      api(`/api/meals?date=${date}`),
      api(`/api/workouts?date=${date}`),
      api(`/api/stats?date=${date}`)
    ]);
    setDashboard(dashboardData);
    setPlans(planData);
    setCheckinData(checkin);
    setMeals(mealData);
    setWorkouts(workoutData);
    setStats(statData);
  }

  function showToast(message) {
    setToast(message);
    window.setTimeout(() => setToast(""), 1800);
  }

  useEffect(() => {
    loadAll().catch((error) => showToast(error.message));
  }, []);

  async function changeDate(value) {
    setCurrentDate(value);
    await loadAll(value);
  }

  return (
    <div className="shell">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      <main className="app">
        <header className="topbar">
          <div>
            <p className="eyebrow">174cm / 71kg / 每周 3-4 次</p>
            <h1>减脂、瘦肚子瘦腿、练腹肌和肩背手臂</h1>
          </div>
          <label className="date-picker">
            记录日期
            <input type="date" value={currentDate} onChange={(event) => changeDate(event.target.value)} />
          </label>
        </header>

        {activeView === "dashboard" && <Dashboard data={dashboard} />}
        {activeView === "plans" && <Plans plans={plans} />}
        {activeView === "checkin" && (
          <Checkin
            date={currentDate}
            data={checkinData}
            reload={() => loadAll(currentDate)}
            showToast={showToast}
          />
        )}
        {activeView === "meals" && (
          <Meals date={currentDate} meals={meals} reload={() => loadAll(currentDate)} showToast={showToast} />
        )}
        {activeView === "workouts" && (
          <Workouts date={currentDate} workouts={workouts} reload={() => loadAll(currentDate)} showToast={showToast} />
        )}
        {activeView === "stats" && <Stats stats={stats} />}
      </main>
      {toast && <div className="toast show">{toast}</div>}
    </div>
  );
}

function Sidebar({ activeView, setActiveView }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">F</span>
        <div>
          <strong>健身助手</strong>
          <small>React + Vite MVP</small>
        </div>
      </div>
      <nav>
        {views.map(([id, label]) => (
          <button key={id} className={`nav ${activeView === id ? "active" : ""}`} onClick={() => setActiveView(id)}>
            {label}
          </button>
        ))}
      </nav>
      <div className="side-note">
        <strong>周期</strong>
        <span>2026-07-06 到 2026-08-26</span>
      </div>
    </aside>
  );
}

function Dashboard({ data }) {
  if (!data) return <Panel title="加载中">正在读取本地 SQLite 数据。</Panel>;
  const stage = data.stage;
  const actions = [
    stage ? `训练重点：${stage.training_focus}` : "选择计划日期",
    "每餐保证蛋白质：鸡蛋、鱼肉、豆腐、瘦肉优先",
    "晚餐主食减量，土豆、米饭、馒头不要同餐叠加",
    "记录体重、腰围、步数和睡眠，方便统计趋势"
  ];
  return (
    <section>
      <div className="hero">
        <div>
          <p className="eyebrow">当前阶段</p>
          <h2>{stage ? `第 ${stage.week_index} 阶段：${stage.title}` : "计划外日期"}</h2>
          <p>
            {stage
              ? `${stage.start_date} 到 ${stage.end_date}，${stage.training_focus}。饮食重点：${stage.diet_focus}。`
              : "请选择 2026-07-06 到 2026-08-26 之间的日期。"}
          </p>
        </div>
        <div className="hero-score">
          <span>{data.stats.completion_rate}%</span>
          <small>本周训练完成率</small>
        </div>
      </div>
      <div className="metric-grid">
        <Metric label="当前体重" value={metric(data.weight_kg, "kg")} />
        <Metric label="当前腰围" value={metric(data.waist_cm, "cm")} />
        <Metric label="连续打卡" value={`${data.streak} 天`} />
        <Metric label="今日热量" value={`${data.today_calories} kcal`} />
      </div>
      <div className="panel-grid">
        <Panel title="今日行动" subtitle="按 MVP 数据实时变化">
          <ul className="action-list">{actions.map((item) => <li key={item}>{item}</li>)}</ul>
        </Panel>
        <Panel title="本周复盘" subtitle="基于真实记录">
          <p className="summary">{data.stats.summary}</p>
        </Panel>
      </div>
    </section>
  );
}

function Plans({ plans }) {
  return (
    <Panel title="2026-07-06 到 2026-08-26 分周计划" subtitle="恢复期到冲刺期">
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>周期</th>
              <th>日期</th>
              <th>阶段</th>
              <th>频率</th>
              <th>训练重点</th>
              <th>饮食重点</th>
              <th>目标效果</th>
            </tr>
          </thead>
          <tbody>
            {plans.map((plan) => (
              <tr key={plan.id}>
                <td>第 {plan.week_index} 周</td>
                <td>{plan.start_date}<br />{plan.end_date}</td>
                <td><strong>{plan.title}</strong></td>
                <td>{plan.frequency}</td>
                <td>{plan.training_focus}</td>
                <td>{plan.diet_focus}</td>
                <td>{plan.expected_result}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

function Checkin({ date, data, reload, showToast }) {
  const c = data.checkin || {};
  const [form, setForm] = useState({});
  const [taskDraft, setTaskDraft] = useState({ title: "", category: "training" });
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    setForm({
      trained: Boolean(c.trained),
      snack_free: Boolean(c.snack_free),
      dinner_controlled: Boolean(c.dinner_controlled),
      water_liters: c.water_liters || "",
      steps: c.steps || "",
      sleep_hours: c.sleep_hours || "",
      weight_kg: c.weight_kg || "",
      waist_cm: c.waist_cm || "",
      thigh_cm: c.thigh_cm || "",
      notes: c.notes || ""
    });
    setTasks(data.tasks || []);
  }, [data, date]);

  async function saveCheckin(event) {
    event.preventDefault();
    await api("/api/checkins", { method: "POST", body: JSON.stringify({ date, ...form }) });
    showToast("打卡已保存");
    await reload();
  }

  async function addTask(event) {
    event.preventDefault();
    if (!taskDraft.title.trim()) return;
    await api("/api/tasks", { method: "POST", body: JSON.stringify(taskDraft) });
    setTaskDraft({ title: "", category: "training" });
    showToast("任务已新增");
    await reload();
  }

  async function deleteTask(id) {
    await api(`/api/tasks/${id}`, { method: "DELETE" });
    showToast("任务已删除");
    await reload();
  }

  async function saveTaskLogs() {
    await api("/api/task-logs", { method: "POST", body: JSON.stringify({ date, tasks }) });
    showToast("任务状态已保存");
    await reload();
  }

  return (
    <div className="panel-grid wide">
      <Panel title="每日打卡" subtitle="保存到 SQLite" as="form" onSubmit={saveCheckin} className="form-panel">
        <div className="checkbox-row">
          <Check label="今日训练" checked={form.trained} onChange={(v) => setForm({ ...form, trained: v })} />
          <Check label="没吃辣条/零食" checked={form.snack_free} onChange={(v) => setForm({ ...form, snack_free: v })} />
          <Check label="晚餐控制主食" checked={form.dinner_controlled} onChange={(v) => setForm({ ...form, dinner_controlled: v })} />
        </div>
        <div className="form-grid">
          {[
            ["water_liters", "饮水 L", "2.0"],
            ["steps", "步数", "7000"],
            ["sleep_hours", "睡眠 h", "7"],
            ["weight_kg", "体重 kg", "71"],
            ["waist_cm", "腰围 cm", ""],
            ["thigh_cm", "大腿围 cm", ""]
          ].map(([key, label, placeholder]) => (
            <label key={key}>{label}<input type="number" step="0.1" value={form[key] || ""} placeholder={placeholder} onChange={(event) => setForm({ ...form, [key]: event.target.value })} /></label>
          ))}
        </div>
        <label>备注<textarea value={form.notes || ""} onChange={(event) => setForm({ ...form, notes: event.target.value })} /></label>
        <button className="primary" type="submit">保存打卡</button>
      </Panel>

      <Panel title="自定义任务" subtitle="新增、完成、删除">
        <form className="inline-form" onSubmit={addTask}>
          <input value={taskDraft.title} placeholder="例如：平板支撑 3 组" onChange={(event) => setTaskDraft({ ...taskDraft, title: event.target.value })} />
          <select value={taskDraft.category} onChange={(event) => setTaskDraft({ ...taskDraft, category: event.target.value })}>
            <option value="training">训练</option>
            <option value="diet">饮食</option>
            <option value="lifestyle">生活</option>
          </select>
          <button type="submit">新增</button>
        </form>
        <div className="task-list">
          {tasks.map((task) => (
            <label className="task" key={task.id}>
              <input
                type="checkbox"
                checked={Boolean(task.completed)}
                onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, completed: event.target.checked } : item))}
              />
              <span>{task.title}</span>
              <button className="danger" type="button" onClick={() => deleteTask(task.id)}>删除</button>
            </label>
          ))}
        </div>
        <button className="secondary" type="button" onClick={saveTaskLogs}>保存任务完成状态</button>
      </Panel>
    </div>
  );
}

function Meals({ date, meals, reload, showToast }) {
  const [mealType, setMealType] = useState("breakfast");
  const [rawText, setRawText] = useState("");
  const totals = useMemo(() => meals.reduce((acc, meal) => ({
    calories: acc.calories + Number(meal.calories || 0),
    protein: acc.protein + Number(meal.protein_g || 0),
    carbs: acc.carbs + Number(meal.carbs_g || 0),
    fat: acc.fat + Number(meal.fat_g || 0)
  }), { calories: 0, protein: 0, carbs: 0, fat: 0 }), [meals]);

  async function saveMeal(event) {
    event.preventDefault();
    if (!rawText.trim()) return;
    const result = await api("/api/meals/analyze", {
      method: "POST",
      body: JSON.stringify({ date, meal_type: mealType, raw_text: rawText })
    });
    setRawText("");
    showToast(`已保存，估算 ${result.calories} kcal`);
    await reload();
  }

  return (
    <div className="panel-grid wide">
      <Panel title="饮食记录" subtitle="关键词估算热量" as="form" className="form-panel" onSubmit={saveMeal}>
        <label>餐次
          <select value={mealType} onChange={(event) => setMealType(event.target.value)}>
            <option value="breakfast">早餐</option>
            <option value="lunch">午餐</option>
            <option value="dinner">晚餐</option>
            <option value="snack">加餐</option>
          </select>
        </label>
        <label>吃了什么
          <textarea value={rawText} placeholder="例如：小米粥一碗，鸡蛋两个，面包一片" onChange={(event) => setRawText(event.target.value)} />
        </label>
        <button className="primary" type="submit">分析并保存</button>
      </Panel>
      <Panel title="当日饮食分析" subtitle="估算值">
        <div className="meal-total">
          <div><strong>{totals.calories.toFixed(0)}</strong><small> kcal</small></div>
          <div><strong>{totals.protein.toFixed(1)}</strong><small> 蛋白</small></div>
          <div><strong>{totals.carbs.toFixed(1)}</strong><small> 碳水</small></div>
          <div><strong>{totals.fat.toFixed(1)}</strong><small> 脂肪</small></div>
        </div>
        <div className="record-list">
          {meals.length ? meals.map((meal) => (
            <article className="record" key={meal.id}>
              <strong>{mealLabel(meal.meal_type)}：{meal.raw_text}</strong>
              <small>{meal.calories} kcal / 蛋白 {meal.protein_g}g / 碳水 {meal.carbs_g}g / 脂肪 {meal.fat_g}g</small>
              <p>{meal.advice}</p>
            </article>
          )) : <p className="summary">今天还没有饮食记录。</p>}
        </div>
      </Panel>
    </div>
  );
}

function Workouts({ date, workouts, reload, showToast }) {
  const [form, setForm] = useState({ body_part: "肩", exercise_name: "", sets: "", reps: "", duration_minutes: "", rpe: 6, notes: "" });

  async function saveWorkout(event) {
    event.preventDefault();
    if (!form.exercise_name.trim()) return;
    await api("/api/workouts", { method: "POST", body: JSON.stringify({ date, ...form }) });
    setForm({ body_part: "肩", exercise_name: "", sets: "", reps: "", duration_minutes: "", rpe: 6, notes: "" });
    showToast("训练记录已保存");
    await reload();
  }

  return (
    <div className="panel-grid wide">
      <Panel title="训练记录" subtitle="动作、组数、RPE" as="form" className="form-panel" onSubmit={saveWorkout}>
        <div className="form-grid">
          <label>部位
            <select value={form.body_part} onChange={(event) => setForm({ ...form, body_part: event.target.value })}>
              {["肩", "背", "肱二头", "肱三头", "腹", "腿", "有氧", "全身"].map((part) => <option key={part}>{part}</option>)}
            </select>
          </label>
          <label>动作<input value={form.exercise_name} placeholder="哑铃划船" onChange={(event) => setForm({ ...form, exercise_name: event.target.value })} /></label>
          <label>组数<input type="number" value={form.sets} placeholder="3" onChange={(event) => setForm({ ...form, sets: event.target.value })} /></label>
          <label>次数<input type="number" value={form.reps} placeholder="12" onChange={(event) => setForm({ ...form, reps: event.target.value })} /></label>
          <label>时长 min<input type="number" value={form.duration_minutes} placeholder="30" onChange={(event) => setForm({ ...form, duration_minutes: event.target.value })} /></label>
          <label>RPE<input type="number" min="1" max="10" value={form.rpe} onChange={(event) => setForm({ ...form, rpe: event.target.value })} /></label>
        </div>
        <label>备注<textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} /></label>
        <button className="primary" type="submit">保存训练</button>
      </Panel>
      <Panel title="当日训练" subtitle="真实记录">
        <div className="record-list">
          {workouts.length ? workouts.map((item) => (
            <article className="record" key={item.id}>
              <strong>{item.body_part}：{item.exercise_name}</strong>
              <small>{item.sets} 组 x {item.reps} 次 / {item.duration_minutes} 分钟 / RPE {item.rpe}</small>
              <p>{item.notes}</p>
            </article>
          )) : <p className="summary">今天还没有训练记录。</p>}
        </div>
      </Panel>
    </div>
  );
}

function Stats({ stats }) {
  if (!stats) return <Panel title="加载中">正在读取统计数据。</Panel>;
  return (
    <section>
      <div className="metric-grid">
        <Metric label="本周训练" value={`${stats.workout_days} 次`} />
        <Metric label="完成率" value={`${stats.completion_rate}%`} />
        <Metric label="连续打卡" value={`${stats.streak} 天`} />
        <Metric label="零食风险天" value={`${stats.snack_risk_days} 天`} />
      </div>
      <div className="panel-grid">
        <Panel title="热量趋势" subtitle="按天汇总"><LineChart rows={stats.meal_trend} field="calories" unit="kcal" color="#2f7d57" /></Panel>
        <Panel title="体重/腰围趋势" subtitle="按打卡记录"><LineChart rows={stats.body_trend} field="waist_cm" unit="cm" color="#d45c47" /></Panel>
      </div>
    </section>
  );
}

function LineChart({ rows, field, unit, color }) {
  const data = rows.filter((row) => row[field] !== null && row[field] !== undefined);
  if (!data.length) return <p className="summary">暂无足够数据。</p>;
  const values = data.map((row) => Number(row[field]));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const width = 520;
  const height = 210;
  const points = data.map((row, index) => ({
    x: data.length === 1 ? width / 2 : (index / (data.length - 1)) * width,
    y: height - ((Number(row[field]) - min) / range) * 150 - 30,
    row
  }));
  return (
    <div className="chart">
      <svg viewBox={`0 0 ${width} ${height}`}>
        <polyline points={points.map((p) => `${p.x},${p.y}`).join(" ")} fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {points.map((p) => (
          <g key={`${p.row.date}-${p.x}`}>
            <circle cx={p.x} cy={p.y} r="5" fill={color} />
            <text x={p.x} y={p.y - 10} textAnchor="middle" fontSize="12" fill="#1f2933">{p.row[field]} {unit}</text>
            <text x={p.x} y="198" textAnchor="middle" fontSize="11" fill="#67717d">{p.row.date.slice(5)}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function Panel({ title, subtitle, children, as: Tag = "section", className = "", ...props }) {
  return (
    <Tag className={`panel ${className}`} {...props}>
      <div className="panel-title">
        <h3>{title}</h3>
        {subtitle && <span>{subtitle}</span>}
      </div>
      {children}
    </Tag>
  );
}

function Metric({ label, value }) {
  return <article className="metric"><span>{label}</span><strong>{value}</strong></article>;
}

function Check({ label, checked, onChange }) {
  return (
    <label>
      <input type="checkbox" checked={Boolean(checked)} onChange={(event) => onChange(event.target.checked)} />
      {label}
    </label>
  );
}

createRoot(document.getElementById("root")).render(<App />);
