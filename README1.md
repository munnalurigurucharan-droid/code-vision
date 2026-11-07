# CodeVision AI — 3-minute demo video script

**Presenter:** [PRESENTER NAME] · **Team:** [TEAM NAME] · **Target:** 3:20 · **Record:** 1920×1080 screen + clear voiceover

**BEFORE RECORDING:** Builder has launched frontend `localhost:5173` and backend `localhost:8000`, loaded DemoAuth, verified real Hindsight retain/recall, and (optionally) Groq. Hide API keys, desktop notifications, private browser tabs, and `.env`. The demo uses an intentionally flawed **synthetic** auth module. If live memory does not work, do **not** say it did: show the configuration blocker and fix it before shooting the final video.

## 0:00–0:25 — The problem

**Screen:** CodeVision landing page.

**Say:** “Hi, I'm [NAME]. When developers open someone else's repository, they spend time figuring out which files matter and repeating debugging work that somebody already solved. CodeVision helps you map a codebase, investigate an error, and remember the outcome for next time.”

## 0:25–1:00 — Import and architecture

**Screen:** Click **Explore interactive demo**. Show overview counters, architecture card, then Architecture tab and click `src/api.py → src/auth.py` if visible.

**Say:** “This sample service has several Python modules. CodeVision scans the files without running their code. It finds probable entry points and builds a dependency map from imports. This gives us a starting point, not a claim to have traced the complete runtime.”

## 1:00–1:30 — Find the bug in code

**Screen:** Code Explorer → `src/auth.py`; briefly highlight `token.startswith(EXPECTED_TOKEN)`.

**Say:** “Here’s the error we’ll investigate. The code accepts a token whenever it starts with the expected value. That means an invalid token with an added suffix can slip through. The demo intentionally contains this bug. We can inspect both the function and its dependencies.”

## 1:30–1:55 — Baseline without memory

**Screen:** AI Investigator. Use exact text:

`Why does the authentication API accept demo-secret-evil as a valid token?`

Toggle memory **off**, click **Run without memory**. Record the response.

**Say:** “With memory off, the agent can only reason from the code we have indexed. It doesn't get the team's previous fix history. In static-only mode, it reports structural observations; if we enabled Groq, it can also generate a code-grounded explanation.”

## 1:55–2:25 — Save a real memory

**Screen:** Agent memory → **Retain sample fix**. Show success notification with bank ID. Do not edit the output.

**Say:** “Now I store a previous incident: the symptom, the root cause, the proposed fix, and which attempts did not help. This request uses Hindsight's real Retain API, scoped to this repository. It creates a memory we can retrieve later.”

## 2:25–3:00 — The same bug, now with history

**Screen:** Return to AI Investigator. Same question, memory **on**, click Investigate. Zoom to Hindsight evidence card. Optionally show Reflect tab (if available).

**Say:** “I repeat exactly the same question. Now CodeVision recalls the earlier resolution from Hindsight. Instead of repeating trial and error, we have the previous root cause, a proposed correction using full comparison, and the attempts that failed. Memory adds context, but we still verify whether the current issue really has the same cause.”

## 3:00–3:20 — Close

**Screen:** Overview or memory evidence, with project name and bank source visible.

**Say:** “That is the idea behind CodeVision: understand the source, trace its static relationships, and retain debugging knowledge across sessions. Our next steps are better language support and repository integrations. Thanks.”

## 20-second backup if judges interrupt

“CodeVision analyzes a repo with Python AST, maps imports with Mermaid, and investigates issues with optional Groq. Hindsight is the actual long-term memory layer: Retain stores an incident; Recall finds the old fix when a similar symptom appears; Reflect summarizes patterns. We show the same auth error before and after memory.”

## Capture checklist

- 1080p or better, **screen recording** (OBS, Loom or QuickTime), not a phone filming the monitor.
- Talking head optional. Increase editor font; hide keys and notifications.
- Show **same exact question** for before/after.
- Show an actual successful **Hindsight Retain → Recall**; if unavailable, report blocker honestly and resolve before submission.
- Explain that demo data is intentionally synthetic; do not claim customer deployment.
- Suggested title: **“My AI Code Reviewer Remembers Bugs We Already Fixed”**.
- Thumbnail prompt: `Create a 16:9 YouTube thumbnail with a dark code editor background, large text "IT REMEMBERED THE BUG", a bright green memory graph, a clean code snippet highlight on startswith(), and a confident developer portrait supplied separately. No fake endorsements or logos.`
