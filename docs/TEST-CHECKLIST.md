# TokenWise Final Test Checklist

Use this after extracting the final ZIP to `E:\A A SPL3\new_september5\TokenWise`.

## A. One-time setup

```powershell
Set-Location -LiteralPath 'E:\A A SPL3\new_september5\TokenWise'
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\copy-model.ps1
.\scripts\setup.ps1
.\scripts\verify.ps1
```

All three commands must complete without an error.

## B. Start backend

```powershell
.\scripts\run-backend.ps1
```

Do not close this terminal.

## C. Health check

In another PowerShell:

```powershell
Set-Location -LiteralPath 'E:\A A SPL3\new_september5\TokenWise'
Invoke-RestMethod 'http://127.0.0.1:8000/health' | Format-List
```

Pass condition:

```text
status              healthy
model_loaded        True
carbon_models_loaded True
```

## D. Automated full smoke test

```powershell
.\.venv\Scripts\python.exe .\scripts\smoke_test.py --full
```

Pass condition:

```text
FULL_SMOKE_OK
```

## E. VS Code UI test

```powershell
code .\vscode-extension
```

Press F5. In Extension Development Host open the project's `Test_project` folder.

### Test 1 — health

Command Palette -> `TokenWise: Check Backend Health`

Expected: healthy, pruner loaded, carbon models loaded.

### Test 2 — authentication pruning

Open `services/auth_service.py`.

Command Palette -> `TokenWise: Prune Current File`

Query:

```text
Find the account lockout and successful authentication logic.
```

Check:

- result panel opens;
- original/pruned token counts are non-zero;
- pruned count does not exceed original;
- relevance is in [0,1];
- carbon section appears;
- Copy Pruned Context works.

### Test 3 — payment pruning

Open `services/payment_service.py`.

Query:

```text
Find payment retry and timeout handling.
```

Check that retry/timeout logic is represented in the retained context.

### Test 4 — repository context

Open `app.py`.

Command Palette -> `TokenWise: Build Repository Context`

Query:

```text
Trace authentication and payment processing from the application entrypoint.
```

Check:

- active `app.py` is Tier 1;
- service files appear as direct/relevant context;
- transitive model/util/config files can appear as Tier 3 signatures;
- packed token count is <= configured repository token budget;
- Carbon impact card appears;
- Copy Unified Context works.

## F. Optional deterministic-goal check

Leave `TokenWise: Enable Local Goal Model` disabled. Repository mode should work without Ollama or LM Studio and should not wait for a local LLM connection timeout.

## G. Optional local-LLM check

Only if Ollama/LM Studio is configured:

- enable `TokenWise: Enable Local Goal Model`;
- set endpoint/model name;
- repeat repository context test;
- confirm a structured goal is generated and pruning still succeeds.
