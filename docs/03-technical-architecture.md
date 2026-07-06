# 技术架构设计

## 1. 总体架构

```text
浏览器 React 页面
  |
  | HTTP/JSON
  v
Node.js Express API
  |
  | SQL
  v
SQLite 本地数据库
```

## 2. 技术选型

| 模块 | 推荐技术 | 说明 |
| --- | --- | --- |
| 前端框架 | React + Vite + TypeScript | 适合快速开发单页应用 |
| UI 样式 | 自定义 CSS 或 Tailwind 风格 CSS | 控制页面质感，避免过度依赖组件库 |
| 图表 | Recharts | 适合趋势图、柱状图、进度展示 |
| 后端 | Node.js + Express | 简单稳定，适合本地 API |
| 数据库 | SQLite | 本地文件数据库，满足持久化要求 |
| SQLite 访问 | better-sqlite3 或 Prisma | better-sqlite3 简洁直接，Prisma 类型体验好 |
| 校验 | Zod | 校验 API 入参 |
| 测试 | Vitest | 覆盖营养估算和统计逻辑 |

## 3. 页面结构

| 页面 | 路由 | 功能 |
| --- | --- | --- |
| 首页仪表盘 | / | 今日概览、关键指标、快速入口 |
| 分周计划 | /plans | 展示 7 周半计划 |
| 每日打卡 | /checkin | 打卡、体重、腰围、步数、睡眠 |
| 饮食记录 | /meals | 三餐输入、热量分析 |
| 训练记录 | /workouts | 训练动作、组数、次数、RPE |
| 后台统计 | /stats | 完成率、趋势图、周复盘 |
| 设置 | /settings | 食物库、动作库、自定义任务 |

## 4. 数据库设计

### 4.1 weekly_plans

保存默认分周计划。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| week_index | integer | 第几周 |
| title | text | 阶段名称 |
| start_date | text | 开始日期 |
| end_date | text | 结束日期 |
| frequency | text | 训练频率 |
| training_focus | text | 训练重点 |
| diet_focus | text | 饮食重点 |
| expected_result | text | 目标效果 |

### 4.2 daily_checkins

保存每日身体和生活数据。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| date | text | 日期，唯一 |
| trained | integer | 是否训练，0/1 |
| water_liters | real | 饮水量 |
| steps | integer | 步数 |
| sleep_hours | real | 睡眠小时 |
| weight_kg | real | 体重 |
| waist_cm | real | 腰围 |
| thigh_cm | real | 大腿围 |
| snack_free | integer | 是否没吃零食，0/1 |
| dinner_controlled | integer | 晚餐是否控主食，0/1 |
| notes | text | 备注 |
| created_at | text | 创建时间 |
| updated_at | text | 更新时间 |

### 4.3 custom_tasks

保存用户自定义任务。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| title | text | 任务名称 |
| category | text | training/diet/lifestyle |
| active | integer | 是否启用 |
| created_at | text | 创建时间 |

### 4.4 task_logs

保存每日任务完成状态。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| task_id | integer | custom_tasks.id |
| date | text | 日期 |
| completed | integer | 是否完成 |

### 4.5 meals

保存每日餐次。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| date | text | 日期 |
| meal_type | text | breakfast/lunch/dinner/snack |
| raw_text | text | 用户输入 |
| calories | real | 估算热量 |
| protein_g | real | 蛋白质 |
| carbs_g | real | 碳水 |
| fat_g | real | 脂肪 |
| advice | text | 饮食建议 |
| created_at | text | 创建时间 |

### 4.6 food_library

保存基础食物库。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| name | text | 食物名称 |
| aliases | text | 别名，JSON 字符串 |
| unit | text | 默认单位 |
| default_amount_g | real | 默认克重 |
| calories_per_100g | real | 每 100g 热量 |
| protein_per_100g | real | 每 100g 蛋白质 |
| carbs_per_100g | real | 每 100g 碳水 |
| fat_per_100g | real | 每 100g 脂肪 |

### 4.7 workout_logs

保存训练记录。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | integer | 主键 |
| date | text | 日期 |
| body_part | text | 部位 |
| exercise_name | text | 动作 |
| sets | integer | 组数 |
| reps | integer | 次数 |
| duration_minutes | integer | 时长 |
| rpe | integer | 主观疲劳度 |
| notes | text | 备注 |
| created_at | text | 创建时间 |

## 5. API 设计

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /api/health | 健康检查 |
| GET | /api/plans | 获取分周计划 |
| GET | /api/dashboard?date=YYYY-MM-DD | 获取首页概览 |
| GET | /api/checkins/:date | 获取某日打卡 |
| POST | /api/checkins | 创建或更新打卡 |
| GET | /api/tasks | 获取自定义任务 |
| POST | /api/tasks | 新增自定义任务 |
| PATCH | /api/tasks/:id | 修改自定义任务 |
| DELETE | /api/tasks/:id | 删除自定义任务 |
| POST | /api/task-logs | 保存任务完成状态 |
| GET | /api/meals?date=YYYY-MM-DD | 获取某日饮食 |
| POST | /api/meals/analyze | 分析饮食并保存 |
| GET | /api/workouts?date=YYYY-MM-DD | 获取训练记录 |
| POST | /api/workouts | 新增训练记录 |
| DELETE | /api/workouts/:id | 删除训练记录 |
| GET | /api/stats?range=week | 获取统计数据 |

## 6. 热量估算策略

第一版采用规则估算：

1. 建立基础食物库。
2. 从用户输入中匹配食物名称和别名。
3. 识别常见数量词，例如一碗、半碗、一个、两个、一片。
4. 如果无法识别数量，则使用默认份量。
5. 按食物库每 100g 营养数据估算总量。
6. 输出可信度，低可信度时提示用户补充份量。

## 7. 统计计算

| 指标 | 计算方式 |
| --- | --- |
| 连续打卡 | 从今天向前查找有记录且关键任务完成的连续天数 |
| 本周训练次数 | 当前自然周 workout_logs 按日期去重 |
| 训练完成率 | 本周实际训练次数 / 本周计划训练次数 |
| 平均热量 | 日期范围内 meals calories 求和后按天平均 |
| 体重变化 | date + weight_kg 时间序列 |
| 腰围变化 | date + waist_cm 时间序列 |

## 8. 数据持久化验收方法

1. 启动服务。
2. 新增一条打卡记录。
3. 新增一条饮食记录。
4. 新增一条训练记录。
5. 关闭服务。
6. 重新启动服务。
7. 页面和 API 仍能读取刚才的数据。
8. 项目目录下存在 SQLite 数据库文件。

