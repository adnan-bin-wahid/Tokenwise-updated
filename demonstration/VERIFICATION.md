# Local Verification Record

## Current Single-Project Layout

The **0.6.6 build** retains this single project and adds outgoing response guidance.
Checked on 2026-10-07: 174 extension tests passed; 119 backend tests discovered,
118 passed and one Windows symlink-privilege skip; all twenty application tests
and its deterministic output passed. These checks include guidance delivery,
budgets, traces, exports, and real-tokenizer accounting, not a live Antigravity
answer-quality comparison. The updated `study.md` and `demonstation.md` are
included in the [0.6.6 release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.6).

### Previous Single-Project Release

The **0.6.5 build** uses only `tokenwise_demo`: one runnable
application, eleven Python files, and twenty standard-library tests. The app
and its twenty tests pass in this Windows/Python 3.12 checkout. The demo manifest,
exclusion regression fixture and real-backend verifier use this same folder.

Checked on 2026-10-06:

- All 167 extension tests passed, including the packaged PNG icon, bundled guide access, stale-demo
  removal, manifest validation, runtime exclusion and junction protection.
- Backend suite: 106 tests, 105 passed and one Windows file-symlink privilege
  skip. The new single-project scope and packet-comparison tests passed.
- The application's twenty tests and deterministic app output passed.
- Local installer builds do not establish publication. Obtain the final assets
  from the versioned [0.6.5 release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.5).
- A fresh real-weight inference/CO2 run and live Antigravity cloud rehearsal
  were not performed for this consolidated fixture during these checks.

The historical records below keep their original project names, source snapshots,
counts and limitations. They are not measurements for the consolidated project.
An app/test check alone does not establish live Antigravity integration, actual
model line scores or CO2 predictions. Rehearse the new guide, export fresh runs,
and label generated-transcript verification separately from a live chat.

## Historical Multi-Project Runs

Date: 2026-10-05. Environment: this Windows checkout, Python 3.12, CPU inference,
local pruning weights, trained carbon artifacts, local 0.6.2 code. Command:
`.venv\Scripts\python.exe scripts/verify_demonstration.py`.

These are observations from one local verification run, not predicted outcomes,
cloud-agent answers, or evidence of universal performance. The generated JSON
and CSV are available under ignored `demonstration/results/` in this checkout.
Repeat the verifier to obtain measurements for your own machine/snapshot.

## Actual Packet Counts

| Project | All Python input tokens | One selected file input tokens | TokenWise input tokens | TokenWise change versus all-code |
| --- | --- | --- | --- | --- |
| Account security | 1549 | 202 | 1387 | 10.46% reduction |
| Checkout | 2035 | 174 | 1575 | 22.60% reduction |
| Issue tracker | 1486 | 256 | 1415 | 4.78% reduction |

Counts use the same real TokenWise tokenizer and include packet formatting.
The automatic budget was 4096 tokens with at most eight candidates. All three
automatic packets included eight files. Manual baselines were entire service
files, not multi-file expert selections.

All-code and automatic packets each contained 4/4 checked source markers per
project; the one-file manual baselines each contained 1/4. This is **marker
presence, not semantic answer correctness**. Only the fresh-chat scoring
experiment can evaluate the actual Antigravity answers.

The complete comparison request took 24.784 seconds for the first project,
5.255 for checkout, and 5.111 for the tracker in that run. These times include
local comparison preparation, not cloud answer time; startup/inference warm-up
and competing machine activity can affect them. Do not use them as a guaranteed
latency or a controlled cold-versus-warm benchmark.

## Modeled CO2

Matched scenario: Llama-3 8B, 256 expected output tokens, 475 gCO2/kWh.

| Project | All Python CO2 g | Selected CO2 g | TokenWise CO2 g |
| --- | --- | --- | --- |
| Account security | 0.146667 | 0.120908 | 0.143569 |
| Checkout | 0.155961 | 0.120373 | 0.147164 |
| Issue tracker | 0.145462 | 0.121941 | 0.144105 |

These predictions do not measure Gemini/Antigravity hardware, actual output
length, local pruning energy, tool overhead, or net end-to-end emissions.
The smaller manual packet has less modeled input cost but also less checked
evidence; cost alone is not the quality criterion.

## Other Checks

- 22 demonstration application tests and all three example apps passed.
- 149 extension tests passed.
- Backend suite: 91 tests, 90 passed, one skipped because this Windows account
  cannot create file symlinks.
- Real-weight HTTP checks passed for same-chat hints, new-chat clarification,
  explicit-topic ignoring the old hint, and bounded packets.
- Browser checks passed at 1280x1000 and 390x844, with no page errors or document
  overflow. The table scrolls horizontally where needed; copy/export messages
  were checked, and actual host copy/export handling has regression tests.
- The verifier stopped its own backend and did not edit demo application source.
- **Antigravity's cloud model was not called or graded by these checks.**

This record describes pre-publication local verification. The 0.6.2 installer
and demonstration bundle are distributed through the versioned GitHub release.
Install the VSIX, update the matching backend, and follow `../demonstation.md` to
rehearse the actual agent interaction before presenting it as a live result.

## Local 0.6.3 Input-Scenario Checks

