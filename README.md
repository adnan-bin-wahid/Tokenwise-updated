# Tokenwise-updated

**Sustainable Context Optimization for Coding Agents**

TokenWise is an academic SPL-3 project that combines two research ideas in one developer workflow:

1. **SWE-Pruner-derived task-aware code pruning** — a local Qwen3-Reranker-0.6B-based neural skimmer reduces irrelevant repository context at line level before the context is passed to a coding LLM.
2. **SEAL-derived prompt-level energy/carbon estimation** — trained phase-specific regressors estimate prefill and decode energy from benchmark-derived features and convert energy to approximate CO2 impact.

The user-facing client is a VS Code extension. The local FastAPI backend performs neural pruning, Python repository indexing/retrieval, bounded context packing, and carbon estimation.

> The large `model.safetensors` weight is intentionally excluded from this ZIP. Copy it into the project with `scripts/copy-model.ps1` before running the backend.

## Project layout

For automatic context in Antigravity IDE, open any local Windows Python
repository and run **TokenWise: Enable Automatic Context**. Select the complete
backend installation once; repositories can live outside the TokenWise checkout.
Follow [the integration guide](docs/ANTIGRAVITY.md). TokenWise builds bounded
repository context from the prompt through an always-on agent-command rule,
or a `PreInvocation` hook on supporting IDE builds. Activity is visible in the
extension. Other workspace rules and hook handlers are preserved.

```text
TokenWise/
├─ scripts/                         Windows setup, verification, run and smoke-test helpers
├─ vscode-extension/                VS Code client
├─ swe-pruner/swe-pruner/           Local FastAPI backend + neural-pruner runtime
│  ├─ model/                         Tokenizer/config files; add model.safetensors here
│  ├─ carbon_artifacts/              Trained XGBoost/Ridge runtime artifacts
│  └─ src/swe_pruner/                Backend implementation
├─ carbon-engine/                   Reproducibility pipeline for the carbon models
├─ Test_project/                    Small Python workspace for end-to-end demonstrations
└─ docs/                            Proposal, research papers, evaluation and test checklist
```

## What the cleaned version does

- Local single-file/selection neural pruning.
- Goal-conditioned repository context construction for **Python workspaces**.
- Two-hop import/call graph expansion and task-conditioned candidate ranking.
- Three-tier packing:
  - Tier 1: active file, lightly pruned.
  - Tier 2: direct/high-relevance dependencies, more aggressively pruned.
  - Tier 3: transitive/low-relevance files, signatures only.
- Hard repository context token budget.
- Optional local LLM goal synthesis. It is **disabled by default**, so TokenWise does not wait for Ollama/LM Studio when none is running.
- Trained carbon estimation only; no fabricated heuristic fallback.
- Before/after carbon estimates in both single-file and repository-context views.
- Copy-only result workflow. Pruned context is not automatically inserted into source files because it is context, not a patch.

## Required software

Install these first:

- Windows 10/11
- **Python 3.12.x**
- Node.js LTS + npm
- VS Code

Python 3.14 is not the target environment for this project. The packaged setup deliberately uses Python 3.12 for model/dependency compatibility.

## 1. Extract the ZIP

If the ZIP is saved in:

```text
E:\A A SPL3\new_september5
```

extract it so this file exists:

```text
E:\A A SPL3\new_september5\TokenWise\README.md
```

Then open PowerShell and run:

```powershell
Set-Location -LiteralPath 'E:\A A SPL3\new_september5\TokenWise'
Set-ExecutionPolicy -Scope Process Bypass -Force
```

## 2. Add the missing model weight

The source weight is expected at:

```text
E:\A A SPL3\new_september5\main\swe-pruner\swe-pruner\model\model.safetensors
```

Recommended command:

```powershell
.\scripts\copy-model.ps1
```

The script copies the file and verifies source/destination SHA256 hashes.

Equivalent direct copy command:

```powershell
Copy-Item -LiteralPath 'E:\A A SPL3\new_september5\main\swe-pruner\swe-pruner\model\model.safetensors' -Destination 'E:\A A SPL3\new_september5\TokenWise\swe-pruner\swe-pruner\model\model.safetensors' -Force
```

