# Development and Source Setup

Normal users should follow the root README and install the VSIX. These commands
are for working on TokenWise itself.

## Windows Backend Checkout

Install 64-bit Python 3.12 and Node.js/npm, then from the checkout root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/setup.ps1 -TorchMode cpu
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/copy-model.ps1 -Source 'C:\path\to\model.safetensors'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Use the official pinned weights linked in the root README or an already verified
local copy. The model is not committed to Git. Do not copy `.venv` between machines.
For an end-user environment, use the extension's managed installer instead.

## Tests

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path 'swe-pruner\swe-pruner\src')
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
cd vscode-extension
npm test
npm run prepare-backend
cd ..
```

With the original checkout backend already running:

```powershell
node scripts/verify-portable-context.cjs
.\.venv\Scripts\python.exe scripts/verify_antigravity.py
```

The verifiers do not call Antigravity's cloud model. The portable verifier uses
two temporary repositories outside the checkout and leaves real workspace
activity alone. The original demo verifier marks its activity `verification: true`.

## Try the Background Index

Background indexing is included in 0.6.0. From `vscode-extension`, run
`npm run prepare-backend` and `npm run compile`, then press F5. In the development
host, open a trusted local Python repository and run **TokenWise: Enable Automatic
Context** if that folder is not configured yet. A registered backend is required;
background indexing never performs first-run installation or downloads itself.

The Python service must run the updated source too. For a checkout backend,
stop its existing process in the terminal where you started it, then start it
again with your usual backend launch command. Do not terminate unrelated Python
processes. **Start Backend** reuses a healthy running service; it does not restart
one to reload source changes. Reloading the extension alone is insufficient.

If using a managed backend, run **TokenWise: Set Up Backend** and approve
**Install Backend** from the updated development extension.
The installer uses a version-and-bundle-hash-specific directory and reuses
verified model downloads. Workspace links resolve the central registration,
so repositories do not need a different link for each backend bundle.
Successful setup reconnects the watcher to the newly registered service.

1. Open **Output > TokenWise Index** and wait for the Python file count.
2. Ask an ordinary Antigravity question. After warm-up, `/prune-workspace`
   reports `index_cache_hit: true` and `retrieval_cache_hit: true`.
3. Save a Python source edit. The output fingerprint should change; ask again
   and check that the excerpts reflect the saved edit.
4. Try a differently worded prompt: search data can be reused, but the complete
   answer cache must miss (`context_cache_hit: false`). Repeat the exact prompt
   without edits to check a complete context-cache hit.
5. Create/delete a Python file or rename a package directory. Check the index
   count and subsequent context; unchanged source metadata remains reusable.

Cache flags are raw API diagnostics; the automatic activity record is not a dump
of every backend field. A file-save update is debounced by 150 ms and becomes
visible after acknowledgment. Unsaved editor buffers are not indexed.

The extension sends batched relative paths (at most 512 per request) to the local
`POST /index-workspace` endpoint. A per-window watcher ID and increasing sequence
number prevent delayed updates from reactivating closed sessions. Heartbeats
renew a 90-second lease every 30 seconds. The backend checks for reconciliation
every 15 seconds; due repositories receive a full content-verified scan after
120 seconds. Without a live watcher, each retrieval checks the repository first.
Per-repository locks and copy-on-write snapshots isolate source updates from
in-flight retrieval. Index/search caches retain at most eight repositories;
complete contexts retain at most 16 exact requests; per-file token counts retain
at most eight tokenizer/text pairs. Eviction causes rebuilding, not stale reuse.

## Overview and Carbon Verification

After compiling the extension, with checkout dependencies and pinned local
weights installed, run from the checkout root:

```powershell
.\.venv\Scripts\python.exe scripts/verify_context_results.py --report tmp/context-results.json
```

This starts its own backend on a temporary loopback port. It checks project-wide
overview selection, a focused real-neural query, token bounds, README cache
invalidation, the initializer-only regression, and CO2 before/after through the
compiled extension API client. It stops only its own backend and removes the
sample repositories. It neither downloads weights nor calls Antigravity's cloud.
The optional ignored JSON report can be used for result-panel browser verification.

For portable panel checks, install Playwright and its Chromium browser in your
development environment (not needed by extension users), then run:

```powershell
node scripts/verify-result-panel.cjs tmp/context-results.json
```

An optional third argument can be an existing Playwright module path. The check
renders the compiled panel with real verification results at desktop and narrow
widths, checks overflow/overlapping stats, CO2 values, sparse-project warnings,
and the copy-button message. Screenshots are saved under `tmp/result-panel/`.
The editor bridge is stubbed, so this does not prove Antigravity cloud consumption.

Overview requests bypass neural pruning and use representative structural
coverage. Root documents are allowlisted, byte-bounded, and included in the
exact-cache fingerprint; Python indexing/watcher behavior is unchanged.
Response fields distinguish `original_tokens`, `retained_source_tokens`,
`pruned_tokens`, `context_overhead_tokens`, and `raw_context_tokens`. The last
field counts the same formatted bundle with unpruned source for carbon comparison.

## Retrieval Benchmark

From the checkout root:

```powershell
.\.venv\Scripts\python.exe scripts/benchmark_retrieval.py --files 1000 --queries 50
```

This creates and removes a temporary synthetic repository. It reports cold index
preparation, warm index/lexical/graph queries, a one-file update, and the
conservative no-watcher fallback. It asserts zero repository walks/AST parses
on warm watched requests and exactly one reparse for a one-file content edit.
These timings exclude neural pruning, HTTP transport, model loading, and
Antigravity's cloud response; do not present them as end-to-end prompt latency.

A Windows run on 2026-10-05 with 1,000 small generated files and 50 distinct
queries measured 0.559 ms median / 0.810 ms p95 for watched queries, versus
328.978 ms median for the content-verified no-watcher fallback. Cold index/search
preparation took 5.795 seconds; a one-file edit plus search preparation took
16.876 ms and reparsed one file. Hardware, file sizes, and filesystem caches
affect results. This is a synthetic measurement, not an Antigravity speed guarantee.

## Shareable Package

For installer changes, prepare the backend bundle and run the isolated native
installer/retry/neural HTTP check (requires network access and pinned local weights):

```powershell
.\.venv\Scripts\python.exe scripts/verify_managed_setup.py
```

It creates a fresh private environment in an ignored temporary release directory,
installs real CPU dependencies, deliberately fails the model step, then retries
using checksum-verifiable local weights. It checks reuse of all three dependency
checkpoints, loads the real neural model, and exercises warm indexing, bounded
retrieval, exact-query caching, and edit invalidation over loopback HTTP. It
stops its own backend and removes its temporary storage. It does not use or stop
your running backend, alter real workspace activity, or call Antigravity's cloud
model. A full 1.35 GB network weight transfer is not part of this verifier.

`npm run package` prepares an integrity-manifested backend bundle, compiles the
extension, creates the VSIX, and writes the release folder under `releases/`.
Only explicitly selected backend files are bundled; weights, virtual
environments, `.tokenwise` data, developer tests, and research PDFs are excluded.
Generated bundle/release outputs are ignored by Git.

For uninstall changes, build first and run the native Windows smoke check:

```powershell
node scripts/verify-uninstall.cjs
```

It uses a separate temporary Antigravity user-data/extension directory and a
harmless private Python process. It never uninstalls your real TokenWise extension
or touches real repository activity. The uninstall hook has no VS Code API
dependency and starts a self-contained worker before the editor deletes its files.
The verifier launches isolated IDE instances and closes only those processes.
CLI removal can defer marking an extension obsolete until the next IDE startup;
the verifier exercises that startup followed by a complete restart as needed.

Public registry publishing and native macOS/Linux verification are separate
release gates. This repository does not claim that a local package build publishes
to Open VSX or the Visual Studio Marketplace.

## Classroom Demonstration Checks

From the checkout root, after compiling the extension:

```powershell
.\.venv\Scripts\python.exe demonstration/run_checks.py
.\.venv\Scripts\python.exe scripts/verify_demonstration.py
```

The first checks 28 example tests and four runnable apps. The second starts an
isolated backend with real local weights/carbon artifacts, exports three context
strategies per project, exercises real selected-file/excerpt pruning through the
compiled service, and checks multi-turn native-hook state/new-chat isolation with
a generated USER transcript. It stops only its own process. Results are ignored under
`demonstration/results/`; source markers are not semantic agent-answer scores.
See `demonstation.md` for the three primary input scenarios and the optional
fresh-chat answer-quality protocol. The replay command requires 0.6.3; update the
backend as well. No automated verifier here calls Antigravity's cloud model.

The panel browser verifier also accepts a demonstration `comparison.json` as its
first argument. It checks desktop/narrow layouts and all copy/export messages.
It also accepts `demonstration/results/pruning-inputs.json` to check repository,
selected file at two thresholds, selected excerpt, native-history, and new-chat
result views. Use `scripts/verify_demonstration.py --inputs-only` to retry just
these real input paths without regenerating the optional packet comparisons.
