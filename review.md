# TokenWise Codebase Review

> Implementation update, October 3, 2026: `TokenWise: Enable Automatic Context`
> configures arbitrary local Windows Python repositories, preserving unrelated
> rules, hooks, and existing context settings. Workspace launchers resolve a
> shared backend registration in extension user storage rather than assuming
> the repository lives in the TokenWise checkout. Model/environment installation
> remains a separate prerequisite; cross-platform and remote setup remain open.
>
> Implementation update, October 2, 2026: automatic Python context retrieval for
> Antigravity IDE is now implemented for `Test_project`, with a `PreInvocation`
> hook, model startup, bounded context, caching, and extension activity display.
> Live IDE testing found that the installed stable build did not invoke the hook.
> A workspace-rule command fallback now retrieves context through the agent's
> command tool. This is agent-driven, not guaranteed pre-model interception.
> See [the integration guide](docs/ANTIGRAVITY.md) for setup and verification.
> The review below describes the earlier baseline and the remaining roadmap.

## Executive summary

TokenWise is not a browser extension. It is a VS Code extension backed by a local FastAPI service. The extension collects a developer task, selected/current code, or active workspace context, sends it to the local backend, receives a pruned context bundle, estimates approximate carbon impact, and renders copyable output in a VS Code Webview.

The idea is strong and useful: developers increasingly paste too much repository context into coding agents. TokenWise tries to keep only task-relevant code, enforce a token budget, and show the approximate energy/carbon difference between raw and pruned prompts.

The current project is best described as a serious academic prototype. It has a coherent architecture, real backend code, model-loading checks, repository indexing, smoke tests, and a functional VS Code client. To become a "perfect working extension" that real users rely on, the biggest work is not only algorithm quality. The project needs easier installation, automatic backend lifecycle management, better UX defaults, multi-language support, stronger repository indexing, trustworthy metrics, packaging, and end-to-end tests.

## High-level architecture

```text
VS Code extension
  package.json commands/settings
  src/extension.ts status bar + command registration
  src/commands/* user workflows
  src/services/apiClient.ts HTTP calls
  src/services/pruneService.ts single-file prune orchestration
  src/ui/resultPanel.ts result Webview

        |
        | HTTP on localhost
        v

FastAPI backend
  src/swe_pruner/online_serving.py
  /health
  /prune
  /prune-workspace
  /estimate-carbon

        |
        v

Runtime engines
  SWE-Pruner neural model wrapper
  Python AST repository index
  import/call dependency graph
  lexical + neural candidate ranking
  tiered context builder
  trained carbon estimator artifacts
```

## How the VS Code extension works

The extension entrypoint is `vscode-extension/src/extension.ts`.

On activation, it:

1. Creates a `PruneService`.
2. Creates a `ResultPanel`.
3. Adds a `TokenWise` status bar item.
4. Registers four commands:
   - `TokenWise: Prune Selected Code`
   - `TokenWise: Prune Current File`
   - `TokenWise: Check Backend Health`
   - `TokenWise: Build Repository Context`

The extension activates on `onStartupFinished`, so it loads after VS Code startup rather than only when a TokenWise command is used. That makes the status bar visible, but it also means the extension is active even for users who may not need it in the current workspace.

## Command workflow: Check Backend Health

File: `vscode-extension/src/commands/checkHealth.ts`

The command calls `PruneService.checkHealth()`, which creates a `TokenWiseApiClient` and sends a GET request to:

```text
http://127.0.0.1:8000/health
```

The backend responds with:

- service status
- whether the neural pruner model is loaded
- whether carbon artifacts are loaded
- active device
- model path

This is a good diagnostic feature. For real users, it should become more actionable: if the backend is not running, the UI should offer "Start backend", "Open setup guide", and "Show logs".

## Command workflow: Prune Selected Code

File: `vscode-extension/src/commands/pruneSelected.ts`

Steps:

1. Reads the active editor.
2. Requires a non-empty selection.
3. Prompts the user for a task query.
4. Prompts for a pruning threshold.
5. Sends selected code to `PruneService.prune()`.
6. Opens the result panel if `tokenWise.autoOpenResultPanel` is enabled.
7. Updates the status bar carbon-savings text.

This workflow is simple and understandable. The weakness is that it asks too many questions every time. A real user will not want to manually tune a threshold on each run.

