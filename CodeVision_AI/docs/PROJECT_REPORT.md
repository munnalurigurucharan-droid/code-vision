# CodeVision AI — short project report

**Title:** CodeVision AI: A Repository Intelligence Agent with Persistent Debugging Memory

**Problem:** Software engineers often enter unfamiliar codebases without a clear picture of entry points, module dependencies, and previous debugging decisions. A stateless assistant can explain source code but has no inherent durable record of what the team already learned.

**Solution:** CodeVision imports a supported repository, extracts static code structure, renders import dependency diagrams, provides grounded debugging assistance, and retains developer-reported debugging outcomes using Hindsight. Later investigations can recall relevant prior incidents.

**MVP scope:** Public GitHub repository or ZIP ingestion; Python AST-based symbols/imports; basic JS/TS import scanning; Mermaid dependency map; React file explorer and investigation panel; Groq optional; Hindsight retain/recall/reflect real API; local SQLite metadata.

**Tech stack:** React 18, Vite 6, TypeScript, Mermaid 11, FastAPI, Python 3.11+, AST, HTTPX, SQLite, official `hindsight-client`, optional Groq Chat Completions.

**Memory flow:** Reporter enters symptom, root cause, fix and failed experiments → FastAPI submits them to Hindsight Retain in a deterministic per-repository bank → later query calls Hindsight Recall → source-based question answering includes historical evidence → Reflect can synthesize common lessons.

**Synthetic demonstration:** DemoAuth contains a deliberate `token.startswith(EXPECTED_TOKEN)` mistake. The sample memory records why prefix validation caused incorrect acceptance of suffixed tokens. The actual memory result depends on live Hindsight service configuration.

**Validation status (generated snapshot):** 15 Python backend tests passed. These cover parsing, safe ZIP import, project endpoints and simulated API memory adapter contracts. Live Hindsight Cloud connection, Groq connection and React npm build were not verified in the generation environment and must be signed off using `LIVE_TEST_CHECK.md`.

**Caveats:** No arbitrary repo code execution; static graph ≠ runtime execution; only limited language analysis; no hosted multi-user security; LLM outputs require review; avoid uploading sensitive code. See README.

**Value:** Better onboarding, earlier access to debugging lessons, and less repeated investigative work in small software teams.

**Future directions:** Tree-sitter parsers, real call traces, team-based memory permissions, GitHub PR/issue history ingestion, evaluated retrieval quality, secure hosted tenancy.
