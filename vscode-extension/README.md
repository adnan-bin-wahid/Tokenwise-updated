# TokenWise VS Code Extension

VS Code client for the TokenWise local backend.

## Automatic Context in Antigravity

Install the VSIX, reload Antigravity IDE, and open any **local Windows Python
repository**. Run **TokenWise: Enable Automatic Context** from the command
palette. Select the complete TokenWise backend installation once, confirm setup,
and start a new Antigravity chat. No manual file selection is required.

The command preserves other workspace rules and hook handlers, retains your
context settings, and registers one shared backend in extension user storage.
Repositories do not need to live inside the TokenWise checkout. Backend Python
dependencies and model weights must already be installed; they are not bundled
in this extension. Remote workspaces and non-Windows launchers are not supported.

On stable IDE builds, an always-on rule asks the agent to run the local retrieval
command. This is tool-output context, not guaranteed native prompt interception.
See [the integration guide](../docs/ANTIGRAVITY.md) for setup and verification.

## Development

Use the project-root setup first, then open this folder in VS Code and press F5:

```powershell
.\scripts\copy-model.ps1
.\scripts\setup.ps1
.\scripts\run-backend.ps1
code .\vscode-extension
```

Commands:

- `TokenWise: Enable Automatic Context`
- `TokenWise: Show Automatic Context`
- `TokenWise: Check Backend Health`
- `TokenWise: Prune Selected Code`
- `TokenWise: Prune Current File`
- `TokenWise: Build Repository Context`

Repository context currently supports Python workspaces. Optional local-LLM goal synthesis is disabled by default. Pruned output is treated as LLM context and can be copied; it is never automatically inserted into the source file.
