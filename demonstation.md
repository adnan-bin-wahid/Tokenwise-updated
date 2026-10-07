# TokenWise: One-Project Teacher Demonstration

This is your presentation script. Follow it in order, with **one Python project
open throughout**: `demonstration/tokenwise_demo`.

The three central experiments answer your teacher's question about how pruning
changes when the input is repository code, selected source, or earlier
conversation intent. The remaining experiments demonstrate the extension's
integration, metrics, exports, setup, and reliability without switching projects.

## Quick Route

| Order | Do this | Show this | Main point |
| --- | --- | --- | --- |
| Before class | Setup, warm backend, run 20 tests | Working application and healthy backend | Rehearsal, not a first installation in class |
| 1 | Ask for a project overview in chat | Fresh tool call, overview, component map | Automatic context for a normal prompt |
| 2 | Repository input, no selection | Goal, files, methods, budget | Discover relevant code without choosing files |
| 3 | Entire `security/models.py` | Session lines and line scores | Actual neural pruning of a supplied file |
| 4 | Highlight only Session | Exact input and original coordinates | Selection scope is different from pruning |
| 5 | Entire `workflows.py`, two thresholds | Actual masks and final excerpts | Tradeoff between reduction and evidence |
| 6 | Earlier-user replay | Earlier intent inside effective objective | Controlled history-informed pruning |
| 7 | Same-chat then new-chat questions | Current tool output and event IDs | Real integration and chat isolation |
| 8 | Compare Context Strategies | All Python / selected / TokenWise packets | Literal context-baseline comparison |
| 9 | Explain token/CO2 values | Baseline, assumptions, signed change | Honest evaluation, not just a large percentage |
| After class | Export observations; optional cleanup | JSON, worksheet, tests, limitations | Repeatable evidence |

For a 15-minute slot, do steps 1-7 and explain the metrics. Treat comparison,
index-edit checks, and cleanup as backup material for questions. For 25 minutes,
perform all sections. Save recorded evidence before class, but label it recorded
if you use it instead of a live run.

## 1. Prepare Before Class

### Choose the Correct Build

Use **0.6.6** for this complete guide, including outgoing prompt engineering.
The one-project layout and **Open Demonstration Guide** command were introduced
in 0.6.5; older releases do not include the new response-guidance block.
Download [the 0.6.6 release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.6)
for the VSIX, study, one-project demonstration ZIP and checksums.

### Normal Installation

1. Download `tokenwise-vscode-0.6.6.vsix` from the release and install it with
   **Extensions > ... > Install from VSIX...**. Reload the editor.
2. Download and extract `TokenWise-0.6.6.zip`. Open its
   `demonstration/tokenwise_demo` folder in Antigravity.
3. Follow **Open and Configure One Folder** below. No compiling or F5 is needed.

### Source Build Alternative

From the source checkout, prepare the installer:

```powershell
cd vscode-extension
npm ci
npm test
npm run package
```

Install `vscode-extension/tokenwise-vscode-0.6.6.vsix` using **Extensions > ... >
Install from VSIX...**, then reload. The shareable folder is
`releases/TokenWise-0.6.6/`; its `demonstration/tokenwise_demo` is the same project.
Never install the source-code ZIP as an extension.

For your existing F5 workflow, run `npm run prepare-backend` and `npm run compile`
in `vscode-extension`, press F5, and use the new Extension Development Host.
Running compile alone does not refresh bundled guides/examples. A friend's
ordinary installation does not need Node, compiling, or F5.

### Open and Configure One Folder

1. Use **File > Open Folder** and open `demonstration/tokenwise_demo` itself.
2. Trust the folder only after checking its contents.
3. Run **TokenWise: Set Up Backend**. Approve the managed dependency/model setup
   or reuse your complete existing backend. Update an older managed backend when
   offered; reloading TypeScript does not update a running Python service.
4. Run **TokenWise: Enable Automatic Context** in this folder. Confirm enabling
   the workspace. Existing unrelated rules/settings should remain intact.
5. Run **TokenWise: Start Backend** before the presentation.
6. Run **TokenWise: Diagnose Setup** and inspect **Output > TokenWise Setup**.
7. Confirm a TokenWise rule exists in Antigravity **Customizations > Rules**.
8. Inspect **Output > TokenWise Index**. This project has eleven saved Python files.
9. Open this script through **TokenWise: Open Demonstration Guide**, or keep
   the source `demonstation.md` preview beside your project window.

Use 64-bit Python 3.12. The application itself needs no pip packages. The
extension's backend is different: initial dependency and pretrained-model
downloads need internet and may take several minutes. Keep it warm afterward.
If setup fails, repair the named problem and choose **Retry Failed Step**.
Do not delete validated downloads or uninstall as your first retry action.

### Fix the Experiment Settings

In Settings, use a stable scenario throughout:

| Setting | Rehearsal value |
| --- | --- |
| Default threshold | `0.45` |
| Repository token budget | `8192` for the main presentation |
| Enable carbon estimation | Enabled |
| Target model name | `meta-llama-3-8b-instruct` |
| Expected output tokens | `256` |
| Carbon intensity | `475` gCO2/kWh |
| Optional model size and input/output latency | Unset or `0` for registry features |
| Optional GPU | Blank for registry features |

