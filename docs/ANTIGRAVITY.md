# Automatic Context in Antigravity

Open `Test_project` as the workspace in **Antigravity IDE** and send a normal
coding prompt. TokenWise discovers relevant Python files, ranks and prunes them,
and returns bounded repository context. No editor selection, manual pruning
command, or copy/paste is required.

There are two integration paths:

- **Native hook:** a supported IDE invokes `PreInvocation`, and TokenWise injects
  context before that model call.
- **Stable-IDE fallback:** the always-on workspace rule instructs the agent to
  run a local context command before inspecting repository code or answering.
  The bounded context reaches the model as command-tool output. This is
  agent-driven retrieval, not interception before the first model call.

Live testing on this machine found that the installed stable IDE did not invoke
the configured native hook: both demo prompts appeared in its real transcript
without TokenWise context. Its installed hook-management UI is gated behind
development/insider mode. The fallback does not require that UI or an MCP server.

## Try the Demo

1. Install the packaged `vscode-extension/tokenwise-vscode-0.2.0.vsix` in
   Antigravity IDE. This development session already installed it on this machine.
2. Reload the Antigravity window after installation, then open `Test_project`.
3. In **Customizations > Rules**, confirm the project `tokenwise.md` rule is
   listed. You do not need a Hooks tab for the fallback. On builds that expose
   **Customizations > Hooks**, keep `tokenwise-automatic-context` enabled too.
4. Start a new conversation and send:

   > Explain the payment retry logic and its related tests. Do not modify any files.

TokenWise starts its local backend automatically when needed. The first prompt
also loads the model, so it takes longer than later requests. The extension's
status bar shows retrieval progress, followed by the file count and packed token
count. A **TokenWise Repository Context** panel opens beside the editor without
taking keyboard focus. It contains the selected files and the actual supplied
context. On the fallback path, you should see the agent invoke
`.agents/tokenwise-context.ps1` through its command tool. Approve it if the IDE's
permission policy requests approval. The rule asks Antigravity to acknowledge
TokenWise only when it actually receives current context.

A second useful prompt is:

> Explain account lockout after failed login attempts and the related tests. Do not modify any files.

Check a **new timestamp and matching query** in `.tokenwise/latest.json`:
`status` should be `ready`, `verification` should be `false`, and `transport`
should be `antigravity-agent-command` for the fallback or `antigravity-hook`
for a native invocation. Also check that the agent's actual tool output or
conversation contains `[TokenWise automatic context]`. A status bar or saved
report alone proves only context preparation, not model consumption.

On window startup, historical activity is labeled **TokenWise last result**.
Verifier output is labeled **TokenWise test** and does not automatically open
a live context panel. Neither label means your current prompt ran TokenWise.

## Requirements

- Antigravity IDE with workspace rules and an available command tool. Native
  hooks are optional for the fallback.
- The existing TokenWise Python environment (`scripts/setup.ps1`).
- Local pruning weights at `swe-pruner/swe-pruner/model/model.safetensors`.
- This demo folder must stay inside the TokenWise checkout: its launcher locates
  the environment and backend through the parent directory.

To rebuild and install the extension after future changes, run from the checkout
root after the usual setup:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install-antigravity.ps1
```

The VS Code extension displays activity. The hook or agent-command adapter and
Python backend supply context; a normal VS Code command cannot intercept chat.

## How It Works

The stable-IDE path is:

```text
Antigravity user prompt
  -> always-on .agents/rules/tokenwise.md
  -> agent command tool runs .agents/tokenwise-context.ps1
  -> scripts/antigravity_context.py
  -> local /prune-workspace, without an active_file
  -> bounded Python repository context returned as tool output
  -> agent answers or continues working
