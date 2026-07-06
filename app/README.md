# Health Assistant MVP

This is the runnable local MVP for the fitness and diet assistant.

It includes:

- React + Vite frontend.
- Python standard-library HTTP API server.
- Local SQLite database.
- Weekly plan display.
- Daily check-in.
- Custom tasks.
- Meal recording and calorie estimation.
- Workout logs.
- Statistics dashboard.

## Install

```powershell
cd D:\DevEnv\Work\health-assistant\app
npm.cmd install --cache .\.npm-cache
```

## Build Frontend

```powershell
npm.cmd run build
```

The build output is generated at:

```text
D:\DevEnv\Work\health-assistant\app\client\dist
```

## Run Local Demo

```powershell
python server.py
```

Open:

```text
http://127.0.0.1:8765
```

If port 8765 is occupied:

```powershell
python server.py 8766
```

Then open:

```text
http://127.0.0.1:8766
```

## Vite Dev Mode

Start the Python API first:

```powershell
python server.py
```

Then in another terminal:

```powershell
npm.cmd run dev
```

Open:

```text
http://127.0.0.1:5173
```

Vite proxies `/api` requests to `http://127.0.0.1:8765`.

## Database

```text
D:\DevEnv\Work\health-assistant\app\data\fitness-assistant.sqlite
```

The database is local and persists check-ins, meals, workouts, tasks, and seeded weekly plans.
