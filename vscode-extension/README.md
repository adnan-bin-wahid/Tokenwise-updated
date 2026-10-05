# TokenWise

Automatic, bounded Python repository context for Antigravity coding prompts.

## Quick Start

Download the [TokenWise 0.6.0 VSIX](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/download/v0.6.0/tokenwise-vscode-0.6.0.vsix)
from the [Windows-tested beta release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.0).
Do not download the source-code ZIP for normal installation.

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

Install the 0.6.0 VSIX and reload the editor. Select **Update Backend** when
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