## Command workflow: Prune Current File

File: `vscode-extension/src/commands/pruneCurrentFile.ts`

This is almost the same as selected-code pruning, except it sends the full current file when there is no selection. This is useful for quick experiments and small files, but for large files it depends heavily on the backend chunking path.

The output is intentionally not applied as an edit. That is correct. The pruned result includes elision markers such as filtered-line summaries, so it is context for an AI assistant, not valid source code.

## Command workflow: Build Repository Context

File: `vscode-extension/src/commands/buildRepositoryContext.ts`

This is the most valuable feature.

Steps:

1. Requires an active editor.
2. Requires the active document to be inside an open workspace.
3. Currently requires `document.languageId === "python"`.
4. Prompts for a repository task.
5. Captures optional selected code or the symbol under cursor.
6. Collects VS Code diagnostics for the active file.
7. Sends `/prune-workspace` request with:
   - query
   - workspace root
   - active file path
   - language
   - selected code or current symbol
   - diagnostics
   - default threshold
   - optional local LLM goal settings
   - repository token budget
8. Optionally sends two `/estimate-carbon` requests for before/after token counts.
9. Shows a repository-context Webview with goal, included files, tiers, token counts, carbon impact, and a copy button.

This feature is where TokenWise can become genuinely useful. Instead of making users manually decide what to paste into an AI coding agent, it builds a bounded context bundle from the repository.

## Backend workflow: startup and health

File: `swe-pruner/swe-pruner/src/swe_pruner/online_serving.py`

At startup, the backend:

1. Resolves the model path from `SWEPRUNER_MODEL_PATH` or defaults to `swe-pruner/swe-pruner/model`.
2. Checks for required model files:
   - `config.json`
   - `model.safetensors`
   - `tokenizer.json`
   - `tokenizer_config.json`
   - `backbone/config.json`
3. Loads the pruner model if files exist.
4. Initializes the carbon estimator from local artifacts.
5. Exposes `/health`.

This is a good local-first approach. The main product issue is that the VS Code extension does not manage the backend process, so the user must run PowerShell scripts manually.

## Backend workflow: single-file pruning

Files:

- `swe-pruner/swe-pruner/src/swe_pruner/prune_wrapper.py`
- `swe-pruner/swe-pruner/src/swe_pruner/swepruner.py`

The `/prune` endpoint validates the request and calls `model.prune()`.

The pruning process:

1. Formats the task query into an instruction/query/document prompt.
2. Counts query and code tokens with the model tokenizer.
3. If the code fits inside the model context, it runs one inference pass.
4. If the code is too large, it splits code into overlapping chunks.
5. Runs the model to get:
   - document relevance score
   - token-level relevance scores
6. Aggregates token scores to source lines.
7. Keeps lines above the threshold.
8. Replaces removed spans with filtered-line markers.
9. Returns pruned code, token counts, relevance score, kept line numbers, and model input token count.

This is a defensible design for context pruning. The result is readable enough for an LLM, but not directly executable code.

## Backend workflow: repository pruning

File: `swe-pruner/swe-pruner/src/swe_pruner/online_serving.py`

The `/prune-workspace` endpoint does much more:

1. Validates model availability.
2. Rejects non-Python repository mode.
3. Validates workspace root and active file.
4. Builds a Python repository index.
5. Compiles the user's query into a structured goal.
6. Builds an import/call dependency graph.
7. Finds lexical seed files from goal identifiers.
8. Expands candidate files by up to two graph hops.
9. Splits candidates into rankable and unranked groups.
10. Uses the neural model to rank likely relevant files.
11. Packs context into a hard token budget.

The context builder uses three tiers:

- Tier 1: active file, lightly pruned.
- Tier 2: direct or high-relevance dependency, more aggressively pruned.
- Tier 3: transitive/low-relevance reference, signatures only.

This is the best part of the project. The idea is practical, explainable, and aligns with real AI coding workflows.

## Backend workflow: repository indexing

Files:

- `swe-pruner/swe-pruner/src/swe_pruner/repository/repository_index.py`
- `swe-pruner/swe-pruner/src/swe_pruner/repository/python_indexer.py`
- `swe-pruner/swe-pruner/src/swe_pruner/repository/dependency_graph.py`

