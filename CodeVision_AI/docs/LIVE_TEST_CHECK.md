# Real-service verification — sign off before submission

**Do not mark Hindsight as verified based only on `/api/health` — that endpoint checks configuration, not connectivity.**

## Hindsight Cloud

1. Open https://ui.hindsight.vectorize.io, sign in and visit **Connect** to retrieve API endpoint and API key.
2. Put `HINDSIGHT_API_KEY=...` in `.env`; keep the base URL as `https://api.hindsight.vectorize.io` unless Connect shows a different one. Restart FastAPI.
3. `/api/health` should show `hindsight_configured: true` and `hindsight_verified: false` (the latter is intentionally conservative).
4. On CodeVision UI, load DemoAuth. Agent memory → **Retain sample fix**.
5. Confirm `stored_in_hindsight: true` in Network/Swagger response. Record bank ID.
6. Run AI Investigator with memory ON. Confirm `memory_status: recalled` and at least one **real** memory evidence record. If it returns `no-results`, retry or inspect indexing delay, without claiming success prematurely.
7. Run Reflect and verify the server returns an actual non-empty Hindsight response.
8. Restart the app, reload same DemoAuth project and ask again to check cross-session memory.

**If you get 401/403:** verify key and scoped bank permission. **402:** check credit balance. **503:** examine API response and backend logs. Treat all failures as blockers to a true memory demo.

## Groq (optional for richer narrative)

1. Set `GROQ_API_KEY` in `.env` from your Groq account. Restart backend.
2. Ask a source-specific question. Confirm `provider: groq`, not `static-only`.
3. Check answer against actual `src/auth.py`; it should distinguish a hypothetical fix from a confirmed test.

## Frontend / API

- [ ] `npm install` completes; `npm run build` succeeds.
- [ ] `cd backend && python -m pytest -q` succeeds.
- [ ] `GET http://127.0.0.1:8000/api/health` returns `status=ok`.
- [ ] `http://127.0.0.1:5173` loads, mobile width ~390 px renders, tabs work.
- [ ] Demo import works. Architecture diagram renders, code explorer shows auth.py.
- [ ] ZIP upload of `examples/demo-repo` works after zipping the folder.
- [ ] Public GitHub import works for a repo within limits, if used in the presentation.
- [ ] Memory comparison uses identical question and recorded live evidence.
- [ ] App does not expose `.env`, keys, private code, actual incident/customer data.

## Evidence table (fill in with actual data)

| Check | Status (pass/fail) | Evidence / screenshot |
|---|---|---|
| Backend tests | TBD | `tests_*.png` |
| Frontend build | TBD | `build.png` |
| Live Hindsight retain | TBD | `retain_success.png` |
| Live Hindsight recall | TBD | `recall_evidence.png` |
| Hindsight reflect | TBD | `reflect.png` |
| Groq response (if used) | TBD | `groq.png` |
| Video 1080p | TBD | YouTube URL |

**Record tests using actual screen output; never generate fake terminal screenshots or memory IDs.**
