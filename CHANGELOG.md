# Changelog

## 0.6.2 - 2026-10-05

### Added

- Controlled all-Python/manual-selection/automatic-context comparison command,
  exact packet counts, copy controls, JSON export, and optional matched-scenario
  carbon estimates. The manual selection does not bias automatic retrieval.
- Three independent demonstration repositories with 22 executable tests,
  a teacher guide, a blank scoring worksheet, and real-backend verification.
- Bounded same-chat user-topic hints for recognized native follow-ups; explicit
  topic switches and new chats do not inherit unrelated prior topics.
- Fallback-rule instructions for same-chat references and clarification when
  their subject is missing; this is not a cross-chat memory feature.
- Short task-matched source bodies are retained without extra neural passes,
  and configuration dependencies get reserved candidate slots so graph callers
  cannot crowd out constants needed to interpret an implementation.

### Safety and Evaluation

- Baseline exports reject oversized repositories, invalid selections, and
  changed snapshots rather than silently presenting incomplete all-code.
- Carbon predictions and source markers are not cloud-agent answer grading.
- Install/update the matching backend and re-enable workspaces after upgrading.

## 0.6.1 - 2026-10-05

### Fixed

- Broad project overview prompts now use a dedicated, deterministic retrieval
  mode instead of treating words such as `FULL` and `PROJECT` as identifiers.
- Overviews include bounded root documentation/package information and
  representative entry points, core modules, data models, and tests, including
  components not connected to the selected file. Package initializers have
  lower priority; initializer-only repositories show an explicit warning.
- Source reduction compares raw and retained source, not raw source against
  formatting overhead. Genuine increases are labeled as increases.
- Automatic result views now request before/after CO2 and energy estimates
  from the actual local backend, with visible pending/disabled/error states.
- Carbon comparisons use the same selected files and formatting before and
  after packing, retain signed changes, and cannot overwrite a newer result.

### Added

- Overview coverage warnings, retained-source/overhead counts, and a matched
  unpruned-context baseline. README/package edits invalidate overview caches.
- Fair-share overview packing, nested Markdown fence handling, and regression
  tests for tiny repositories, small budgets, stale estimates, and backend errors.
- Normalized project-document line endings so Windows agent tool output matches
  the context whose token count was checked.
- Isolated real-model HTTP/carbon verification and portable result-panel checks.

### Upgrade

- Install the new VSIX, reload, then update the managed backend through
  **TokenWise: Set Up Backend**. Updating only the extension cannot change
  retrieval in an already running older Python service.
- These remain approximate configured-scenario carbon estimates, not measured
  Antigravity emissions. Bounded overviews do not invent missing implementation.

## 0.6.0 - 2026-10-05

### Added

- Background Python indexing for configured, trusted local workspaces, with
  debounced file create/save/delete events and package rename handling.
- Local `/index-workspace` synchronization, independently leased watchers,
  ordered updates, and periodic content-verified reconciliation of missed events.
- Cached per-file term counts, symbol locations, signatures, and bounded
  tokenizer-specific token counts; reusable lexical postings and dependency graphs.
- A synthetic retrieval benchmark and tests covering lifecycle, cache freshness,
  exact-query isolation, and bounded update batches.
- Seven numbered setup steps, structured recovery advice, **Retry Failed Step**,
  **Retry Enable**, and validated dependency checkpoints for resumable setup.
- Recovery of complete verified partial downloads and damaged private environments.
- Managed backend update prompts and automatic watcher reconnection after setup.

### Changed

- Live watched requests no longer walk the repository. Unchanged source metadata
  survives edits elsewhere; content fingerprints invalidate affected caches.
- Already configured backends can warm on workspace open without install/download
  consent prompts. Disabling context, closing a folder, or cleanup stops watchers.
- Expired/missing watchers and older backends retain conservative retrieval.
  Neural pruning behavior and Antigravity's rule/tool integration are unchanged.
- Successful managed upgrades stop the previous process only after installation
  succeeds and only through existing strict process-identity checks. Checkout
  backends and unrelated processes are never stopped by this workflow.

## 0.5.0 - 2026-10-05

### Added

- Automatic editor uninstall hook and a self-contained cleanup worker that
  survives extension deletion and the editor's short lifecycle timeout.
- Tracked workspace/profile inventory, including discovery of older configured
  repositories in local IDE workspace history.
- Removal of managed environments/model/pip caches, owned backend/setup
  processes, generated integration files, context records, and TokenWise settings.
- **TokenWise: Remove All Local Data** for immediate cleanup and visible warnings.
- Comment-preserving JSONC settings edits, path/junction guards, PID identity
  checks, exact ignore restoration, and preservation of unrelated/customized data.
- Native Windows isolated Antigravity uninstall verification.

### Changed

- New managed installs keep pip downloads in private TokenWise storage, not the
  shared user pip cache.
- Setup retains ownership history across platform/rule changes so old generated
  launchers can be removed later.

### Limits

- Complete editor removal may require a full restart; clicking Uninstall is not
  a guaranteed immediate cleanup event.
- Customized/unavailable files, existing backend checkouts, Python itself,
  editor-owned history, and old shared caches are not indiscriminately deleted.
- Users upgrading from 0.4.0 should reload 0.5.0 once before uninstalling and open
  old configured repositories not present in the editor's workspace history.

## 0.4.0 - 2026-10-04

First public Windows-tested beta for Antigravity users.

### Added

- Managed local backend installation from the VSIX, without a source checkout,
  Node.js, Git, F5, or a manually started server.
- Consent-based CPU dependency and model downloads, pinned model checksums,
  download progress, resumable model transfers, cancellation, and retry.
- Automatic context setup for arbitrary local Python repositories, with one
  centrally managed backend shared across workspaces.
- Setup diagnostics, backend warm-up, a bundled guide, and first-run onboarding.
- Portable macOS/Linux launchers; native platform validation is still pending.
- Shareable release artifacts, SHA-256 checksums, and draft-first publishing.

### Fixed

- Local Antigravity `vscode-userdata` storage is no longer mistaken for a remote
  workspace.
- Portable Python launchers correctly handle Windows paths containing spaces.
- Python launcher resolution uses the real executable for owned setup-process
  cancellation and installation-lock cleanup.
- Existing unrelated rules, hook handlers, and context settings are preserved.

### Validation and Limits

- 51 Node tests and 36 Python tests cover setup, retrieval integration, downloads,
  configuration preservation, cancellation, and failure handling.
- A fresh managed environment, CPU cold start, and bounded retrieval from two
  repositories outside the checkout were tested on Windows.
- The fresh install reused checksum-verified local weights. A real HTTPS range
  request was verified; a full 1.35 GB network download was not re-run.
- Stable Antigravity uses an agent rule/tool-output fallback, not guaranteed
  interception before the first model call.
- Remote/virtual workspaces are unsupported. Carbon values remain estimates,
  not measurements of a user's cloud-model consumption.
