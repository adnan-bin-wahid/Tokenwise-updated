# TokenWise Setup and Recovery

This guide supports TokenWise 0.6.8. Start with the [project README](https://github.com/adnan-bin-wahid/Tokenwise-updated#readme)
for downloads and your first prompt. In the installed extension, **TokenWise: Open
Setup Guide** opens the bundled user guide. Read this reference for detailed recovery.

## Requirements

- Antigravity with workspace rules and an available command tool.
- A trusted local Python repository, independent of the TokenWise checkout.
- **64-bit Python 3.12**; Python 3.13/3.14 alone is insufficient.
- Initial dependency/model download access, approximately **10 GB free disk**
  and adequate memory. **8 GB RAM** is a starting recommendation.

Windows is tested. Portable macOS/Linux setup is included but not native-verified;
Python/PyTorch wheels must support your OS and architecture. On macOS/Linux,
`python3` must be on PATH for the workspace bootstrap. Remote SSH, WSL/Dev
Containers, browser editors and virtual workspaces are unsupported by this workflow.

No GPU, Ollama, MCP server or TokenWise API key is required. Antigravity model
access/billing is separate. Users do not need Node.js, Git, compilation or F5.

## Check Python on Windows

Install Python 3.12 from [the official downloads](https://www.python.org/downloads/),
then open a new PowerShell terminal:

```powershell
py -3.12 -c "import sys,struct; print(sys.version); print(struct.calcsize('P')*8); print(sys.executable)"
```

Expect **3.12.x**, **64** and an executable path. If you use the Python Install
Manager and 3.12 is missing, run `pymanager install 3.12`, then repeat the check.
Restart Antigravity. If detection still fails, set the user setting **TokenWise >
Python Path** to the printed executable. Do not remove your project's Python
environment to install TokenWise.

## Install and Enable

1. Install the VSIX through **Extensions > ... > Install from VSIX...** and reload.
2. Open and review your Python folder; trust it only if appropriate.
3. Run **TokenWise: Enable Automatic Context** from the command palette.
4. Choose **Install Managed Backend**, review the confirmation and approve it.
5. Wait for seven stages and confirm workspace enablement.
6. Start a new chat and enter your task without selecting files.

Setup creates a private Python environment and downloads about **1.35 GB** of
pinned weights with SHA-256 verification. It can take several minutes. Notifications
and **Output > TokenWise Setup** identify the current stage.

For an existing complete checkout/environment, choose **Use Existing Backend**
and select the root containing `.venv`, `scripts` and `swe-pruner`. Do not select
your application or the nested `swe-pruner` folder. See [DEVELOPMENT.md](DEVELOPMENT.md).

In multi-folder windows, choose the repository being configured and repeat for
others. Workspaces share the registered backend. Setup adds owned rules/launchers,
merges hooks and ignores runtime data. Unrelated rules, handlers and retained
budget settings are preserved. Malformed JSON and customized launchers are not
silently overwritten. No application source changes.

## Recover a Failed Stage

Fix the reported cause and click **Retry Failed Step**. If you dismissed the
notification or cancelled, run **TokenWise: Set Up Backend** again in the same
IDE profile. Validated dependency steps and download caches are reused.

| Stage | Work | Recovery |
| --- | --- | --- |
| **1. Prerequisites** | Detect 64-bit Python 3.12 and verify bundled files. | Install/check Python and restart. Set Python Path if needed; re-download a damaged VSIX. |
| **2. Backend files** | Copy verified source to private storage. | Check storage permissions and free disk at the logged path, then retry. |
| **3. Environment** | Create/check the private environment. | Repair Python if needed. A broken owned environment can be recreated while downloads remain. |
| **4. Dependencies** | Install packaging tools, CPU PyTorch and packages. | Check internet/proxy access to PyPI and `download.pytorch.org`, then retry. Validated substeps and cached wheels can be reused. |
| **5. Model** | Download/check pinned weights. | Check Hugging Face/CDN access and disk. Resume is used when supported; corrupt weights are replaced. Hash checks can take time after 100%. |
| **6. Verification** | Check imports, tokenizer and carbon artifacts. | Read the exact import/system error, fix its cause and retry. |
| **7. Registration** | Save backend registration and user setting. | Check storage/settings permissions and retry; verified environment/weights remain. |

Then run **Enable Automatic Context** if the workspace is not enabled. For a
rule/configuration error, fix the named file and use **Retry Enable**. Preserve
unrelated keys/rules. Do not delete all caches as the first recovery step.

If a setup lock remains after an IDE crash, first confirm no setup is running.
Use the diagnostic storage path and remove only `backend/install.lock` for that
inactive installation. Never remove another running installer's lock.

## Verify a Current Prompt

Check the rule, command approval and current chat tool output. The status bar
should report **TokenWise Auto** and a new activity record should match the task
with `status: "ready"`, `verification: false` and a fresh timestamp. An old
panel, **TokenWise last result** or **TokenWise test** is not current live evidence.
The fallback relies on the agent following its rule, not model-request interception.

## Upgrade Without Losing Downloads

1. Finish active prompts/setup, install the newer VSIX and reload.
2. Accept **Update Backend** or run **TokenWise: Set Up Backend** manually.
3. Approve setup and wait for verification; validated model downloads are reused.
4. Run **TokenWise: Enable Automatic Context** again to refresh owned integration.
5. Check **Output > TokenWise Index**, start a new chat and inspect a fresh result.

Reloading the extension does not update a running old Python server. Managed
setup stops the previous managed process only after successful installation and
verified identity. Checkout processes are not stopped/edited: restart your own.

Do not uninstall or use **Remove All Local Data** merely to upgrade. After moving
or cloning a workspace, changing backend location or IDE profile, run **Enable
Automatic Context** again to recreate its machine-specific link.

## Diagnose Runtime Issues

| Symptom | Check |
| --- | --- |
| Backend offline / model not ready | **Diagnose Setup**, **Start Backend**, reported `backend.log`. |
| No fresh context | Rule activation, command approval and current invocation; start a new chat. |
| Slow retrieval | First model load, **TokenWise Index**, backend version, budget/candidate settings. Saved updates and neural inference take time. |
| Remote/virtual folder rejected | Open a trusted local drive folder. A locally backed IDE storage scheme alone is not a remote repository. |
| Only initializer in overview | Matching current backend/extension, source root, indexed count and coverage warnings. |
| CO2 disabled/pending/unavailable | Displayed error/state and **Enable Carbon Estimation**. Update backend and repeat; prepared context remains usable. |
| Carbon error names zero size/latency | Current 0.6.8 permits zero/unset automatic values. Update older installs; positive overrides must be valid. |
| Rules/JSON conflict | Fix the named malformed file or preserve customized launchers under another name; do not discard unrelated configuration. |

Carbon settings are assumptions, not automatically detected agent properties.
Blank GPU and zero/unset size/latency use registered features; zero benchmark
scores remain valid explicit values. Automatic estimates are not written into
`latest.json` or sent as agent instructions.

Network policies must permit the dependency/model hosts. TokenWise does not bypass
corporate controls. Missing native libraries on Linux must be provided by the OS.
Native macOS/Linux operation still needs validation.

## Stop or Remove TokenWise

To stop automatic retrieval/indexing, retain your existing config properties and
set `.agents/tokenwise.json` `enabled` to `false`. For manual integration removal,
remove only TokenWise's rule/handler, not unrelated workspace configuration.

For immediate visible cleanup:

1. Finish active agent/setup commands.
2. Run **TokenWise: Remove All Local Data**, confirm and wait.
3. Read preserved-file warnings in **Output > TokenWise Cleanup**.
4. Uninstall and fully restart the editor when required.

Ordinary uninstall invokes ownership-aware cleanup when editor removal completes;
a background worker can finish large deletions. It is not necessarily immediate.
Owned environments/models, registration/logs/processes, unchanged generated rules,
hook/config entries, links and runtime state can be removed while unrelated data remains.

Customized files, malformed config, inaccessible drives, unverifiable processes,
checkout backends, Python itself and shared caches can remain. Partial cleanup
retains a small registry/report for diagnosis. Editor history, backups, Git
history and downloaded installers are not wiped. Zero traces cannot be guaranteed.

Keep configured folders/drives available. When migrating from 0.4.0, install and
reload the current release once first so storage can be tracked; open older
configured folders if absent from the IDE's workspace history.
