# TokenWise: Teacher Demonstration

## 1. What Your Teacher Is Asking

Your teacher appears to be asking **how different inputs affect pruning**,
not merely whether one context packet is smaller than another.

| Scenario | Available input | Demonstration |
| --- | --- | --- |
| All repository code, no selected file | Eligible saved Python source in the workspace | Automatic discovery without an editor anchor |
| Selected code | Exactly one captured file or highlighted excerpt | Neural pruning of that exact scope |
| Earlier conversation context | Current task plus a bounded same-topic user reference | History changing the effective retrieval/pruning objective |

Two distinctions matter:

- **Repository discovery is not sending every line to the neural model.**
  All indexed files are searchable; only bounded candidates are processed.
- **Same-chat history is not cross-chat memory.** Earlier user intent can resolve
  a referring follow-up. Unrelated chats must not silently share their topics.

The teacher's wording is ambiguous. Present these three input scenarios first.
If they meant literally sending every file to the final agent, use the optional
comparison in Section 12. If they meant persistent memory across separate chats,
explain that this is not implemented and would need explicit consent and scope.

## 2. Version and Installation

The new input trace, line decisions, and **TokenWise: Demonstrate Pruning Inputs**
command require **0.6.3 and its matching backend**. Download them from the
[0.6.3 GitHub release](https://github.com/adnan-bin-wahid/Tokenwise-updated/releases/tag/v0.6.3).
Older releases remain unchanged.

### Install the Release VSIX

1. In Antigravity, open **Extensions > ... > Install from VSIX...**.
2. Select the downloaded `tokenwise-vscode-0.6.3.vsix`. For a local source build,
   the same file is under `releases/TokenWise-0.6.3/`.
3. Reload the editor window.
4. Run **TokenWise: Set Up Backend** and approve installing the matching backend.
5. Open a demo leaf folder, trust it, and run **Enable Automatic Context**.
6. Re-run Enable in previously configured folders to refresh generated rules.
7. Warm the model with **TokenWise: Start Backend** before class.

Python 3.12 (64-bit) and supported CPU dependencies are required. Initial setup
needs download access and disk space. Verified model downloads can be reused.
Do not uninstall or clear all local data just to update.

### Development Host Alternative

From `vscode-extension`:

```powershell
npm ci
npm run prepare-backend
npm run compile
```

Press F5 and open a demo leaf folder in the development host. Update the managed
backend there too. For a checkout backend, restart its own process from the new
source. Reloading the extension does not reload a running Python service.
Use `npm run package` to create the local VSIX and shareable release folder.

## 3. Demonstration Repositories

Download `TokenWise-0.6.3.zip` from the release assets and extract it for these
examples. Open one leaf folder at a time, not the `demonstration` parent.

| Folder | Behavior | Tests | Purpose |
| --- | --- | --- | --- |
| `04_pruning_inputs` | Sessions plus unrelated invoice/shipping logic | 6 | First example: inspect actual line decisions |
| `01_account_security` | Failed-login lockout and session boundaries | 8 | Repository retrieval and referring follow-ups |
| `02_checkout_delivery` | Coupons, pricing, inventory, delivery | 8 | Repeat with another dependency structure |
| `03_issue_tracker` | Permissions, transitions, audit | 6 | Generalization to another application |

These standard-library fixtures are teaching examples, not production security
or financial software. Their executable source/tests are the behavior baseline.

From the TokenWise checkout root:

```powershell
py -3.12 demonstration/run_checks.py
```

This runs four apps and 28 tests. From a leaf project:

```powershell
py -3.12 -m unittest discover -s tests -v
py -3.12 app.py
```

Do not enable automatic context in `baseline_lab`; it is for the optional
context-only answer comparison.

## 4. Explain the Pipeline

```text
Current task + optional bounded earlier user reference
  -> effective task / synthesized objective
  -> repository discovery OR exact selected source
  -> task-dependent representation / neural line decisions
  -> retained excerpts
  -> bounded formatted context
  -> Antigravity's ordinary model request
```

TokenWise is a local **context preparation layer**, not the final reasoning
model. It prepares reference data. It does not modify application source or
automatically turn pruned text into a patch.

Show **Pruning inputs** in the result panel. It records:

- Mode, current task, and exact code scope.
- Requested threshold and history source.
- Actual inference objective.
- Earlier user reference, when one was used.
- Indexed file count or original excerpt starting line.

Use **Export Pruning Run** to preserve the actual trace. A percentage alone does
not explain why code was retained or omitted.

## 5. Scenario A: No File Is Selected

For the exclusions and CO2-setting fixes below, install the locally built
**0.6.4 VSIX**, reload, run **Set Up Backend**, and re-enable the workspace.
The previously published 0.6.3 installer does not contain these fixes. See the
README's **Local 0.6.4 Update** section for the artifact and retry steps.

Open `demonstration/04_pruning_inputs`. You may close editor tabs. The teaching
command sends no active-file, symbol, selection, or diagnostic hint, even if a
file remains open.

1. Run **TokenWise: Demonstrate Pruning Inputs**.
2. Choose **Repository: no selected file**.
3. Enter `Explain session expiry and revocation, not invoice pricing.`
4. Use threshold `0.45`.
5. Show repository mode, scope, indexed count, and the inference objective.
6. Show included files, their relations, methods, applied thresholds, and excerpts.
7. Export the run and record its actual omissions and counts.

With 0.6.4, show **Excluded topics: invoice pricing**. The goal identifiers must
not promote `invoice` or `pricing`. In this mixed demo, inspect the final packet
for session expiry/revocation and their tests, and verify that the independent
`invoice_total`, invoice tests, and invoice display call are omitted. This is a
query-specific reference view, not a change to the demonstration files. Then
ask `Explain invoice pricing.` separately: invoice code must still be retrievable.

### What Happens Internally

The index discovers eligible saved Python files and extracts AST-based symbols,
signatures, lexical terms, and dependency metadata. Task words and identifiers
rank candidate source. Dependency expansion can add related implementation,
constants, interfaces, and tests.

The full repository is the **discovery scope**, not necessarily neural input.
The teaching command allows eight candidates; normal automatic setup defaults
to six. At most three candidate files receive neural line pruning per request.
Other candidates can use interfaces or short-source retention. The complete
formatted output is bounded by the token budget afterward.

Per-file methods make the different branches visible:

| Method | Meaning |
| --- | --- |
| `neural_lines` | Neural relevance and thresholds applied to source |
| `scope_filter+...` | Independent explicitly excluded units omitted before the indicated packing/pruning method |
| `short_source_retained` | Small task-matched body retained without another model pass |
| `signature_interface` | Interfaces, signatures, or relevant constants |
| `overview_excerpt` | Structural overview coverage; no neural line pruning |
| `original_source_fallback` / `signature_fallback` | Recovery after a pruning failure |

Neural anchors use `max(0.10, requested_threshold - 0.15)`; other neural
candidates use `min(0.85, requested_threshold + 0.15)`. Show the applied value
rather than claiming every file used the same threshold.

The explicit topic filter is a separate AST-based stage, not an extra neural
score or a claim that the model perfectly understood negation. Shared helpers
needed by the positive task can remain with a warning. Ordinary conditions such
as `not session.revoked` must remain eligible. Selected-source commands do not
apply this repository filter, and broad overview mode remains structural.

### What to Say

> No file was selected. TokenWise searched repository metadata using the task,
> followed relevant dependencies, and prepared bounded excerpts. It did not
> concatenate every repository file into a single neural-model call.

Then repeat the task in a **new actual Antigravity chat** with no selection and
`Do not modify files.` Inspect the current TokenWise tool output and fresh event.
The teaching command's panel does not itself inject a packet into a chat or
prove that the cloud agent consumed it.

## 6. Scenario B: Selected File or Excerpt

Keep the project and task unchanged so the source scope is the variable.

### Entire File

1. Open `workflows.py` and clear the text selection.
2. Run **Demonstrate Pruning Inputs**.
3. Choose **Selected file or highlighted excerpt**.
4. Use the same task and threshold `0.45`.
5. Show **Selected entire file**, Original, **Line decisions**, and Pruned context.
6. Inspect actual decisions around sessions versus invoice/shipping source.
7. Export the run.

The regular **Prune Current File** command always processes the complete file,
even if text is highlighted. A highlight no longer accidentally changes scope.

### Exact Excerpt

1. Highlight only the definition/body of `session_is_valid`.
2. Run the teaching command and choose selected mode.
3. Use the same task and threshold.
4. Show **Selected excerpt**, First source line, and the captured Original text.
5. Explain that invoice code and neighboring definitions were never supplied.

The regular **Prune Selected Code** also uses exactly the highlighted fragment.
Direct selected pruning does not expand dependencies or retrieve related tests.
The fragment can therefore omit imports, constants, or callers needed to explain
it. Source excluded by selection was not removed by the model.

Both operations capture a buffer snapshot before waiting for the backend. Source
line coordinates show the original excerpt location. Scores correspond to lines
of the supplied fragment. The registered managed backend URL is used rather than
an assumed fixed port.

### Threshold Experiment

Repeat the exact entire-file input with threshold `0.85`. Keep task, source,
and preservation settings unchanged. Compare the actual line scores, masks, and
final text with the `0.45` run.

Higher thresholds generally retain fewer scored lines, but formatting and
preservation affect final text. Do not promise a particular percentage or
specific removed line. A tiny relevant excerpt can legitimately remain intact.
Record whether necessary evidence was lost, not just how much text disappeared.

### What to Say

> This input is exactly the captured file or fragment. The task conditions
> neural line relevance. Unlike repository mode, no extra file is retrieved.
> Selecting less input and pruning supplied input are different operations.

## 7. How Neural Line Pruning Works

The local pretrained query/document model returns token-level relevance logits
and a document-level relevance score. Token logits pass through sigmoid; source
offset mappings associate tokens with lines. TokenWise averages the scores of
constituent scored tokens for each line:

```text
line relevance = mean(relevance of scored tokens belonging to the line)
initial line decision = line relevance >= threshold
```

These are task-conditioned model scores, not a correctness proof or calibrated
probability that a line is necessary. Repository file-ranking scores combine
other evidence and are not the same quantity.

Depending on settings, preservation can retain the first line. The mask can
bridge one-line gaps. Formatting may restore short removed ranges where a marker
would be larger, and treats blank lines specially. That is why the table says
**decision mask includes preservation and gap bridging, before output formatting**. `keptFrags`
is not guaranteed exact membership in final displayed text.

Long source is chunked with overlap. Scores for duplicate source offsets are
averaged before line aggregation. The current wrapper uses an 8,192-token model
input window and 50-token document overlap. Source offsets, not approximate text
search, map scores back to code. The panel displays up to 200 lines; JSON export
retains the full returned scores.

Repository packing can trim source after neural selection. Its applied threshold
describes the neural step, not the final budget cutoff.

Pruned text is **context**, not executable replacement code. Omissions and markers
can make it incomplete or syntactically invalid. TokenWise does not insert it
into your file automatically.

## 8. Scenario C: Earlier Conversation Context

A follow-up such as `Which tests cover that behavior?` does not identify the
behavior by itself. Show whether earlier intent changes the actual retrieval/
pruning objective, not merely the final agent's answer.

### Controlled Replay

Open `demonstration/01_account_security`.

1. Run **Demonstrate Pruning Inputs**.
2. Choose **Conversation: replay earlier user context**.
3. Supply the earlier user task:
   `Explain account lockout after failed login attempts and its related tests.`
4. Supply the current task: `Which tests cover that behavior?`
5. Use threshold `0.45`.
6. Show conversation-informed mode and **Supplied replay (not live chat capture)**.
7. Expand Earlier user reference and Inference objective. The lockout subject
   should be present in the actual effective objective.
8. Inspect source/tests and export the run.

The replay uses the real backend, but you deliberately supply an earlier task.
It does **not capture Antigravity chat automatically**. Label it as replay.

For a negative control, run repository mode with only the ambiguous follow-up
and no reference. Missing-subject clarification or a limited result is expected.

For a topic-switch control, replay the lockout task but use the self-contained
current query `Explain session expiry boundary tests.` The backend ignores the
unrelated hint; repository mode with no history is then intentional.

### Live Same-Chat Test

Start a new actual Antigravity chat in the account-security project:

```text
Explain account lockout after failed login attempts and its related tests.
Do not modify any files.
```

Then, in that same chat:

```text
What about its expiry boundary?
```

Then:

```text
Which tests cover that behavior?
```

For each retrieval inspect actual current tool output and the fresh
`.tokenwise/latest.json`. Distinguish these integration paths:

| Path | How history reaches pruning | What the backend can show |
| --- | --- | --- |
| Native PreInvocation hook | Bounded earlier user turns, scoped by workspace/conversation ID | `native_scoped_user_turns`, reference, and effective objective |
| Stable-build rule/tool fallback | Agent resolves the reference into a self-contained query | That current query, not the raw earlier transcript |

Native state retains at most **three earlier user turns** for the current topic,
within **2,000 combined characters**. With more turns, it preserves the topic
opening and the most recent two. Text can be truncated to enforce the bound.
Only recognized referring follow-ups reuse it; explicit tasks reset the topic.

A nonempty conversation ID is required. Without one, reuse is disabled. State
is workspace-scoped too. Records from another conversation, model/assistant
answers, and injected context are not treated as authoritative remembered intent.
An unresolved referring question does not become a new remembered topic.

Fallback rules request the same bounded current-topic user intent when rewriting
a query, or clarification if its subject is missing. Their execution depends on
the agent following the rule. The backend cannot certify how a fallback agent
constructed its query or claim access to the full Antigravity chat.

### Isolation Controls

1. Ask a self-contained new topic in the same chat. Inspect a fresh objective;
   unrelated lockout history should not remain attached.
2. Start a **new chat** and ask only `Which tests cover that behavior?`.
   It should clarify the missing subject, not silently reuse another chat's topic.
3. Open a different demo leaf project and start a fresh chat. Verify included
   paths belong to it and previous topics are not inherited.

If the agent asks for clarification without running a tool, there is no new
retrieval event. An old status item is not proof of history leakage. Check event
IDs, timestamps, and the actual chat call.

### What to Say

> Earlier user intent can resolve a referring follow-up and change retrieval
> and the pruning objective. This is bounded same-topic context, not permanent
> model learning or memory shared across unrelated chats. Assistant answers are
> not trusted as user requirements.

## 9. Honest Metrics

Compression alone is not usefulness. Removing a relevant boundary check can
reduce tokens while making the answer worse. Compare evidence against source/tests.

### Token Counts

- Source/retained source: before/after supplied or included source.
- Packed tokens: complete formatted repository context including wrapper/fences.
- Formatting overhead: wrapper contribution, not removed source.
- Raw context: matched formatted bundle with unpruned included source.
- Model input tokens: query/code input count, not measured total computation across
  overlapping chunks, repository passes, or final agent requests.

Keeping 17 source tokens in a 117-token packet means **0% source reduction and
100 tokens overhead**, not -588.24% useful savings. Report actual expansion as
an increase. A selected excerpt's counts do not describe the entire repository.

### Carbon Estimates

Selected-source predictions use backend-native original/retained source counts.
Repository predictions use matched formatted bundles. Identify that different
baseline before comparing these values.

Both sides keep the configured target model, output-token assumption, hardware
scenario, and carbon intensity fixed. These are approximate SEAL-derived scenario
predictions, **not measured provider emissions**, local pruning energy, or proven
net environmental savings. The actual agent model is not detected automatically.

Pending, disabled, unavailable, zero savings, and actual increases are legitimate.
A carbon error does not discard prepared context. No fixture guarantees savings.

## 10. Evidence and Presentation Schedule

Use [the blank worksheet](demonstration/results-template.md). Record actual task,
scope, reference/history source, objective, thresholds, methods, scores, omissions,
tokens, timing, and errors. Attach exported Pruning Run JSON and dated screenshots.

A live-integration claim also needs the actual chat's current tool output.
A result panel or saved status count alone is insufficient.

Private transcripts should only be retained with consent. Generated results
under `demonstration/results/` are ignored by Git. Do not commit secrets or
full private chat logs.

The native-hook verifier uses a **generated USER transcript** and real local
HTTP/model calls. Its report says `verification_only: true` and
`antigravity_cloud_called: false`. It does not prove live cloud-agent behavior
or grade semantic answers.

| Time | Demonstration | Main point |
| --- | --- | --- |
| 0-2 minutes | Explain pipeline and input modes | Task-dependent context preparation |
| 2-5 minutes | Repository, no editor hint | Automatic discovery, bounded processing |
| 5-8 minutes | Whole file, excerpt, two thresholds | Scope versus actual line pruning |
| 8-11 minutes | History replay and negative control | Earlier intent changes the objective |
| 11-13 minutes | Rehearsed same-chat/new-chat test | Real integration and isolation |
| 13-15 minutes | Metrics, omissions, executable tests | Quality and honest limitations |

Warm the backend before class. Keep dated recorded runs as a fallback for slow
startup or connectivity, but label them as recorded, not current live activity.

## 11. Defense Questions

**What determines what gets removed?**
The effective task and supplied scope. Selected mode uses mean neural line
relevance and threshold/preservation/formatting rules. Repository mode first
discovers candidates and uses several representation branches before packing.

**Does no selection mean every file enters the model?**
No. Indexed source is searchable; candidate limits, interfaces, short bodies,
and capped neural passes bound processing.

**Does selecting a fragment add its dependencies?**
Not in direct selected-source pruning. Repository retrieval is a separate path.

**Does history affect pruning or just the final answer?**
For recognized follow-ups, it enters the actual effective retrieval/pruning
objective. Show that objective. Fallback can provide a resolved query instead;
the backend does not see that path's raw earlier chat.

**Does TokenWise remember all chats?**
No. Native state is bounded and workspace/conversation-scoped. Explicit topics
replace older ones. Separate chats are isolated.

**Why can a low-scoring line remain?**
Preservation, gap bridging, and output formatting. The mask and final context
are distinct; subsequent repository packing can remove retained source too.

**Why not maximize reduction?**
Necessary evidence can be lost. Evaluate correctness and omissions as well as size.

**Why are overviews different?**
They preserve representative architecture and bounded root documentation, rather
than apply narrow neural pruning to generic words such as PROJECT.

**Did you train the neural model from scratch?**
This implementation integrates pretrained SWE-pruner. Your contribution includes
retrieval/indexing, task preparation, bounded packing, Antigravity integration,
managed setup, tracing, and evaluation. Credit upstream model/code and carbon
work; do not claim their training as your own.

**Is it universal or guaranteed?**
No. The beta targets trusted local Python repositories and is Windows-tested.
Remote/virtual workspaces, arbitrary coreference, native macOS/Linux validation,
perfect retrieval, and guaranteed cloud-agent rule compliance remain limitations.

## 12. Optional Literal Context-Packet Comparison

If the teacher wants to compare *what reaches the final agent*, use
**TokenWise: Compare Context Strategies**, available from 0.6.2 onward:

| Strategy | Packet |
| --- | --- |
| All Python | Unpruned eligible indexed Python, with explicit export size limits |
| Selected | Unpruned saved file or excerpt |
| TokenWise | Retrieved, bounded context with no hidden selection anchor |

The unpruned Selected baseline is **not** the neural selected-source experiment
in Section 6. All Python excludes ignored paths and non-Python source; it does
not mean every project asset. The command counts packets and estimates a fixed
carbon scenario. It does not automatically grade answers.

For a controlled context-only quality trial:

1. Export the three packets from one unchanged snapshot and task.
2. Open `baseline_lab`, with no application source and no TokenWise integration.
3. Use independent fresh chats, same model/settings/global rules, and rotate order.
4. Paste one packet and the same task; require answers only from supplied evidence,
   no tools or file reads, and explicit missing-evidence statements.
5. Check the tool log. Extra reads violate a context-only protocol.
6. Define expected facts from the runnable source/tests before scoring answers.
   Record supported facts, unsupported claims, and omissions separately.

A tool-assisted answer can be evaluated as a separate workflow, but not silently
mixed into context-only scores. Source-marker diagnostics are not semantic grades.
Four small fixtures do not prove universal superiority.

## 13. Troubleshooting and Cleanup

| Symptom | Check / retry |
| --- | --- |
| New command missing | Install 0.6.3, reload the correct window/profile |
| Input trace unavailable | Update/restart the matching Python backend |
| Slow first run | Warm backend; separate cold loading from warm preparation |
| Replay uses no history | Explicit tasks intentionally ignore hints; use a recognized follow-up |
| No native history label | Stable builds may use rule fallback; inspect its resolved query |
| New-chat prompt has no fresh event | Agent may clarify without retrieval; old status is not a new event |
| Selected output lacks dependencies | Exact selected mode does not retrieve extra source |
| Tiny excerpt is not reduced | All supplied lines can be relevant; inspect scores |
| CO2 unavailable | Check settings/artifacts/health and record the visible error |
| Wrong project source | Open the leaf folder, begin a fresh chat |
| Unsaved edits absent in retrieval | Indexing reads saved disk files; selected mode captures the buffer |

Setup preserves unrelated rules/settings. Set `enabled: false` in
`.agents/tokenwise.json` to temporarily disable automatic retrieval/indexing, or
use **Remove All Local Data** to remove owned integration when finished. Customized
or unrecognized files are preserved rather than deleted indiscriminately.

## 14. Closing Statement

> TokenWise prepares task-relevant Python context locally. With no selected file,
> it discovers repository evidence and packs bounded excerpts. With selected
> source, it prunes exactly that scope. For a referring same-chat follow-up,
> bounded earlier user intent can change the retrieval/pruning objective.
> I show actual inputs and decisions, distinguish replay from live integration,
> and evaluate omissions as well as token savings.
