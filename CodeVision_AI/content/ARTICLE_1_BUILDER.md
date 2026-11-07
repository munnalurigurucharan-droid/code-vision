# Why I Made Hindsight Remember Our Debugging Decisions

Opening an unfamiliar repository is rarely the hard part of a developer's day. The hard part is discovering why code looks the way it does, and then learning that someone on the team already spent an afternoon ruling out the same hypothesis you are about to try.

I started building CodeVision AI to address both sides of that problem. The first is structural: how do I get a useful picture of a codebase without running it? The second is historical: how do I stop the project from losing the reasoning behind bug fixes? I found that these are separate problems, and trying to solve them with a single chatbot prompt hides an important design decision.

## First, understand what is in the repository

CodeVision accepts a ZIP upload or a public GitHub repository link. The backend checks the source archive size, skips common dependency folders, filters known secret-file names, and limits the number and size of files it will inspect. We do not install or execute untrusted source code just to learn what its components are.

For Python projects, I use the standard library `ast` module. It lets me identify functions, classes, imports, and likely entry points while treating source files as text. JavaScript and TypeScript get more limited import scanning; that is an explicit scope boundary rather than a claim of complete multi-language understanding.

The core parsing idea is small:

```python
import ast

tree = ast.parse(source_text, filename=path)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        imported = [alias.name for alias in node.names]
    elif isinstance(node, ast.FunctionDef):
        function_name = node.name
```

This gives the application symbols and dependency candidates. Import names can be resolved against the uploaded file list, producing edges such as `src/api.py → src/auth.py`. Those edges become a Mermaid diagram in the React interface. It is a useful *static map*, not a runtime trace; imports do not tell us every function that executes.

I deliberately kept that distinction visible in the UI. A chart is persuasive, which makes it easy to overstate what it proves. When a developer asks where execution starts, CodeVision shows likely entry points and says that dynamic tracing would be required to confirm the actual order.

## The missing dimension is project history

A parser can tell us that an authentication function uses `startswith()`. It cannot tell us that the team already tried restarting the service, changing expiry settings, and testing a cache hypothesis before finding the actual cause. That history is usually scattered across chat messages or forgotten altogether.

This is where [Hindsight's persistent agent memory](https://github.com/vectorize-io/hindsight) matters. CodeVision uses one memory bank per repository identity. When someone records an incident, they enter the symptom, the root cause, a fix or proposed fix, and any failed attempts. The backend then calls the official Hindsight client to store that history.

The critical integration is intentionally direct:

```python
await client.aretain(
    bank_id=repo_bank,
    content=incident_narrative,
)
```

Later, a developer asks a similar question. We first retrieve historical evidence before passing the relevant context into the investigation workflow:

```python
result = await client.arecall(
    bank_id=repo_bank,
    query=developer_question,
)
```

The memory is not hidden inside a magic prompt. It is a separate layer with a separate API. We can enable or disable memory retrieval and observe what changed. The same Hindsight integration also supports Reflect, which can synthesize themes across a history of incidents. The [Hindsight documentation](https://hindsight.vectorize.io/) describes these retain, recall, and reflect operations in more detail.

## A concrete failure that makes the difference visible

For a repeatable example, we include an intentionally flawed synthetic authentication service. Its authorization check contains this line:

```python
return token.startswith(EXPECTED_TOKEN)
```

That code can accept `demo-secret-evil` when the expected token is `demo-secret`, because prefix matching is not exact token validation. Our repository explorer identifies the file and its imports. A developer can inspect the mistake directly without the application claiming to have reproduced a real customer incident.

The historical incident record adds something distinct. It says that the previous suspected causes did not help and proposes comparing the entire token with `hmac.compare_digest()`. The point is not that a memory system discovers a bug that static source analysis could never notice. The point is that the memory carries *what the team has already learned* and can bring that evidence into a later investigation.

We designed the UI to make this difference demonstrable. Ask the same question with memory off; save the incident through a real Retain call; ask again with memory on; inspect the Recall evidence. A configured Hindsight account is required for that flow. Without it, CodeVision explicitly reports that memory is unavailable. The local project database is never allowed to impersonate a successful cloud memory retrieval.

[SCREENSHOT TO INSERT: CodeVision architecture graph]

[SCREENSHOT TO INSERT: Before/after same question with genuine Hindsight Recall evidence]

## Why the split architecture matters

React handles the code explorer, diagram and memory controls. FastAPI handles uploads, static inspection, and the external integrations. SQLite keeps local project snapshots and an audit record after a retain request succeeds. Groq is optional; without an LLM key, the application can still present deterministic structural observations.

That separation avoids a subtle trap. When an AI provider is unavailable, the app can still show files, imports, and symbols. When Hindsight is unavailable, it must not invent memories. And when a model suggests a fix, the response needs to distinguish a source observation from a hypothesis that still requires testing.

There are practical limits. The current MVP is not a full program analyzer, it does not run test suites on imported code, and it should not be opened as an unauthenticated multi-user service. Uploading proprietary code to an external model also needs permission and a privacy review. These boundaries are more useful to document than to conceal.

## What I learned

First, retrieval becomes meaningful when memory contains decisions and outcomes, not just chat transcripts. A failed approach is often as valuable as a successful one.

Second, static architecture views reduce the time spent finding relevant code, but they should not claim to show exact execution order.

Third, a clear memory toggle is an excellent debugging instrument. If a historical note does not add useful context, the team should improve its memory capture and retrieval quality, not simply declare success.

Fourth, persistent context is valuable only when its provenance remains clear. We label stored notes as developer-reported history, not automatic proof that a future incident shares the same cause.

The broader lesson is the distinction between understanding code and understanding a team's experience with that code. CodeVision aims to combine the two. For a concise introduction to the memory problem itself, the [Vectorize guide to agent memory](https://vectorize.io/what-is-agent-memory) is useful background.

**Project source:** [INSERT PUBLIC CODEVISION GITHUB URL]

*Before publishing: replace both screenshot placeholders with genuine captures, verify the live Retain/Recall claims on your account, add your own observations, and tag Code.in where supported.*
