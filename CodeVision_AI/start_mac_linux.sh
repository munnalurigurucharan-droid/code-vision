#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -f .env ]]; then cp .env.example .env; echo 'Created .env. Add API keys to enable live Hindsight and Groq.'; fi
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
(cd backend && ../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &
BACK_PID=$!
trap 'kill "$BACK_PID" 2>/dev/null || true' EXIT
cd frontend
npm install --no-audit --no-fund
echo 'Open http://127.0.0.1:5173'
npm run dev