```

The launcher transfers the query as UTF-8 data, preserving quotes and Unicode.
It shares the hook's backend startup, settings, retrieval, and budget validation.
Every new command invocation creates a fresh activity event; the backend can
reuse cached context when the query and repository fingerprint match.

The optional native path is:

```text
Antigravity user prompt
  -> Test_project/.agents/hooks.json: PreInvocation
  -> .agents/tokenwise-hook.ps1
  -> scripts/antigravity_hook.py
  -> explicit user request from Antigravity's JSONL transcript
  -> local /prune-workspace, without an active_file
  -> prompt-based discovery, dependency expansion, neural ranking and pruning
  -> injectSteps[userMessage] containing reference excerpts
  -> Antigravity's model
```

The native adapter reads `USER_INPUT` records with `USER_EXPLICIT` source, ignoring model
responses, tool output, incomplete trailing records, and its own context messages.
It injects once per user turn. Asking the same question in a later turn triggers
a new retrieval; intermediate model calls do not repeatedly add the same context.
The backend checks file versions on each request and reuses unchanged ASTs and
context results. Saving edits, adding files, or deleting files invalidates the
index fingerprint.

Automatic mode bounds expensive neural work to three relevant files per prompt,
using each pruning pass's relevance score for ranking. Other discovered
dependencies contribute actual signatures, imports, and configuration values.
CPU model work uses four threads
by default, configurable with `TOKENWISE_CPU_THREADS` (1-8).

The default budget is **4,096 tokens**, including the context preamble, file
headers, separators and excerpts. This count uses the local TokenWise/Qwen
tokenizer; Antigravity's chosen model may tokenize the text differently. Context
can omit lines and is reference material, so the agent should inspect original
files before editing. Antigravity retains its own ability to retrieve more files.

## Configuration and Activity

Edit `Test_project/.agents/tokenwise.json` for the token budget, pruning threshold,
candidate limit, timeouts, and automatic startup. Set `enabled` to `false` to
disable the adapter. Turn off `tokenWise.autoOpenAutomaticContext` in editor
settings to keep the status bar and logs without opening a result panel.

- `Test_project/.tokenwise/latest.json`: current prompt, selected files, tokens,
  result and errors.
- `Test_project/.tokenwise/conversations/`: duplicate-injection state.
- `.tokenwise/backend.log` in the checkout root: local model/server diagnostics.
- `.tokenwise/backend.json`: backend PID and local port.
- **Output > TokenWise**: editor activity log.
- **TokenWise: Show Automatic Context**: reopen the latest result.

These runtime folders are ignored by Git. They contain local prompt/context
records. The adapter itself calls only the local backend. Injected code is then
part of Antigravity's normal model request.

If startup or retrieval fails, the hook returns `{}` so Antigravity can continue.
The command adapter returns a nonzero exit code and a concise stderr error;
the rule instructs the agent to continue normal discovery without claiming success.
The extension shows an unavailable state with the error in its output log. It
does not claim that failed context was injected. CPU inference can take several
seconds; the first run may also take time to load the approximately 1.3 GB model.

Workspace rules guide a model; they cannot technically force it to call a tool.
The fallback depends on the rule being loaded, the agent following it, and tool
permission being granted. It does not guarantee native pre-model interception.
If the agent skips the command, `.tokenwise/latest.json` will remain unchanged.
Do not enable unrestricted terminal permissions merely to make the demo work.

To stop the automatically started backend:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/stop-antigravity-backend.ps1
```

## Verification

From the checkout root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
.\.venv\Scripts\python.exe scripts/verify_antigravity.py
```

The live verifier uses a synthetic Antigravity transcript and both exact Windows
launchers. It verifies payment discovery, auth discovery, real-model context
packing, exact tokenizer counts, hook stdout JSON, duplicate prevention, a
256-token budget, and prompt preservation through the command fallback. It
marks its demo activity report with `verification: true`. It does not call
Antigravity's cloud model. Confirm the final IDE behavior with a new agent
conversation and the demo prompt above.

Official integration contracts:
[Antigravity hooks](https://antigravity.google/docs/hooks?tab=ide) and
[workspace rules](https://antigravity.google/docs/rules).
