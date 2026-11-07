# Deployment — local-first, with caution

**Current recommendation:** Present from the laptop on `127.0.0.1` because this version has no login, user isolation, hosted abuse controls, or privacy assurance for arbitrary code uploads. Do not expose FastAPI publicly without adding those protections first.

To build the React static frontend:

```sh
cd frontend
npm install
npm run build
```

To run FastAPI locally:

```sh
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

When deployed separately, set `FRONTEND_ORIGIN` to the actual trusted frontend origin(s), and configure the frontend's API base URL/proxy accordingly. The included Vite proxy only works for development. Secure deployments must also arrange managed PostgreSQL or durable SQLite storage, secret management, auth, rate limits, safe handling of uploaded source and consent to external Groq data transmission.

No hosting accounts or resources were provisioned. No live public URL is claimed in this package.