These carbon settings describe an estimation scenario; they do not detect the
Antigravity model or the cloud provider's actual hardware. Keep them identical
for before/after estimates. Positive overrides can be used, but record them.

Do not change the task, source snapshot, threshold, and budget all at once.
Vary one factor when explaining its effect. Separate cold startup from warm
preparation time; a cache hit is not a new neural inference benchmark.

## 2. Establish the Application's Ground Truth

In the terminal of the open `tokenwise_demo` folder:

```powershell
py -3.12 app.py
py -3.12 -m unittest discover -s tests -v
```

The test command should finish with **20 tests, OK**. The app should print:

```text
Locked until: 160
Login before expiry: False
Login at expiry: True
Session expiry: 400
Session at 399: True
Session at 400: False
Revoked session at 101: False
Invoice total: 12000
Shipping days: 4
Activity: {'invoice': 1, 'login': 1}
```

From a checkout or extracted bundle root, this checks the same app and tests:

```powershell
py -3.12 demonstration/run_checks.py
```

### What Is in This One Project?

| Source | Working behavior | Why it is useful in the demonstration |
| --- | --- | --- |
| `security/models.py` | Account/Session dataclasses and teaching digest | Session is relevant to one query; Account/digest are unrelated |
| `security/settings.py` | 3 failures, 60-second lockout, 300-second session | Essential facts outside the main selected implementation |
| `security/auth_service.py` | Lockout, rejection before deadline, reset at deadline | Cross-file repository retrieval with related tests |
| `workflows.py` | Sessions, invoice totals, shipping times | One whole-file input with relevant and unrelated functions |
| `reports.py` | Action counts and CSV | A genuine unrelated feature, not padding |
| `app.py` | Deterministic runnable example | Architecture, callers, and behavior baseline |
| `tests/test_auth.py` | Five lockout/reset tests | Boundary evidence for lockout questions |
| `tests/test_workflows.py` | Ten session/invoice/shipping tests | Mixed test methods and topic exclusions |
| `tests/test_models.py` | Two default/digest tests | Data-model evidence |
| `tests/test_reports.py` | Three report/CSV tests | Independent feature validation |

All time values are function inputs. Nothing waits for a real minute. The
SHA-256 password digest is explicitly a teaching fixture, not production
password storage. The application has no database, real users, or payment API.

**Say:**

> This small application is the ground truth for my experiments. Its features
> and tests are real, but deterministic. I can check whether the prepared context
> retains the facts needed for the task instead of judging only compression.

## 3. Explain TokenWise in One Minute

**Say:**

> TokenWise is a local context-preparation extension. A developer supplies a task.
> It discovers relevant Python source or accepts exact selected source, prepares
> task-dependent excerpts, and packs a bounded context. Antigravity uses that
> reference data in its ordinary agent workflow. TokenWise is not the final
> reasoning model, and it does not replace the source file with pruned text.

```text
Latest task + optional bounded same-topic earlier user intent
    -> effective objective
    -> repository discovery OR exact captured file/excerpt
    -> relevant candidates / source representation / neural line scores
    -> preservation and formatting
    -> bounded context packet
    -> Antigravity's normal agent request
```

The two source modes are different. In repository mode, every eligible indexed
file is searchable, but only bounded candidates receive further processing.
In selected mode, the model sees only the captured file or excerpt; it does
not automatically add constants, callers, or tests from other files.

On stable Antigravity, a workspace rule asks the agent to run the TokenWise tool.
This is not guaranteed interception before the first cloud model call. Native
hooks, where supported, are a separate integration path. Always show the actual
current tool invocation when claiming the agent used the context.

## 4. Start with a Normal Automatic Prompt

1. Close Python tabs or clear selection. Start a **new Antigravity chat**.
2. Type this into chat, not into the command palette:

```text
Give me the full overview of my project. Do not modify any files.
```

3. Show the agent's TokenWise command/tool call and returned
   `[TokenWise automatic context]`.
4. Show the fresh automatic result and its overview/file map.
5. Open `.tokenwise/latest.json` if necessary. Check its current query,
   timestamp, new event ID, `status: "ready"`, and `verification: false`.
6. Check the final answer against the app: account lockout, sessions, invoices,
   shipping, reports, and tests. Note any missing component rather than hiding it.

If the automatic panel does not open, run **TokenWise: Show Automatic Context**.
This displays the last result; verify that it belongs to the current prompt.
The status bar count alone is not proof of a new retrieval or agent consumption.

An overview is a **structural representation**, not narrow neural line pruning.
It uses bounded root documentation and representative application components.
Coverage warnings and file/token limits still apply. A model-generated summary
can use tools to read more files; distinguish those later reads from the initial
TokenWise packet.

**Say:**

> I typed a normal project question without selecting source. The agent retrieved
> the current repository context. For a broad overview, TokenWise preserves
> architecture rather than treating generic words like PROJECT as code symbols.

## 5. Teacher Scenario A: All Repository Code Available, No Selection

For a controlled input trace, use the teaching command. It deliberately sends
no active-file, selected text, current-symbol, or diagnostic hint, even if an
editor is open. This separates repository discovery from accidental editor bias.

