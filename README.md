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

## Quick Start

### 1. Install TokenWise

Download [**TokenWise 0.5.0 for Antigravity (.vsix)**](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/download/v0.5.0/tokenwise-vscode-0.5.0.vsix)
from the [GitHub release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.5.0).
This is a **Windows-tested beta**, not a marketplace listing. The release also
provides an installer-and-docs ZIP and `SHA256SUMS.txt`. Choose the VSIX for normal
installation, not GitHub's automatically generated source-code ZIP.

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

You do not need to select an editor file, run a pruning command, or paste code.
The backend starts automatically when needed. The first request also loads the
model and can take longer; keep the context command running until it finishes.
Approve its local command if Antigravity's permission policy asks. You do not
need to enable unrestricted terminal execution.

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
| A download/setup fails | Open **Output > TokenWise Setup**, check network/disk space, and run setup again. Verified downloads are reused; partial model downloads can resume. |
| Setup was cancelled | Run setup again. The owned setup process is stopped; its private environment/cache are retained for retry. |
| A setup lock remains after an IDE crash | First ensure no setup process is still running. The diagnostic paths identify user storage; remove only its `backend/install.lock` and retry. |
| Backend is offline or the model is not ready | Run **TokenWise: Diagnose Setup**, then **Start Backend**. Inspect `backend.log` at the reported runtime path if startup fails. |
| No context appears in chat | Start a new chat, confirm the workspace rule is loaded, and check command approval. An unchanged `latest.json` means no new retrieval ran. |
| An old result is displayed | Check the timestamp/query and current tool output. A previous result is not evidence about your new prompt. |
| Workspace is rejected | Use a trusted local folder. Version 0.5.0 accepts Antigravity's local `vscode-userdata` storage; remote/virtual repositories remain unsupported. |
| You cloned/moved a repository or changed IDE profile | Run **Enable Automatic Context** again to create a valid local backend link. |
| Existing rules or JSON conflict | Read the reported filename. Fix invalid JSON or retain customized files under another name; setup will not discard them. |
| Retrieval is slow | Warm the backend with **Start Backend**, keep its process running, and try a smaller budget/candidate limit. Repeated unchanged queries benefit from caching. |

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

If upgrading from 0.4.0, install 0.5.0 and **reload once before uninstalling** so
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

Carbon values in manual result views are **approximate, SEAL-derived estimates**,
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
environment, and creates `releases/TokenWise-0.5.0/` with the VSIX, this guide,
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
