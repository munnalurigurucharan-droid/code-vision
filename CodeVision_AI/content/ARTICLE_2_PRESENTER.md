# How Hindsight Changed My Authentication Bug Walkthrough

A bug explanation can be technically correct and still waste the developer's time. If it repeats ideas that the team rejected last week, it has forgotten half the problem.

When I prepared a walkthrough of CodeVision AI, I wanted to avoid the usual sequence of features: upload, click, click, click, done. A more useful story begins with one unexpected symptom and asks a simple question: what can a code-aware assistant know today, and what can it learn from the previous debugging session?

We used a deliberately flawed authentication example so that every part of the explanation can be inspected. The scenario is synthetic, not an incident borrowed from a real service. That matters because a controlled example lets an audience understand the cause rather than relying on unexplained screenshots.

## The symptom: a token that should fail does not

The sample application is small. `src/api.py` exposes a private endpoint. It gets an authorization value and delegates the decision to `src/auth.py`. The authorization helper is supposed to verify that the supplied token matches the expected token exactly.

Here is the intentionally incorrect implementation:

```python
def authorize(token: str) -> bool:
    return token.startswith(EXPECTED_TOKEN)
```

Suppose `EXPECTED_TOKEN` is `demo-secret`. Passing `demo-secret-evil` will return true. `startswith()` checks whether the input begins with a given prefix; it does not check equality. The logic is a bug even though the code looks superficially reasonable at a glance.

A corrected approach for a full token comparison is:

```python
import hmac

def strict_authorize(token: str) -> bool:
    return hmac.compare_digest(token, EXPECTED_TOKEN)
```

The full authentication design would need additional consideration in a production service, but this change is enough to communicate the error in the sample. A complete fix also needs regression tests for correct, malformed, suffixed, and missing token values.

## Before memory: understand the current code

The first CodeVision view is not a chatbot. It is a file explorer and a map. The Python backend uses `ast.parse()` to identify definitions and imports, then resolves internal file references. Mermaid presents those file relationships in the browser.

For this example, the API file imports the authorization module. The authorization module imports configuration. In the code explorer, the presenter can choose `src/auth.py` and see the exact line that needs attention.

Next, I ask:

> Why does the authentication API accept demo-secret-evil as a valid token?

With the Hindsight toggle off, the assistant is limited to current source evidence. Optional Groq integration can produce a source-grounded explanation; if Groq is not configured, CodeVision returns a structural summary instead. Either way, the baseline does not pretend that a historical investigation exists.

This matters because it gives us a fair comparison. To evaluate whether memory helps, we need the same repository and the same question. If those conditions change, an improved response might be caused by something other than memory.

## Retain: make the debugging experience reusable

Once we have described the issue, the memory view lets us record a structured outcome. The input includes the symptom, root cause, reported fix, and failed experiments. The backend formats those fields into an incident narrative associated with the current repository.

Then it makes a real Hindsight API request:

```python
await memory.retain(project_id, incident_narrative)
```

CodeVision uses a stable project identifier to choose a per-repository Hindsight memory bank. It logs a resolution locally only after the Hindsight Retain request succeeds. If the API key is absent or the server rejects the request, the UI displays an error rather than showing a fake success state.

A user-friendly demonstration should show the Retain success message and, ideally, the bank identifier or the successful API response. The [Hindsight GitHub project](https://github.com/vectorize-io/hindsight) includes the memory server and client ecosystem behind these calls.

[SCREENSHOT TO INSERT: successful real retain response or notification]

## Recall: ask again, without changing the question

Now I return to the exact same question and turn historical memory on. The backend calls Hindsight Recall with the project-specific bank and the question. Matching records are returned as evidence; if Groq is configured, the application can use those records alongside source excerpts to draft an investigation.

```python
history = await memory.recall(project_id, question)
answer = await investigate(project, question, history, settings)
```

This is where the interesting distinction appears. The code in `src/auth.py` has not changed. The question has not changed. What changed is that the assistant can now consult the previous resolution note: a prefix comparison was the root cause, and earlier unrelated approaches did not address it.

Historical evidence is not the same thing as certainty. If a second authentication failure has a different root cause, blindly applying the old fix would be a mistake. A responsible assistant should suggest checking whether the symptoms and code paths still match. We designed CodeVision's prompt around that separation of observed source facts, reported history, and unverified hypotheses.

[SCREENSHOT TO INSERT: same question with genuine Hindsight recall evidence]

## Reflect: what can the system learn across incidents?

Retain stores experience. Recall retrieves related experience. The third operation, Reflect, asks Hindsight to synthesize insights from the memory bank. The [official Hindsight documentation](https://hindsight.vectorize.io/) explains how that synthesis differs from returning raw memories.

For the sample walkthrough, a reflection question might be: “What did we learn about token validation and failed approaches?” With only one retained incident, the answer should not claim a statistically proven team-wide pattern. With many real incidents, reflection can become more interesting: repeated configuration mistakes, recurring regressions, or approaches that often fail.

This is one reason I like the concept for software engineering teams. A postmortem is useful when someone reads it. A searchable memory layer makes it more likely that past lessons show up at the moment they matter.

## The boundaries we decided to show

CodeVision does not run imported repositories. Its execution overview is heuristic, not a trace recorded from a running process. JavaScript and TypeScript support is limited to basic import scanning. There is no automatic patch application, and private customer code should not be uploaded without consent.

We also distinguish the live Hindsight service from the local sample. Loading the sample does not mean we have successfully stored a memory. The presenter must demonstrate a real Retain and Recall interaction with an actual configured service. Without that proof, the correct statement is that the integration code is present but the live end-to-end scenario remains unverified.

## What makes a clear demonstration

I learned four things while preparing the walkthrough. One, choose a bug the audience can understand in seconds. Two, display the code instead of asking people to trust a model's summary. Three, keep the question identical across the before/after comparison. Four, show memory provenance and state limitations honestly.

A feature demo can show many buttons. A good engineering explanation shows an effect and how it was produced. That is the story behind CodeVision: code context helps identify a candidate cause, while Hindsight helps preserve the team's earlier reasoning. The [Vectorize overview of agent memory](https://vectorize.io/what-is-agent-memory) provides additional context for this design.

**Project source:** [INSERT PUBLIC CODEVISION GITHUB URL]

*Before publishing: personalize the narrative, add two genuine screenshots, link your actual video if available, and tag Code.in where supported.*
