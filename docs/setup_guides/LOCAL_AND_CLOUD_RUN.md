# Local and Cloud Run Guide

Open LaMMA-R is intentionally portable. You can run it as local Python/Node processes, local Docker containers, or cloud containers.

## Option A: Local Native Run

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Option B: Local Docker

```bash
cp .env.example .env
docker compose -f docker-compose.local.yml up --build
```

Open `http://localhost:5173`.

## Option C: Cloud Backend

Deploy `backend/Dockerfile` to Render, Railway, Fly.io, Azure Container Apps, Google Cloud Run, AWS App Runner, or any Docker host.

Minimum environment:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://your-ollama-or-openwebui-endpoint
OLLAMA_MODEL=llama3.1:8b
USE_PAID_API=false
EXECUTION_MODE=dry_run
```

Cloud note: many free cloud hosts do not run local LLMs well. The recommended setup is:

- Backend in cloud.
- Ollama/OpenWebUI either on a GPU VM, university machine, or local machine exposed through a secure tunnel.
- `USE_PAID_API=false` unless you intentionally enable a paid fallback.

## Option D: Cloud Frontend

Deploy `frontend/` to Netlify, Vercel, Render Static Site, Cloudflare Pages, or any static host.

Set:

```env
VITE_API_BASE_URL=https://your-backend-url
```

## Option E: Single-VM Cloud Docker

On a Linux VM:

```bash
git clone <your-repo-url>
cd open-lamma-r-independent
cp .env.example .env
docker compose -f docker-compose.cloud.yml up --build -d
```

Serve ports `80` and `8000` according to your VM firewall and reverse proxy.

