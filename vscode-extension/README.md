# TokenWise

Automatic, bounded Python repository context for Antigravity coding prompts.

## Quick Start

Local **0.6.2** adds **TokenWise: Compare Context Strategies**. Open a saved Python
file for the manual baseline, enter one common task, then compare all indexed
Python code, the selection, and automatic context. Copy or export the actual
packets and evaluate answers in independent chats. The command requires the
matching updated backend; it does not grade agent answers. The source checkout's
`demonstation.md` includes three runnable example repositories and a teacher guide.
The public 0.6.1 download below does not include this command.

Download the [TokenWise 0.6.1 VSIX](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/download/v0.6.1/tokenwise-vscode-0.6.1.vsix)
from the [Windows-tested beta release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.1).
Do not download the source-code ZIP for normal installation.

The project-overview, token-accounting, and automatic-carbon fixes require
**0.6.1 or later, including its updated backend**. After installing and reloading,
run **TokenWise: Set Up Backend** to update the managed backend. Use the versioned
release link above; GitHub's `/releases/latest` does not select beta pre-releases.

1. Install the TokenWise VSIX through **Extensions > ... > Install from VSIX**.
2. Install **64-bit Python 3.12** if it is not already available, then restart the IDE.
3. Open and trust your local Python repository.
4. Run **TokenWise: Enable Automatic Context** from the command palette.
5. Choose **Install Managed Backend**, confirm the dependency/model download,
   wait for setup, then confirm enabling this repository.
6. Start a new Antigravity chat and enter your normal repository prompt.

No Git checkout, Node.js, compilation, F5, API key, GPU, or manual file selection
is needed for normal users. Initial setup downloads about 1.35 GB of model weights
plus CPU dependencies; allow about 10 GB free. Existing complete backend
installations can be reused instead of downloading a managed installation.

On Windows, install the [official Python Install Manager](https://www.python.org/downloads/)
if needed, run `pymanager install 3.12`, and restart Antigravity. Python 3.13/3.14
alone does not meet the requirement. The bundled setup guide includes a version
and 64-bit check plus recovery instructions.

Setup shows **Step 1/7** through **Step 7/7**. If it fails, fix the reported cause
and click **Retry Failed Step**. Completed dependency steps are validated and
reused; partial model downloads can resume. If you closed the notification, run
**TokenWise: Set Up Backend** again, then **Enable Automatic Context** if needed.
Use **Retry Enable** for a workspace configuration error after fixing the named
file. You do not need to uninstall or clear your caches to retry.

## Upgrading

Install the 0.6.1 VSIX and reload the editor. Select **Update Backend** when
prompted, or run **TokenWise: Set Up Backend** manually. Finish active prompts
before confirming setup. A successful upgrade stops only the verified old
managed backend and reconnects background indexing automatically. Verified
model downloads are reused; unrelated processes and checkout backends are not
stopped. Keep your existing workspace link and do not uninstall just to upgrade.

Windows is tested. macOS/Linux portable setup is included but not yet verified
on native machines; compatible Python/PyTorch wheels are required. Remote and
virtual workspaces are unsupported.

## Verify and Troubleshoot

The agent should invoke the TokenWise command and receive
`[TokenWise automatic context]` for the current prompt. The status bar and context
panel show selected files and packed tokens. A saved result alone does not prove
the agent consumed it.

Use **TokenWise: Diagnose Setup** for installation/health information,
**TokenWise: Start Backend** to warm the model, and **Output > TokenWise Setup**
for install logs. **TokenWise: Open Setup Guide** opens the complete bundled guide.
Setup preserves unrelated workspace rules and hook handlers.

In 0.6.0, already configured trusted folders index in the background. Python
save/create/delete/rename events update affected metadata; periodic reconciliation
catches missed events. **Output > TokenWise Index** shows counts and fingerprints.
Different prompts reuse search data, while exact-query/content keys prevent
incorrect complete-context cache reuse. Only saved files are indexed. Neural
pruning still contributes to latency.

On stable Antigravity, an always-on rule guides the agent to retrieve context
through tool output. It is not guaranteed native prompt interception. Retrieved
code enters your selected Antigravity model's normal request and privacy policy.

Full instructions: [project README](https://github.com/adnan-bin-wahid/Tokenwise-updated#readme).

## Overview and Carbon Results

Ask `Give me the full overview of my project. Do not modify any files.` to
retrieve a representative overview across entry points, implementation, models,
tests, and bounded root README/package information. This mode preserves
architectural coverage without neural line pruning. The file limit and complete
token budget still apply; coverage warnings identify omitted Python files.

Source reduction compares source with retained excerpts. Packed tokens include
the wrapper, headings, and fences; formatting overhead is shown separately.
Keeping 17 source tokens in a 117-token bundle means **0% source reduction and
100 tokens of overhead**, not negative reduction. Actual increases are labeled
as increases. A package containing only version metadata cannot provide evidence
of application behavior; the panel warns about sparse scaffolds or a wrong root.

New automatic panels also show estimated CO2 before/after and signed energy/CO2
changes. Estimates load after context retrieval, use the actual local backend,
and compare the same selected files and formatting with and without pruning.
Disable **TokenWise > Enable Carbon Estimation** to turn this off. Pending,
disabled, and failed estimates remain visible; failures do not discard context.

These are approximate configured-model/hardware/intensity scenarios, not measured
Antigravity emissions or net carbon benefits. The cloud model is not detected
automatically. Update both the extension and backend, then issue a new prompt;
an older saved report may not contain the matched baseline needed for comparison.

## Uninstall

Click **Uninstall** and fully restart the IDE when required. TokenWise runs
automatic cleanup for tracked workspace integration, managed backend/model/cache
data, owned processes, and TokenWise preferences. Large deletions continue in a
self-contained background worker.

Use **TokenWise: Remove All Local Data** for immediate cleanup with visible
warnings. After upgrading from 0.4.0, reload the current release once before uninstalling.
Customized/unrecognized files, unrelated settings, existing backend checkouts,
Python itself, and editor-managed history are preserved; zero traces cannot be
guaranteed for unavailable folders or shared caches from older versions.

## Development

```sh
npm ci
npm test
npm run package
```

Packaging prepares the backend bundle and creates a shareable release folder.
F5 is for extension development only. Manual code-pruning and repository-context
commands remain available in VS Code with a configured backend.