1. Run **TokenWise: Demonstrate Pruning Inputs**.
2. Choose **Repository: no selected file**.
3. Enter:

```text
Explain session expiry and revocation, not invoice pricing.
```

4. Enter threshold `0.45`.
5. Show **Pruning inputs**: repository mode, current task, no selection scope,
   no history, eleven indexed Python files, and the inference objective.
6. Show **Excluded topics: invoice pricing**. Excluded terms should not be
   promoted as positive goal identifiers.
7. Show included files, relations, tiers, pruning methods, applied thresholds,
   retained source, packed tokens, and the actual unified context.
8. Check for `session_is_valid`, `revoke_session`, and session boundary tests.
   Verify the independent `invoice_total`, invoice test methods, and invoice
   print call are not included. Shipping/report interfaces may still appear
   through dependency expansion; inspect and report the actual packet.
9. Click **Export Pruning Run** and save the JSON as `A-repository.json` in your
   presentation evidence folder, not in an indexed Python source directory.

Now rerun repository mode with `Explain invoice pricing.` Invoice source must
still be retrievable: the exclusion altered a query-specific view, not the file.
The app/tests should still pass unchanged.

### How to Explain the Methods

| Method shown in panel | What happened |
| --- | --- |
| `neural_lines` | Task-conditioned neural line relevance and a threshold |
| `scope_filter+...` | Independent explicitly excluded AST units omitted before the following method |
| `short_source_retained` | Small task-matched source retained without another neural pass |
| `signature_interface` | Bounded signatures/interfaces/relevant constants |
| `overview_excerpt` | Structural overview representation, not neural pruning |
| `original_source_fallback` / `signature_fallback` | Recovery after a pruning failure |

Repository processing searches cached AST/symbol/lexical/dependency metadata.
The teaching command allows eight candidates; ordinary automatic setup defaults
to six. At most three candidate files receive neural line pruning per request.
Others can use short bodies or interfaces. The final wrapper is included in the
token budget; not every discovered file fits in the packet.

For neural candidates, the anchor threshold is
`max(0.10, requested_threshold - 0.15)` and other candidates use
`min(0.85, requested_threshold + 0.15)`. With requested `0.45`, these can be
`0.30` and `0.60`. Show **Applied threshold** instead of claiming every file used
exactly `0.45`. Methods without a neural pass say **not applied**.

Topic exclusion is a separate AST-based step, not a neural probability of
negation. Required shared helpers can remain with a warning. Conditions such
as `not session.revoked` are not deletion instructions. Selected-source pruning
does not apply this repository topic filter.

**Say:**

> All eligible repository code is available for discovery, but I did not select
> a file. The task ranks relevant evidence, dependencies and tests can be added,
> and the final packet is bounded. This is not one giant model call over every
> file. The panel tells me which representation was actually used.

For **real automatic integration**, type the same task plus `Do not modify files.`
in a new Antigravity chat and show its actual tool output. The teaching-command
panel is a controlled experiment; it does not itself inject that packet into chat.

## 6. Teacher Scenario B1: Entire Selected File

This repeats the experiment visible in your Session output.

1. Open `security/models.py` and clear all highlighted text.
2. Run **TokenWise: Demonstrate Pruning Inputs**.
3. Choose **Selected file or highlighted excerpt**.
4. Enter `Explain the Session class.`
5. Enter threshold `0.45`.
6. Show **Selected entire file**, the exact path, First source line `1`, and
   History source **None**.
7. Show Original, **Line decisions**, and Pruned context.
8. Explain the three fields: `username`, `expires_at`, and `revoked = False`.
9. Compare retained Session lines with the unrelated Account/password-digest
   lines in Original. Inspect actual scores rather than predicting them.
10. Export `B1-session-entire-file.json`.

The regular **TokenWise: Prune Current File** command also captures the whole
file, even if a highlight exists. Its explicit name matters. The teaching command
uses a highlight when present, so clear it for a whole-file demonstration.

### Explain Your Existing Screenshot Correctly

Your recorded run used the task `explain me the session class` and reported:

| Recorded value | Explanation |
| --- | --- |
| Original `117` tokens | Supplied full-file source measured by the pruning tokenizer |
| Pruned `26` tokens | Final selected-source excerpt, including its omission formatting |
| Reduction `77.78%` | `(117 - 26) / 117 * 100`, rounded |
| Model input `195` tokens | Query/instruction/source input; not the same denominator |
| Relevance `0.4693` | Document/task relevance score, not percentage accuracy |
| Kept line fragments `19-22` | Actual decision-mask source coordinates for that run |
| Session fields around `0.93-0.95` | Mean task-conditioned relevance of scored tokens on those lines |

These numbers are historical observations from your screenshot, not guaranteed
results for another machine, task spelling, setting, or build. Re-export the
new run and report its own values. You may show the screenshot as recorded
evidence, provided no personal information needs hiding.

The recorded mask omitted `@dataclass` while retaining the class and fields.
That is an important limitation: the excerpt is useful for identifying the data
fields, but it does not contain every fact about construction or behavior.
An explanation of automatically generated initialization/equality methods needs
the original decorator or a repository view that supplies it. Do not claim that
this excerpt is complete or executable replacement source.

