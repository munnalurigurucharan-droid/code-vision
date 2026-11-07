# CodeVision AI — judge Q&A (short, speaking-ready)

**One-line pitch**: “CodeVision understands a repository’s static structure and, using Hindsight, remembers previous debugging experiences so developers can avoid repeatedly solving the same incidents.”

**What problem?** Developers spend time learning unfamiliar repos; fixes and failed debugging attempts get lost across sessions.

**Who is it for?** Software teams, junior engineers onboarding to existing codebases, maintainers and incident responders.

**Why not ChatGPT?** CodeVision indexes a repository, visualizes internal imports, and retrieves project-specific historical resolution notes from a durable bank. These are specific integrations; it is not intrinsically more accurate than a well-connected general assistant.

**How is Hindsight used?** `aretain` stores incident + root cause + fix + failed attempts in a per-repo bank; `arecall` retrieves similar incidents during another investigation; `areflect` synthesizes historical lessons.

**Why is memory essential?** Static inspection cannot know which workaround was tried last Tuesday. Hindsight supplies that historical context and helps avoid repeated dead ends.

**What happens without an API key?** Static analysis and browsing still work; there is **no** Hindsight recall. The app explicitly shows it is unconfigured. The honest demo of memory requires live credentials.

**What is the key demo?** A synthetic auth bug: prefix matching mistakenly accepts `demo-secret-evil`. Before memory, inspect code; then save the earlier fix through Hindsight; after memory, retrieve the past root cause and unsuccessful attempts.

**Is the architecture a runtime trace?** No. It is a static import map. The execution sequence is a heuristic overview, not observed call order.

**Can it guarantee bug fixes?** No. It offers source-informed investigation and historical evidence; humans still reproduce and test fixes.

**Why Python AST?** It provides a parser shipped with Python to extract syntax symbols and imports without executing arbitrary repo code.

**Does it support all languages?** Python structurally, basic JS/TS import scanning, plus some config/doc files. True multi-language AST support with Tree-sitter is future work.

**What is the architecture?** React → FastAPI → safe importer + AST scanner → local SQLite. FastAPI also calls Groq for optional explanations and Hindsight for persistent memory.

**How do you isolate memory?** Stable per-repo IDs are hashed to form a Hindsight bank name. It works for a single-machine prototype, but isn't a replacement for user authentication and authorization.

**Is it production-ready?** Not yet. It needs authentication, secrets management, larger repo support, per-user isolation, rate limits, and security hardening.

**Most important tradeoff?** We chose one polished static code-investigation flow and authentic memory integration instead of claiming automatic code execution and arbitrary language support.

**What would you improve next?** Tree-sitter language plugins, GitHub OAuth and PR history (with consent), richer call-graph analysis, tested fix proposals, and hosted tenant isolation.

**How does it align with scoring?** Innovation (code map + debugging-history memory), real use of Hindsight, functional engineering, visible before/after UX, and practical developer workflow.
