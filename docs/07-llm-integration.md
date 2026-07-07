# LLM Integration Notes

## Goal

The app keeps the local calorie rule engine as an explainable baseline, then optionally sends the user's meal text, matched foods, estimated calories, macro nutrients, check-ins, workouts, recovery, and weekly statistics to a configurable large language model for coaching advice.

This avoids fully hard-coded advice while still allowing the app to work offline or without an API key.

## Provider Contract

The backend calls an OpenAI-compatible Chat Completions endpoint:

```text
POST {LLM_BASE_URL}/chat/completions
Authorization: Bearer {LLM_API_KEY}
```

Required `.env` fields:

```text
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct
LLM_TIMEOUT_SECONDS=20
```

`LLM_MODEL` can be changed to the exact model name supplied by the provider, including a Llama model, a flash model, or another chat model exposed through the same API shape.

## Prompt Design

The prompts use role-based messages:

- `system`: durable rules, safety boundaries, user profile, output format.
- `user`: the current structured local data from SQLite and the rule-engine estimate.

The nutrition prompt asks the model to:

- Treat local calorie output as an estimate, not a medical result.
- Point out uncertainty when food amount is unclear.
- Focus on protein, main carbs, vegetables, oil, snacks, and dinner control.
- Give a short next-meal adjustment based on the user's common foods.

The coach prompt asks the model to:

- Avoid promising spot fat loss.
- Keep weekly training within 3 to 4 sessions.
- Read real local check-in, meal, workout, recovery, and stats data.
- Return short sections: weekly judgment, today's action, diet adjustment, training adjustment.

## Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /api/ai-status` | Shows whether `.env` has an API key and which base URL/model will be used. |
| `GET /api/ai-coach?date=YYYY-MM-DD` | Generates a coach review from real local records, or returns rule fallback. |
| `POST /api/meals/analyze` | Runs local food matching first, then uses LLM meal advice when configured. |

## Safety

- `.env` is ignored by Git.
- API keys are never returned by API responses.
- If the model call fails, the backend returns local rule-based fallback advice.
- The app does not call the LLM unless `LLM_API_KEY` is present.
