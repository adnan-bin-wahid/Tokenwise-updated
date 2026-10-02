# TokenWise VS Code Extension

VS Code client for the TokenWise local backend.

Use the project-root setup first, then open this folder in VS Code and press F5:

```powershell
.\scripts\copy-model.ps1
.\scripts\setup.ps1
.\scripts\run-backend.ps1
code .\vscode-extension
```

Commands:

- `TokenWise: Check Backend Health`
- `TokenWise: Prune Selected Code`
- `TokenWise: Prune Current File`
- `TokenWise: Build Repository Context`

Repository context currently supports Python workspaces. Optional local-LLM goal synthesis is disabled by default. Pruned output is treated as LLM context and can be copied; it is never automatically inserted into the source file.