The indexer walks the workspace and only includes `.py` files. It skips common directories such as `.git`, `.venv`, `node_modules`, `__pycache__`, `build`, and `dist`.

For each Python file, it extracts:

- classes
- functions
- imports
- call names

The graph then links files through:

- matching imports to repository paths
- matching called symbols to files defining those symbols

This is enough for the demo project. It will be fragile in larger Python projects because it does not fully resolve packages, relative imports, aliases, dynamic imports, method ownership, framework routing, config files, or tests as first-class context.

## Backend workflow: goal compilation

File: `swe-pruner/swe-pruner/src/swe_pruner/goal_compiler.py`

Goal compilation turns a natural-language query into a `StructuredGoal`.

There are two paths:

1. Optional local OpenAI-compatible LLM, disabled by default.
2. Deterministic fallback using keyword templates and regex identifier extraction.

The default deterministic path is a good reliability choice because TokenWise should not block on Ollama or LM Studio. But the fallback is still basic. It can miss intent, over-filter useful terms, and does not use the full repository vocabulary when validating identifiers.

## Backend workflow: carbon estimation

Files:

- `swe-pruner/swe-pruner/src/swe_pruner/carbon_estimator.py`
- `swe-pruner/swe-pruner/src/swe_pruner/carbon_model_engine.py`
- `swe-pruner/swe-pruner/carbon_artifacts/*`

The extension estimates carbon impact by comparing:

- original input token count
- pruned input token count

It holds expected output tokens constant. That means the savings mainly come from prefill/input processing, which is a fairer claim than pretending pruning always reduces the number of future agent turns.

The code correctly treats this as approximate. The project evaluation says the local carbon engine is SEAL-derived, not an exact SEAL reproduction.

For real product use, the UI must keep this wording careful: "estimated prompt-level impact", not "actual carbon saved".

## Current strengths

1. The architecture is coherent: VS Code client, local backend, model wrapper, repository retrieval, carbon estimator.
2. The backend exposes clear endpoints.
3. Health checks are practical and include model/carbon readiness.
4. The extension avoids unsafe source edits.
5. Repository mode has a hard token budget.
6. Local LLM goal generation is optional, not mandatory.
7. The setup, verify, run, and smoke-test scripts are useful for repeatable demos.
8. Python repository mode has a reasonable first implementation using AST extraction.
9. The carbon feature is integrated into both single-file and repository workflows.
10. The result panel is copy-focused, which matches how developers use coding agents today.

## Current blockers for real users

### 1. Installation is too heavy

Users must install Python 3.12, Node/npm, run setup scripts, copy `model.safetensors`, start the backend, then run the VS Code extension. That is acceptable for an academic submission, but not for a marketplace extension.

Real users expect one of these:

- install extension and let it download/manage the backend
- use an already packaged backend binary
- connect to a hosted/private backend
- use a lightweight model path with clear automatic setup

### 2. Backend lifecycle is manual

The extension does not start, stop, restart, or monitor the backend. If the backend is not running, commands fail.

For a useful extension, VS Code should:

- detect backend status
- start the backend automatically
- show backend logs
- restart after crashes
- expose model-loading progress
- guide users through missing dependency/model states

### 3. The model weight problem is unresolved

The README says `model.safetensors` is intentionally excluded. That may be necessary for ZIP size, but it blocks normal usage.

A production path needs:

- documented model license
- automatic download or first-run installer
- checksum verification
- clear storage location
- fallback lightweight mode
- CPU performance expectations

### 4. Repository mode is Python-only

Python-only support is okay if TokenWise is marketed as a Python extension. But most VS Code AI-coding users work with TypeScript, JavaScript, Python, Java, Go, C#, and mixed repositories.

To become broadly useful, add at least:

- TypeScript/JavaScript parser support
- package/import graph support
- test file discovery
- framework entrypoint discovery
- config file inclusion

### 5. Threshold tuning is exposed too early

Manual thresholds make the extension feel like a research tool. Users care about outcomes:

- "compact"
- "balanced"
- "thorough"
- target token budget
- active-file priority

The threshold can remain as an advanced setting, but routine commands should not ask for it every time.

### 6. The UI is useful but not yet workflow-native

The Webview shows useful data, but it does not yet integrate deeply with AI tools.

High-value integrations would be:

