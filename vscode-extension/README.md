# TokenWise

Automatic, bounded Python repository context for Antigravity coding prompts.

## Quick Start

Download the [TokenWise 0.5.0 VSIX](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/download/v0.5.0/tokenwise-vscode-0.5.0.vsix)
from the [Windows-tested beta release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.5.0).
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

On stable Antigravity, an always-on rule guides the agent to retrieve context
through tool output. It is not guaranteed native prompt interception. Retrieved
code enters your selected Antigravity model's normal request and privacy policy.

Full instructions: [project README](https://github.com/adnan-bin-wahid/Tokenwise-updated#readme).

## Uninstall

Click **Uninstall** and fully restart the IDE when required. Version 0.5.0 runs
automatic cleanup for tracked workspace integration, managed backend/model/cache
data, owned processes, and TokenWise preferences. Large deletions continue in a
self-contained background worker.

Use **TokenWise: Remove All Local Data** for immediate cleanup with visible
warnings. After upgrading from 0.4.0, reload 0.5.0 once before uninstalling.
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