**Say:**

> The whole file was input. The Session fields scored above the threshold,
> while unrelated Account and digest lines did not. This demonstrates task-aware
> line selection. I still check completeness: losing a decorator can lose
> important semantics even when the reduction percentage is impressive.

## 7. Teacher Scenario B2: Exact Highlighted Excerpt

Keep `security/models.py` open.

1. Highlight the `@dataclass` immediately above `class Session` and all of the
   Session class body. Do not include Account or the password function.
2. Run **Demonstrate Pruning Inputs** and choose selected mode again.
3. Use the same task and threshold.
4. Show **Selected excerpt**, the original starting line, and captured Original.
5. Check whether the decorator survives this run; do not assume it must.
6. Export `B2-session-excerpt.json`.

The ordinary **TokenWise: Prune Selected Code** command uses exactly a highlighted
fragment. With no selection it asks you to highlight code; it does not mean
repository discovery. No extra files or tests are automatically added.

**Say:**

> In this run Account was never input. Its absence is due to my selection, not
> the model removing it. Neural pruning only operates within this captured
> fragment. A smaller input can legitimately need little or no pruning.

Selections capture the editor buffer, including unsaved text. Repository search
uses saved files. Record that distinction before comparing experiments. Selected
source coordinates are the fragment's original position, not a fresh line 1.

## 8. Threshold Experiment in the Same Project

1. Open `workflows.py`, clear selection, and use selected entire-file mode.
2. Task: `Explain session expiry and revocation, not invoice pricing.`
3. Run with `0.45` and export `B3-workflows-threshold-045.json`.
4. Run again with the same source/task and threshold `0.85`.
5. Export `B4-workflows-threshold-085.json`.
6. Compare session functions with invoice/shipping functions in Original,
   line scores, masks, final context, reduction, and omitted necessary facts.

This is a neural experiment on the same mixed file, not the repository AST
exclusion stage. The words `not invoice pricing` are part of the neural query;
selected mode does not guarantee perfect handling of them. Report any unrelated
retained line honestly. The higher threshold generally retains fewer scored
lines, but preservation/formatting affect final text.

### Explain the Neural Decisions

```text
query + source -> pretrained relevance model
token logits -> sigmoid relevance scores
source offset mappings -> tokens belonging to each line
line relevance -> mean of scored token relevance on that line
initial keep decision -> line relevance >= threshold
preservation/gap bridging -> decision mask
formatting -> final reference excerpt
```

Scores are not calibrated probabilities that a line is required or correct.
Blank lines can be unscored. First-line preservation, one-line gap bridging,
and formatting can retain or restore low-scoring lines. For short removed
ranges, a marker can be larger than the source it replaces. The table describes
the **mask before output formatting**, not exact final membership.

Long inputs are chunked with overlap; duplicate source-offset scores are averaged
before line aggregation. The wrapper uses an 8,192-token input window and
50-token document overlap. The panel shows at most 200 source lines; JSON
export retains the full returned line scores. This small fixture is not a
benchmark of huge-repository/chunking throughput.

**Say:**

> Threshold controls which scored lines initially qualify. It is not a quality
> score or a guaranteed compression setting. I compare the final context with
> source/tests to see whether necessary evidence was lost.

## 9. Teacher Scenario C1: Controlled Earlier-User Replay

Keep the same `tokenwise_demo` folder open. No new project is needed.

1. Run **TokenWise: Demonstrate Pruning Inputs**.
2. Choose **Conversation: replay earlier user context**.
3. Earlier user task:

```text
Explain account lockout after failed login attempts and its related tests.
```

4. Current task:

```text
Which tests cover that behavior?
```

5. Use threshold `0.45`.
6. Show **Supplied replay (not live chat capture)**.
7. Expand Earlier user reference and Inference objective. Check that the actual
   effective objective includes the lockout subject from the earlier task.
8. Inspect lockout implementation, settings and relevant tests.
9. Export `C1-history-replay.json`.

Then run two controls:

| Control | Input | Expected distinction |
| --- | --- | --- |
| No earlier reference | Repository mode; only `Which tests cover that behavior?` | Missing-subject clarification or limited context, not an invented topic |
| Explicit topic switch | Replay lockout, current task `Explain session expiry and revocation and their tests.` | New task is self-contained; unrelated lockout hint is ignored |

The replay uses the real backend and actual supplied history, but **you entered
the earlier task manually**. It is not proof of automatic Antigravity transcript
capture. A referring follow-up changes the effective retrieval/pruning objective;
it is not merely a history phrase appended to the final answer.

**Say:**

> That behavior is ambiguous on its own. The earlier user requirement supplies
> the subject, and the effective objective shows how it changes retrieval.
> This experiment is explicitly a replay; I will test live integration next.

## 10. Teacher Scenario C2: Actual Same-Chat and New-Chat Tests

Start one **new actual Antigravity chat** in the same folder.

First prompt:

```text
Explain account lockout after failed login attempts and its related tests.
Do not modify any files.
```

Second prompt in that same chat:

```text
What about its expiry boundary? Do not modify any files.
```

Third prompt:

```text
Which tests cover that behavior? Do not modify any files.
```

