# TokenWise

Automatic, bounded Python repository context for Antigravity coding prompts.
Open a repository, enable TokenWise once, and enter your normal prompt. TokenWise
retrieves relevant code and tests without asking you to select files manually.

**For normal users: install the VSIX. You do not need to clone this repository,
install Node.js, compile the extension, press F5, or manually start a server.**

## Before You Start

| Requirement | Details |
| --- | --- |
| Editor | Antigravity IDE with workspace rules and a command tool |
| Python | A **64-bit Python 3.12** installation; [official downloads](https://www.python.org/downloads/) |
| Repository | A local folder containing Python source |
| Internet | Needed for initial dependency/model downloads; retrieval runs locally afterward |
| Disk | Allow about **10 GB free** for the environment, model, and package caches |
| Memory | 8 GB RAM is a practical starting recommendation; a CPU is sufficient |

Windows installation and retrieval are tested. Portable setup and launchers are
also included for macOS/Linux, but those platforms have not yet been verified
on native machines. Python/PyTorch wheels must support your OS and architecture.
On macOS/Linux, `python3` must be on PATH for the small workspace bootstrap.
Remote SSH, WSL/Dev Containers, browser editors, and virtual workspaces are not
supported by this first-run workflow.

TokenWise itself does not need an API key. Your Antigravity model access and
billing remain separate. A GPU, Ollama, and an MCP server are not required.

### Install or Check Python on Windows

Python 3.13/3.14 alone is not sufficient; TokenWise currently requires **3.12**.
If it is missing, install the [official Python Install Manager](https://www.python.org/downloads/),
open a new PowerShell terminal, and run:

```powershell
pymanager install 3.12
py -3.12 -c "import sys,struct; print(sys.version); print(struct.calcsize('P')*8); print(sys.executable)"
```

The check should show **3.12.x**, **64**, and an executable path. Restart
Antigravity afterward. If the manager installation/download fails, fix the
reported issue and retry that step; do not remove your existing project Python.
If detection still fails, set **TokenWise > Python Path** to the printed path.
See [official Windows installation troubleshooting](https://docs.python.org/3/using/windows.html#troubleshooting).

## Quick Start

### 1. Install TokenWise

Download [**TokenWise 0.6.1 for Antigravity (.vsix)**](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/download/v0.6.1/tokenwise-vscode-0.6.1.vsix)
from the [0.6.1 GitHub release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.1).
This is a **Windows-tested beta**, not a marketplace listing. The release also
provides an installer-and-docs ZIP and `SHA256SUMS.txt`. Choose the VSIX for normal
installation, not GitHub's automatically generated source-code ZIP.

**The overview/token-accounting/automatic-carbon fixes require 0.6.1 or later,
including its updated backend.** Install the VSIX, reload, and update the managed
backend through **TokenWise: Set Up Backend**. Use the versioned release link
above: GitHub's `/releases/latest` does not select beta pre-releases.

In Antigravity:

1. Open the **Extensions** view.
2. Open its **...** menu and choose **Install from VSIX...**.
3. Select the TokenWise VSIX and reload the editor window when asked.

Install the extension normally. **F5 is only for extension developers.**

### 2. Open Your Python Repository

Use **File > Open Folder** and select your project, for example
`C:\Projects\my-python-app`. The folder can be anywhere; it does not need to sit
inside a TokenWise checkout. Trust it only if you trust the repository's contents.

### 3. Enable Automatic Context

Open the command palette and run **TokenWise: Enable Automatic Context**.

On a new computer:

1. Choose **Install Managed Backend**.
2. Review the download/setup confirmation and choose **Install Backend**.
3. Wait for setup. It creates a private Python environment, installs CPU
   dependencies, downloads about **1.35 GB** of pinned model weights, and checks
   their SHA-256 checksum. Progress appears in a notification; detailed logs are
   in **Output > TokenWise Setup**. First setup can take several minutes.
4. Confirm enabling TokenWise in the selected repository.

The notification shows **Step 1/7** through **Step 7/7**. If a step fails, fix
the reported cause and click **Retry Failed Step**. Successful dependency steps
are checked and reused; downloads are verified or resumed, not blindly trusted.
You do not need to uninstall the extension or begin from scratch.

If you already have a complete TokenWise checkout/environment, choose
**Use Existing Backend** and select its root folder instead. Do not select your
Python repository or the `swe-pruner` subfolder as the backend installation.

Setup adds TokenWise launchers and a workspace rule, merges its hook settings,
and ignores local runtime data. Existing unrelated rules, hook handlers, and
your context budget are preserved. Malformed JSON or customized launchers are
not silently overwritten. No application source files are changed by setup.

In a multi-folder window, choose the repository you want to enable. Repeat the
command for each additional repository; they share one backend installation.

### 4. Start a New Chat and Enter a Prompt

For example:

> Explain the login failure handling and its related tests. Do not modify files.

Or:

> Find why invoice retries fail and identify the relevant service and tests.

For a project tour:

> Give me the full overview of my project. Do not modify any files.

You do not need to select an editor file, run a pruning command, or paste code.
The backend starts automatically when needed. The first request also loads the
model and can take longer; keep the context command running until it finishes.
Approve its local command if Antigravity's permission policy asks. You do not
need to enable unrestricted terminal execution.

## If a Setup Step Fails

Open **View > Output**, then choose **TokenWise Setup** in its dropdown for the
full error. The notification identifies the failed stage and its recovery advice.

| Step | What happens | Fix and retry |
| --- | --- | --- |
| **1. Prerequisites** | Finds 64-bit Python 3.12 and verifies bundled files | Install Python 3.12, restart Antigravity, then run setup again. For a custom Python location, set **TokenWise > Python Path**. If the VSIX is damaged, download it again. |
| **2. Backend files** | Copies verified backend files into private user storage | Check free disk space and permissions for the storage path in the log. Click **Retry Failed Step**. |
| **3. Environment** | Creates or checks TokenWise's private Python environment | Repair your Python 3.12 installation if needed, then retry. A broken private environment is recreated; model/download caches remain. |
| **4. Dependencies** | Installs packaging tools, CPU PyTorch, and backend dependencies | Check internet/proxy access to PyPI and `download.pytorch.org`, and available disk space. Retry reuses completed, validated substeps and cached wheels. |
| **5. Model** | Downloads about 1.35 GB of pinned weights and checks their hash | Check access to Hugging Face and free disk space. Retry resumes partial downloads when the server permits it; corrupt weights are replaced. Hash verification can take time even at 100%. |
| **6. Verification** | Checks imports, tokenizer, and trained carbon artifacts | Read the import error in **TokenWise Setup**, fix the reported system/dependency issue, then retry. Previously completed dependencies are checked again. |
| **7. Registration** | Saves the verified backend and its user setting | Check storage/settings permissions and retry. The installed environment and verified weights are retained. |

If you dismissed the failure notification or cancelled setup, run **TokenWise:
Set Up Backend** again. Keep the same IDE profile so its cached progress can be
reused. Then run **Enable Automatic Context** if the repository is not enabled.
For a repository rule/configuration error, choose **Retry Enable** after fixing
the named file. Existing unrelated rules and files are preserved.

Do not delete the backend/cache folders as your first troubleshooting step.
An installer lock after an IDE crash is different: ensure no TokenWise setup is
still running, use the logged storage path, remove only `backend/install.lock`,
and retry. Never remove another running installer's lock.

## Upgrade from an Earlier Version

1. Finish active TokenWise prompts/setup commands. Install the new 0.6.1 VSIX
   through **Install from VSIX...**, then reload the editor window.
2. For a managed backend, select **Update Backend** when prompted. If you
   dismissed the prompt, run **TokenWise: Set Up Backend** manually.
3. Approve **Install Backend** and wait for the numbered steps. Verified model
   downloads are reused. The previous managed process is stopped only after
   installation succeeds and only when its process identity can be verified.
4. Background indexing reconnects automatically. Open **Output > TokenWise
   Index** to confirm the Python file count, then start a new Antigravity chat.

Your repository's central backend link remains valid. Do not uninstall or use
**Remove All Local Data** just to upgrade: those actions remove reusable caches.
If you use an existing **checkout backend** instead of a managed installation,
update that checkout and restart its own backend process yourself; setup does
not stop or alter checkout processes. See the developer guide for source setup.

## How to Tell It Is Working

- In **Customizations > Rules**, a TokenWise workspace rule should be listed.
- In the chat, the agent should run the TokenWise context command, receive
  `[TokenWise automatic context]`, and use the relevant excerpts.
- The status bar changes from awaiting a prompt to **TokenWise Auto: N files,
  N tokens**. The repository-context panel shows the selected files and excerpts.
- Your repository's `.tokenwise/latest.json` should have a **new timestamp**,
  the current query, `status: "ready"`, and `verification: false`.

**A saved report or status bar alone does not prove that the model consumed the
context. Check the current chat's actual tool output too.** Historical results
are labeled **TokenWise last result**; verifier output is labeled **TokenWise test**.

On stable Antigravity builds, an always-on rule asks the agent to invoke the
local retrieval command. Context reaches the model through tool output. On IDE
builds supporting native hooks, `PreInvocation` can inject it instead. The rule
fallback is not guaranteed interception before the first model call: it depends
on the agent following the rule and being permitted to run the command.

## Everyday Controls

### Background Indexing

Version 0.6.0 warms the repository index when you open an already
configured, trusted local folder. It uses your registered backend; it does not
install dependencies or download models without setup consent.

- Saving, creating, deleting, or renaming Python files updates the affected
  metadata in the background. Bursts of edits are grouped together.
- Different prompts reuse term counts, symbol locations, signatures, and the
  dependency graph. File token counts are cached per tokenizer and content.
- Source-content fingerprints invalidate search/context caches after edits.
  Complete context results require the exact query, goal, repository fingerprint,
  active file, threshold, budget, and candidate limit, not similar wording.
- Full reconciliation runs approximately every two minutes to catch missed
  events, including content changes with preserved timestamps. Unchanged ASTs
  and derived metadata are retained. Only saved files on disk are indexed.
- A watcher heartbeat runs every 30 seconds. If no watcher remains alive for
  90 seconds, retrieval falls back to checking the repository before each query.
  An edit becomes available after its background update completes; missed events
  can remain unseen until reconciliation.

Open **Output > TokenWise Index** to see the indexed file count and fingerprint
after a change. Set `enabled: false` in `.agents/tokenwise.json` to stop indexing
and automatic retrieval. Setting `auto_start_backend: false` also prevents
background warm-up from starting an offline backend. Unconfigured, untrusted,
remote, and virtual folders remain idle.

An older backend continues to provide context using the conservative fallback.
Update and restart the backend to activate background indexing; reloading only
the extension does not reload Python code. See the
[development instructions](docs/DEVELOPMENT.md#try-the-background-index) below.
These changes reduce repository/search overhead; neural pruning and the
Antigravity model response can still dominate total prompt latency.

### Project Overviews and Honest Metrics

An overview prompt uses a different retrieval mode from a focused bug or symbol
question. It selects representative entry points, implementation modules, data
models, and tests, plus bounded root README/package information when present.
This mode does not use neural line pruning: preserving architectural coverage
is more useful than narrowly selecting lines about a generic word such as
`PROJECT`. Large modules use structural excerpts; small modules are kept intact.
The same total token budget and file-candidate limit still apply.

The panel reports how many Python files were indexed, which files were included,
and any coverage warnings. A six-file bounded overview is not a promise to send
every file in a large repository. Increase `max_candidates` (up to 32) and the
budget if useful; the agent can read originals to fill gaps. If the project only
contains `__init__.py` with a version string, TokenWise says so. Check that you
opened the actual application root, not an empty scaffold or unrelated folder.

Token statistics separate three quantities:

- **Source tokens / Retained source:** before/after excerpt content from the
  included files, excluding the context wrapper. Source reduction compares these
  values. It is not a percentage of the entire repository or conversation.
- **Packed tokens:** the complete supplied context, including paths, fences,
  headings, repository map, and safety text. This is the bounded quantity.
- **Formatting overhead:** the difference between the packed count and retained
  source count. Tokenization across block boundaries is not exactly additive.

For the reported case of 17 source tokens kept in a 117-token bundle, source
reduction is **0%**, with **100 tokens of overhead**, not -588.24%. No savings are
claimed when nothing was removed. Any real expansion is labeled as an increase.

### Automatic Carbon Results

With **TokenWise > Enable Carbon Estimation** enabled (the default), new automatic
results display context immediately, then request carbon predictions separately.
The panel shows CO2 before/after, estimated CO2 savings or increase, phase energy,
the model scenario, and carbon intensity. Tiny values retain enough precision
to remain visible. This does not add an Antigravity model call or delay the context command.

Both predictions use the same selected files, formatting, output-token assumption,
target model/hardware, and intensity. Only the input-context token count changes.
The baseline is the same bundle with unpruned source, not the whole repository.
An initializer-only bundle therefore has zero estimated savings, even though
the wrapper is larger than its source. Increases are never hidden as savings.

Carbon estimates are **approximate, SEAL-derived configured-scenario estimates**,
not measurements of your Antigravity provider, local pruning energy, the whole
conversation, or net environmental benefit. You can change the target scenario
in TokenWise settings; it is not automatically detected from your agent model.

Pending, disabled, and unavailable states are visible in the panel. If estimating
fails, your prepared context remains usable; read the displayed error and check
**TokenWise: Diagnose Setup**. An older backend without a matched baseline must
be updated. With automatic panels disabled, **Show Automatic Context** opens the
latest result with its estimate. Estimates live in the extension view and are
not written back into `.tokenwise/latest.json` or injected as agent instructions.

### Commands

| Command | Use |
| --- | --- |
| **Enable Automatic Context** | Configure this Python repository or repair its backend link |
| **Set Up Backend** | Install/repair a managed backend without configuring a repository |
| **Start Backend** | Warm the model before a prompt; updates the manual API URL to its actual port |
| **Diagnose Setup** | Check the registered installation, actual backend health, and workspace links |
| **Show Automatic Context** | Reopen the latest supplied context |
| **Open Setup Guide** | Read this guide inside the editor, even without the source checkout |
| **Remove All Local Data** | Clean TokenWise data now, before uninstalling or starting over |

All commands have the **TokenWise:** prefix. The manual **Prune Selected Code**,
**Prune Current File**, and **Build Repository Context** commands remain available
in VS Code as well; automatic chat retrieval needs Antigravity's agent integration.

For a smaller context, edit your repository's `.agents/tokenwise.json`:

```json
{
  "enabled": true,
  "token_budget": 2048,
  "threshold": 0.45,
  "max_candidates": 6
}
```

Other settings use defaults when omitted. The default budget is 4,096 tokens;
the supported range is 256-32,768. This counts the complete supplied context with
TokenWise's local tokenizer, not necessarily the tokenizer of your chosen agent
model. Set `enabled` to `false` to stop retrieval. To remove the rule entirely,
remove only TokenWise's generated rule and handler, retaining your other rules.

Turn off **TokenWise > Auto Open Automatic Context** in editor settings to keep
the status bar and logs without automatically opening a panel.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Python 3.12 is not found | Install 64-bit Python 3.12 and restart the IDE. For a nonstandard installation, set the **TokenWise > Python Path** user setting to its executable. |
| A download/setup fails | Use the numbered recovery table above, fix the reported cause, and click **Retry Failed Step**. Completed dependency steps and verified/partial downloads are retained. |
| Setup was cancelled | Run setup again. The owned setup process is stopped; its private environment/cache are retained for retry. |
| A setup lock remains after an IDE crash | First ensure no setup process is still running. The diagnostic paths identify user storage; remove only its `backend/install.lock` and retry. |
| Backend is offline or the model is not ready | Run **TokenWise: Diagnose Setup**, then **Start Backend**. Inspect `backend.log` at the reported runtime path if startup fails. |
| No context appears in chat | Start a new chat, confirm the workspace rule is loaded, and check command approval. An unchanged `latest.json` means no new retrieval ran. |
| An old result is displayed | Check the timestamp/query and current tool output. A previous result is not evidence about your new prompt. |
| Workspace is rejected | Use a trusted local folder. Version 0.5.0 accepts Antigravity's local `vscode-userdata` storage; remote/virtual repositories remain unsupported. |
| You cloned/moved a repository or changed IDE profile | Run **Enable Automatic Context** again to create a valid local backend link. |
| Existing rules or JSON conflict | Read the reported filename. Fix invalid JSON or retain customized files under another name; setup will not discard them. |
| Retrieval is slow | Check **Output > TokenWise Index**, keep the backend running, and try a smaller budget/candidate limit. An older backend must be updated to use background indexing. Neural pruning still contributes to latency. |
| Overview includes only a package initializer | Update both extension and backend to 0.6.1 or later. Confirm the application root contains real implementation. Check the panel's indexed-file count and coverage warnings. |
| CO2 is missing or unavailable | Enable carbon estimation, run **Diagnose Setup**, update the backend through **Set Up Backend**, and issue a new prompt. The panel explains disabled, pending, and failed estimates; old saved reports may lack the matched baseline. |

Corporate firewalls/proxies must permit PyPI, the PyTorch wheel host, Hugging Face,
and Hugging Face's download CDN. TokenWise does not bypass your network policies.
On Linux, missing system libraries such as OpenMP must be supplied by your OS.

## Uninstall and Remove Local Data

**Version 0.5.0 adds automatic uninstall cleanup.** Finish active agent/setup
commands, click **Uninstall** in the Extensions view, then **fully restart the
IDE** when required. The editor invokes TokenWise's Node uninstall hook when
removal completes; a background worker finishes large environment deletions.
Uninstall cleanup is not guaranteed to run at the instant you click the button.

For an ordinary managed installation, cleanup removes:

- Managed Python environments, model downloads, partial downloads, private pip
  cache, backend registration/logs, and verified owned backend/setup processes.
- Unchanged generated repository rules/launchers, TokenWise hook handlers,
  `.agents/tokenwise.json`, backend links, context records, and conversation state.
- TokenWise's added `.gitignore` block and editor/workspace TokenWise preferences,
  retaining unrelated settings, comments, hook handlers, and application files.
- Its own tracking registry and temporary worker when cleanup succeeds.

**For cleanup immediately**, run **TokenWise: Remove All Local Data**, confirm,
and wait for completion before uninstalling. This also shows any preserved-file
warnings in **Output > TokenWise Cleanup**.

If upgrading from 0.4.0, install the current release and **reload once before uninstalling** so
it can register your storage. It discovers old repositories recorded in this
IDE's workspace history; open older configured repositories once if they are not
in that history. Keep their drives/folders available during removal.

Cleanup deliberately preserves customized rules/launchers, unrecognized files,
malformed configuration, pre-existing backend checkouts, Python itself, and shared
caches used by other software. A failed/partial cleanup retains a small registry
and report for diagnosis rather than silently deleting user data. Uninstall-hook
logs identify the report under the OS temporary directory; use the immediate
cleanup command before uninstalling to see issues directly.

No extension can promise zero traces in editor-managed databases/history/logs,
OS backups, source-control history, downloaded VSIX files, or shared pip caches
created by older versions. These are not wiped by TokenWise. macOS/Linux cleanup
is included but still needs native validation. The editor lifecycle timing is
documented in [the uninstall-hook reference](https://code.visualstudio.com/api/references/extension-manifest#extension-uninstall-hook).

## Privacy, Storage, and Limits

The setup process downloads software and model files. Retrieval calls only the
local backend on `127.0.0.1`; it does not execute repository Python files. Relevant
source excerpts then enter **Antigravity's normal model request**, subject to
your selected provider's privacy policy. Do not treat local pruning as a promise
that code never leaves your machine.

Managed environments, verified model downloads, backend registration, and logs
live in **TokenWise's extension user storage**, not in your repository. Each
repository has an ignored `.tokenwise/` directory containing prompt/context
records and a machine-specific backend link. Do not commit or share that directory.
The small `.agents/` rule/launcher files may be committed; teammates must still
enable TokenWise locally to create their own backend link.

Retrieval currently indexes Python files and supported static imports/calls.
Dynamic imports, generated code, unsupported Python syntax, ignored directories,
and very large files may not be represented. Context is a bounded selection,
not a complete repository dump. The agent should read original files before
editing. TokenWise never writes pruned excerpts into application source files.

Carbon values in manual and automatic result views are **approximate, SEAL-derived estimates**,
not measurements of your Antigravity cloud-model consumption. See
[evaluation notes](docs/PROJECT-EVALUATION.md) and
[the detailed integration guide](docs/ANTIGRAVITY.md).

## For Maintainers

To build a shareable release from this checkout, with Node.js dependencies installed:

```powershell
cd vscode-extension
npm ci
npm test
npm run package
```

Packaging bundles the backend source/configuration, not the weight or a virtual
environment, and creates `releases/TokenWise-0.6.1/` with the VSIX, this guide,
licenses, and SHA-256 checksums. Send your friend that folder or just the VSIX
and guide. See [GitHub publishing instructions](docs/PUBLISHING.md) for the
draft/upload/verify/publish process. Public marketplace publishing is a separate
step requiring a publisher account; creating this package does not publish it.

F5 remains available for extension development. Use
[developer setup notes](docs/DEVELOPMENT.md) for source/environment setup and tests.
The research pipeline remains under `carbon-engine/`; paper PDFs remain under
`docs/papers/`. No developer-specific absolute paths are required for normal users.

## Credits and License

TokenWise source is MIT licensed. The neural model is derived from
[SWE-Pruner](https://github.com/Ayanami1314/swe-pruner), with weights from
[ayanami-kitasan/code-pruner](https://huggingface.co/ayanami-kitasan/code-pruner).
Model assets and dependencies retain their respective licenses; see
[third-party notices](docs/THIRD-PARTY-NOTICES.md).
