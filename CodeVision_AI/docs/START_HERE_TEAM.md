# CodeVision AI — 3-person team handoff

## Responsibilities

| Person | Owner | Responsibility | Deliverable |
|---|---|---|---|
| 1 | Builder (you) | Run app, configure real Hindsight/Groq credentials, validate demo and code, make GitHub repo public, capture evidence | Working app, public repo URL, screenshots, live checklist |
| 2 | Presenter (friend) | Practice script, record voice + 1080p screen demo, explain before/after and field judge questions | One **public** 2–5 minute YouTube video |
| 3 | Publishing lead (friend) | Coordinate three distinct technical articles, LinkedIn posts, article Reddit share, YouTube upload/thumbnail and final links | All published public URLs, final submission form |

**Content requirement:** Each team member must have their own article + social post; **one** team video is sufficient according to the Content Submission Guide. The publisher can coordinate/edit, but each member should review their own authored account content before posting.

## Sequence — do not skip live proof

1. Builder: extract ZIP, install requirements and npm packages, start frontend + backend.
2. Builder: open `.env` and connect **Hindsight Cloud API key**. Optional Groq key for narrative investigation. Restart backend.
3. Builder: load synthetic demo, inspect `src/auth.py`, run baseline question with memory off.
4. Builder: Agent Memory → click **Retain sample fix**. Verify success; if an error appears, resolve it before continuing.
5. Builder: repeat question with memory ON; verify **memory_status=recalled** and a real evidence card. Try Reflect. Reload page to test persistence.
6. Presenter: use `VIDEO_SCRIPT.md`; show actual screen, not fabricated screenshots. Record 1920×1080 or higher. Edit to 2–5 minutes.
7. Publishing lead: use `content/ARTICLE_*.md`, `content/LINKEDIN_*.md`; personalize and verify each claim; replace screenshot markers, insert real public repo URL and live results, publish.
8. Publishing lead: publish a link post on one of the recommended Reddit communities; create a 16:9 YouTube thumbnail, upload team video publicly, collect URLs.
9. Team: install/use Band AI desktop as required by the problem statement. Practice 60-second live demo and validate the official submission link fields.

## Rules that can disqualify your content

- Articles and LinkedIn posts **must not mention the event type or name**, including in titles, bodies or hashtags.
- Article must be public, not just a Google Drive/Docs link. Video must be public on YouTube, not only Drive.
- Do not claim Hindsight worked unless it actually returned saved memory.
- All content should be in English; include Hindsight links in articles, the project GitHub URL in the main LinkedIn post, and Hindsight GitHub as a LinkedIn comment.
- The guide lists an **800–1,500-word** article headline requirement and a more ambitious **1,200–2,000-word** draft prompt. Drafts in `content/` aim at ~900–1,200 words to satisfy the headline range. Check platform word counts.
- Tag Code.in in the articles and LinkedIn posts as requested in the guide where the platform allows it.

## Do we need Google Drive?

No mandatory Drive folder was specified. Optionally create a folder `CodeVision_AI_Final_Submission` containing screenshots, raw video backup, slides (if any), and `docs/SUBMISSION_LINKS.md`. **Public links remain the actual deliverables.**