For each prompt, show the current tool call/output and fresh `latest.json`.
Check the task/reference/effective objective, event ID, included files, and
the answer. Boundary evidence should distinguish lockout from session expiry.

| Integration path | How earlier intent reaches the backend |
| --- | --- |
| Native PreInvocation hook, where supported | Bounded earlier explicit user turns; trace can say `native_scoped_user_turns` |
| Stable-build workspace rule/tool fallback | Agent resolves the subject into a self-contained current query; backend sees that query, not raw earlier chat |

Do not require a native history label on a fallback build. Instead inspect the
resolved current query and current tool output. The backend cannot prove exactly
how the fallback agent constructed that query or claim it saw the whole chat.

### Isolation Controls Without Another Project

1. In the same chat, ask a new explicit topic:

```text
Explain invoice tax rounding and its related tests. Do not modify files.
```

2. Show that the new query/objective is about invoices, not attached lockout intent.
3. Start another **new chat** and ask only:

```text
Which tests cover that behavior?
```

4. The agent should clarify the missing subject, not silently reuse another
   chat's topic. If it clarifies without a tool call, no new retrieval event is
   expected. An unchanged status or old JSON is not evidence of a new run.

Native state retains at most **three earlier user turns** from the current topic,
within **2,000 combined characters**, preserving the topic opening and recent
constraints. Explicit new tasks reset the topic. Reuse requires a conversation
ID and is workspace-scoped. Assistant answers, injected context, unrelated chats,
and unresolved questions are not authoritative remembered user intent.

**Say:**

> This is bounded same-topic context, not permanent memory or model training.
> Separate chats must be isolated. I show a replay and live tool behavior
> separately because they establish different facts.

## 11. Optional Literal All-Code / Selected / Automatic Comparison

This answers the alternative interpretation: what context reaches the final
agent under three strategies? It is different from how the neural mask is made.

1. Open and save `security/auth_service.py`; clear selection.
2. Run **TokenWise: Compare Context Strategies**.
3. Use this common task:

```text
Explain account lockout after failed login attempts, the expiry boundary,
and its related tests. Do not modify any files.
```

4. Show the three strategies, actual token counts, file lists and CO2 scenario.
5. Inspect each packet and use its copy control. Export the comparison JSON.

| Strategy | What it contains | What to inspect |
| --- | --- | --- |
| All Python | Unpruned eligible indexed Python from the same saved snapshot | Constants, implementation, tests, and unrelated workflows |
| Selected | Unpruned saved file/excerpt | Implementation only; settings values and tests may be missing |
| TokenWise | Bounded retrieved packet with no selection bias | Whether the necessary cross-file evidence fits |

The Selected baseline here is **unpruned**, not the neural selected-source
experiment. All Python excludes ignored paths and non-Python assets. Oversized
baselines and changed snapshots fail visibly rather than silently truncating an
all-code baseline. The command compares packets; it does not grade answers.

### Optional Answer-Quality Trial

Use fresh independent chats with the same agent model/settings, one packet and
the same question per chat. Rotate strategy order. Ask answers to use only the
supplied packet, cite evidence, and state what is missing. No browsing, file
reads, terminals, or extra context tools are allowed in a context-only trial.

A project-connected Antigravity chat still has potential repository access and
TokenWise rules. Reject a context-only trial if any extra tool runs. For strict
isolation, paste exported packets into independent chats outside this workspace,
with no repository attachment/integration. This needs no second Python project.
If you cannot enforce it, label the trial a **tool-assisted workflow**, not a
controlled context-only quality comparison.

Score against facts defined from the tests **before** viewing answers:

- Threshold: three failed attempts.
- Duration: 60 seconds from the lockout-triggering failed login.
- Correct password rejected while `now < locked_until`.
- Exact deadline allows timed reset; successful login clears failures.
- Wrong password at expiry starts a fresh count.
- Relevant boundary/reset test names and supported assertions.

Record supported facts, omissions, unsupported claims, packet/answer timing,
and tool violations separately. Literal source-marker presence is not semantic
answer correctness. One small demo does not prove universal superiority.

## 12. Token Metrics and Your CO2 Screenshot

### Different Counts Have Different Meanings

| Metric | Meaning |
| --- | --- |
| Original/source | Input source or original included-source baseline |
| Pruned/retained source | Retained excerpt source |
| Packed tokens | Complete repository wrapper, headings, fences and excerpts |
| Formatting overhead | Packet tokens beyond retained source |
| Raw context tokens | Matched packet with same files/formatting before pruning |
| Model input tokens | Query/instruction/source input, not total multi-pass/provider compute |

Source reduction is `(original - retained) / original * 100`. Do not compare
17 source tokens with a 117-token wrapped packet and call it -588.24% useful
reduction: unchanged source has 0% source reduction and 100 overhead tokens.
Actual increases are valid and must be labeled as increases, not hidden.

### Why 77.78% Fewer Tokens Does Not Mean 77.78% Less CO2

Your **recorded selected-file** run estimated:

| Quantity | Before | After |
| --- | --- | --- |
| Prefill energy | 17.0119 J | 3.7804 J |
| Decode energy | 981.9252 J | 981.9252 J |
| Total energy | 998.9371 J | 985.7057 J |
| CO2 | 0.131804 g | 0.130058 g |

