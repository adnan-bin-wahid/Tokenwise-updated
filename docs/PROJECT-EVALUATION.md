# TokenWise Project Evaluation

This document records the cleanup and technical audit performed on the submitted project snapshot. It is intentionally conservative: it distinguishes what the code currently implements from what the underlying research papers report.

## Overall assessment

The project has a coherent research-to-tool story: task-aware code context pruning is combined with non-intrusive prompt-level sustainability estimation inside a VS Code workflow. The final cleaned snapshot is substantially more suitable for an SPL-3 demonstration than the original archive because the runtime path is now explicit, bounded, testable, and separated from training/research-only material.

The core runtime is:

```text
VS Code -> FastAPI -> Goal compilation -> Python repository retrieval
        -> Qwen3-Reranker-0.6B SWE-Pruner model -> bounded context
        -> trained XGBoost/Ridge carbon estimator -> result dashboard
```

## Important fixes made

### Packaging and repository hygiene

- Corrected the root `.gitignore`; the original rule could exclude the entire SWE-Pruner backend instead of only the large checkpoint.
- Removed caches, compiled outputs, temporary reports, duplicate runtime carbon artifacts, upstream training/evaluation directories not needed to run TokenWise, and the extension's generated `dist`/`node_modules` output.
- Kept the carbon training pipeline and benchmark data because they support research reproducibility.
- Consolidated proposal and paper PDFs under `docs/`.
- Added deterministic PowerShell setup/copy/verify/run scripts.

### Neural-pruner runtime

- Kept the actual Qwen3-Reranker-0.6B-derived TokenWise/SWE-Pruner architecture and tokenizer/config assets.
- Added a local backbone `config.json`, preventing an unnecessary Hugging Face network lookup during local model construction.
- Added explicit offline model loading.
- Added CPU/CUDA device selection through `TOKENWISE_DEVICE` and the packaged run script.
- Corrected document relevance output to expose an actual [0,1] probability instead of a raw log-probability.
- Corrected line-score aggregation to average token scores per line and handle LF/CRLF offsets correctly.

### Repository-context mode

- Made the current support boundary explicit: repository AST indexing is Python-only.
- Corrected active-file resolution and workspace validation.
- Expanded graph traversal to two hops so a real Tier 3/transitive layer can exist.
- Added a hard repository token budget.
- Restricted context packing to retrieved/ranked candidates rather than silently processing the whole repository.
- Added active-file/direct-dependency/transitive tiering.
- Kept Tier 3 as signatures-only context.
- Made local LLM goal synthesis opt-in. Without an Ollama/LM Studio server, deterministic goal generation now returns immediately rather than waiting for a failed network request.

### Carbon estimation

- Removed the untrained hand-written heuristic fallback from the VS Code path. If trained artifacts are unavailable, the UI now reports that instead of inventing a carbon number.
- Corrected normalized MMLU-Pro/BBH handling to the [0,1] scale used by the local feature pipeline.
- Resolved artifact paths relative to the installed backend instead of the current shell directory.
- Pinned the serialization-sensitive runtime packages: scikit-learn 1.9.0 and XGBoost 3.3.0.
- Uses XGBoost in the configured interpolation range (7B-111B) and Ridge outside it.
- Uses a benchmark-backed in-range model (`meta-llama-3-8b-instruct`) as the default demonstration target instead of relying on unpublished GPT-4o size/hardware assumptions.
- Normalizes predictions to the local benchmark pipeline's reference 256-input/128-output-token workload before scaling phase energy to the actual request length. This makes before/after context comparisons meaningful while avoiding request token counts being used twice.
- Added carbon before/after display for both single-file and repository-context workflows.

### Demo workspace

- Repaired the corrupted authentication service.
- Repaired the corrupted/duplicated payment service.
- Preserved retry, timeout, invalid-input, audit and session behavior needed for realistic pruning queries.
- Removed deprecated naive UTC timestamp creation.

### VS Code UX and safety

- Removed the unsafe action that inserted pruned context directly into source code. Pruned output contains contextual elisions and is not a patch.
- The panel now provides copy actions only.
- Fixed panel message handling when a Webview panel is reused.
- Added clearer backend-health diagnostics for pruner model, carbon models and device.

## What is intentionally not in the ZIP

`model.safetensors` is excluded because it is very large. The rest of the local model directory is present. Use `scripts/copy-model.ps1` to copy and SHA256-verify the existing checkpoint supplied by the user.

## Verification performed before packaging

The cleaned snapshot passed these checks in the packaging environment:

- Python `compileall` for backend, carbon engine, scripts and demo project.
- `unittest` demo authentication/payment tests: 6/6 passed.
- Offline carbon artifact load and prediction checks.
- Verification that doubling input context doubles the prefill component under the packaged reference-workload normalization.
- Python repository index creation on `Test_project`.
- Dependency graph expansion from `app.py`, including direct and transitive files.
- TypeScript syntax/transpilation validation of every extension source file.

A complete live neural inference could not be executed during packaging because the submitted ZIP intentionally omitted `model.safetensors`. The user's post-copy validation path is therefore explicit: `scripts/verify.ps1`, start the backend, then `scripts/smoke_test.py --full`.

## Current scientific/engineering limitations

### 1. Carbon engine is SEAL-derived, not an exact SEAL reproduction

The local artifacts have their own metrics:

| Artifact | MAPE | R2 |
|---|---:|---:|
| XGBoost prefill/interpolation | 13.83% | 0.879 |
| XGBoost decode/interpolation | 22.41% | 0.246 |
| Ridge prefill/extrapolation | 22.08% | 0.993 |
| Ridge decode/extrapolation | 46.59% | 0.901 |

The local external validation report contains two Llama-2 samples and an average relative error of about 17.46%. These numbers are the project's artifact metrics and should not be presented as the SEAL paper's results.

The decode interpolation model has weak R2 and the extrapolation decoder has high MAPE. Carbon output must therefore be presented as an **approximate sustainability indicator**, not physical meter-grade telemetry.

### 2. Repository indexing is Python-only

Single-file neural pruning can process text/code generally, but the current AST graph/index/repository tiering implementation uses Python's `ast` module. Do not claim full JavaScript/TypeScript/Java repository graph support in a presentation unless it is implemented later.

### 3. Pruned context is not guaranteed to be executable source

Line-level pruning is designed for LLM context. Elision markers can make the returned snippet unsuitable as a direct source-code replacement. This is why the cleaned extension only copies context and never applies it as an edit.

### 4. Carbon savings currently model request-level inference, not full agent trajectories

The extension compares prompt input tokens before and after pruning while holding expected output tokens fixed. It does not attempt to predict future reductions in agent rounds. This is deliberately more defensible than assuming a fixed round reduction from the SWE-Pruner paper.

### 5. Optional local LLM is not required

The project contains deterministic goal compilation, so an additional local LLM should be described as an enhancement, not a mandatory dependency.

## Presentation-safe claim

A defensible summary is:

> TokenWise integrates a SWE-Pruner-derived local neural context-pruning pipeline with a SEAL-derived trained carbon-estimation layer inside VS Code. It reduces task-irrelevant code context, builds bounded Python repository context, and estimates the approximate prompt-level energy/carbon impact of sending raw versus pruned context.

Avoid claiming that TokenWise reproduces the exact benchmark scores of either source paper unless you independently run those papers' evaluation protocols.
