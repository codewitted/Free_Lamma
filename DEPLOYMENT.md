# Deployment

## Recommended Local Development

Use native Python and Node while developing:

```bash
pip install -r requirements.txt
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd frontend
npm install
npm run dev
```

## Recommended Cloud Demonstration

For dissertation demonstration, deploy the backend and frontend separately:

- Backend: Docker service from `backend/Dockerfile`.
- Frontend: static Vite build from `frontend/`.
- LLM: local Ollama/OpenWebUI, GPU VM, or secure tunnel endpoint.

This avoids paying for cloud LLM APIs and keeps the architecture honest.

## Cloud Provider Templates

- Render: `render.yaml`
- Railway: `railway.json`
- Fly.io: `fly.toml`
- Generic Docker: `docker-compose.cloud.yml`

## Important Cloud Limitations

AI2-THOR, Gazebo, ROS 2 and physical LIMO execution are normally local/lab workloads, not free-tier cloud workloads. Cloud mode should run:

- GUI
- API
- JSON validation
- PDDL generation
- MILP allocation
- dry-run execution
- evaluation dashboard/results

Run simulator and robot demos locally or on a robotics workstation.