The difference is **13.2315 J** and approximately **0.001746 g CO2**. At the
displayed intensity, the conversion is:

```text
CO2 grams = energy joules / 3,600,000 * carbon intensity gCO2/kWh
13.2315 / 3,600,000 * 475 ~= 0.001746 g
```

The token reduction mainly changes estimated **prefill**. The assumed output
length stays fixed, so estimated **decode** is unchanged and dominates this
small-input scenario. Total estimated CO2 reduction is about **1.32%**, not
77.78%. This is expected under those assumptions, not proof of measured savings.

### Baselines and Limits You Must State

- Selected-source estimates use the source-only original/retained counts.
- Repository estimates compare matched formatted packets with the same files.
- Context-strategy estimates compare each actual complete packet's input count.
- Hold target model, hardware assumptions, output length, and intensity fixed.
- `artifact_models:model_registry` means registered features; a suffix
  `+request_overrides` means explicit scenario overrides also contributed.
- The displayed prefill/decode routes identify the actual estimator branch.
- These are trained SEAL-derived scenario predictions, not measured Antigravity
  consumption, provider emissions, or energy used by local indexing/pruning.
- The extension does not automatically identify the agent's cloud hardware/model.
- A net environmental claim would also require measuring local pruning overhead
  and actual downstream inference. This presentation does not establish that.
- Pending, disabled, unavailable, zero savings, or an increase are valid states.
  A carbon error should not discard prepared context or invent a green number.

**Say:**

> The estimator compares a fixed inference scenario before and after context
> reduction. Input processing falls, while assumed output processing is fixed.
> I report the baseline and assumptions and do not call predictions measured
> emissions or claim a guaranteed net environmental benefit.

## 13. Budget, Indexing, and Freshness Checks

These are optional questions-and-answers demonstrations, not changes needed for
the main run. Record original settings/content before changing anything.

### Bounded Context

1. Save the main repository result at an 8,192-token budget.
2. Temporarily set **Repository Token Budget** to `512` in this workspace.
3. Repeat the same repository task and threshold.
4. Show packed tokens within the new budget and any coverage/omission warnings.
5. Do not assume a tiny packet still contains all required evidence.
6. Restore the budget to `8192`.

The automatic launcher has its own `.agents/tokenwise.json` budget; changing an
editor setting for teaching commands does not necessarily change that generated
configuration. Read the panel's actual budget. Keep the automatic run's settings
fixed unless deliberately testing them too.

### Background Index / Cache Freshness

1. Observe the configured workspace in **Output > TokenWise Index**.
2. Repeat exactly the same task with no saved changes. Record cold/warm/cache
   conditions rather than claiming every quicker run reran neural inference.
3. If you want an edit test, change `SESSION_SECONDS = 300` to `301` in
   `security/settings.py`, save, and wait for the index update.
4. Run repository mode with `Explain SESSION_SECONDS session expiry.` Show
   that fresh context uses `301`, not a stale cached result.
5. Restore `300`, save, and rerun all 20 tests. Boundary tests intentionally
   fail if the constant remains changed; do not leave the fixture modified.

Already configured trusted workspaces index in the background. Saved Python
create/change/delete/rename events update affected metadata; periodic
reconciliation catches missed events. Cached terms, symbols, signatures,
dependencies, and token counts are reused. Answer reuse is tied to the task,
history, configuration and source fingerprint; similar wording alone must not
reuse another task's answer. Exact selected pruning uses a buffer snapshot.

## 14. Save the Evidence

Use [the blank worksheet](demonstration/results-template.md). For each run record:

- Date, machine, editor/extension/backend/source versions.
- Task spelling, scope, current saved snapshot, selected buffer and starting line.
- Effective objective, history source/reference, requested/applied thresholds.
- Actual methods, relevant retained facts, unnecessary context, necessary omissions.
- Source/retained/packed/raw counts, budget, timing and cache conditions.
- CO2 scenario, baseline, values, state or error.
- JSON export and dated screenshot filename.
- Actual current chat tool output when claiming live integration.

Suggested filenames: `01-overview`, `A-repository`, `B1-session-entire-file`,
`B2-session-excerpt`, `B3-workflows-threshold-045`,
`B4-workflows-threshold-085`, `C1-history-replay`, `C2-live-same-chat`,
`C3-new-chat-control`, and `D-context-strategies`.

Export selected/repository runs using **Export Pruning Run**. The comparison
panel also has comparison export/copy controls. Copy Unified Context and Copy
Pruned Context copy the excerpts, not an executable application replacement.

Generated evidence under `demonstration/results/` is ignored by Git. Do not
commit secrets, personal chat history, local absolute-path registrations, or
model weights. Keep private transcript evidence only with permission.

### Developer Verification Is Different from a Live Defense

`scripts/verify_demonstration.py` exercises real local weights, HTTP calls,
compiled client mappings, and a generated explicit-user transcript. Its reports
say `verification_only: true` and `antigravity_cloud_called: false`. That is
useful local verification, not proof of a real cloud-agent answer or live native
hook support in every Antigravity build. Historical results from the previous
four demos are not numeric results for the new project.

## 15. Troubleshooting During Rehearsal

