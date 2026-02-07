# devfest-2026

Starter Svelte (Vite) frontend + FastAPI backend scaffold.

Quickstart

Frontend

```bash
cd web
npm install
npm run dev
```

Backend

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Docker (optional)

```bash
docker compose up --build
```

Files created
- web/ — Svelte + Vite app
- api/ — FastAPI app
- docker-compose.yml — local services