- copy as Markdown context
- copy as prompt with task and files
- send to GitHub Copilot Chat context if API allows
- save context bundle to `.tokenwise/context.md`
- compare multiple pruning runs
- rerun with compact/balanced/thorough modes
- include/exclude files from the panel

### 7. Indexing is rebuilt per request

The backend builds the repository index every `/prune-workspace` call. That is simple but may become slow on real repositories.

Production behavior should include:

- persistent workspace index
- incremental updates on file change
- cache invalidation
- max file size limits
- binary/generated/vendor file exclusion
- progress reporting

### 8. Error messages need product polish

Many errors are technically correct but not user-actionable. For example, backend unavailable, missing model, unsupported GPU, or carbon artifact failure should tell the user exactly what to do next.

### 9. Packaging is not marketplace-ready

The extension has no complete marketplace packaging workflow. It needs:

- `vsce` packaging
- extension icon
- screenshots/GIFs
- activation strategy review
- license review for model/assets
- privacy statement
- telemetry policy
- changelog
- release notes

### 10. Trust and privacy need to be explicit

The local-first story is a strength. The extension should clearly state:

- code stays on `127.0.0.1` by default
- optional local LLM endpoint only runs when enabled
- no cloud calls are made unless explicitly configured
- what data is sent to the backend
- where model files and caches are stored

## Recommended product direction

The best version of TokenWise is:

> A local-first VS Code extension that builds small, task-focused context bundles from a repository so developers can paste or send better context to AI coding tools, while showing approximate token and prompt-energy impact.

Do not position it primarily as a carbon calculator. The carbon feature is a valuable differentiator, but the daily user value is better AI context with less manual copying.

## Roadmap to make it genuinely useful

### Phase 1: Make the existing Python workflow smooth

Priority: highest.

1. Add automatic backend management from the extension.
2. Add a first-run setup wizard.
3. Replace per-run threshold prompt with presets:
   - Compact
   - Balanced
   - Thorough
4. Keep threshold only in settings.
5. Add a "TokenWise: Build Context for Current Task" command as the main command.
6. Add actionable error recovery:
   - backend not running
   - model missing
   - Python missing
   - carbon artifacts missing
7. Add a log output channel in VS Code.
8. Add cancellation support for long backend calls.
9. Add result actions:
   - Copy unified context
   - Copy as AI prompt
   - Save context file
   - Re-run compact/balanced/thorough
10. Fix encoding artifacts in README/docs/UI strings.

This phase would make the extension feel usable even if it remains Python-only.

### Phase 2: Make repository context smarter

Priority: high.

1. Cache repository indexes between requests.
2. Watch file changes and update the index incrementally.
3. Improve Python import resolution:
   - relative imports
   - aliases
   - `__init__.py`
   - package roots
   - common framework patterns
4. Include non-code files when relevant:
   - `pyproject.toml`
   - `requirements.txt`
   - `.env.example`
   - config files
   - README sections
5. Treat tests as first-class:
   - nearest tests
   - failing diagnostics
   - test naming conventions
6. Let users pin files to always include.
7. Let users exclude files directly from the result panel.
8. Add a repository-size safety model:
   - file count limits
   - file size limits
   - ignored folder settings

This phase improves correctness in real Python repositories.

### Phase 3: Add TypeScript and JavaScript support

Priority: high if targeting general VS Code users.

Minimum useful support:

1. Parse TypeScript/JavaScript with Tree-sitter or the TypeScript compiler API.
2. Extract:
   - exports
   - imports
   - functions
   - classes
   - React components
   - route handlers
3. Resolve common project structures:
   - `src/*`
   - path aliases from `tsconfig.json`
   - package exports
   - Next.js app/pages routes
   - Vite/React entrypoints
4. Include related files:
   - tests
   - schemas
   - API routes
   - components
   - hooks
   - package scripts

This would dramatically expand the audience.

### Phase 4: Make output directly useful with AI tools

Priority: medium-high.

1. Add prompt templates:
   - "Debug this"
   - "Explain this flow"
   - "Write tests"
   - "Refactor safely"
   - "Implement feature"
2. Add a context bundle format:

```markdown
# Task
...

# Repository Context
...

# Included Files
...

# Notes
TokenWise pruned this context. Elisions are marked.
```