| Symptom | What to do |
| --- | --- |
| New guide command missing | Install the 0.6.6 VSIX; reload the correct host/profile |
| First setup failed | Read Output > TokenWise Setup; fix the named cause; Retry Failed Step |
| Slow first retrieval | Warm with Start Backend; record startup separately; do not hide timeouts |
| Trace/method fields absent | Update the matching Python backend and repeat the task |
| Wrong file list | Open `tokenwise_demo` itself, not its parent/TokenWise root |
| Automatic context never runs | Check workspace rule, command approval, new chat, current tool call |
| Old panel/status remains | Verify timestamp/query/event ID; Show Automatic Context only reopens latest |
| History replay is ignored | Use a referring follow-up; an explicit new task intentionally resets subject |
| No native history source | Stable rule fallback may supply a resolved query instead |
| New-chat question only gets clarification | Expected for an unidentified subject; a new event may not exist |
| Selected excerpt lacks imports/decorator/tests | Inspect Original; exact selection and neural pruning can omit semantics |
| 0% reduction | Input can be tiny or wholly relevant; report it as a valid result |
| Extra invoice/shipping line retained | Identify mode/method; inspect dependency/preservation; record the limitation |
| CO2 unavailable | Check Enable Carbon Estimation, scenario settings, backend artifacts and health |
| Carbon error mentions zero size/latency | Use corrected 0.6.4+ client; unset/zero optional overrides; rerun |
| PowerShell profile execution-policy warning | Distinguish the terminal's outer profile warning from TokenWise tool output; use a clean no-profile shell for rehearsal |
| Changed session constant makes tests fail | Restore `SESSION_SECONDS = 300`, save, rerun tests |

Do not globally disable execution-policy protections just for the demo. Generated
Windows launchers already use their scoped no-profile/bypass process. An outer
terminal profile can still emit a warning independently, as in your pasted chat;
check whether the actual TokenWise context command succeeded afterward.

For a saved evidence fallback, tell the teacher when/where it was recorded and
what failed live. Do not present recorded results as a current successful run.

## 16. Teacher Defense Answers

**What did you build?**
The extension workflow, repository indexing/retrieval, goal preparation, bounded
packing, Antigravity integration, managed setup/recovery, inspection/export
controls, carbon integration, and verification/demonstration infrastructure.
The implementation integrates pretrained SWE-Pruner; credit upstream work.

**Did you train every model from scratch?**
No. The neural pruning model is pretrained upstream. Explain your implementation
and the SEAL-derived carbon estimator pipeline accurately; do not attribute
upstream training or research to yourself.

**How does it know what is relevant?**
Task-dependent lexical/symbol/dependency retrieval chooses candidates; selected
or neural candidates use token relevance aggregated by source line. Other methods
are visible in the panel. The scores are not a correctness guarantee.

**Does all code mean all files are sent to the model?**
No. All eligible indexed Python is discoverable, but candidate limits, method
selection, a cap on neural passes, and token packing bound actual processing.
The optional All Python export is a separate unpruned baseline.

**Why do repository thresholds differ from my input?**
Anchor and related neural files use adjusted thresholds; interfaces/short bodies
may not use a neural threshold. Show requested and applied values separately.

**Why did the Session decorator disappear?**
Neural line selection is not a complete AST reconstruction. The recorded score
fell below the threshold. It is a visible completeness limitation, not something
to call correct executable code. Inspect original source before semantic claims.

**Does history affect pruning, or only the final response?**
For a recognized referring follow-up, bounded earlier user intent contributes to
the effective retrieval/pruning objective. Show the trace. Fallback may provide
a self-contained query rather than a raw transcript.

**Does it remember conversations in other chats?**
No. This is scoped same-topic history, not persistent cross-chat memory. New
chats and explicit topic switches must not reuse unrelated intent.

**Why not remove the maximum amount?**
Useful evidence, boundary checks, constants, and test assertions can be lost.
Evaluation includes correctness, omissions, overhead and latency, not just size.

**What does the carbon number prove?**
A prediction under fixed configured assumptions. It is not measured emissions,
the actual provider's hardware, or a demonstrated net savings after local work.

**Is the extension guaranteed to work everywhere?**
No. It targets trusted local Python repositories and is Windows-tested.
Remote/virtual workspaces, native macOS/Linux verification, arbitrary coreference,
perfect retrieval, and guaranteed agent-rule compliance remain limitations.

**Does the one-project demo prove generalization?**
No. It makes the presentation controlled and understandable. Larger diverse
repositories, repeated trials, supported-fact scoring and failure reporting are
needed for broad performance/quality claims.

## 17. Optional Setup and Cleanup Demonstration

### Complete Command Checklist

All names below have the **TokenWise:** prefix. The demonstration and comparison
commands are controlled experiments; everyday automatic use still starts with
your normal prompt in Antigravity chat.

