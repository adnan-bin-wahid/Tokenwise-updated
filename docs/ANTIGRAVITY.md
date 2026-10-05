# Automatic Context in Antigravity

Open any local Python repository as the workspace in **Antigravity IDE**, run
`TokenWise: Enable Automatic Context` once, then send a normal
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

## Enable Any Python Repository

1. Install `vscode-extension/tokenwise-vscode-0.5.0.vsix` in Antigravity IDE and
   reload its window. For development, compile the extension and press F5 instead.
2. Open your Python repository. It can be anywhere on your machine; it does not
   need to be inside the TokenWise checkout. Trust the workspace before setup.
3. Open the command palette and run **TokenWise: Enable Automatic Context**.
   In a multi-folder workspace, select the repository to configure.
4. On first use, choose **Install Managed Backend** to create a private environment
   and download verified weights automatically. Normal users need Python 3.12,
   not a Git checkout, Node.js, or F5. Alternatively select an existing complete
   TokenWise backend installation: the folder
   containing `.venv`, `scripts`, and `swe-pruner`. During F5 development the
   checkout is discovered automatically. Existing registered installations are
   reused, so subsequent repositories do not require another backend selection.
   See the root README for download size, prerequisites, and first-run troubleshooting.
5. Confirm setup. In **Customizations > Rules**, confirm that the TokenWise
   workspace rule is listed. Start a new chat and enter your normal prompt.

Setup installs launchers under `.agents/tokenwise/`, merges the TokenWise hook
and `.agents/tokenwise.json`, and adds a `.tokenwise/` Git ignore entry. It leaves
unrelated rules and hook handlers intact and retains your budget and threshold.
If `.agents/rules/tokenwise.md` contains custom instructions, setup uses a new
rule filename instead. It can migrate the exact old generated demo rule, but
refuses to overwrite customized launchers or malformed JSON configuration.
Setup confirmation explicitly re-enables `enabled` in the TokenWise settings.

The backend installation is registered in the extension's **user storage**.
Each workspace has an ignored `.tokenwise/backend-link.json` pointing to that
registration. Launchers derive the target workspace from their own location;
they no longer derive the backend from the repository's parent folder. Shared
rules contain no machine-specific backend paths.

Re-run the command after cloning on another machine, clearing `.tokenwise/`,
or changing IDE profiles. To relocate the backend, update the application-level
`tokenWise.backendInstallationPath` user setting and re-run setup. Workspaces
linked to that registration will use the new installation. Keep the backend
environment and model available; the VSIX bundles backend source/configuration
and its installer, but downloads dependencies and the weight separately.

Windows is verified. **macOS/Linux portable setup is included but not yet
native-tested**; `python3` must be available for the small workspace bootstrap.
Remote/virtual workspaces remain unsupported. Retrieval still uses
the Python indexer's supported files and exclusions; it cannot promise that
every possible Python repository layout or dynamic import will be resolved.

If version 0.3.0 reports "supports local folders only" for a normal drive folder
in an F5 window, upgrade or recompile and restart the development host. Version
0.3.1 accepts Antigravity's locally backed `vscode-userdata` extension storage;
that storage scheme does not make your repository remote.

## Try the Demo

1. Follow the setup above with `Test_project` as the repository.
2. Run **TokenWise: Enable Automatic Context** to migrate its generated rule
   to the shared-backend launchers.
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
`.agents/tokenwise/tokenwise-context.ps1` through its command tool. Approve it if the IDE's
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
- 64-bit Python 3.12 and a managed installation created through **Set Up Backend**,
  or the existing TokenWise environment (`scripts/setup.ps1`).
- Verified local pruning weights, downloaded by managed setup or supplied locally.
- A complete backend installation selected once, independently of repository
  location. The older checked-in demo launchers remain available for backwards
  compatibility until you run the new setup command.

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
  -> agent command tool runs .agents/tokenwise/tokenwise-context.ps1
  -> workspace backend-link.json resolves the shared installation
  -> scripts/antigravity_context.py
  -> local /prune-workspace, without an active_file
  -> bounded Python repository context returned as tool output
  -> agent answers or continues working
```

On macOS/Linux the rule invokes `python3 .agents/tokenwise/tokenwise-launcher.py`
instead of PowerShell. That bootstrap reads the same backend registration and
executes the actual adapter in the private Python 3.12 environment.

The launcher transfers the query as UTF-8 data, preserving quotes and Unicode.
It shares the hook's backend startup, settings, retrieval, and budget validation.
Every new command invocation creates a fresh activity event; the backend can
reuse cached context when the query and repository fingerprint match.

The optional native path is:

```text
Antigravity user prompt
  -> workspace/.agents/hooks.json: PreInvocation
  -> .agents/tokenwise/tokenwise-hook.ps1
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

Edit your workspace's `.agents/tokenwise.json` for the token budget, pruning threshold,
candidate limit, timeouts, and automatic startup. Set `enabled` to `false` to
disable the adapter. Turn off `tokenWise.autoOpenAutomaticContext` in editor
settings to keep the status bar and logs without opening a result panel.

- `.tokenwise/latest.json` in the workspace: current prompt, selected files, tokens,
  result and errors.
- `.tokenwise/conversations/` in the workspace: duplicate-injection state.
- `.tokenwise/backend-link.json` in the workspace: extension user registration path.
- `backend/installation.json` in extension user storage: shared installation and
  runtime directory paths.
- `backend/runtime/backend.log` and `backend.json` in extension user storage:
  new server diagnostics, PID and local port. If setup adopts the old checkout
  server, its log remains in the checkout's `.tokenwise/backend.log` until restart.
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

To stop the automatically started backend, take `runtime_dir` from the shared
`installation.json` and pass it to the shutdown helper:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/stop-antigravity-backend.ps1 -RuntimeDirectory 'C:\absolute\path\to\backend\runtime'
```

Without `-RuntimeDirectory`, the helper stops the older checkout-managed server.
Multiple repositories share one model process, startup lock, and backend log;
prompt activity and duplicate-injection state remain separate per repository.

## Verification

From the checkout root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
.\.venv\Scripts\python.exe scripts/verify_antigravity.py
cd vscode-extension
npm test
cd ..
node scripts/verify-portable-context.cjs
```

The live verifier uses a synthetic Antigravity transcript and both exact Windows
launchers. It verifies payment discovery, auth discovery, real-model context
packing, exact tokenizer counts, hook stdout JSON, duplicate prevention, a
256-token budget, and prompt preservation through the command fallback. It
marks its demo activity report with `verification: true`. It does not call
Antigravity's cloud model. Confirm the final IDE behavior with a new agent
conversation and the demo prompt above.

The portable verifier configures two temporary Python repositories **outside**
the checkout, preserves pre-existing rules and hooks, and exercises the exact
new command and hook launchers against the real local model. It checks a shared
backend, quoted/Unicode prompts, exact tokenizer counts, bounded context, repeat
setup, and duplicate prevention. Start the backend first; this verifier refuses
to launch a detached model process. Temporary files are cleaned up and it does
not replace your real workspace activity report or call Antigravity's cloud model.

Official integration contracts:
[Antigravity hooks](https://antigravity.google/docs/hooks?tab=ide) and
[workspace rules](https://antigravity.google/docs/rules).