## 3. Install the project

```powershell
.\scripts\setup.ps1
```

The setup script:

- creates `.venv` with Python 3.12;
- installs PyTorch;
- installs the backend in editable mode;
- installs VS Code extension dependencies with `npm ci`;
- compiles TypeScript.

GPU selection is automatic. To force CPU:

```powershell
.\scripts\setup.ps1 -TorchMode cpu
```

To force the CUDA 12.6 PyTorch wheel:

```powershell
.\scripts\setup.ps1 -TorchMode cu126
```

## 4. Verify the installation

```powershell
.\scripts\verify.ps1
```

This checks:

- Python syntax;
- demo unit tests;
- carbon artifacts and request-length behavior;
- repository index/graph behavior;
- local tokenizer/config availability;
- VS Code TypeScript compilation.

## 5. Start TokenWise backend

```powershell
.\scripts\run-backend.ps1
```

Keep that PowerShell window open. The backend listens only on:

```text
http://127.0.0.1:8000
```

The default device is `auto`. You can force a device:

```powershell
.\scripts\run-backend.ps1 -Device cpu
```

or:

```powershell
.\scripts\run-backend.ps1 -Device cuda
```

## 6. Check backend health

Open a second PowerShell window:

```powershell
Set-Location -LiteralPath 'E:\A A SPL3\new_september5\TokenWise'
Invoke-RestMethod 'http://127.0.0.1:8000/health' | Format-List
```

A fully ready system should report:

```text
status               : healthy
model_loaded          : True
carbon_models_loaded  : True
```

## 7. Run the full API smoke test

With the backend still running:

```powershell
.\.venv\Scripts\python.exe .\scripts\smoke_test.py --full
```

Expected final marker:

```text
FULL_SMOKE_OK
```

The test exercises `/health`, `/estimate-carbon`, `/prune`, and `/prune-workspace`, including repository token-budget enforcement.

## 8. Run the VS Code extension

From the project root:

```powershell
code .\vscode-extension
```

Then:

1. Press **F5** in VS Code.
2. A new **Extension Development Host** window opens.
3. In that new window, open:
   `E:\A A SPL3\new_september5\TokenWise\Test_project`
4. Open `services\auth_service.py`.
5. Press `Ctrl+Shift+P` and run `TokenWise: Check Backend Health`.
6. Run `TokenWise: Prune Current File` with:
   `Find the account lockout and successful authentication logic.`
7. Open `services\payment_service.py` and try:
   `Find payment retry and timeout handling.`
8. Open `app.py`, then run `TokenWise: Build Repository Context` with:
   `Trace authentication and payment processing from the application entrypoint.`
9. Confirm the repository panel shows Tier 1/2/3 files, a packed token count within the configured budget, and approximate carbon impact when carbon estimation is enabled.

## Optional: local LLM goal synthesis

TokenWise works without Ollama/LM Studio. Its deterministic goal compiler is the default.

If you have an OpenAI-compatible local endpoint and want LLM-generated structured goals, enable VS Code setting:

```text
TokenWise › Enable Local Goal Model
```

Then configure the URL/model settings if necessary.

## Carbon-estimation scope

The runtime estimator is **SEAL-derived**, not a claim of exact reproduction of the SEAL paper's reported models. This repository contains locally trained XGBoost/Ridge artifacts and their own validation metrics under:

```text
swe-pruner\swe-pruner\carbon_artifacts\
```

For the default benchmark-backed `meta-llama-3-8b-instruct`, input-context reduction primarily reduces **prefill** energy. The expected output token count is held constant, so decode savings can legitimately be zero.

Current artifact metrics and limitations are documented in `docs/PROJECT-EVALUATION.md`.

## Research material

- `docs/papers/SWE-Pruner.pdf`
- `docs/papers/SEAL-Carbon-Estimation.pdf`
- `docs/TokenWise-Proposal.pdf`

## License

See `LICENSE`. Research papers and model assets remain subject to their respective authors' and distributors' terms.
