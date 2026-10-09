# TokenWise Test and Verification Report

## 1. Snapshot and Scope

**Version:** 0.6.8, Windows beta. **Verification date:** October 9, 2026.
**Implementation commit:** `573b82b` (the tagged 0.6.8 release).

The repeated suites used Node.js 22.12.0 and Python 3.12.4 on Windows 11.

The release checks were repeated while preparing this report. The figures below
are observed test outcomes, not planned coverage or predicted results. The study
harness and report files added afterward do not change the extension/backend
test counts. See [comparative_study.md](comparative_study.md) for research
measurements; software tests and comparative experiments answer different questions.

## 2. Results

| Verification group | Discovered / exercised | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Extension automated tests | 193 | 193 | 0 | 0 |
| Backend automated tests | 142 | 141 | 0 | 1 |
| Demonstration application tests | 20 | 20 | 0 | 0 |
| Browser fixture views | 10 | 10 | 0 | 0 |

The three automated test suites contain **355 discovered tests: 354 passed and
one skipped**. The **ten browser views are separate UI verification scenarios**,
not ten additional backend tests. The demonstration's deterministic `app.py`
execution also passed; it is not an extra unittest test case.

There was no failing test in these runs. A passing suite is not proof that every
possible input is correct, and no line/branch code-coverage percentage was measured.

## 3. Extension Tests

Run from `vscode-extension`:

```powershell
npm test
```

The `pretest` script runs `npm run compile`, then Node's built-in test runner
executes `node --test tests/*.test.cjs`. Compilation and the test command both
completed successfully. The repeated TAP result was:

```text
tests 193
pass 193
fail 0
cancelled 0
skipped 0
todo 0
```

The eighteen test files exercise these areas:

| Area | Test files | Behaviors checked |
|---|---|---|
| Automatic activity | `automaticContext.test.cjs` | Valid/invalid activity records, input provenance, bounded memory metadata, old-record compatibility and freshness |
| Workspace integration | `automaticSetup.test.cjs`, `enableAutomaticContext.test.cjs` | Local/trusted workspaces, rules and launcher generation, preservation/ownership, portable transport and repeatable setup |
| Backend management | `backendManager.test.cjs`, `managedBackend.test.cjs` | Managed paths, startup/health, retryable installation state, verified downloads and diagnostics |
| Index synchronization | `repositoryIndexSync.test.cjs` | Background indexing, change events, refresh sequencing and synchronization boundaries |
| Context strategies | `compareContextStrategies.test.cjs`, `preparedComparisonApi.test.cjs` | Selected/all-code baselines, prepared-packet reuse, API validation and snapshot handling |
| Pruning and guidance | `pruningInputs.test.cjs`, `responseGuidance.test.cjs` | File/excerpt/repository scope, thresholds, source-line information and outgoing guidance contracts |
| Sustainability | `carbonComparison.test.cjs` | Before/after mapping, fixed assumptions, unavailable/error states, overhead and signed savings |
| Agent usage | `antigravityUsage.test.cjs`, `importAntigravityComparison.test.cjs` | Reported CLI counters, independent-session pairing, invalid logs and user labels |
| Result panel | `resultPanel.test.cjs` | HTML escaping, memory inspection, input traces, comparison states, copy/export messages and estimates |
| Distribution | `demoPackaging.test.cjs`, `icon.test.cjs` | One demo project, guides, manifest/checksum contracts and packaged PNG icon |
| Cleanup | `uninstall.test.cjs`, `uninstall-tracker.test.cjs` | Ownership validation, unrelated-file preservation, profile isolation, malicious paths, PID reuse, junction protection and detached cleanup |

These are automated contract/component checks. Many mock VS Code APIs, network
clients or process operations. They do not represent 193 live Antigravity chats,
193 fresh model downloads, or a complete native IDE end-to-end compatibility study.

## 4. Backend Tests

