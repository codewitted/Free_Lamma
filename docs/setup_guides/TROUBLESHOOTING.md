# Troubleshooting

## Ollama Unavailable

The backend will use the rule-based parser. Start Ollama with `ollama serve`.

## Fast Downward Missing

Set `FAST_DOWNWARD_PATH`. Until then, the planner endpoint returns a fallback plan.

## ROS 2 Missing

The dispatcher uses mock mode and records the intended actions.

## AI2-THOR Fails to Launch

Use dry-run mode or run on a machine with display support.

## Frontend Cannot Reach Backend

Set `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

