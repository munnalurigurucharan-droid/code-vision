# What Hindsight Adds to a Static Repository Map

Developers have no shortage of ways to visualize code. Import graphs, call graphs, symbol indexes, and editor navigation all help answer where a function lives. The harder question is what happened when someone changed it last month and why the team decided on that approach.

CodeVision AI explores the overlap between code structure and debugging history. Instead of pretending a language model inherently remembers everything, it combines a static repository map with an explicit persistent memory layer. The design is intentionally narrower than “an AI engineer that can do anything.” It aims to make one recurring workflow less frustrating: understanding a codebase and avoiding the same debugging dead ends.

## Why a code map alone is incomplete

Consider a typical software onboarding task. A new engineer receives a repository and needs to learn which file starts the server, which module validates requests, and where configuration is read. A static analyzer can often help without needing any AI text generation.

CodeVision's FastAPI backend accepts a ZIP or a public GitHub URL and inspects source safely as data. It has limits on archive size and extracted source. It skips common dependency directories and known sensitive filenames. It does not run code from the uploaded repository.

Python files are parsed with the standard `ast` module. The scan collects imported modules, function names, class names and likely entry points. A resolver matches imported module names to the files present in the archive. The result is a set of source-to-target edges.

```python
for imported in parsed_imports:
    target = resolve_to_local_file(imported, known_paths)
    if target:
        dependency_edges.add((source_path, target))
```

The snippet above summarizes the resolution logic in plain pseudocode. The implementation lives in `backend/app/analysis.py`. CodeVision then creates a Mermaid diagram using file IDs and edge relationships. The result answers, for example, that `src/api.py` imports `src/auth.py`, which imports `src/config.py`.

This is useful, but incomplete. An import does not prove that an imported function was called on a particular request. The UI therefore calls the result an architecture map and labels the execution flow as heuristic. We deliberately do not call the diagram a profiler or dynamic execution trace.

## The other half: decisions, not just dependencies

Imagine that the team once fixed an authorization problem. Someone suggested changing an expiry value, someone restarted the server, and a third person found the actual bug in string comparison. The final change may appear in a commit, but the failed hypotheses might never be captured anywhere searchable.

CodeVision provides a small resolution form for that missing history. A developer can save the original symptom, the identified cause, the applied or proposed fix, and the experiments that did not help. Those fields form a narrative that is sent to [Hindsight's memory service](https://github.com/vectorize-io/hindsight).

The code follows a simple separation:

```python
await hindsight.aretain(
    bank_id=repository_bank,
    content=incident_report,
)
```

A later investigation retrieves related experiences:

```python
historical = await hindsight.arecall(
    bank_id=repository_bank,
    query=developer_question,
)
```

This is persistent *project* memory, not a general chatbot's current context window. By using a bank associated with a repository, the application can connect a new question with previous reported incidents for that codebase. The [Hindsight documentation](https://hindsight.vectorize.io/) also describes Reflect, which synthesizes higher-level lessons from stored experiences.

## A controlled example: one character sequence, two meanings

The included sample repository has a deliberately incorrect token check:

```python
return token.startswith(EXPECTED_TOKEN)
```

If the expected string is `demo-secret`, a user might provide `demo-secret-evil` and still pass this check. Prefix matching is the wrong primitive for exact authorization. A full comparison using `hmac.compare_digest()` is the proposed correction in the sample, paired with additional regression tests.

Without memory, CodeVision can show the suspicious line and explain the file relationships. With a real retained historical record, Hindsight can return the previous explanation of why the bug occurred, which fix was proposed, and which earlier attempts were irrelevant. This is a much stronger story than simply saying the assistant is “personalized.” It highlights a concrete addition to the available evidence.

Importantly, history is not ground truth. A similar symptom can result from different faults. Recalled information should shorten investigation time, not replace verification. CodeVision's investigation prompt tells the optional Groq model to distinguish source observations, historical statements and hypotheses.

[SCREENSHOT TO INSERT: architecture map and code explorer]

[SCREENSHOT TO INSERT: before/after same-question comparison with live Hindsight evidence]

## Why I think this architecture is worth sharing

The interface is built in React with Mermaid for diagrams. FastAPI controls inputs and route validation. SQLite stores snapshots of imported analyses and a log of successful memory saves. Optional Groq calls generate explanations from selected code excerpts, but there is a deterministic structural fallback if an LLM is unavailable.

The Hindsight connection remains separate. It is responsible for real historical storage and retrieval; SQLite never produces invented Hindsight recall messages. This may sound like a small implementation detail, but it becomes critical during demonstrations and production debugging. A system that silently fakes a backend success makes it difficult to know which part of the product actually works.

There are obvious extensions: language-aware Tree-sitter parsing, GitHub pull request and issue integration, a validated test runner inside a restricted sandbox, and more sophisticated history evaluation. None of those should be confused with what the current version implements. The current project focuses on honest static context and explicit retained incident history.

## Lessons worth carrying into other tools

The first lesson is to keep different kinds of knowledge separate. Code structure, user-reported incident history and model-generated explanations should not all be presented as equally verified facts.

The second lesson is to choose a before/after scenario with one controlled variable. Turning historical retrieval on while keeping the question constant makes it easier to explain memory's contribution.

The third lesson is that failed attempts deserve first-class storage. They help future engineers avoid repeating expensive work and provide useful context when an apparent regression returns.

The fourth lesson is to be precise about security. Uploading someone else's repository, storing history, and sending excerpts to an external LLM all have data-handling implications. A local-first prototype is appropriate for exploration, but a public multi-user service would require authentication, isolation and permission checks.

Persistent memory is most meaningful when it preserves *why* a team learned something, not just *what* code exists today. That distinction is central to CodeVision's approach and to the broader [idea of agent memory](https://vectorize.io/what-is-agent-memory).

**Project source:** [INSERT PUBLIC CODEVISION GITHUB URL]

*Before publishing: replace placeholders with true results, include actual UI captures and your own editorial observations, and tag Code.in where supported.*