| Command | How to demonstrate it in this same project |
| --- | --- |
| Enable Automatic Context | Configure `tokenwise_demo`; show the loaded rule, then a fresh normal chat tool call |
| Set Up Backend | Show numbered managed setup/recovery before class; reuse validated downloads |
| Start Backend | Warm the local model before class; show its actual health/port |
| Diagnose Setup | Show installation, backend health and workspace registration in Output |
| Check Backend Health | Show the direct API health check; inspect a missing/offline backend error instead of assuming readiness |
| Open Setup Guide | Open the bundled installation and recovery documentation |
| Open Demonstration Guide | Open this script from the installed 0.6.6 extension |
| Show Automatic Context | Reopen the current automatic packet; check timestamp/query first |
| Build Repository Context | Run the manual repository-context command from an open Python file with the lockout task; unlike controlled no-anchor mode, editor hints can affect this route |
| Prune Current File | Process all of `security/models.py` even when a highlight exists |
| Prune Selected Code | Process only the highlighted Session definition |
| Demonstrate Pruning Inputs | Run the repository, exact selection, and supplied-history experiments above |
| Compare Context Strategies | Export the all-Python, unpruned selected, and automatic packets from one saved snapshot |
| Remove All Local Data | Destructive cleanup only after exporting evidence and finishing the presentation |

The manual repository command is an editor-assisted workflow, so do not label
its result the no-selection control. The teaching command's repository mode
is the route that deliberately removes editor hints.

Use **Diagnose Setup** to show the central installation, health, model readiness,
and repository link. Explain seven-step setup and **Retry Failed Step** using the
guide/logs; do not deliberately break a working installation during class.
Unrelated rules/settings are preserved, and multiple Python workspaces can use
one centrally managed backend without nesting inside the TokenWise checkout.

Only after finishing and exporting evidence, demonstrate cleanup if requested.
**TokenWise: Remove All Local Data** removes owned integration/backend data with
warnings; it is not a harmless switch and can require setup again. Ordinary
Uninstall invokes cleanup when removal completes, potentially after a full IDE
restart. Customized/unrecognized files, checkout backends, Python itself and
editor-managed history are preserved. Do not promise absolutely zero traces.

## Response Guidance

This optional rehearsal demonstrates **prompt engineering in 0.6.6**.
Earlier installers do not include it. Your earlier pruning/history/carbon
demonstrations still apply; this is an extra stage after relevant evidence is found.

1. Install the 0.6.6 VSIX, reload, and open this same `demonstration/tokenwise_demo`
   folder. Refresh **Set Up Backend** and **Enable Automatic Context**, then
   **Start Backend**. Follow the [README steps](README.md#response-guidance).
   F5/compiling is only an alternative for developers, not normal users.
2. In the existing `.agents/tokenwise.json`, set `"response_guidance": true`
   without removing other settings. Start a new Antigravity chat and enter:

   ```text
   Explain session expiry and revocation and identify the related tests.
   Cite the relevant files and symbols. Do not modify any files.
   ```

3. Show the **current** retrieval tool output and **Show Automatic Context**.
   Point to `Response guidance (v1: ...)` before the source excerpts and the
   panel's `applied` trace. Export a comparison/run or retain the matching
   `.tokenwise/latest.json` result, including `response_guidance.text`.
4. Explain that the selected profile requests grounded behavior and boundaries,
   citations, user-constraint compliance, and honest missing-evidence reporting.
   It does not inject application facts: the duration and expiry boundary must
   still come from real source. It is not permission to edit, and it does not
   make another LLM call.
5. Set `"response_guidance": false`, start a fresh chat, and repeat the exact
   task. Show the new result's `disabled` trace and the absence of the guidance
   block. Retrieval and the source-reference labels should still work. Compare
   the evidence actually included as well as total tokens; the extra block can
   change how much source fits under the same budget. Re-enable it afterwards.
6. For a **prompt-only quality study**, instead use one exported packet and remove
   only its exact guidance block for the paired condition. Keep all source,
   task, model, and tool conditions identical, use isolated chats without a
   TokenWise rule reinjecting guided context, and repeat several trials in
   alternating/randomized order. Record additional file reads and score factual
   correctness, boundaries, citations, unsupported claims, and constraint
   compliance against the tests. These trials have not been performed for you.

The separate editor setting **TokenWise > Enable Response Guidance** controls
manual repository/demo/comparison requests. It does not control automatic chat
retrieval; automatic retrieval uses the workspace JSON above. Selected-source
neural commands remain raw excerpt demonstrations. Small budgets may report
`omitted_budget`; older backend/report data shows `not reported`, which requires
a backend refresh and a current prompt before demonstrating this feature.

Say: **"I added task-aware, evidence-grounded instruction prompting to TokenWise's
outgoing context. It is designed to improve answer reliability, and I can compare
it with the exact same evidence without guidance to measure that effect."**
Do not say that a nicer-looking answer proves higher accuracy or measured carbon
savings. See [study Section 13.7](study.md#137-outgoing-response-guidance-and-prompt-engineering)
for the full mechanism and evaluation boundaries.

## 18. Closing Statement

> In one working Python repository I have shown three pruning inputs: repository
> discovery without a selected file, exact selected source, and bounded earlier
> user intent for a follow-up. I have shown actual objectives, line decisions,
> context budgets and tool output, and checked them against executable tests.
> I distinguish token savings from formatting overhead, estimates from measured
> emissions, and recorded/replayed evidence from live integration. The goal is
> useful task evidence with less unnecessary context, not the largest percentage
> at any cost.