3. Add one-click copy formats:
   - Markdown
   - XML-style file tags
   - plain code blocks
4. Add "why included" explanations per file.
5. Add file-level confidence indicators.
6. Add context diff between runs.

The extension should not just produce less text; it should produce context that AI coding assistants consume well.

### Phase 5: Verification and quality gates

Priority: high before public release.

Add automated tests for:

1. VS Code command behavior.
2. API client failures and timeouts.
3. Webview message handling.
4. Backend startup without model.
5. Backend startup with model.
6. `/prune` request validation.
7. `/prune-workspace` path traversal protection.
8. Python indexer edge cases.
9. Dependency graph resolution.
10. Token budget enforcement.
11. Carbon estimator failure behavior.
12. End-to-end extension plus backend smoke test.

Also add benchmark-style evaluations:

1. Does pruned context preserve answerability?
2. Does it reduce tokens consistently?
3. How often does it remove required code?
4. How long does it take on real repositories?
5. CPU vs GPU performance.
6. Memory usage.

Without these metrics, it will be difficult to prove usefulness beyond demos.

## Concrete code improvements

### Extension

1. Change activation from only `onStartupFinished` to command-based activation plus status behavior if needed.
2. Add an output channel:

```text
TokenWise
```

Use it for backend command, logs, errors, and setup diagnostics.

3. Add backend process manager using `child_process.spawn`.
4. Add a `TokenWise: Start Backend` command.
5. Add a `TokenWise: Stop Backend` command.
6. Add a `TokenWise: Open Logs` command.
7. Add cancellation with `AbortController` wired to VS Code progress cancellation.
8. Replace threshold prompt with a quick pick:

```text
Compact   lower token count
Balanced  default
Thorough  preserve more context
```

9. Save the last query per workspace.
10. Add workspace settings for ignored folders and always-include globs.

### Backend

1. Add a workspace index cache keyed by root path and file mtimes.
2. Add request IDs to logs and responses.
3. Add structured error responses with remediation hints.
4. Add `/version` endpoint.
5. Add `/workspace/index` endpoint for prewarming.
6. Add `/workspace/status` endpoint.
7. Add max file size and max repository file count settings.
8. Improve import resolution for Python packages.
9. Add parser interface so Python and TypeScript can share retrieval/ranking/packing.
10. Return "why included" metadata per file:

```json
{
  "file_path": "...",
  "reason": "active file | imports active file | defines identifier X | called by Y",
  "tier": 1,
  "score": 0.83
}
```

### Result panel

1. Add run settings summary.
2. Add copy dropdown:
   - Copy unified context
   - Copy prompt + context
   - Copy file list
3. Add include/exclude toggles per file.
4. Add "rerun" buttons for compact/balanced/thorough.
5. Add warnings when:
   - active file was heavily truncated
   - carbon estimation unavailable
   - model not loaded
   - repository indexing skipped many files

## Suggested MVP for public release

The smallest public release I would trust should include:

1. Python repository support only, stated clearly.
2. One-command setup or first-run wizard.
3. Automatic backend start/stop.
4. Main command: `TokenWise: Build AI Context`.
5. No threshold prompt in normal flow.
6. Copyable Markdown context bundle.
7. Clear local-only privacy promise.
8. Health/status panel.
9. Marketplace-ready README with screenshots.
10. End-to-end smoke test documented and passing.

## Suggested positioning

Good positioning:

> TokenWise builds task-focused AI coding context from your local repository. It prunes irrelevant code, respects a token budget, and estimates prompt-level token and carbon impact.

Avoid overclaiming:

- Do not claim exact real-world carbon savings.
- Do not claim full language support while repository mode is Python-only.
- Do not claim pruned output is executable code.
- Do not claim it replaces AI coding assistants.

## Final assessment

TokenWise already has the core of a useful tool. The research idea is sound, the VS Code integration exists, and the backend pipeline is more complete than a simple mockup. The main gap is productization.

To make someone really use it, focus on reducing friction:

1. Make setup automatic.
2. Make backend management invisible.
3. Make the default command produce a high-quality AI-ready context bundle.
4. Expand repository understanding beyond the demo.
5. Be honest and careful with carbon claims.

If those pieces are handled, TokenWise could become a genuinely useful local-first context optimizer for AI-assisted development.