Separately checked on 2026-10-05 in the same Windows/Python 3.12 CPU environment.
The earlier 0.6.2 measurements above are historical, not rewritten as new runs.
These are local checks, not proof of publication. Obtain the installer and demo
bundle separately from the versioned v0.6.3 GitHub release and verify its checksums.

- 155 extension tests passed, including scope capture, managed URL resolution,
  native token counts, input-trace validation, line decisions, and export.
- Backend suite: 93 tests, 92 passed and one Windows file-symlink privilege skip.
- Four demonstration apps and 28 tests passed; the original Test_project's six
  tests also passed.
- Real pretrained weights exercised repository discovery without editor hints,
  exact whole-file/excerpt pruning through the compiled extension service, and
  a two-threshold comparison using identical source/task.
- A generated USER transcript exercised the real native hook and HTTP backend:
  the effective objective contained both earlier lockout intent and the subsequent
  boundary follow-up. A different conversation ID did not inherit that reference.
- Six real result views passed at 1280x1000 and 390x844: repository, entire file,
  higher threshold, excerpt, native history, and new chat. There were no page
  errors, document overflow, or overlapping stats. Copy/export messages passed.
- The verifier stopped its own isolated backend and removed temporary chat state;
  it did not modify demonstration application source or call Antigravity's cloud.

### Observed Selected-Source Results

Task: `Explain session expiry and revocation, not invoice pricing.` Source:
`04_pruning_inputs/workflows.py`. Counts use the real pruning tokenizer.

| Input | Threshold | Original source tokens | Retained tokens | Source reduction |
| --- | --- | --- | --- | --- |
| Entire file | 0.45 | 287 | 222 | 22.65% |
| Same entire file | 0.85 | 287 | 19 | 93.38% |
| Exact session_is_valid excerpt | 0.45 | 27 | 27 | 0.00% |

The 0.85 output contained only `session.revoked = True` between filtered-lines
markers. It lost the expiry evidence and function context. **This is observed
over-pruning, not a claim of excellent quality.** At 0.45, unrelated invoice
source also remained; this model is not a perfect relevance filter. The excerpt
needed no reduction because both supplied lines were relevant. The two thresholds
produced the same line relevance scores; the decision criterion changed.

All three selected-source carbon comparisons were ready; the unchanged excerpt
had equal before/after predictions and zero estimated savings. These are still
configured-scenario predictions, not measured emissions.

The fourth fixture's optional all-code/automatic packets were 787 and 790 tokens:
an approximately 0.38% packet increase. Its matched unpruned automatic bundle was
860 tokens; these are different baselines. Wrapper overhead can outweigh reduced
source on a small repository. Do not hide that result or enlarge the fixture just
to manufacture savings.

## Local 0.6.4 Regression Checks

Checked on 2026-10-06 in this Windows/Python 3.12 CPU checkout. Earlier records
above describe their original versions and are not relabeled as new runs.

- 161 extension tests passed. Backend: 104 tests, 103 passed and one Windows
  file-symlink privilege skip. Four demo applications and 28 tests passed.
- Six real result views passed desktop/narrow checks: no page errors, document
  overflow, or overlapping statistics; copy/export controls were exercised.
- The mixed demo's repository task was `Explain session expiry and revocation,
  not invoice pricing.` No editor-selection anchor was supplied. The final
  packet included session expiry/revocation and their tests, while the independent
  invoice function, tests, and display call were omitted. Files were not edited.
- Source tokens: **701 before, 439 retained (37.38% reduction)**; packed context:
  **606 tokens**; matched unpruned bundle: **868 tokens**. These are different
  baselines and are not an all-repository answer-quality score.
- Compiled-client carbon calls succeeded despite zero optional model-size and
  latency overrides, using `artifact_models:model_registry` features. The
  matched formatted-context predictions were **0.133644221 g before** and
  **0.128633917 g after**, a modeled difference of **0.005010304 g**. These do
  not measure Antigravity hardware, local pruning energy, or net emissions.
- Required-helper, import-alias, ordinary-negation, source-preservation,
  query-cache isolation, and saved-file-edit invalidation regressions passed.

The real-weight run completed its repository, selected-source, two-threshold,
excerpt, native-history, and new-chat assertions, but Windows locked its
temporary log during cleanup. A repeat run timed out on local inference.
Temporary backend PIDs were confirmed stopped and both owned scratch folders
were subsequently removed. Do not describe these as two clean verifier exits,
a controlled latency benchmark, or a live Antigravity cloud test. The generated
report from the completed assertions remains under ignored `results/` locally.

The explicit repository filter is separate from neural line relevance. Direct
selected-source commands still use the model on exactly the captured source,
including its previously observed over-pruning risk. Install the v0.6.4 VSIX
and matching backend, and evaluate the actual answers before presenting quality
claims. No older published installer or historical measurement was replaced.

Ignored reports: `results/pruning-inputs.json`, project comparison JSON/CSV, and
`results/result-panel/checks.json` plus screenshots. Regenerate them for a new
source snapshot. The native-hook transcript is test input, not a live cloud chat.
Run the teacher guide's actual Antigravity rehearsal before claiming live behavior.