Run from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s swe-pruner/swe-pruner/tests -v
```

The repeated run reported:

```text
Ran 142 tests
OK (skipped=1)
Passed: 141
Failures: 0
Errors: 0
```

| Test file | Main coverage |
|---|---|
| `test_antigravity.py` | Hook/adapter request handling, workspace validation, events, budgets, activity recording and failure reporting |
| `test_conversation_memory.py` | Topic continuity, standalone requirements, resets, supersession, bounded history, native identity, fallback transport, opt-out, cache isolation and real-tokenizer budgets |
| `test_demonstration.py` | Comparison packets, selected source scopes, demo contracts, threshold/input traces and integration fixtures |
| `test_installer.py` | Checkpoints, integrity checks, retry/resume behavior, dependencies, invalid state and reusable verified downloads |
| `test_overview.py` | Broad project overviews, source/document selection, scaffold warnings, budgets and snapshot changes |
| `test_query_focus.py` | Topic extraction, exclusions and prevention of excluded-topic contamination |
| `test_repository_cache.py` | Incremental AST/search caches, watched/unwatched behavior, file changes, reconciliation and path boundaries |
| `test_response_guidance.py` | Task-aware outgoing instructions, opt-out, packet overhead and matched token accounting |

Backend contracts use controlled model doubles where deterministic outcomes are
required. Real tokenizer checks count actual tokens; they do not independently
validate the learned model's relevance accuracy. Installer fixture logs simulate
installation paths and are not evidence that every operating system was tested.
Expected invalid-input error messages and deprecation warnings occurred during
negative tests; these were not test failures.

### The One Skipped Test

**Test:**
`test_repository_cache.RepositoryCacheTests.test_retargeted_symlink_removes_previous_cached_content`

**Recorded reason:** `This Windows account cannot create file symlinks`.

This test requires creating a file symlink, changing its target and verifying that
cached content is invalidated. The current Windows account lacked that permission,
so unittest skipped it. It did not pass and must not be counted as a successful
symlink-retargeting validation. Re-run under a Windows account/environment with
file-symlink permission, or a supported Unix environment, to close that gap.
Other path/ownership tests passing does not substitute for this particular check.

## 5. Demonstration Tests

Run from the project root:

```powershell
.\.venv\Scripts\python.exe demonstration/run_checks.py
```

Observed summary:

```text
tokenwise_demo: 20 tests passed; app.py passed
```

The runner invokes standard-library unittest discovery in the demo's `tests`
directory, then executes `app.py` and checks successful completion. Tests are in
`test_auth.py`, `test_models.py`, `test_reports.py` and `test_workflows.py`.
They cover the teaching application's authentication/lockout, sessions/models,
reporting and workflow behavior. These tests validate the fixture used for
demonstration; they do not measure whether Antigravity answers the same questions
better with TokenWise.

## 6. Browser Verification

The compiled `ResultPanel` renderer was exercised with Playwright/Chromium using
**synthetic data**, at **1280x1000** and **390x844**. Five states at two sizes give
ten views:

| State | Desktop | Narrow |
|---|---|---|
| Conversation memory | Passed | Passed |
| Automatic two-packet comparison | Passed | Passed |
| Comparison pending | Passed | Passed |
| Comparison unavailable | Passed | Passed |
| Imported CLI usage | Passed | Passed |

All views had zero page errors, no document-level horizontal overflow, no
overflowing statistic elements and no overlapping statistic elements. Assertions
for copy/export command messages passed. The narrow memory screenshot was also
visually inspected during release preparation.

Reproduce using an existing local Playwright installation:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) 'tmp/release-ui-0.6.7/browsers'
node scripts/verify-comparison-panels.cjs tmp/release-ui-0.6.7/node_modules/playwright tmp/report-validation-ui
```

The first path must contain installed Chromium binaries and the second the
Playwright module. Those ignored local paths are prerequisites, not bundled
dependencies or portable locations guaranteed on a friend's machine. With a
different local installation, replace them accordingly. The repeated output is
`tmp/report-validation-ui/checks.json`, with ten screenshots beside it. Release
screenshots remain in `tmp/release-0.6.8-ui/`. This test mocks the webview host; it
does not prove that every Antigravity version runs the native hook correctly.
The repeated check results are also retained in
[browser-checks.json](evaluation/test-validation/browser-checks.json).

## 7. Additional Study Harness Checks

The comparative-study harness has **ten separate tests**, not included in the
193/141/20 release totals. Run:

```powershell
.\.venv\Scripts\python.exe evaluation/comparative-study/test_protocol.py -v
```

All ten passed. They check source-only evidence scoring, exact file identity,
definition-plus-body requirements, whitespace normalization, qualified methods,
overloaded declarations, embedded headings/fences and safe extraction/destination
rejection. The research results themselves remain separate observations, not ten
unit test outcomes.

## 8. Report-Ready Paragraph

> TokenWise version 0.6.8 was validated on Windows using automated extension,
> backend and demonstration suites. Of 355 discovered tests, 354 passed and one
> backend test was skipped because the account could not create file symlinks.
> The passed tests comprised 193 extension tests, 141 backend tests and 20
> demonstration tests, with no failures. In addition, ten synthetic browser
> fixture views passed at desktop and narrow viewport sizes. These checks
> support functional correctness of the exercised contracts and UI states;
> they do not establish universal correctness, measured carbon savings or
> improved downstream Antigravity answer quality.

## 9. Remaining Validation Gaps

No line/branch coverage percentage, mutation score or universal bug-free claim
is supported. Native macOS/Linux installation and a full live Antigravity
with/without quality study are not covered by these counts. Fixed-scenario carbon
predictions are not electricity measurements. The separate comparative study
discloses its bounded neural inputs and retrieval-only ablations; it must not be
relabeled as a completed full-file automatic-agent benchmark.
